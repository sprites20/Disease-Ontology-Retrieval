import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# Load only the first 1000 rows from the CSV
csv_file = 'D:/pyfiles/HumanDiseaseOntology-main/HumanDiseaseOntology-main/Lokahi_Innovation_in_Healthcare_Hackahton/Lokahi_Innovation_in_Healthcare_Hackahton/Claims_Services/combined_data_enrollment.csv'  # replace with your actual CSV file path
df = pd.read_csv(csv_file, nrows=10000)  # This will read the first 1000 rows

# Initialize a graph
G = nx.Graph()

# Initialize a counter for term frequency
term_freq = Counter()

# Process each row and add edges to the graph
for _, row in df.iterrows():
    term1 = row['DIAG_CCS_1_LABEL']
    term2 = row['DIAG_CCS_2_LABEL']
    term3 = row['DIAG_CCS_3_LABEL']
    if pd.isna(term1) or pd.isna(term2) or pd.isna(term3):
        continue  # Skip this row if any term is NaN

    # Add edges between the terms
    G.add_edge(term1, term2)
    G.add_edge(term2, term3)

    # Update term frequencies
    term_freq[term1] += 1
    term_freq[term2] += 1
    term_freq[term3] += 1

# Set node size based on frequency (larger for more frequent terms)
node_sizes = [term_freq[node] * 10 for node in G.nodes]
# Generate a unique color for each node (using a color map)
colors = np.random.rand(len(G.nodes))  # Random colors for each node

# Create the layout
pos = nx.spring_layout(G, k=0.3, iterations=50)

# Create the figure
plt.figure(figsize=(12, 12))

# Draw the graph with random node colors and smaller fonts
nx.draw(
    G, 
    pos, 
    with_labels=True, 
    node_size=node_sizes, 
    node_color=colors,  # Set the random colors
    cmap=plt.cm.Pastel1,  # Lighter colormap
    font_size=4,  # Smaller font size for readability
    font_weight='bold', 
    edge_color='gray'
)

# Display the plot with the title
plt.title("Term Connections from First 1000 Rows with Frequency-based Node Size")
plt.show()  # Ensure this is present to keep the plot window open
