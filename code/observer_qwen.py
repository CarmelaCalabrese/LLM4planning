
import yarp
import sys
import time
import json
import base64
import os.path
import importlib
import inspect
from PIL import Image
from io import BytesIO
from typing import (
    Literal,
    Union,
)
from openai import AzureOpenAI
import numpy as np
from datetime import datetime
import cv2
from matplotlib import pyplot as plt
from PIL import Image
from lmdeploy import pipeline, TurbomindEngineConfig
from lmdeploy.vl import load_image
import time
import warnings
warnings.filterwarnings("ignore")



class LLMobserver(yarp.RFModule):

    def configure(self, rf) :
        self.period = 2.0

        self.agent_output_portName = "/observer/text:o"
        self.agent_output_port = yarp.BufferedPortBottle()
        self.agent_output_port.open(self.agent_output_portName)

        self.LLMobs_rpc_portName = "/observer/rpc"
        self.LLMobs_rpc_port = yarp.Port()
        self.LLMobs_rpc_port.open(self.LLMobs_rpc_portName)
        self.attach(self.LLMobs_rpc_port)

        self._input_image_port = yarp.BufferedPortImageRgb()
        imageInPortName = '/observer/image:i'
        self._input_image_port.open(imageInPortName)
        print('{:s} opened'.format(imageInPortName))

        print('Preparing input image...')
        self._in_buf_array = np.ones((480, 640, 3), dtype=np.uint8)
        self._in_buf_image = yarp.ImageRgb()
        self._in_buf_image.resize(640, 480)
        self._in_buf_image.setExternal(self._in_buf_array.data, self._in_buf_array.shape[1], self._in_buf_array.shape[0])
        print('... ok \n')


        # self.config_path = rf.check("config", yarp.Value("")).asString()
        # if not self.config_path:
        #     print("Error: config file path is missing")
        #     return False

        # # Load sequences from JSON file
        # try:
        #     with open(self.config_path, 'r') as f:
        #         self.config = json.load(f)
        # except Exception as e:
        #     print(f"Error loading sequences file: {e}")
        #     return False


        self.engine_config = TurbomindEngineConfig(model_format='awq')
        self.pipe = pipeline("Qwen/Qwen2.5-VL-3B-Instruct-AWQ", backend_config=self.engine_config)
        self.prev_inf = ''

        # self.azureOpenAI_client = AzureOpenAI(
        #     azure_endpoint = self.config['endpoint'], 
        #     api_key=os.getenv("AZURE_API_KEY"),
        #     api_version=self.config['api_version']
        #     )
        # self.model = self.config['model_name']
        # self.temperature = self.config['temperature']
        # self.top_p = self.config['top_p']
        # self.max_length = self.config['max_length']
        # self.character: str = self.config['system_prompt']
        # print(self.character)
        # self.messages = [
        #     {"role": "system", "content": self.character},
        #     ]

        return True

        
    
    def generate_vlm_answer(self, image, specific_obj= None):
        
        image = Image.fromarray(image) 

        try:
            start_time = time.time()
            response = self.pipe((f'Describe VERY BRIEFLY what you see in the image. Provide the output in the format: [ENVIRONMENT]: (focus on the environment) \n [CHARACTER]: (focus on the person/animal) \n [OBJECTS]: (focus on the objects)\n', image))
            finish_time = time.time()
            print(f"Inference time: {finish_time - start_time} seconds")

            inf = response.text   
            self.prev_inf = inf         
            print(f'Inference:\n {inf} \n')
            return inf
        except Exception as e:

            return None
 



    def respond(self, command, reply):
        if command.get(0).asString()=='get_obj':
            print('\n Received command GET_OBJ \n')
            received_image = self._input_image_port.read()
            self._in_buf_image.copy(received_image)   
            frame = self._in_buf_array   
            
            inference = self.generate_vlm_answer(frame, True)
            reply.addString(inference)
        return True

 
    
    def updateModule(self):
      
        received_image = self._input_image_port.read()
        self._in_buf_image.copy(received_image)   
        frame = self._in_buf_array   
        
        inference = self.generate_vlm_answer(frame)
        
        if inference:
            # Open the log file in append mode
            with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/logfile.txt", "a") as log_file:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"[{current_time}] \n {inference}.\n")

            #print(f'Risposta: {response.choices[0].message.content}')
            #self.messages.append(response.choices[0].message)
            
            bot = self.agent_output_port.prepare()
            bot.clear()
            bot.addString(inference)
            self.agent_output_port.write()

            # if len(self.messages) == 9:
            #     self.messages = self.messages[0:3] + self.messages[5:9]  # Keep the first element, remove the rest
        else:
            bot = self.agent_output_port.prepare()
            bot.clear()
            bot.addString('')
            self.agent_output_port.write()

        return True

    # def reset(self): 
    #     self.messages = [
    #         {"role": "system", "content": self.character},
    #     ]
    #     print(f"📝 Message history reset.")
    #     return True

    def getPeriod(self):
        return self.period
    
        
    def close(self):
        self.agent_text_port.close()
        self.agent_output_port.close()
        return True
    
    
    def interruptModule(self):
        self.agent_text_port.interrupt()
        self.agent_output_port()
        return True
    
#########################################333

if __name__ == '__main__':
    
    yarp.Network.init()

    mod = LLMobserver()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
