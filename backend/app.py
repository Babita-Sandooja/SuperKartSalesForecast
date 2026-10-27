import os
import joblib
import pandas as pd
import io
from flask import Flask, request, jsonify

# Instantiate the Flask application
app = Flask(__name__)

# Load the pre-trained ML model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'superkart_model.joblib')
model = joblib.load(MODEL_PATH)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/v1/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        # Convert request payload to DataFrame
        df_input = pd.DataFrame([data])
        prediction = model.predict(df_input)[0]
        return jsonify({"prediction": float(prediction)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/v1/predictbatch', methods=['POST'])
def predict_batch():
    try:
        # Check if a file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        # Read the CSV content from uploaded file bytes
        csv_data = file.read().decode('utf-8')
        df_input = pd.read_csv(io.StringIO(csv_data))

        predictions = model.predict(df_input)
        # Map indices to predictions as a dictionary response
        results = {str(i): float(pred) for i, pred in enumerate(predictions)}
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
