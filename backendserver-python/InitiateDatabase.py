import os
import json
from pymongo import MongoClient

# Navigating to 'attack-pattern' folder where all the attack patterns files are stored.
parent_folder: str = os.path.abspath(os.path.join(os.getcwd(), '..'))
target_folder: str = os.path.join(parent_folder, 'attack-pattern')

# Creating an empty list for the attack.
attacks: list[dict[str, str]] = []

for root, dirs, files in os.walk(target_folder):
    for file_name in files:
        with open(os.path.join(root, file_name), 'r') as file:
            
            # Loading each file's content as a json dictionary
            json_data: dict[str, str] = json.loads(file.read())

            json_data: dict[str, str] = json_data['objects'][0]

            # Getting the data from the json
            id: str = json_data.get('id', 'NA').replace('attack-pattern--', '')
            name: str = json_data.get('name', 'NA')
            description: str = json_data.get('description', 'NA')
            x_mitre_platforms: list[str] = json_data.get('x_mitre_platforms', 'NA')
            x_mitre_detection: list[dict[str, str]] = json_data.get('x_mitre_detection', 'NA')
            phase_names: dict[str, str] = json_data.get('kill_chain_phases', 'NA')[-1]
            phase_name: str= phase_names.get('phase_name', 'NA')
            result: dict[str, str] = {'id': id, 'name': name, 'description': description, 'x_mitre_platforms': x_mitre_platforms, 'x_mitre_detection': x_mitre_detection, 'phase_name': phase_name}
            
            # Adding the current attack pattern to the attacks list
            attacks.append(result)

# Creating a connection with  the database
client = MongoClient('mongodb://localhost:27017/')

# Checking if the database is already exists
if 'ninjas_database' not in client.list_database_names():
    db = client['ninjas_database']

    # Creating a new collection to store attack patterns
    collection = db['attacks_patterns_collection']

    # Inserting all attack patterns
    collection.insert_many(attacks)