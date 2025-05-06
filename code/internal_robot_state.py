
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


class LLMinternalState(yarp.RFModule):

    def configure(self, rf) :
        self.period = 0.5

        self.LLMintState_output_portName = "/intState/text:o"
        self.LLMintState_output_port = yarp.BufferedPortBottle()
        self.LLMintState_output_port.open(self.LLMintState_output_portName)

        self.LLMintState_rpc_portName = "/intState/rpc"
        self.LLMintState_rpc_port = yarp.Port()
        self.LLMintState_rpc_port.open(self.LLMintState_rpc_portName)
        self.attach(self.LLMintState_rpc_port)

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
        with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt", "r") as file:
            file_content = file.read()

        message=[
            {"role": "user", "content": f"From what you read, understand and summarize very briefly the most updated state of the internal state of the robot in terms of running modules. Provide the output in the form 'Nothing is running' or 'Function x is still running', \n\n{file_content}. Focus on the timestamp to understand the actual status."}
        ]
        chatGPT_answer = False
        while not chatGPT_answer:
            try:
                response = self._query_llm(message).choices[0].message.content 
                chatGPT_answer = True
            except Exception as e:
                print(f'Error: {e}')
        return response


    
    def updateModule(self):

        with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt", "r") as file:
            file_content = file.read()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message={"role": "user", "content": f"It's {current_time}. From what you read, understand and summarize very briefly the most updated state of the internal state of the robot: \n\n{file_content}."}
        self.messages.append(message)

        chatGPT_answer = False
        while not chatGPT_answer:
            try:
                response = self._query_llm(self.messages) 
                chatGPT_answer = True
            except Exception as e:
                print(f'Error: {e}')     
        
        print(f'Risposta: {response.choices[0].message.content}')
        self.messages.pop()

        bot = self.LLMintState_output_port.prepare()
        bot.clear()
        bot.addString(response.choices[0].message.content)
        self.LLMintState_output_port.write()

        return True


    def reset(self): 
        self.messages = [
            {"role": "system", "content": self.character},
        ]
        print(f"📝 Message history reset.")


    def getPeriod(self):
        return self.period
    
        
    def close(self):
        self.LLMintState_output_port.close()
        self.LLMintState_rpc_port.close()
        return True
    
    
    def interruptModule(self):
        self.LLMintState_output_port.interrupt()
        self.LLMintState_rpc_port.interrupt()
        return True
    
#########################################

if __name__ == '__main__':
    
    yarp.Network.init()

    mod = LLMinternalState()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
