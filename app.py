import os
import json
import uuid
import time
from flask import Flask, request, render_template, redirect, url_for, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename

import config
from agents import vision, color, audience, copywriter, guardrails, cta_optimizer, rag, assistant

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
DOC_ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}

_run_store = {}  # run_id → {output, image_filename}
RUN_LOG = "run_log.jsonl"


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_doc(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in DOC_ALLOWED_EXTENSIONS


def _log_run(output: dict, pipeline_s: float) -> None:
    cta = output.get("cta_analysis", {})
    scores = [cta.get(k, {}).get("score", 0) for k in ("variant_1", "variant_2")]
    valid_scores = [s for s in scores if s]
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_id": output.get("run_id", ""),
        "model_used": output.get("vision", {}).get("model_used", ""),
        "pipeline_s": round(pipeline_s, 1),
        "compliance_flags": len(output.get("compliance_flags", [])),
        "cta_score_avg": avg_score,
        "rag_chunks_used": output.get("rag_chunks_used", 0),
        "persona": output.get("audience", {}).get("persona_label", ""),
    }
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _check_models_on_startup() -> None:
    import requests as req
    try:
        resp = req.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        tags = {m["name"] for m in resp.json().get("models", [])}
        needed = {config.OLLAMA_MODEL, config.OLLAMA_FAST_MODEL}
        missing = needed - tags
        if missing:
            print(f"[STARTUP WARNING] Ollama models not found: {missing}")
        else:
            print(f"[STARTUP OK] Ollama models ready: {', '.join(needed)}")
    except Exception as e:
        print(f"[STARTUP WARNING] Cannot reach Ollama at {config.OLLAMA_URL}: {e}")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if "image" not in request.files:
        return redirect(url_for("index"))
    file = request.files["image"]
    description = request.form.get("description", "").strip()
    tone = request.form.get("tone", "energetic").strip()

    if not file or file.filename == "" or not allowed_file(file.filename):
        return redirect(url_for("index"))
    if not description:
        return redirect(url_for("index"))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(image_path)

    run_id = str(uuid.uuid4())[:8]

    def _stream():
        t_start = time.time()
        try:
            yield 'data: {"step":"vision","label":"Analyzing product image..."}\n\n'
            color_data = color.extract(image_path)
            vision_data = vision.analyze(image_path, description)

            yield 'data: {"step":"audience","label":"Segmenting target audience..."}\n\n'
            rag_query = description + " " + " ".join(vision_data.get("product_tags", []))
            doc_context = rag.retrieve(rag_query)
            audience_data = audience.segment(description, vision_data, doc_context=doc_context)

            yield 'data: {"step":"copywriter","label":"Writing ad variants..."}\n\n'
            raw_copy = copywriter.generate(
                description, vision_data, color_data, tone, audience_data, doc_context=doc_context
            )

            yield 'data: {"step":"guardrails","label":"Checking compliance..."}\n\n'
            result = guardrails.check(raw_copy)

            yield 'data: {"step":"cta","label":"Optimizing CTAs..."}\n\n'
            cta_result = cta_optimizer.optimize(
                result["clean_copy"], tone, audience_data, doc_context=doc_context
            )

            pipeline_s = time.time() - t_start
            output = {
                "run_id": run_id,
                "meta": {"tone": tone, "description": description},
                "vision": vision_data,
                "colors": color_data,
                "audience": audience_data,
                "ads": result["clean_copy"],
                "cta_analysis": cta_result,
                "compliance_flags": result["flags"],
                "rag_chunks_used": len(doc_context),
                "pipeline_s": round(pipeline_s, 1),
            }
            _run_store[run_id] = {"output": output, "image_filename": filename}
            _log_run(output, pipeline_s)

            yield f'data: {{"step":"done","run_id":"{run_id}","pipeline_s":{round(pipeline_s,1)}}}\n\n'
        except Exception as e:
            msg = str(e).replace('"', "'")
            yield f'data: {{"step":"error","message":"{msg}"}}\n\n'

    return Response(
        stream_with_context(_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/result/<run_id>")
def result(run_id):
    entry = _run_store.get(run_id)
    if not entry:
        return redirect(url_for("index"))
    return render_template("result.html", output=entry["output"], image_filename=entry["image_filename"])


@app.route("/export/<run_id>")
def export_campaign(run_id):
    entry = _run_store.get(run_id)
    if not entry:
        return jsonify({"error": "Run not found or server was restarted"}), 404
    return app.response_class(
        json.dumps(entry["output"], indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename=campaign_{run_id}.json"},
    )


@app.route("/health")
def health():
    import requests as req
    ollama_ok = False
    try:
        r = req.get(f"{config.OLLAMA_URL}/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    status = "ok" if ollama_ok else "degraded"
    return jsonify({"status": status, "ollama": ollama_ok, "runs_in_memory": len(_run_store)})


@app.route("/stats")
def stats():
    if not os.path.exists(RUN_LOG):
        return jsonify({"runs": 0, "avg_pipeline_s": 0, "avg_cta_score": 0, "compliance_rate": 0})
    with open(RUN_LOG, encoding="utf-8") as f:
        lines = [json.loads(ln) for ln in f if ln.strip()]
    if not lines:
        return jsonify({"runs": 0, "avg_pipeline_s": 0, "avg_cta_score": 0, "compliance_rate": 0})
    return jsonify({
        "runs": len(lines),
        "avg_pipeline_s": round(sum(l["pipeline_s"] for l in lines) / len(lines), 1),
        "avg_cta_score": round(sum(l["cta_score_avg"] for l in lines) / len(lines), 1),
        "compliance_rate": round(sum(1 for l in lines if l["compliance_flags"] > 0) / len(lines), 2),
        "recent": lines[-5:][::-1],
    })


@app.route("/docs", methods=["GET"])
def docs():
    documents = rag.list_documents()
    return render_template("docs.html", documents=documents)


@app.route("/ingest-docs", methods=["POST"])
def ingest_docs():
    files = request.files.getlist("docs")
    os.makedirs(config.DOC_UPLOAD_FOLDER, exist_ok=True)

    saved_paths = []
    for f in files:
        if f and f.filename and allowed_doc(f.filename):
            filename = secure_filename(f.filename)
            dest = os.path.join(config.DOC_UPLOAD_FOLDER, filename)
            f.save(dest)
            saved_paths.append(dest)

    result = rag.ingest_files(saved_paths) if saved_paths else {"ingested": 0, "skipped": 0}
    return redirect(url_for("docs", ingested=result.get("ingested", 0), skipped=result.get("skipped", 0)))


@app.route("/suggest", methods=["POST"])
def suggest():
    data = request.get_json(force=True, silent=True)
    if not data or "output" not in data:
        return jsonify({"message": "Could not analyze campaign output."}), 400
    try:
        message = assistant.suggest(data["output"])
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"message": f"Suggestion service unavailable: {e}"}), 200


@app.route("/refine", methods=["POST"])
def refine():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    current_output = data.get("output_state", {})
    user_message   = data.get("user_message", "").strip()
    tone_val       = int(data.get("tone", 3))
    age_val        = int(data.get("age", 35))
    formality_val  = int(data.get("formality", 3))
    chat_history   = data.get("chat_history", [])

    routing = assistant.get_routing(
        current_output, user_message, tone_val, age_val, formality_val, chat_history
    )
    agents_to_run = routing["agents_to_run"]

    params = assistant.map_sliders_to_params(tone_val, age_val, formality_val)
    tone_str        = params["tone"]
    age_hint        = params["age_hint"]
    formality_instr = params["formality_instruction"]

    updated_output = dict(current_output)
    updated_output["meta"] = dict(current_output.get("meta", {}))
    updated_output["meta"]["tone"] = tone_str

    description = current_output.get("meta", {}).get("description", "")
    vision_data = current_output.get("vision", {})
    color_data  = current_output.get("colors", {})

    doc_context = []
    if agents_to_run:
        rag_query = description + " " + " ".join(vision_data.get("product_tags", []))
        doc_context = rag.retrieve(rag_query)
        updated_output["rag_chunks_used"] = len(doc_context)

    audience_data = current_output.get("audience", {})

    if "audience" in agents_to_run:
        augmented_vision = dict(vision_data)
        augmented_vision["target_signals"] = list(
            vision_data.get("target_signals", [])
        ) + [f"target age group: {age_hint}"]
        audience_data = audience.segment(description, augmented_vision, doc_context=doc_context)
        updated_output["audience"] = audience_data

    ads_dict = current_output.get("ads", {})

    if "copywriter" in agents_to_run:
        effective_tone = f"{tone_str}. Writing style: {formality_instr}"
        ads_dict = copywriter.generate(
            description, vision_data, color_data,
            effective_tone, audience_data, doc_context=doc_context
        )

    guardrails_result = {
        "clean_copy": ads_dict,
        "flags": current_output.get("compliance_flags", []),
    }

    if "guardrails" in agents_to_run:
        guardrails_result = guardrails.check(ads_dict)
        updated_output["ads"] = guardrails_result["clean_copy"]
        updated_output["compliance_flags"] = guardrails_result["flags"]

    if "cta_optimizer" in agents_to_run:
        cta_result = cta_optimizer.optimize(
            guardrails_result["clean_copy"], tone_str, audience_data, doc_context=doc_context
        )
        updated_output["cta_analysis"] = cta_result

    assistant_message = _build_assistant_reply(
        routing["reasoning"], agents_to_run, updated_output
    )

    return jsonify({
        "output": updated_output,
        "routing_label": routing["routing_label"],
        "reasoning": routing["reasoning"],
        "assistant_message": assistant_message,
    })


def _build_assistant_reply(reasoning: str, agents_ran: list, updated_output: dict) -> str:
    parts = [reasoning]
    if "audience" in agents_ran:
        persona = updated_output.get("audience", {}).get("persona_label", "")
        if persona:
            parts.append(f"Updated audience persona: {persona}.")
    if "copywriter" in agents_ran:
        parts.append("Ad copy variants regenerated.")
    if "cta_optimizer" in agents_ran:
        cta = updated_output.get("cta_analysis", {})
        scores = [
            str(cta.get(k, {}).get("score", ""))
            for k in ("variant_1", "variant_2")
            if cta.get(k, {}).get("score") is not None
        ]
        if scores:
            parts.append(f"New CTA scores: {' / '.join(scores)} out of 10.")
    flags = updated_output.get("compliance_flags", [])
    if flags:
        parts.append(f"Note: {len(flags)} compliance flag(s) detected.")
    return " ".join(parts)


if __name__ == "__main__":
    _check_models_on_startup()
    app.run(debug=True)
