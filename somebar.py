import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

# Path to the CSV file
csv_file = 'D:/pyfiles/HumanDiseaseOntology-main/HumanDiseaseOntology-main/Lokahi_Innovation_in_Healthcare_Hackahton/Lokahi_Innovation_in_Healthcare_Hackahton/Claims_Services/combined_data_enrollment.csv'

# Initialize counters for term frequencies
counter_1 = Counter()
counter_2 = Counter()
counter_3 = Counter()

# Process the file in chunks
chunksize = 1_000_000  # Read 1 million rows at a time
for chunk in pd.read_csv(csv_file, chunksize=chunksize):
    # Drop rows with NaN values in relevant columns
    chunk = chunk.dropna(subset=['MEMBER_ID', 'DIAG_CCS_1_LABEL', 'DIAG_CCS_2_LABEL', 'DIAG_CCS_3_LABEL'])
    
    # Combine MEMBER_ID and each label column to form unique keys
    chunk['unique_1'] = chunk[['MEMBER_ID', 'DIAG_CCS_1_LABEL']].astype(str).agg('-'.join, axis=1)
    chunk['unique_2'] = chunk[['MEMBER_ID', 'DIAG_CCS_2_LABEL']].astype(str).agg('-'.join, axis=1)
    chunk['unique_3'] = chunk[['MEMBER_ID', 'DIAG_CCS_3_LABEL']].astype(str).agg('-'.join, axis=1)

    # Count occurrences of each unique combination in the chunk
    unique_counts_1 = chunk['unique_1'].value_counts()
    unique_counts_2 = chunk['unique_2'].value_counts()
    unique_counts_3 = chunk['unique_3'].value_counts()

    # Filter to keep only rows with unique combinations
    filtered_1 = chunk[chunk['unique_1'].isin(unique_counts_1[unique_counts_1 == 1].index)]
    filtered_2 = chunk[chunk['unique_2'].isin(unique_counts_2[unique_counts_2 == 1].index)]
    filtered_3 = chunk[chunk['unique_3'].isin(unique_counts_3[unique_counts_3 == 1].index)]
    
    # Update term frequencies for each label
    counter_1.update(filtered_1['DIAG_CCS_1_LABEL'])
    counter_2.update(filtered_2['DIAG_CCS_2_LABEL'])
    counter_3.update(filtered_3['DIAG_CCS_3_LABEL'])


def count_label_occurrences(csv_file, label_column, output_csv, chunksize=1_000_000):
    """
    Counts the occurrences of a specific label in a CSV file and saves the results to a CSV.

    Args:
        csv_file (str): Path to the CSV file.
        label_column (str): The column name of the label to count occurrences.
        output_csv (str): Path to save the CSV with label counts.
        chunksize (int): Number of rows to process per chunk (default is 1,000,000).
    """
    counter = Counter()  # Initialize counter for label frequencies
    
    for chunk in pd.read_csv(csv_file, chunksize=chunksize):
        # Drop rows with NaN values in the specified column
        chunk = chunk.dropna(subset=[label_column])
        
        # Update the counter with the occurrences in the current chunk
        counter.update(chunk[label_column])
    
    # Convert the counter to a DataFrame and sort by count
    label_counts = pd.DataFrame(counter.items(), columns=['Label', 'Count'])
    label_counts = label_counts.sort_values(by='Count', ascending=False)
    
    # Save the results to a CSV file
    label_counts.to_csv(output_csv, index=False)

    print(f"Counts for {label_column} saved to {output_csv}.")


# Plot the final aggregated results
def plot_frequencies(counter, title, ax):
    most_common_terms = counter.most_common(20)  # Top 20 terms
    terms, frequencies = zip(*most_common_terms) if most_common_terms else ([], [])
    
    ax.bar(terms, frequencies, color='skyblue')
    ax.set_title(title)
    ax.set_xticklabels(terms, rotation=45, ha='right')
    ax.set_xlabel('Terms')
    ax.set_ylabel('Frequency')

# Create subplots for each label
fig, axs = plt.subplots(3, 1, figsize=(10, 18))

# Plot for DIAG_CCS_1_LABEL
plot_frequencies(counter_1, 'Top 20 Unique Terms in DIAG_CCS_1_LABEL', axs[0])

# Plot for DIAG_CCS_2_LABEL
plot_frequencies(counter_2, 'Top 20 Unique Terms in DIAG_CCS_2_LABEL', axs[1])

# Plot for DIAG_CCS_3_LABEL
plot_frequencies(counter_3, 'Top 20 Unique Terms in DIAG_CCS_3_LABEL', axs[2])

# Adjust layout
plt.tight_layout()
plt.show()

# Save term frequencies to CSV files
def save_frequencies_to_csv(counter, filename):
    # Convert the Counter to a DataFrame
    df = pd.DataFrame(counter.items(), columns=['Term', 'Frequency'])
    # Sort the DataFrame by frequency in descending order
    df = df.sort_values(by='Frequency', ascending=False)
    # Save to a CSV file
    df.to_csv(filename, index=False)

# Save term frequencies for each label
save_frequencies_to_csv(counter_1, 'DIAG_CCS_1_LABEL_frequencies.csv')
save_frequencies_to_csv(counter_2, 'DIAG_CCS_2_LABEL_frequencies.csv')
save_frequencies_to_csv(counter_3, 'DIAG_CCS_3_LABEL_frequencies.csv')

# Define file path, label column, and output CSV
csv_file = 'D:/pyfiles/HumanDiseaseOntology-main/HumanDiseaseOntology-main/Lokahi_Innovation_in_Healthcare_Hackahton/Lokahi_Innovation_in_Healthcare_Hackahton/Claims_Services/combined_data_enrollment.csv'
label_column = 'CPT_CCS_LABEL'
output_csv = 'CPT_CCS_LABEL_counts.csv'

# Call the function
count_label_occurrences(csv_file, label_column, output_csv)