from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain.vectorstores.neo4j_vector import Neo4jVector

from langchain_community.llms import Ollama
from langchain_community.graphs import Neo4jGraph

from dotenv import load_dotenv

from rdflib import Graph
from neo4j import GraphDatabase

from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
import getpass
import os

from langchain_core.documents import Document

# Load environment variable for OpenAI API key


def convert_ttl_to_dict(ttl_file, pkl_file, txt_for_validation):
    out = dict()
    g = Graph()
    g.parse(ttl_file, format="turtle")
    json_ld_data = g.serialize(format="json-ld", indent=4)
    with open(txt_for_validation, "w") as file:
        # Iterate through each triple in the graph
        subjects = set(g.subjects())
        for subject in subjects:
            org_subject = subject
            if "api/item" in subject:
                subj_formalized = str(subject).split("/")[-1]
                if "#" in subj_formalized:
                    subject = subj_formalized.split("#")[-1]
                else:
                    subject = subj_formalized
                out[subject] = {}
                file.write(f"Subject {subject}\n")
                # Iterate over all triples where this subject is the subject
                for pred, obj in g.predicate_objects(subject=org_subject):
                    pred_formalized = str(pred).split("/")[-1]
                    if "#" in pred_formalized:
                        pred = pred_formalized.split("#")[-1]
                    else:
                        pred = pred_formalized
                    if "http" not in obj:
                        out[subject][pred] = str(obj)
                        file.write(f"{pred}: {obj}\n")

    with open(pkl_file, "wb") as f:
        pickle.dump(out, f)

    return out


def generate_readable_content_v2(instance, properties):
    lines = []
    instance_id = str(instance).split("/")[-1]
    # lines.append(f"The item {instance_id} has the following information:")

    for predicate, obj in properties:
        simplified_predicate = simplify_predicate(str(predicate))
        if "is_public" in str(predicate):
            lines.append(
                f"The item {instance_id} is {'public' if obj == 'true' else 'not public'}."
            )
        elif "title" in str(predicate):
            lines.append(f'The identifier of this artifact is "{obj}".')
        elif "description" in str(predicate):
            lines.append(f'The description of this artifact is "{obj}"')
        elif "date" == str(predicate):
            # print (predicate, obj)
            lines.append(f"This artifact was created from the following period: {obj}.")
        elif "modified" in str(predicate):
            lines.append(f"This artifact was last modified on {obj}.")
        elif "medium" in str(predicate):
            lines.append(f"The medium of this artifact includes {obj}.")
        elif "extent" in str(predicate):
            lines.append(f"The dimensions of this artifact are {obj}.")
        elif "publisher" in str(predicate):
            lines.append(f"The publisher of this artifact is {obj}.")
        elif "subject" in str(predicate):
            lines.append(f"The subject of this artifact includes {obj}.")
        elif "shortDescription" in str(predicate):
            obj = obj.replace("\n", "")
            lines.append(f'The context of this artifact is "{obj}".')
        elif "P48_has_preferred_identifier" in str(predicate):
            lines.append(f"The preferred identifier of this artifact is {obj}.")
        elif "P50_has_current_keeper" in str(predicate):
            lines.append(f"The current keeper of this artifact is {obj}.")
        elif "P55_has_current_location" in str(predicate):
            lines.append(f"The current location of this artifact is in {obj}.")
        elif "dateSubmitted" in str(predicate):
            lines.append(f"This artifact was submitted on {obj}.")
        elif "identifierGroupType" in str(predicate):
            lines.append(f"The group type of this artifact is  {obj}.")
        elif "identifierGroupValue" in str(predicate):
            lines.append(f"The group value of this artifact is {obj}.")
        elif simplified_predicate == "id":
            continue
        else:
            # print (simplified_predicate)
            lines.append(f"The {simplified_predicate} of this artifact is {obj}.")

    return lines


def simplify_predicate(predicate):
    match = re.search(r"[#/](\w+)$", predicate)
    return match.group(1).replace("_", " ") if match else predicate


def convert_pkl_to_doc(dataset, docs_path, save_txt=True):

    docs = list()
    combined_texts = dict()
    for item, val in dataset.items():
        item_id = str(item).split("/")[-1]
        properties = [(k, v) for k, v in val.items()]
        # lines = generate_readable_content(item, properties)
        lines = generate_readable_content_v2(item, properties)
        for line in lines:
            docs.append(Document(page_content=line, metadata={"item_id": item_id}))

        combined_texts[item_id] = "\n".join(lines)

        if save_txt:
            file_name = item_id + ".txt"
            file_path = os.path.join(docs_path, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

    return docs, combined_texts


if __name__ == "__main__":
    load_dotenv()

    # # loader = TextLoader("./Data/items_filtered.ttl")
    # documents = loader.load()
    # text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    # texts = text_splitter.split_documents(documents)
    # # Initialize LLM
    # # llm = Ollama(model="llama3.2:1b")
    # Configuration files
    ttl_file = "/Users/Ruben/Github/MoMuHackathon/Data/items_filtered.ttl"
    pkl_file = "/Users/Ruben/Github/MoMuHackathon/Data/dataset.pkl"
    txt_for_validation = "/Users/Ruben/Github/MoMuHackathon/Data/graph_output.txt"
    docs_path = "/Users/Ruben/Github/MoMuHackathon/output_documents"
    dataset = convert_ttl_to_dict(ttl_file, pkl_file, txt_for_validation)
    # Specify the folder path
    folder_path = "output_documents"
    docs, combined_texts = convert_pkl_to_doc(dataset, docs_path)

    # https://python.langchain.com/docs/integrations/vectorstores/faiss/

    # embeddings = OllamaEmbeddings(model="llama3.2:1b")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(documents=docs, ids=uuids)
    # TEST DEMO: Similarity search
    results = vector_store.similarity_search(
        "What are the artefacts that are created in the 1900s",
        k=5,
    )
    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")
