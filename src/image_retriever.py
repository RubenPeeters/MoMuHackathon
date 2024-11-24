# 16076
import requests
from PIL import Image
import io
import json

BASE = "https://heron.libis.be/momu/api/items/"


def image_retriever(item_id):
    full_url = BASE + str(item_id)
    response = requests.get(full_url)
    print(response.content)

    # Convert JSON-LD to TTL

    data_dict = json.loads(response.content)
    print(data_dict)

    image = Image.open(io.BytesIO(data_dict["thumbnail_display_urls"]["large"]))
    return image


if __name__ == "__main__":
    image_retriever(16076)
