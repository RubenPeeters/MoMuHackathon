# 16076
import matplotlib.pyplot as plt
import requests
from PIL import Image
import io
import json

BASE = "https://heron.libis.be/momu/api/items/"


def image_retriever(item_id):
    full_url = BASE + str(item_id)
    response = requests.get(full_url)

    # Convert JSON-LD to TTL

    data_dict = json.loads(response.content)

    image = Image.open(
        io.BytesIO(requests.get(data_dict["thumbnail_display_urls"]["large"]).content)
    )
    return image


if __name__ == "__main__":
    image_retriever(16076)
    images = [image_retriever(res.metadata["item_id"]) for res in results]

    # for idx, img in enumerate(images):
    #     plt.figure()  # Create a new figure for each image
    #     plt.imshow(img)
    #     plt.axis("off")  # Turn off axis for better visualization
    #     plt.title(f"Image {idx + 1}")
    #     plt.show()
