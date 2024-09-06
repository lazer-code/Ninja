import os

parent_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
target_folder = os.path.join(parent_folder, 'attack-pattern')

for root, dirs, files in os.walk(target_folder):
    for file in files:
        print(os.path.join(root, file))
