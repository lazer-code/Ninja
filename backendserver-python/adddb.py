import os
import json
from pymongo import MongoClient

parent_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
target_folder = os.path.join(parent_folder, 'attack-pattern')

attacks = []

for root, dirs, files in os.walk(target_folder):
    for file_name in files:
        with open(os.path.join(root, file_name), 'r') as file:
            json_data = json.loads(file.read())
            json_data = json_data['objects'][0]

            id = json_data.get('id', 'NA')
            name = json_data.get('name', 'NA')
            description = json_data.get('description', 'NA')
            x_mitre_platforms = json_data.get('x_mitre_platforms', 'NA')
            x_mitre_detection = json_data.get('x_mitre_detection', 'NA')
            phase_names = json_data.get('kill_chain_phases', 'NA')[-1]
            phase_name = phase_names.get('phase_name', 'NA')
            result = {'id': id, 'name': name, 'description': description, 'x_mitre_platforms': x_mitre_platforms, 'x_mitre_detection': x_mitre_detection, 'phase_name': phase_name}
            attacks.append(result)

client = MongoClient('mongodb://localhost:27017/')
if 'ninjas_database' not in client.list_database_names():
    db = client['ninjas_database']
    collection = db['attacks_patterns_collection']

    collection.insert_many(attacks)