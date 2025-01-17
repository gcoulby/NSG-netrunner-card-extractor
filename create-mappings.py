from jinja2 import Template
import requests
import os
import json

def get_card_mappings():
    url = "https://raw.githubusercontent.com/gcoulby/Netrunner600DpiMapper/refs/heads/master/raw.json"
    response = requests.get(url)
    data = response.json()
    return data

from jinja2 import Template
import requests
import json

with open('./templates/mapping.jinja', 'r') as file:
    template_content = file.read()
template = Template(template_content)


mapping = get_card_mappings()
cards = mapping["data"]


for card in cards:
    print(card["netrunnerdb_code"])

# get all files in the sliced_cards folder
def get_files():
    files = []
    for root, dirs, file in os.walk("sliced_cards"):
        for f in file:
            files.append({"netrunnerdb_code": os.path.splitext(f)[0], "link":  f'{root.split("\\")[-1]}/{f}', "nsg": True })
    return files

files = get_files()
cards.extend(files)

# build the template
cls_data = {
    "cards": cards,
}

rendered = template.render(cls_data)
# print(rendered)
with open('mapping.json', 'w') as file:
    file.write(rendered)
    file.close()
