import os
import json
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

import config
from agents import vision, color, audience, copywriter, guardrails, cta_optimizer

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    audience_data = audience.segment(description, vision_data)
    raw_copy = copywriter.generate(description, vision_data, color_data, tone, audience_data)
    result = guardrails.check(raw_copy)
    cta_result = cta_optimizer.optimize(result["clean_copy"], tone, audience_data)

    output = {
        "meta": {"tone": tone, "description": description},
        "vision": vision_data,
        "colors": color_data,
        "audience": audience_data,
        "ads": result["clean_copy"],
        "cta_analysis": cta_result,
        "compliance_flags": result["flags"],
    }

    return render_template("result.html", output=output, image_filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
