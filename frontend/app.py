import streamlit as st
import requests
import pandas as pd
import io
import os

# Configure Streamlit page layout and title
st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")
st.title(" SuperKart Sales Forecasting & Predictive System")
st.write("Operationalize your sales predictions using our interactive machine learning deployment portal.")

# Retrieve backend URL from environment variables (defaults to codespace port 5000)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:5000")

# Sidebar Navigation
option = st.sidebar.selectbox("Select Mode", ["Single Prediction (Online)", "Batch Prediction (CSV)"])

if option == "Single Prediction (Online)":
    st.header("Single Product Store Sales Prediction")
    st.write("Input the required product and store attributes below:")

    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.0)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0, value=0.05)
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=100.0)
        product_id_char = st.selectbox("Product ID Character prefix", ["FD", "DR", "NC"])

    with col2:
        store_size = st.selectbox("Store Size", ["Medium", "High", "Low"])
        store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
        store_age_years = st.number_input("Store Age (Years)", min_value=0, value=15)
        product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age_years),
            "Product_Type_Category": product_type_category
        }

        try:
            res = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
            if res.status_code == 200:
                prediction = res.json().get("prediction", 0.0)
                st.success(f"Predicted Product Store Sales Total: ${prediction:,.2f}")
            else:
                st.error(f"Error from API: {res.text}")
        except Exception as e:
            st.error(f"Could not reach prediction API backend. Exception: {e}")

elif option == "Batch Prediction (CSV)":
    st.header("Batch Sales Prediction via CSV Upload")
    st.write("Upload a CSV file containing all features needed for predictions:")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read and display uploaded CSV structure
        try:
            df_preview = pd.read_csv(uploaded_file)
            st.dataframe(df_preview.head(5))

            # Reset pointer and prepare payload file
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}

            if st.button("Generate Batch Predictions"):
                with st.spinner("Processing batch predictions..."):
                    res = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files)

                if res.status_code == 200:
                    predictions_dict = res.json()
                    # Map predictions back to the preview dataset
                    pred_list = [predictions_dict[str(i)] for i in range(len(predictions_dict))]
                    df_preview["Predicted_Sales"] = pred_list

                    st.success("Predictions generated successfully!")
                    st.dataframe(df_preview)

                    # Enable download of complete results
                    output_csv = df_preview.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Prediction Results",
                        data=output_csv,
                        file_name="superkart_predictions.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Error from API: {res.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
