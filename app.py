import os
import json
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

import config
from agents import vision, color, audience, copywriter, guardrails, cta_optimizer, rag

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


if __name__ == "__main__":
    app.run(debug=True)
