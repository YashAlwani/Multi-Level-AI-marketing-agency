import os
import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

import config
from agents import vision, color, audience, copywriter, guardrails, cta_optimizer, rag, assistant

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
DOC_ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_doc(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in DOC_ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # --- Validate inputs ---
    if "image" not in request.files:
        return redirect(url_for("index"))
    file = request.files["image"]
    description = request.form.get("description", "").strip()
    tone = request.form.get("tone", "energetic").strip()

    if not file or file.filename == "" or not allowed_file(file.filename):
        return redirect(url_for("index"))
    if not description:
        return redirect(url_for("index"))

    # --- Save upload ---
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(image_path)

    # --- Agent pipeline ---
    color_data = color.extract(image_path)
    vision_data = vision.analyze(image_path, description)

    rag_query = description + " " + " ".join(vision_data.get("product_tags", []))
    doc_context = rag.retrieve(rag_query)

    audience_data = audience.segment(description, vision_data, doc_context=doc_context)
    raw_copy = copywriter.generate(description, vision_data, color_data, tone, audience_data, doc_context=doc_context)
    result = guardrails.check(raw_copy)
    cta_result = cta_optimizer.optimize(result["clean_copy"], tone, audience_data, doc_context=doc_context)

    output = {
        "meta": {"tone": tone, "description": description},
        "vision": vision_data,
        "colors": color_data,
        "audience": audience_data,
        "ads": result["clean_copy"],
        "cta_analysis": cta_result,
        "compliance_flags": result["flags"],
        "rag_chunks_used": len(doc_context),
    }

    return render_template("result.html", output=output, image_filename=filename)


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

    # Step 1: ReAct routing decision
    routing = assistant.get_routing(
        current_output, user_message, tone_val, age_val, formality_val, chat_history
    )
    agents_to_run = routing["agents_to_run"]

    # Step 2: Map sliders to agent params
    params = assistant.map_sliders_to_params(tone_val, age_val, formality_val)
    tone_str        = params["tone"]
    age_hint        = params["age_hint"]
    formality_instr = params["formality_instruction"]

    # Step 3: Start from current output, selectively overwrite
    updated_output = dict(current_output)
    updated_output["meta"] = dict(current_output.get("meta", {}))
    updated_output["meta"]["tone"] = tone_str

    description = current_output.get("meta", {}).get("description", "")
    vision_data = current_output.get("vision", {})
    color_data  = current_output.get("colors", {})

    # RAG: re-retrieve whenever any agent is running
    doc_context = []
    if agents_to_run:
        rag_query = description + " " + " ".join(vision_data.get("product_tags", []))
        doc_context = rag.retrieve(rag_query)
        updated_output["rag_chunks_used"] = len(doc_context)

    # Step 4: Run selected agents in pipeline order
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
    app.run(debug=True)
