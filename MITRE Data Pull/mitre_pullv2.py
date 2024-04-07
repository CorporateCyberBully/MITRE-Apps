# Import required libraries
from attackcti import attack_client
import pandas as pd
from datetime import datetime

# Initialize the client
lift = attack_client()

# Fetch all techniques
techniques = lift.get_techniques()

# Initialize an empty list to hold our extracted data
data = []

# Loop through each technique and extract the details
for technique in techniques:
    # Some techniques may not have all fields, so we use .get() to avoid KeyError
    t_id = technique.get('external_references')[0].get('external_id') if technique.get('external_references') else 'N/A'
    t_name = technique.get('name', 'N/A')
    t_description = technique.get('description', 'N/A').replace('\n', ' ').replace('\r', '')  # Clean up newlines for CSV compatibility

    # Append the tactic, technique ID, and description to our data list
    data.append([t_id, t_name, t_description])

# Convert our data list to a pandas DataFrame
df = pd.DataFrame(data, columns=['ID', 'Name', 'Description'])

# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')

# Write the DataFrame to a CSV file with the current date as prefix
filename = f'{current_date}_mitre_attack_techniques.csv'
df.to_csv(filename, index=False)

print(f"CSV file '{filename}' has been created.")
