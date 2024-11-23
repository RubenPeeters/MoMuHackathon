from rdflib import Graph, Namespace
import os
from rdflib.namespace import XSD, RDF
import re

ttl_file = "Data/items.ttl" 
output_dir = "output_documents" 


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

g = Graph()
g.parse(ttl_file, format="ttl")

NS1 = Namespace("http://omeka.org/s/vocabs/o#") 
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

items = g.subjects(RDF.type, NS1["Item"])

def simplify_predicate(predicate):
    match = re.search(r"[#/](\w+)$", predicate)
    return match.group(1).replace("_", " ") if match else predicate

def generate_readable_content(instance, properties):
    lines = []
    instance_id = str(instance).split("/")[-1]  
    lines.append(f"The item {instance_id} has the following properties:")

    for predicate, obj in properties:
        simplified_predicate = simplify_predicate(str(predicate))

        if "is_public" in str(predicate):
            lines.append(f"The item {instance_id} is {'public' if obj == 'true' else 'not public'}.")
        elif "title" in str(predicate):
            lines.append(f"The title of item {instance_id} is \"{obj}\".")
        elif "description" in str(predicate):
            lines.append(f"The description of item {instance_id}: {obj}")
        elif "item_set" in str(predicate):
            lines.append(f"The item_set of item {instance_id} includes: {obj}.")
        elif "created" in str(predicate):
            lines.append(f"The item {instance_id} was created on {obj}.")
        elif "modified" in str(predicate):
            lines.append(f"The item {instance_id} was last modified on {obj}.")
        elif "medium" in str(predicate):
            lines.append(f"The medium of item {instance_id} includes: {obj}.")
        elif "extent" in str(predicate):
            lines.append(f"The dimensions of item {instance_id} are: {obj}.")
        elif "publisher" in str(predicate):
            lines.append(f"The publisher of item {instance_id} is {obj}.")
        elif "subject" in str(predicate):
            lines.append(f"The subject of item {instance_id} includes: {obj}.")
        elif "shortDescription" in str(predicate):
            lines.append(f"Short description of item {instance_id}: {obj}.")
        elif "P48_has_preferred_identifier" in str(predicate):
            lines.append(f"The preferred identifier for item {instance_id} is {obj}.")
        elif "P50_has_current_keeper" in str(predicate):
            lines.append(f"The current keeper of item {instance_id} is {obj}.")
        elif "P55_has_current_location" in str(predicate):
            lines.append(f"The current location of item {instance_id} is {obj}.")
        else:
            # 默认描述
            lines.append(f"The property \"{simplified_predicate}\" of item {instance_id} is: {obj}.")
    
    return "\n".join(lines)

for item in items:
    properties = g.predicate_objects(subject=item)
    content = generate_readable_content(item, properties)

    file_name = str(item).split("/")[-1] + "_readable.txt"  
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
