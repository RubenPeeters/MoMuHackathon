from rdflib import Graph
from dotenv import load_dotenv
import pickle
from pprint import pprint

# Load environment variable for OpenAI API key

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

if __name__ == "__main__":
    load_dotenv()
    out = dict()
    g = Graph()
    g.parse("Data/items_filtered.ttl", format="turtle")
    json_ld_data = g.serialize(format="json-ld", indent=4)
    with open("Data/graph_output.txt", "w") as file:
       
        # Iterate through each triple in the graph
        subjects = set(g.subjects())
        for subject in subjects:
            
            org_subject = subject
            if "api/item" in subject:
                print(subject)
                subj_formalized = str(subject).split('/')[-1]
                if '#' in subj_formalized:
                    subject = subj_formalized.split('#')[-1]
                else:
                    subject = subj_formalized
                out[subject] = {}
                file.write(f"Subject {subject}\n")
                # Iterate over all triples where this subject is the subject
                for pred, obj in g.predicate_objects(subject=org_subject):
                    pred_formalized = str(pred).split('/')[-1]
                    if '#' in pred_formalized:
                        pred = pred_formalized.split('#')[-1]
                    else:
                        pred = pred_formalized
                    if "http" not in obj:
                        out[subject][pred] = str(obj)
                        file.write(f"{pred}: {obj}\n")
                     
    with open("Data/dataset.pkl", "wb") as f:
        pickle.dump(out, f)
    with open("Data/dataset.pkl", "rb") as f:
        new = pickle.load(f)
        pprint(new)
        # for subj, pred, obj in g:
            # Write the triple in a readable format
            # seen_subjects = set()
            # if subj not in seen_subjects:
            #     file.write(f"\n")
            #     file.write(f"\n")
            #     file.write(f"{subj}\n")
            #     seen_subjects.add(subj)

    # Optionally, write the total number of triples
    # print(json_ld_data)   


