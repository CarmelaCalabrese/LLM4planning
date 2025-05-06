import moondream as md
from PIL import Image
import time

# Initialize with local model path. Can also read .mf.gz files, but we recommend decompressing
# up-front to avoid decompression overhead every time the model is initialized.
model = md.vl(model="./moondream-2b-int8.mf")

# Load and process image
image = Image.open("/home/ccalabrese-iit.local/dev_iit/prova2.jpg")
encoded_image = model.encode_image(image)

# # # Generate caption
# start_time = time.time()
# caption = model.caption(encoded_image)["caption"]
# print("Caption:", caption)
# end_time = time.time()
# print("Total time taken:", end_time - start_time)

# Generate bbox detection
start_time = time.time()
detection = model.detect(encoded_image, "knife")
print("Detection result:", detection)
end_time = time.time()
print("Total time taken:", end_time - start_time)

# Get centroid coordinates
start_time = time.time()
coordinates=model.point(encoded_image, "onion")
print("Coordinates:", coordinates)
end_time = time.time()
print("Total time taken:", end_time - start_time)

# Ask questions
query_text= "You are asked to describe synthetically the scene that you see from a frame in the format: [ENVIRONMENT]: (here you put a synthetic description of the environment), [PEOPLE]: (if any, here you put a synthetic description of the person), [OBJECTS]: (if any, here you put a synthetic description of the present objects) .\n In the [ENVIRONMENT] section you describe ONLY the environment.\n In the [PEOPLE] part you describe ONLY if there is a person and what they are doing.\n In [OBJECTS] you list briefly ONLY the objects you see.\n From your feedback, a person has to understand the actual state of the environment, object, and the people in it.\n Your MUST be only '[ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:...'.\n"
start_time = time.time()
answer = model.query(encoded_image, query_text)["answer"]
print("Answer:", answer)
end_time = time.time()
print("Total time taken:", end_time - start_time)

# Ask questions
query_text= "You are asked to describe synthetically the scene that you see from a frame in the format: [PEOPLE]: If any, here you put a synthetic description of the person in the scene. You describe ONLY if there is a person and what they are doing.\n Your output MUST be only [PEOPLE]: ...\n"
start_time = time.time()
answer = model.query(encoded_image, query_text)["answer"]
print("Answer:", answer)
end_time = time.time()
print("Total time taken:", end_time - start_time)

# # Ask questions
# #query_text= "Briefly (max 10 words!) from a frame you MUST list the objects and things in the scene. You describe ONLY what actually is there.\n Your output MUST be only [OBJECT]: ... NOT INCLUDE PEOPLE HERE\n"
# #query_text= "You MUST list the objects and things in the scene (do not repeat the same entry). You describe ONLY what actually is there.\n DO NOT INCLUDE PEOPLE HERE \n" #AND DO NOT REPEAT THE SAME OBJECT
# query_text= "You MUST list only once the objects in the scene. You describe ONLY what actually is there.\n DO NOT INCLUDE PEOPLE HERE \n" #AND DO NOT REPEAT THE SAME OBJECT
# start_time = time.time()
# answer = model.query(encoded_image, query_text)["answer"]
# print("Answer:", answer)
# end_time = time.time()
# print("Total time taken:", end_time - start_time)
