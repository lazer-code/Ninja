import os
import json

parent_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
target_folder = os.path.join(parent_folder, 'attack-pattern')

attacks = []

for root, dirs, files in os.walk(target_folder):
    for file_name in files:
        with open(os.path.join(root, file_name), 'r') as file:
            json_data = json.loads(file.read())
            json_data = json_data['objects'][0]

            id = json_data['id']
            name = json_data['name']
            description = json_data['description']
            x_mitre_platforms = json_data['x_mitre_platforms']
            x_mitre_detection = json_data['x_mitre_detection']
            phase_name = json_data['phase_name']
            result = {'id': json_data['id'], 'name': json_data['name'], 'description': json_data['description'], 'x_mitre_platforms': json_data['x_mitre_platforms'], 'x_mitre_detection': json_data['x_mitre_detection']}
            attacks.append(result)

print(attacks)

