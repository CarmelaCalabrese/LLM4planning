
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


class LLMobserver(yarp.RFModule):

    def configure(self, rf) :
        self.period = 5.0

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


        self.config_path = rf.check("config", yarp.Value("")).asString()
        if not self.config_path:
            print("Error: config file path is missing")
            return False

        # Load sequences from JSON file
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading sequences file: {e}")
            return False

        self.azureOpenAI_client = AzureOpenAI(
            azure_endpoint = self.config['endpoint'], 
            api_key=os.getenv("AZURE_API_KEY"),
            api_version=self.config['api_version']
            )
        self.model = self.config['model_name']
        self.temperature = self.config['temperature']
        self.top_p = self.config['top_p']
        self.max_length = self.config['max_length']
        self.character: str = self.config['system_prompt']
        print(self.character)
        self.messages = [
            {"role": "system", "content": self.character},
            ]

        return True
               

    def encode_image(self, image):
            return base64.b64encode(image).decode("utf-8")
                                

    def _query_llm(self, messages, tool_choice: Union[Literal["none", "auto"]] = "auto"):
        response = ""
        response = self.azureOpenAI_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p = self.top_p,
            max_tokens = self.max_length,
            messages=messages,
        )
        return response
    
    def resume(self):
        with open("logfile.txt", "r") as file:
            file_content = file.read()

        message=[
            {"role": "user", "content": f"From what you read, understand and summarize very briefly the most updated state of the interaction described in this file, providing the output in the form [ENVIRONMENT]: ..., [PEOPLE]: ..., and [OBJECTS]:..., \n\n{file_content}. Focus on the timestamp to understand the actual status."}
        ]
        chatGPT_answer = False
        while not chatGPT_answer:
            try:
                response = self._query_llm(message).choices[0].message.content 
                chatGPT_answer = True
            except Exception as e:
                print(f'Error: {e}')
        return response



    def respond(self, command, reply):
        if command.get(0).asString()=='get_resume':
            print('Received command GET_RESUME')
            reply.addString(self.resume())
        return True



    
    def updateModule(self):
      
        received_image = self._input_image_port.read()
        self._in_buf_image.copy(received_image)   
        frame = self._in_buf_array
        img=Image.fromarray(np.uint8(frame)).convert('RGB')
        buffered = BytesIO()
        img.save(buffered, format='png')
        base64_image = self.encode_image(buffered.getvalue())
        self.messages.append({"role": "user", "content":[
            {"type": "text", "text": 'Notify only significant changes in the scene. Remember the output format: [ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:... .'},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]})

        #self.messages.append({"role": "user", "content":"How are you?"})

        #start_time = time.time()
        chatGPT_answer = False
        while not chatGPT_answer:
            try:
                response = self._query_llm(self.messages) 
                chatGPT_answer = True
            except Exception as e:
                print(f'Error: {e}')     
        #end_time = time.time()
        # print(f'Answer time:{end_time-start_time}')   

        # Open the log file in append mode
        with open("logfile.txt", "a") as log_file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{current_time}] \n {response.choices[0].message.content}.\n")

        print(F'Risposta: {response.choices[0].message.content}')
        self.messages.append(response.choices[0].message)
        
        bot = self.agent_output_port.prepare()
        bot.clear()
        bot.addString(response.choices[0].message.content)
        self.agent_output_port.write()

        if len(self.messages) == 9:
            #print('Resume')
            #print(self.resume())
            self.messages = self.messages[0:3] + self.messages[5:9]  # Keep the first element, remove the rest

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
