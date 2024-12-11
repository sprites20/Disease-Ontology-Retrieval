import os
import re
import shelve
import pickle

# Define the folder containing the files
folder_path = "./somepath"  # Replace this with the actual folder path

# Regex patterns for extracting multiple symptoms and their details
symptom_pattern = re.compile(
    r"<start_symptom_name>(.*?)</start_symptom_name>.*?<start_synonyms>(.*?)</start_synonyms>",
    re.DOTALL,
)


# Define pickle file for storing counters
counter_file = "counters.pickle"

# Load counters from pickle file if it exists
def load_counters():
    if os.path.exists(counter_file):
        with open(counter_file, "rb") as f:
            return pickle.load(f)
    else:
        # Return initial counters if pickle file does not exist
        return {
            "symptom_counter": 1,
            "disease_counter": 1
        }

# Save counters to pickle file
def save_counters(counters):
    with open(counter_file, "wb") as f:
        pickle.dump(counters, f)

# Load counters
counters = load_counters()
symptom_counter = counters["symptom_counter"]
disease_counter = counters["disease_counter"]

# Open shelves to store the dictionaries
with shelve.open("symptom_to_number", writeback=True) as symptom_to_number_db, \
     shelve.open("number_to_symptom", writeback=True) as number_to_symptom_db, \
     shelve.open("number_to_synonyms", writeback=True) as number_to_synonyms_db, \
     shelve.open("disease_to_number", writeback=True) as disease_to_number_db, \
     shelve.open("number_to_disease", writeback=True) as number_to_disease_db, \
     shelve.open("symptom_to_disease", writeback=True) as symptom_to_disease_db:
    print("Opened")

    # Iterate through files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        print(file_path)

        # Ensure it's a file (not a directory)
        if os.path.isfile(file_path):
            # Extract disease name from the file name (remove extension if present)
            disease_name = os.path.splitext(file_name)[0].strip()

            # Map the disease name to a unique number if not already mapped
            if disease_name not in disease_to_number_db:
                disease_to_number_db[disease_name] = str(disease_counter)
                number_to_disease_db[str(disease_counter)] = disease_name
                disease_counter += 1
                # Save counters after adding a new disease
                save_counters({"symptom_counter": symptom_counter, "disease_counter": disease_counter})
            else:
                print("Exists")
                continue
            # Retrieve the current disease number
            disease_number = disease_to_number_db[disease_name]

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Find all symptoms and their synonyms in the content
                matches = symptom_pattern.findall(content)
                for symptom_name, synonyms in matches:
                    symptom_name = symptom_name.strip().lower()
                    synonyms_list = [synonym.strip().lower() for synonym in synonyms.split(",")]

                    # Map the symptom name to a unique number if not already mapped
                    if symptom_name not in symptom_to_number_db:
                        symptom_to_number_db[symptom_name] = str(symptom_counter)
                        number_to_symptom_db[str(symptom_counter)] = symptom_name
                        symptom_counter += 1
                        # Save counters after adding a new symptom
                        save_counters({"symptom_counter": symptom_counter, "disease_counter": disease_counter})

                    # Retrieve the current symptom number
                    symptom_number = str(symptom_to_number_db[symptom_name])

                    # Map the symptom to the current disease
                    symptom_diseases = symptom_to_disease_db.get(symptom_number, set())
                    symptom_diseases.add(disease_number)
                    symptom_to_disease_db[symptom_number] = symptom_diseases

                    # Update synonyms for the symptom
                    synonym_numbers = number_to_synonyms_db.get(symptom_number, [])
                    for synonym in synonyms_list:
                        # Map synonym to a unique number if not already mapped
                        if synonym not in symptom_to_number_db:
                            symptom_to_number_db[synonym] = str(symptom_counter)
                            number_to_symptom_db[str(symptom_counter)] = synonym
                            synonym_numbers.append(str(symptom_counter))
                            symptom_counter += 1
                            # Save counters after adding a new synonym
                            save_counters({"symptom_counter": symptom_counter, "disease_counter": disease_counter})
                        else:
                            synonym_numbers.append(symptom_to_number_db[synonym])

                        # Retrieve the current synonym number
                        synonym_number = symptom_to_number_db[synonym]

                        # Map the synonym to the current disease
                        synonym_diseases = symptom_to_disease_db.get(synonym_number, set())
                        synonym_diseases.add(disease_number)
                        symptom_to_disease_db[synonym_number] = synonym_diseases

                    # Remove duplicates from synonym numbers and update the shelf
                    number_to_synonyms_db[symptom_number] = list(set(synonym_numbers))

    print("All mappings have been successfully stored in the shelves.")

    # Save counters one last time after processing all files
    save_counters({"symptom_counter": symptom_counter, "disease_counter": disease_counter})

# Function to retrieve symptom number by name
def get_symptom_number(symptom_name):
    with shelve.open("symptom_to_number") as symptom_to_number_db:
        return symptom_to_number_db.get(symptom_name, None)

# Function to retrieve symptom name by number
def get_symptom_name_by_number(symptom_number):
    with shelve.open("number_to_symptom") as number_to_symptom_db:
        return number_to_symptom_db.get(symptom_number, None)

# Function to retrieve synonyms by symptom number
def get_synonyms_by_number(symptom_number):
    with shelve.open("number_to_synonyms") as number_to_synonyms_db:
        return number_to_synonyms_db.get(symptom_number, [])

# Function to retrieve disease number by name
def get_disease_number(disease_name):
    with shelve.open("disease_to_number") as disease_to_number_db:
        return disease_to_number_db.get(disease_name, None)

# Function to retrieve disease name by number
def get_disease_name_by_number(disease_number):
    with shelve.open("number_to_disease") as number_to_disease_db:
        return number_to_disease_db.get(disease_number, None)

# Function to retrieve symptom-to-disease mappings
def get_diseases_by_symptom(symptom_name):
    with shelve.open("symptom_to_number") as symptom_to_number_db, \
         shelve.open("symptom_to_disease") as symptom_to_disease_db, \
         shelve.open("number_to_disease") as number_to_disease_db:
        symptom_number = symptom_to_number_db.get(symptom_name, None)
        if symptom_number:
            disease_numbers = symptom_to_disease_db.get(symptom_number, [])
            return [number_to_disease_db.get(disease_number, None) for disease_number in disease_numbers]
        return []


# File names for bidirectional mapping
key_to_value_file = 'key_to_value.db'  # pdf_file -> doc_id
value_to_key_file = 'value_to_key.db'  # doc_id -> pdf_file

def load_doc_mapping_by_key(pdf_file):
    """Load a single document mapping using the pdf_file (key)."""
    try:
        with shelve.open(key_to_value_file, flag='r') as db:
            # Return the doc_id for the given pdf_file, or None if not found
            return db.get(pdf_file, None)
    except (FileNotFoundError, KeyError) as e:
        # If the file doesn't exist or the key is not found, handle it gracefully
        print(f"Error loading mapping for '{pdf_file}' by key: {e}")
        return None

def load_doc_mapping_by_value(doc_id):
    """Load a single document mapping using the doc_id (value)."""
    try:
        with shelve.open(value_to_key_file, flag='r') as db:
            # Return the pdf_file for the given doc_id, or None if not found
            return db.get(doc_id, None)
    except (FileNotFoundError, KeyError) as e:
        # If the file doesn't exist or the key is not found, handle it gracefully
        print(f"Error loading mapping for doc_id '{doc_id}' by value: {e}")
        return None

def delete_doc_mapping_by_key(pdf_file):
    """Delete a specific document mapping using the pdf_file (key)."""
    try:
        # Key to value (pdf_file -> doc_id)
        with shelve.open(key_to_value_file, flag='c') as key_db:
            if pdf_file in key_db:
                doc_id = key_db.pop(pdf_file)  # Delete the mapping for the given file
                print(f"Deleted mapping for '{pdf_file}' -> {doc_id}.")
            else:
                print(f"No mapping found for '{pdf_file}' in key-to-value database.")
        
        # Value to key (doc_id -> pdf_file)
        with shelve.open(value_to_key_file, flag='c') as value_db:
            # If the key is deleted, ensure the reverse mapping is also deleted
            with shelve.open(key_to_value_file, flag='r') as key_db:
                doc_id = key_db.get(pdf_file, None)
                if doc_id and doc_id in value_db:
                    value_db.pop(doc_id)  # Delete the reverse mapping for the doc_id
                    print(f"Deleted mapping for doc_id {doc_id} -> '{pdf_file}' from value-to-key database.")
                else:
                    print(f"No reverse mapping found for doc_id {doc_id} in value-to-key database.")
    
    except KeyError as e:
        print(f"Error: The key '{pdf_file}' was not found in the database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while deleting mapping: {e}")

def delete_doc_mapping_by_value(doc_id):
    """Delete a specific document mapping using the doc_id (value)."""
    try:
        # Value to key (doc_id -> pdf_file)
        with shelve.open(value_to_key_file, flag='c') as value_db:
            if doc_id in value_db:
                pdf_file = value_db.pop(doc_id)  # Delete the reverse mapping for the doc_id
                print(f"Deleted mapping for doc_id {doc_id} -> '{pdf_file}'.")
            else:
                print(f"No mapping found for doc_id {doc_id} in value-to-key database.")
        
        # Key to value (pdf_file -> doc_id)
        with shelve.open(key_to_value_file, flag='c') as key_db:
            # If the value is deleted, ensure the key mapping is also deleted
            with shelve.open(value_to_key_file, flag='r') as value_db:
                pdf_file = value_db.get(doc_id, None)
                if pdf_file and pdf_file in key_db:
                    key_db.pop(pdf_file)  # Delete the mapping for the given file
                    print(f"Deleted mapping for '{pdf_file}' -> {doc_id} from key-to-value database.")
                else:
                    print(f"No reverse mapping found for '{pdf_file}' in key-to-value database.")
    
    except KeyError as e:
        print(f"Error: The doc_id '{doc_id}' was not found in the database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while deleting mapping: {e}")

def check_key_exists(pdf_file):
    """Check if a pdf_file exists in the key-to-value mapping (key file)."""
    try:
        with shelve.open(key_to_value_file, flag='r') as db:
            return pdf_file in db  # Return True if the key exists, else False
    except (FileNotFoundError, KeyError) as e:
        print(f"Error checking existence of '{pdf_file}': {e}")
        return False

def check_value_exists(doc_id):
    """Check if a doc_id exists in the value-to-key mapping (value file)."""
    try:
        with shelve.open(value_to_key_file, flag='r') as db:
            return str(doc_id) in db  # Return True if the value exists, else False
    except (FileNotFoundError, KeyError) as e:
        print(f"Error checking existence of doc_id '{doc_id}': {e}")
        return False

print("Some stuff")
# Example usage
symptom_name = "Joint Pain"
disease_name = "arthritis"
disease_text = "autosomal dominant nocturnal frontal lobe epilepsy 1.txt"
print(f"Loading doc {disease_name}, {load_doc_mapping_by_key(disease_text)}")

print(get_disease_name_by_number("1"))
# Retrieve disease number
disease_number = get_disease_number(disease_name)
if disease_number:
    print(f"Disease Number for {disease_name}: {disease_number}")
else:
    print(f"Disease '{disease_name}' not found.")

# Retrieve diseases by symptom name
diseases = get_diseases_by_symptom(symptom_name)
if diseases:
    print(f"Diseases associated with symptom '{symptom_name}': {diseases}")
else:
    print(f"No diseases found for symptom '{symptom_name}'.")


symptom_name = "Joint Pain"
symptom_number = get_symptom_number(symptom_name)
if symptom_number:
    print(f"Symptom Number for {symptom_name}: {symptom_number}")
    synonyms = get_synonyms_by_number(symptom_number)
    print(f"Synonyms for {symptom_name} (Number {symptom_number}): {synonyms}")
    for i in synonyms:
        print(get_symptom_name_by_number(i))
    # Retrieve the symptom name by number (reverse lookup)
    retrieved_symptom_name = get_symptom_name_by_number(symptom_number)
    print(f"Symptom name for Number {symptom_number}: {retrieved_symptom_name}")
else:
    print(f"Symptom '{symptom_name}' not found.")
