import moondream as md
from PIL import Image
import time

# Initialize with local model path. Can also read .mf.gz files, but we recommend decompressing
# up-front to avoid decompression overhead every time the model is initialized.
model = md.vl(model="./moondream-2b-int8.mf")

# Load and process image
image = Image.open("/home/carmela/Desktop/prova.jpg")
encoded_image = model.encode_image(image)

# # Generate caption
# caption = model.caption(encoded_image)["caption"]
# print("Caption:", caption)


# Ask questions
query_text= "You are asked to describe synthetically the scene that you see from a frame in the format: [ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:... .\n In the [ENVIRONMENT] section you describe ONLY the environment.\n In the [PEOPLE] part you describe ONLY if there is a person and what they are doing.\n In [OBJECTS] you list briefly ONLY the objects you see.\n From your feedback, a person has to understand the actual state of the environment, object, and the people in it.\n Your MUST be only '[ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:...' OR 'No significant changes in the scene'.\n"
print("Inizio")
print(time.time())
answer = model.query(encoded_image, query_text)["answer"]
print("Answer:", answer)
print("Fine")
print(time.time())