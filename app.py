from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from model import load_model, predict

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16384
model = load_model()


@app.get("/")
def home():
    return render_template("home.html")


@app.post("/predict")
def predict_form():
    try:
        value = predict(request.form.to_dict(), model)
    except ValueError as error:
        return render_template("home.html", error=str(error), values=request.form.to_dict()), 400
    return render_template("home.html", pred_1="Estimated historical dataset price:", pred_2=f"{value:.2f}$", values=request.form.to_dict())


@app.post("/predict_api")
def predict_api():
    try:
        return jsonify(predict(request.get_json(), model))
    except (BadRequest, UnsupportedMediaType):
        return jsonify(error="Send a valid JSON object with Content-Type application/json"), 400
    except ValueError as error:
        return jsonify(error=str(error), values=request.form.to_dict()), 400


@app.get("/health")
def health():
    return jsonify(status="ok", model_schema=model["schema_version"])


if __name__ == "__main__":
    app.run(host="127.0.0.1")
