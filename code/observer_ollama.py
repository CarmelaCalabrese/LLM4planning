
import yarp
import sys
import time
import json
import base64
import os.path
import importlib
import inspect
from ollama import generate
from PIL import Image
from io import BytesIO
from typing import (
    Literal,
    Union,
)
from openai import OpenAI
import numpy as np


class LLMobserver(yarp.RFModule):

    def configure(self, rf) :
        self.period = 5.0

        self.agent_output_portName = "/observer/text:o"
        self.agent_output_port = yarp.BufferedPortBottle()
        self.agent_output_port.open(self.agent_output_portName)

          
        self.config_path = rf.check("config", yarp.Value("")).asString()
        if not self.config_path:
            print("Error: config file path is missing")
            return False

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


        # Load sequences from JSON file
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading sequences file: {e}")
            return False
        
        self.azureOpenAI_client = OpenAI(
            base_url = 'http://localhost:11434/v1',
            api_key='ollama', # required, but unused
            )
        self.model = "moondream"

        self.temperature = self.config['temperature']
        self.top_p = self.config['top_p']
        self.max_length = self.config['max_length']
        # self.character = 'You are the observer of the environment and provide feedback to another LLM that is in control of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad.\n\
        #             Ergocub will call some functions based on reasoning on the feedback that you give on the environment.\n'
        #             #For example: .\n(Step n) [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n\
        #             #if at (Step n+1) the output were: [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n\
        #             #You should return: [ENVIRONMENT]: No changes. [PEOPLE]: No changes. [OBJECTS]: No changes.\n'
        self.character = ''
        print(self.character)

        self.prompt=[]

        self.messages = [
            {"role": "system", "content": self.character},
            ]

        return True
               

    def encode_image(self, image):
            return base64.b64encode(image).decode("utf-8")                                

    
    def updateModule(self):
        
        
        received_image = self._input_image_port.read()
        self._in_buf_image.copy(received_image)   
        frame = self._in_buf_array
        img=Image.fromarray(np.uint8(frame)).convert('RGB')
        buffered = BytesIO()
        img.save(buffered, format='png')
        img.save('/home/carmela/Desktop/image_prova.png')
        exit()
        base64_image = self.encode_image(buffered.getvalue())
       
        start_time = time.time()
        #response = self._query_llm(base64_image)        
        
        # descriptions = ', '.join(sticker['desc'] for sticker in self.stickers)
        # question = f'YOU ARE A CLASSIFIER, YOU MUST ANSWER WITH ONLY ONE OF THE AVAILABLE OPTIONS.\n\
        #             ONLY ONE ANSWER IS CORRECT, IF YOU ARE UNABLE TO RECOGNIZE, YOU MUST ANSWER ONLY 0 \n\
        #             DO NOT INVENT, BE CONSERVATIVE. YOU HAVE TO BE VERY CONFIDENT IN YOUR ANSWER.\n\
        #             DO NOT CHANGE THE LABELS, NO ADDITIONAL TEXT, NO BRACKETS, NO PUNTUATION.\n\
        #             USE ONLY- MANDATORY- WITH THE CORRESPONDING NUMBER, FOR EXAMPLE 4.\n\
        #             Which answer describes what is inside the cartoon: {descriptions}?'

        # question = 'You are the observer of the environment and provide feedback to another LLM that is in control of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad.\n\
        #             Ergocub will call some functions based on reasoning on the feedback that you give on the environment.\n\
        #             You are asked to describe the scene that you see from a frame in the format: [ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:... .\n\
        #             In the [ENVIRONMENT] section you describe the environment, in the [PEOPLE] part you describe if there is a person and how s-/he looks like and in [OBJECTS] you list the objects you see.\n\
        #             If nothing has changed in the environment, return [ENVIRONMENT]: No changes.\nIf the person or the number of people doesnt really change return [PEOPLE]: No changes.\n\
        #             If the objects or the number of available tools doesn/t really change, please return [OBJECTS]: No changes.\n\
        #             Remember to always include the fields [ENVIRONMENT], [PEOPLE], and [OBJECTS] in your response.\n'
        #             #For example: .\n(Step n) [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n\
        #             #if at (Step n+1) the output were: [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n\
        #             #You should return: [ENVIRONMENT]: No changes. [PEOPLE]: No changes. [OBJECTS]: No changes.\n'
        self.prompt.append(self.character)
        # extracted_meassage= "\n".join(self.prompt)
        # print(extracted_meassage)
        #response = generate('llava',extracted_meassage, images=[base64_image], stream=False)
        response = generate('moondream', 'What is in the image?', images=[base64_image], stream=False)
        self.prompt.append(response['response'])
        answer= {"role": "assistant", "content": response['response']}
        print(answer)
     

        end_time = time.time()
        print(f'Inference time:{end_time-start_time}')    

        self.messages.append(answer)
        
        bot = self.agent_output_port.prepare()
        bot.clear()
        bot.addString(response['response'])
        self.agent_output_port.write()

        # if len(self.messages) == 9:
        #    self.messages = self.messages[0:3] + self.messages[5:9]  # Keep the first element, remove the rest

        return True

    def reset(self): 
        self.messages = [
            {"role": "system", "content": self.character},
        ]
        print(f"📝 Message history reset.")


    def getPeriod(self):
        return self.period
    
        
    def close(self):
        self.agent_text_port.close()
        self.client_action_rpc_port.close()
        self.client_emotion_rpc_port.close()
        self.agent_output_port.close()
        return True
    
    
    def interruptModule(self):
        self.agent_text_port.interrupt()
        self.client_action_rpc_port.interrupt()
        self.client_emotion_rpc_port.interruption()
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
