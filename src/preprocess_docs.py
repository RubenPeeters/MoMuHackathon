from rdflib import Graph
from dotenv import load_dotenv
import pickle
from pprint import pprint

# Load environment variable for OpenAI API key

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


