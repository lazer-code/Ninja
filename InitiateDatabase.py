import os
import json
from pymongo import MongoClient

attacks: list[dict[str, str]] = []

for filename in os.listdir('attack-patterns'):
    file_path = os.path.join('attack-patterns', filename)
    
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            json_data: dict[str, str] = json.loads(file.read())
            json_data: dict[str, str] = json_data['objects'][0]
            id: str = json_data.get('id', 'NA').replace('attack-pattern--', '')
            name: str = json_data.get('name', 'NA')
            description: str = json_data.get('description', 'NA')
            x_mitre_platforms: list[str] = json_data.get('x_mitre_platforms', 'NA')
            x_mitre_detection: list[dict[str, str]] = json_data.get('x_mitre_detection', 'NA')
            phase_names: dict[str, str] = json_data.get('kill_chain_phases', 'NA')[-1]
            phase_name: str= phase_names.get('phase_name', 'NA')
            result: dict[str, str] = {'id': id, 'name': name, 'description': description, 'x_mitre_platforms': x_mitre_platforms, 'x_mitre_detection': x_mitre_detection, 'phase_name': phase_name}
            attacks.append(result)

client = MongoClient('mongodb://localhost:27017/')

if 'ninjas_database' not in client.list_database_names():
    db = client['ninjas_database']
    collection = db['attacks_patterns_collection']
    collection.insert_many(attacks)
    print('Database was created successfully')

else:
    print('Database is already there')