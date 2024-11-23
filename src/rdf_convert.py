from rdflib import Graph

# Convert JSON-LD to TTL

g = Graph()
g.parse("Data/items.json", format="json-ld")
g.serialize("Data/items.ttl", format="turtle")