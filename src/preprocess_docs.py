from rdflib import Graph
from dotenv import load_dotenv

# Load environment variable for OpenAI API key

if __name__ == "__main__":
    load_dotenv()
        
    g = Graph()
    g.parse("Data/items_filtered.ttl", format="turtle")
    json_ld_data = g.serialize(format="json-ld", indent=4)
    with open("graph_output.txt", "w") as file:
        file.write("RDF Graph Triples:\n")
        file.write("==================\n\n")
        
        # Iterate through each triple in the graph
        subjects = set(g.subjects())
        for subject in subjects:
            org_subject = subject
            if "api/item" in subject:
                subj_formalized = str(subject).split('/')[-1]
                if '#' in subj_formalized:
                    subject = subj_formalized.split('#')[-1]
                else:
                    subject = subj_formalized
            file.write(f"Subject {subject}\n")
            # Iterate over all triples where this subject is the subject
            for pred, obj in g.predicate_objects(subject=org_subject):
                if "http" not in obj:
                    file.write(f"{pred}: {obj}\n")
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


