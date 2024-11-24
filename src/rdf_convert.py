from rdflib import Graph

# Convert JSON-LD to TTL

g = Graph()
g.parse("Data/new_data.json", format="json-ld")
g.serialize("Data/new_data.ttl", format="turtle")
