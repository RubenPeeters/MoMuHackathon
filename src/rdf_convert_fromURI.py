# filter the json-ld file and convert it to turtle format
# properties to omit:
# o:item_set
# o:created
# o:modified
# for this ontology: "http://omeka.org/s/vocabs/o#"

from rdflib import Graph
import json
import requests

# We create a turtle file based on an api response from omeka S (json-ld)
uri = "https://heron.libis.be/momu/api/items?item_set_id=339931"

# request the data
response = requests.get(uri)
data = response.json()

# print the headers
print("Headers:", response.headers)

# from the header get the Omeka-S-Total-Results value
total_results = int(response.headers["Omeka-S-Total-Results"])
print("Total results:", total_results)
# calculate the number of pages needed (50 per page)
pages = total_results // 50 + 1
print("Pages:", pages)

# iterate over the pages and collect the data
all_data = []
for page in range(1, pages + 1):
    paginated_uri = f"{uri}&page={page}"
    response = requests.get(paginated_uri)
    response = requests.get(uri)
    data = response.json()
    all_data.extend(data)

# save the data to a file
with open("Data/items.json", "w") as f:
    json.dump(all_data, f)

with open("Data/items_filtered.json", encoding='utf-8') as f:
    data = json.load(f)

    # remove unwanted properties from the JSON-LD file
    for item in data:
        item.pop("o:item_set", None)
        item.pop("o:created", None)
        item.pop("o:modified", None)
        item.pop("o:resource_template", None)
        item.pop("o:resource_class", None)
        item.pop("o:owner", None)
        item.pop("o:is_public", None)
        item.pop("o:site", None)

    # Save the filtered JSON-LD file
    with open("Data/items_filtered.json", "w") as f:
        json.dump(data, f)



# Convert JSON-LD to TTL
g = Graph()
g.parse("Data/items_filtered.json", format="json-ld")
g.serialize(destination="Data/items_filtered.ttl", format="turtle")