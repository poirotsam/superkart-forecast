"""
SuperKart Streamlit UI – calls the Flask API for single & batch predictions.
"""
 
import os
import io
import json
import requests
import pandas as pd
import streamlit as st
 
# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------
# Inside a Docker network the backend service name is 'backend'
API_ROOT = os.environ.get("API_ROOT", "http://backend:7860")
PREDICT_URL  = f"{API_ROOT}/v1/predict"
BATCH_URL    = f"{API_ROOT}/v1/predictbatch"
 
st.set_page_config(page_title="SuperKart Sales Forecaster",
                   page_icon="🛒", layout="wide")
 
st.title("🛒 SuperKart Sales Forecaster")
st.markdown("**Predict product-level sales revenue for the upcoming quarter.**")
 
tab_single, tab_batch = st.tabs(["Online (single SKU)", "Batch (CSV upload)"])
 
# ---------------------------------------------------------------------------
# Online inference tab
# ---------------------------------------------------------------------------
with tab_single:
    st.subheader("Single-product prediction")
 
    col1, col2, col3 = st.columns(3)
    with col1:
        product_weight = st.number_input("Product Weight", 3.0, 25.0, 12.66, step=0.1)
        product_allocated_area = st.number_input("Product Allocated Area",
                                                 0.001, 0.500, 0.027, step=0.001)
        product_mrp = st.number_input("Product MRP", 30.0, 300.0, 117.08, step=0.5)
    with col2:
        product_sugar_content = st.selectbox("Sugar Content",
                                             ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = st.selectbox("Product Category Prefix",
                                       ["FD", "DR", "NC"])
        product_type_category = st.selectbox("Product Type Category",
                                             ["Perishables", "Non Perishables"])
    with col3:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("Store Location City Type",
                                                ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type",
                                  ["Departmental Store", "Supermarket Type1",
                                   "Supermarket Type2", "Food Mart"])
        store_age_years = st.slider("Store Age (Years)", 0, 50, 16)
 
    if st.button("🔮 Predict Sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }
        try:
            r = requests.post(PREDICT_URL, json=payload, timeout=30)
            r.raise_for_status()
            pred = r.json().get("predicted_sales")
            st.success(f"Predicted Sales: **₹ {pred:,.2f}**")
            st.json(payload)
        except Exception as e:
            st.error(f"API call failed: {e}")
 
# ---------------------------------------------------------------------------
# Batch inference tab
# ---------------------------------------------------------------------------
with tab_batch:
    st.subheader("Batch prediction (upload CSV)")
    st.markdown(
        """Upload a CSV with these columns:  
        `Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP,
         Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char,
         Store_Age_Years, Product_Type_Category`."""
    )
    up = st.file_uploader("Choose a CSV file", type=["csv"])
    if up is not None:
        df = pd.read_csv(up)
        st.write("**Preview**", df.head())
        if st.button("🚚 Send to API"):
            try:
                files = {"file": ("batch.csv",
                                  df.to_csv(index=False).encode("utf-8"))}
                r = requests.post(BATCH_URL, files=files, timeout=120)
                r.raise_for_status()
                preds = r.json()
                out = df.copy()
                out["Predicted_Sales"] = [preds[str(i)] for i in range(len(out))]
                st.success(f"Received {len(out)} predictions")
                st.dataframe(out)
                st.download_button("⬇️ Download predictions",
                                   data=out.to_csv(index=False).encode("utf-8"),
                                   file_name="superkart_predictions.csv",
                                   mime="text/csv")
            except Exception as e:
                st.error(f"Batch call failed: {e}")
