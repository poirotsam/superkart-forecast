"""
SuperKart Flask backend – online + batch inference.
 
Endpoints
---------
GET  /                    Health check
POST /v1/predict          Single-record inference
POST /v1/predictbatch     Batch inference on a CSV file
"""
 
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import io
import os
 
# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
MODEL_PATH = os.environ.get("SUPERKART_MODEL", "superkart_model.joblib")
model = joblib.load(MODEL_PATH)
 
EXPECTED_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]
 
superkart_api = Flask(__name__)
 
 
# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def validate_columns(df: pd.DataFrame) -> None:
    """Raise ValueError if any expected column is missing."""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
 
 
# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@superkart_api.get("/")
def health():
    return {"status": "ok", "service": "SuperKart Sales Forecast API"}
 
 
@superkart_api.post("/v1/predict")
def predict_single():
    """Online (single-record) inference."""
    try:
        payload = request.get_json(force=True)
        row = pd.DataFrame([payload])
        validate_columns(row)
        row = row[EXPECTED_COLUMNS]
        pred = float(model.predict(row)[0])
        return jsonify({"predicted_sales": round(pred, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
 
 
@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """Batch inference — consumes an uploaded CSV file (`file` key)."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Please upload the CSV with key 'file'"}), 400
        f = request.files["file"]
        content = f.read().decode("utf-8")
        batch_df = pd.read_csv(io.StringIO(content))
        validate_columns(batch_df)
        batch_df = batch_df[EXPECTED_COLUMNS]
        preds = model.predict(batch_df).round(2).tolist()
        # Return {"0": 2842.4, "1": 1985.7, ...} to match assignment sample
        return jsonify({str(i): p for i, p in enumerate(preds)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
 
 
# ---------------------------------------------------------------------------
# Local dev entry-point (production uses gunicorn – see Dockerfile)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
