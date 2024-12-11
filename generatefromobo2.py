import re
import pprint
import os
import requests
import time

# Replace with your TogetherAI API Key
# Set your Together API key
TOGETHER_API_KEY = "4070baa3baed3400f79377ea3b4221f2024725f970bbf02dd0b6d4fba2175bc6"

def parse_symptoms_as_strings(response: str) -> list:
    """
    Parses symptoms from a response and stores them as strings with name, description, synonyms concatenated.
    
    Args:
        response (str): The input string containing symptom data formatted with tags.
        start_id (str): The start tag ID for the symptom data.
        end_id (str): The end tag ID for the symptom data.

    Returns:
        list: A list of strings, each containing symptom name, description, synonyms, and monologues.
    """
    # Define a regular expression pattern to extract symptom details using dynamic start and end tags
    symptom_pattern = re.compile(
        rf"<{start_id}>(.*?)</{start_id}>\s*"
        rf"<start_description>(.*?)</start_description>\s*"
        rf"<start_synonyms>(.*?)</start_synonyms>\s*"
        rf"<start_monologues>(.*?)</start_monologues>"
    )
    
    # Find all matches in the input response
    matches = symptom_pattern.findall(response)
    
    # Convert each match into a concatenated string and enclose in <symptom></symptom>
    symptoms = []
    for match in matches:
        symptom_str = f"<symptom>Name: {match[0].strip()}, Description: {match[1].strip()}, Synonyms: {match[2].strip()}, Monologues: {match[3].strip()}</symptom>"
        symptoms.append(symptom_str)
    
    return symptoms

def parse_symptoms_as_strings_with_indices(response: str) -> list:
    """
    Parses symptoms from a response, including their start and end character indices in the string.
    
    Args:
        response (str): The input string containing symptom data formatted with tags.

    Returns:
        list: A list of dictionaries, each containing:
              - start_index: The starting character index of the symptom in the string.
              - end_index: The ending character index of the symptom in the string.
              - symptom: The formatted string containing symptom details.
    """
    # Define a regular expression pattern to extract symptom details
    symptom_pattern = re.compile(
        r"<start_symptom_name>(.*?)</start_symptom_name>\s*"
        r"<start_description>(.*?)</start_description>\s*"
        r"<start_synonyms>(.*?)</start_synonyms>\s*"
        r"<start_monologues>(.*?)</start_monologues>",
        re.DOTALL
    )
    
    # Find all matches in the input response with their indices
    matches = symptom_pattern.finditer(response)
    
    symptoms = []
    for match in matches:
        start_index = match.start()
        end_index = match.end()
        symptom_details = {
            "start_index": start_index,
            "end_index": end_index,
            "symptom": f"<symptom>Name: {match.group(1).strip()}, "
                       f"Description: {match.group(2).strip()}, "
                       f"Synonyms: {match.group(3).strip()}, "
                       f"Monologues: {match.group(4).strip()}</symptom>"
        }
        symptoms.append(symptom_details)
    
    return symptoms

def save_symptoms_to_file(symptoms: list, filename: str):
    """
    Saves the formatted symptoms as chunks to a text file.
    
    Args:
        symptoms (list): List of symptoms to save.
        filename (str): The name of the file where the symptoms will be saved.
    """
    with open(filename, 'w') as file:
        for symptom in symptoms:
            file.write(symptom + '\n')
            
# Function to parse OBO format entries into a dictionary
def parse_obo_to_dict(entries: str) -> list:
    terms = []
    current_term = {}
    
    for line in entries.strip().split("\n"):
        try:
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
        except:
            pass

    if current_term:
        terms.append(current_term)

    return terms

# Function to generate medical data using TogetherAI for each category and save it in a text file
def generate_medical_data_with_togetherAI(categories, disease_name, output_file="medical_data.txt"):
    results = {}
    with open(output_file, "w", encoding="utf-8") as file:
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
                print(f"{category}:\n{content}\n")
                results[category] = content
                
                # Write content to text file
                file.write(f"### {category} ###\n")
                file.write(content + "\n\n")
            else:
                error_message = f"Error for {category}: {response.text}"
                print(error_message)
                results[category] = "Error generating data."
                
                # Write error to text file
                file.write(f"### {category} ###\n")
                file.write("Error generating data.\n\n")
    
    print(f"Medical data saved to {output_file}")
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
def parse_obo_to_dict_from_file(file_path: str) -> list:
    """
    Parses OBO format entries from a file and returns a list of terms as dictionaries.
    
    Args:
        file_path (str): The path to the OBO file.
    
    Returns:
        list: A list of dictionaries representing the terms in the OBO file.
    """
    with open(file_path, 'r') as file:
        entries = file.read()  # Read the content of the file
        #print(entries)
    return parse_obo_to_dict(entries)  # Use the existing parse_obo_to_dict function

# Example of using the function with a file path
obo_file_path = './src/ontology/doid.obo'  # Replace with your file path
parsed_terms = parse_obo_to_dict_from_file(obo_file_path)

# Add medical data structure to each term
for term in parsed_terms:
    term["categories"] = medical_data_structure

print(parsed_terms)


# Generate detailed data for each term and print the results
pp = pprint.PrettyPrinter(indent=2)
# List of unwanted terms to skip
UNWANTED_TERMS = {"allergic", "allergy", "gene", "unknown", "generic"}

curr_terms = 0
max_terms = len(parsed_terms)
def download_things():
    global parsed_terms, curr_terms
    curr_terms = 0
    for term in parsed_terms:
        # Get the disease name and sanitize it
        disease_name = term.get("name", "Unknown Disease").replace("/", "_")
        definition = term.get("def", "Unknown Definition")
        subset = term.get("subset", "Unknown Definition")
        
        
        # Skip unwanted terms
        if any(unwanted in disease_name.lower() for unwanted in UNWANTED_TERMS):
            #print(f"Skipping unwanted term: {disease_name}")
            continue
        
        if any(unwanted in definition.lower() for unwanted in UNWANTED_TERMS):
            #print(f"Skipping unwanted term: {disease_name}")
            continue
        
        if subset != "NCIthesaurus":
            continue
            
        file_path = f"./disease_symptoms/{disease_name}.txt"
        if os.path.exists(file_path):
            print("File exists.", file_path)
        else:
            print("File does not exist.")
            if disease_name != "Unknown Disease":
                print(f"Generating data for: {disease_name}")
                detailed_data = generate_medical_data_with_togetherAI(term["categories"], disease_name, output_file=f"./disease_symptoms/{disease_name}.txt")
                if detailed_data["Formatted Symptoms"]:
                    print("Parsing")
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_content = file.read()
                        #print(file)
                        temp = parse_symptoms_as_strings_with_indices(file_content)
                        for i in temp:
                            print(i, "\n")
                term["detailed_data"] = detailed_data
        curr_terms += 1

while curr_terms < max_terms:
    curr_terms = 0
    try:
        download_things()
    except:
        pass
    print("Retrying", curr_terms)
    time.sleep(2)
    