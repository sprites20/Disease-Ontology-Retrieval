from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your Together API key
TOGETHER_API_KEY = "4070baa3baed3400f79377ea3b4221f2024725f970bbf02dd0b6d4fba2175bc6"

# Define the categories
categories = [
    "Medical Data and Diagnostics",
    "Treatment",
    "Medication",
    "Epidemiology and Prevalence",
    "Pathophysiology",
    "Risk Factors",
    "Diagnosis and Screening",
    "Prognosis and Complications",
    "Prevention",
    "History and Background",
    "Global and Societal Impact",
    "Patient Experience and Quality of Life",
    "Research and Innovations",
    "Genetics and Inheritance Patterns",
    "Healthcare Management and Policy",
    "Symptoms",
    
]

categories = [
  "Meal Plan",               
  "Medication Plan",         
  "Daily Schedule and Tasks"
]
  
# Function to call TogetherAI API and generate medical data for a given category
def generate_medical_data_with_togetherAI(category, disease_name):
    prompt = f"Generate a detailed description for the '{category}' category related to the disease '{disease_name}'. Provide clear and medically accurate information."

    message_array = [
        {"role": "system", "content": "You are a medical expert tasked with generating medically accurate and detailed information for diseases in various categories."},
        {"role": "user", "content": prompt}
    ]

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Interact with the LLM (this can take time, so it runs asynchronously)
    response = requests.post(
        'https://api.together.xyz/v1/chat/completions',
        headers=headers,
        json={
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": message_array
        }
    )
    data = response.json()
    print(data['choices'][0]['message']['content'].strip())
    
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        return "Error generating data."

@app.route('/api/generate-medical-data', methods=['POST'])
def generate_medical_data():
    data = request.get_json()
    disease_name = data.get('diseaseName')

    if not disease_name:
        return jsonify({"error": "Disease name is required"}), 400

    medical_data = {}
    for category in categories:
        medical_data[category] = generate_medical_data_with_togetherAI(category, disease_name)
        print(medical_data[category])

    return jsonify(medical_data)

if __name__ == '__main__':
    app.run(debug=True)
