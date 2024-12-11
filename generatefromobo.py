import re
import pprint
import requests

# Replace with your TogetherAI API Key
# Set your Together API key
TOGETHER_API_KEY = "4070baa3baed3400f79377ea3b4221f2024725f970bbf02dd0b6d4fba2175bc6"

def parse_symptoms_as_strings(response: str) -> list:
    """
    Parses symptoms from a response and stores them as strings with name, description, and synonyms concatenated.
    
    Args:
        response (str): The input string containing symptom data formatted with tags.

    Returns:
        list: A list of strings, each containing symptom name, description, and synonyms.
    """
    # Define a regular expression pattern to extract symptom details
    symptom_pattern = re.compile(
        r"<start_symptom_name>(.*?)</start_symptom_name>\s*"
        r"<start_description>(.*?)</start_description>\s*"
        r"<start_synonyms>(.*?)</start_synonyms>\s*"
        r"<start_monologues>(.*?)</start_monologues>"
    )
    
    # Find all matches
    matches = symptom_pattern.findall(response)
    
    # Convert matches into concatenated strings
    symptoms = []
    for match in matches:
        symptom_str = f"Name: {match[0].strip()}, Description: {match[1].strip()}, Synonyms: {match[2].strip()}, Monologues: {match[3].strip()}"
        symptoms.append(symptom_str)
    
    return symptoms
    
# Function to parse OBO format entries into a dictionary
def parse_obo_to_dict(entries: str) -> list:
    terms = []
    current_term = {}
    
    for line in entries.strip().split("\n"):
        line = line.strip()
        
        if line.startswith("[Term]"):
            if current_term:
                terms.append(current_term)
                current_term = {}
        elif line:
            key, value = line.split(": ", 1)
            
            if key == "def":
                # Extract definition and any URLs (allowing multiple)
                def_match = re.findall(r'"(.*?)" \[url:(.*?)\]', value)
                if def_match:
                    current_term[key] = def_match[0][0]  # The definition
                    current_term["urls"] = [url for _, url in def_match]  # Collect all URLs
                    comment_match = re.search(r'\{comment="(.*?)"\}', value)
                    if comment_match:
                        current_term["comment"] = comment_match.group(1)  # Extract comment
                else:
                    current_term[key] = value
            else:
                if key not in current_term:
                    current_term[key] = value
                else:
                    if isinstance(current_term[key], list):
                        current_term[key].append(value)
                    else:
                        current_term[key] = [current_term[key], value]

    if current_term:
        terms.append(current_term)

    return terms

# Function to generate medical data using TogetherAI for each category
def generate_medical_data_with_togetherAI(categories, disease_name):
    results = {}
    for category, description in categories.items():
        prompt = f"Generate a detailed description for the '{category}' category related to the disease '{disease_name}'. {description}"
        
        message_array = [
            {"role": "system", "content": "You are a medical expert tasked with generating medically accurate and detailed information for diseases in various categories."},
            {"role": "user", "content": prompt}
        ]
        
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            'https://api.together.xyz/v1/chat/completions',
            headers=headers,
            json={
                "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "messages": message_array
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            print(content)
            results[category] = content
        else:
            print(f"Error for {category}: {response.text}")
            results[category] = "Error generating data."
    
    return results

# Medical data structure with categories
medical_data_structure = {
    "Medical Data and Diagnostics": "Includes tests and evaluations relevant to the disease.",
    "Treatment": "Descriptions of available treatments and interventions.",
    "Medication": "Information about medications related to the disease.",
    "Epidemiology and Prevalence": "Data regarding the occurrence and distribution of the disease.",
    "Pathophysiology": "Explanation of the physiological changes associated with the disease.",
    "Risk Factors": "Factors that may increase the likelihood of developing the disease.",
    "Diagnosis and Screening": "Methods for diagnosing and screening for the disease.",
    "Prognosis and Complications": "Expected outcomes and potential complications associated with the disease.",
    "Prevention": "Strategies to prevent the disease.",
    "History and Background": "Historical context and background information about the disease.",
    "Global and Societal Impact": "Effects of the disease on society and global health.",
    "Patient Experience and Quality of Life": "Insights into the patient experience and quality of life.",
    "Research and Innovations": "Current research trends and innovations related to the disease.",
    "Genetics and Inheritance Patterns": "Genetic aspects and inheritance patterns relevant to the disease.",
    "Healthcare Management and Policy": "Information on healthcare management and policies related to the disease.",
    "Symptoms": "Descriptions of the symptoms associated with the disease"
}

medical_data_structure = {
    "Formatted Symptoms": "Descriptions of the symptoms associated with the disease. format <start_symptom_name>Symptom Name</start_symptom_name> <start_description>Description</start_description><start_synonyms>Synonyms</start_synonyms><start_monologues>What patients might report</start_monologues>. Make symptoms specific, dont answer with a general disease, just each symptom"
}

# Example OBO input
obo_entries = """
[Term]
id: DOID:0040004
name: pneumonia
def: "A beta-lactam allergy that has_allergic_trigger amoxicillin." [url:https://www.ncbi.nlm.nih.gov/pubmed/11746950] {comment="IEDB:RV"}
subset: DO_IEDB_slim
xref: SNOMEDCT_US_2023_03_01:294505008
xref: UMLS_CUI:C0571417
is_a: DOID:0060519 ! beta-lactam allergy

"""

# Parse entries into a list of dictionaries
parsed_terms = parse_obo_to_dict(obo_entries)

# Add medical data structure to each term
for term in parsed_terms:
    term["categories"] = medical_data_structure

# Generate detailed data for each term and print the results
pp = pprint.PrettyPrinter(indent=2)

for term in parsed_terms:
    disease_name = term.get("name", "Unknown Disease")
    print(f"Generating data for: {disease_name}")
    detailed_data = generate_medical_data_with_togetherAI(term["categories"], disease_name)
    if detailed_data["Formatted Symptoms"]:
        print("Parsing")
        temp = parse_symptoms_as_strings(detailed_data["Formatted Symptoms"])
        for i in temp:
        
            print(i, "\n")
    term["detailed_data"] = detailed_data
"""
# Pretty print the terms with detailed data
for term in parsed_terms:
    pp.pprint(term)
"""

#Workflow
#We generate symptom queries based on what the user says.
