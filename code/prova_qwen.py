from lmdeploy import pipeline, TurbomindEngineConfig
from lmdeploy.vl import load_image
import time
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("lmdeploy").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Silence all logging globally
logging.basicConfig(level=logging.CRITICAL)


engine_config = TurbomindEngineConfig(model_format='awq')
pipe = pipeline("Qwen/Qwen2.5-VL-3B-Instruct-AWQ", backend_config=engine_config)

#image = load_image('https://raw.githubusercontent.com/open-mmlab/mmdeploy/main/tests/data/tiger.jpeg')
image = load_image('/home/ccalabrese-iit.local/dev_iit/prova.jpeg')
start_time = time.time()
response = pipe((f'describe this image. Provide the output in the format: [ENVIRONMENT]: [CHARACTER]: [OBJECTS]:', image))
finish_time = time.time()
print(f"Inference time: {finish_time - start_time} seconds")

#response = pipe(["Hi, pls intro yourself", "Shanghai is"])
print(response.text)

