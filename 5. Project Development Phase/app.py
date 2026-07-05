from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

FEATURES = [
    {"name": "Temp", "label": "Temperature (°C)", "placeholder": "28"},
    {"name": "Humidity", "label": "Humidity (%)", "placeholder": "75"},
    {"name": "Cloud Cover", "label": "Cloud Cover (%)", "placeholder": "40"},
    {"name": "ANNUAL", "label": "Annual Rainfall (mm)", "placeholder": "3326.6"},
    {"name": "Jan-Feb", "label": "Jan-Feb Rainfall (mm)", "placeholder": "9.3"},
    {"name": "Mar-May", "label": "Mar-May Rainfall (mm)", "placeholder": "275.7"},
    {"name": "Jun-Sep", "label": "Jun-Sep Rainfall (mm)", "placeholder": "2403.4"},
    {"name": "Oct-Dec", "label": "Oct-Dec Rainfall (mm)", "placeholder": "638.2"},
    {"name": "avgjune", "label": "Avg June Rainfall (mm)", "placeholder": "130.3"},
    {"name": "sub", "label": "Seasonal Flood Index", "placeholder": "256.4"}
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "floods.save")
scaler_path = os.path.join(BASE_DIR, "transform.save")
load_error = None

try:
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
    else:
        model = None
        scaler = None
        load_error = "Saved model or scaler file not found. Run train_model.py first."
except Exception as exc:
    model = None
    scaler = None
    load_error = str(exc)

@app.route('/')
def home():
    return render_template('home.html')

def build_input_dataframe(data):
    values = [float(data.get(feature['name'], 0)) for feature in FEATURES]
    return pd.DataFrame([values], columns=[feature['name'] for feature in FEATURES])


def compute_risk_scores(X_scaled):
    if model is None or scaler is None:
        raise RuntimeError(load_error or "Prediction assets are missing.")

    if not hasattr(model, 'predict_proba'):
        raise RuntimeError('Loaded model does not support probability estimates.')

    probability = float(model.predict_proba(X_scaled)[0][1]) * 100
    risk_score = round(probability, 2)
    safe_score = round(100 - probability, 2)

    if risk_score >= 70:
        status = "High risk"
    elif risk_score >= 40:
        status = "Moderate risk"
    else:
        status = "Safe"

    return risk_score, safe_score, status


@app.route('/api/predict', methods=['POST'])
def api_predict():
    if model is None or scaler is None:
        return jsonify({"error": load_error or "Prediction assets are missing."}), 500

    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()

    try:
        X = build_input_dataframe(data)
        X_scaled = scaler.transform(X)
        risk_score, safe_score, status = compute_risk_scores(X_scaled)

        return jsonify({
            "risk": risk_score,
            "safe": safe_score,
            "status": status,
            "model": type(model).__name__
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('index.html', features=FEATURES)

    if model is None or scaler is None:
        return render_template('index.html', features=FEATURES, error=load_error or 'Prediction assets are missing.')

    try:
        data = request.form.to_dict()
        X = build_input_dataframe(data)
        X_scaled = scaler.transform(X)
        risk_score, safe_score, status = compute_risk_scores(X_scaled)

        if risk_score >= 70:
            return render_template('chance.html', risk=risk_score)
        return render_template('no_chance.html', safety=safe_score)
    except Exception as exc:
        return render_template('index.html', features=FEATURES, error=str(exc))


if __name__ == '__main__':
    app.run(debug=True)