import os
import re
import pickle
import json
import requests
from PIL import Image
from pprint import pprint
from dotenv import load_dotenv
from rdflib import Graph

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain_core.messages import AIMessage

import faiss
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from pathlib import Path

import datetime


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
                    # if "http" not in obj:
                    if "http" not in obj or pred == "P48_has_preferred_identifier":

                        out[subject][pred] = str(obj)
                        file.write(f"{pred}: {obj}\n")

    with open(pkl_file, "wb") as f:
        pickle.dump(out, f)

    return out


def simplify_predicate(predicate):
    match = re.search(r"[#/](\w+)$", predicate)
    return match.group(1).replace("_", " ") if match else predicate


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


def convert_pkl_to_doc(dataset, docs_path, context_path, save_txt=True):

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

    with open(context_path, "wb") as f:
        pickle.dump(combined_texts, f)

    return docs, combined_texts


def txt_to_vec(docs, embeddings, vec_path):
    # embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(documents=docs, ids=uuids)
    vector_store.save_local(vec_path)

    return vector_store


def image_retriever(item_id):

    BASE = "https://heron.libis.be/momu/api/items/"
    full_url = BASE + str(item_id)
    response = requests.get(full_url)
    data_dict = json.loads(response.content)
    # image = Image.open(io.BytesIO(data_dict["thumbnail_display_urls"]["large"]))
    image = data_dict["thumbnail_display_urls"]["large"]
    return image


def create_context(combined_texts):

    context_dict = dict()
    for item_id, full_text in combined_texts.items():
        context_dict[item_id] = dict()
        context_dict[item_id]["full_text"] = full_text
        context_dict[item_id]["image"] = image_retriever(item_id)

    with open(context_path, "wb") as f:
        pickle.dump(context_dict, f)


if __name__ == "__main__":
    cwd = Path.cwd()
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Format the datetime into a string
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    ttl_file = cwd / "Data" / "items_filtered.ttl"
    pkl_file = cwd / "Data" / f"dataset_{datetime_str}.pkl"
    txt_for_validation = cwd / "Data" / "graph_output.txt"
    docs_path = cwd / "output_documents"
    vec_path = cwd / "Data" / f"vector_store_{datetime_str}"
    context_path = cwd / "Data" / f"context_{datetime_str}.pkl"

    dataset = convert_ttl_to_dict(ttl_file, pkl_file, txt_for_validation)
    docs, combined_texts = convert_pkl_to_doc(dataset, docs_path, context_path)
    create_context(combined_texts)
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = txt_to_vec(docs, embeddings, vec_path)
