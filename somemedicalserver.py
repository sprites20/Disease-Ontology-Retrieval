from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your Together API key
TOGETHER_API_KEY = "4070baa3baed3400f79377ea3b4221f2024725f970bbf02dd0b6d4fba2175bc6"

# Define default categories (if needed for fallback)
default_categories = [
    "Meal Plan",
    "Medication Plan",
    "Daily Schedule and Tasks"
]

def generate_plan(category, diseases, age, sex, weight, activity_level):
    prompt = f"""
    Generate a detailed '{category}' for the following conditions: {', '.join(diseases)}.
    The person is {age} years old, {sex}, weighs {weight} kg, and has an activity level of {activity_level}.
    Provide medically accurate recommendations tailored to these details.
    """

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        'https://api.together.xyz/v1/chat/completions',
        headers=headers,
        json={
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    if response.status_code == 200:
        return response.json().get('choices')[0].get('message').get('content', "No data available.")
    else:
        return "Error generating plan."

@app.route('/api/generate-medical-data', methods=['POST'])
def generate_medical_data():
    try:
        data = request.get_json()
        diseases = data.get('diseases', [])
        age = data.get('age')
        sex = data.get('sex')
        weight = data.get('weight')
        activity_level = data.get('activityLevel')
        selected_categories = data.get('categories', [])

        if not diseases or not age or not sex or not weight or not activity_level:
            return jsonify({"error": "All fields are required"}), 400

        if not selected_categories:
            return jsonify({"error": "At least one category must be selected"}), 400

        result = {}
        for category in selected_categories:
            result[category] = generate_plan(category, diseases, age, sex, weight, activity_level)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')  # Allow Lambda to properly route
