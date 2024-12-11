import re

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


# Example usage
response = """
<start_symptom_name>Headache</start_symptom_name>
<start_description>A pain in the head that may be mild or severe.</start_description>
<start_synonyms>Cephalalgia</start_synonyms>
<start_monologues>Occurs frequently with stress or illness.</start_monologues>
<start_symptom_name>Fever</start_symptom_name>
<start_description>An elevated body temperature often caused by an infection.</start_description>
<start_synonyms>Pyrexia, Hyperthermia</start_synonyms>
<start_monologues>Usually accompanied by chills and sweating.</start_monologues>
"""

# Parse symptoms with indices
symptoms_with_indices = parse_symptoms_as_strings_with_indices(response)

# Print the parsed symptoms with indices
for symptom in symptoms_with_indices:
    print(symptom)
