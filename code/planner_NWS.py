
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


class Planner(yarp.RFModule):

    def configure(self, rf) :
        self.period = 1.0

        self.agent_text_portName = "/agent/text:i"
        self.agent_text_port = yarp.BufferedPortBottle()
        self.agent_text_port.open(self.agent_text_portName)

        self.agent_output_portName = "/agent/text:o"
        self.agent_output_port = yarp.BufferedPortBottle()
        self.agent_output_port.open(self.agent_output_portName)

        self.observer_text_portName = "/observer/text:i"
        self.observer_text_port = yarp.BufferedPortBottle()
        self.observer_text_port.open(self.observer_text_portName)

        self.intState_text_portName = "/intState/text:i"
        self.intState_text_port = yarp.BufferedPortBottle()
        self.intState_text_port.open(self.intState_text_portName)


        self.client_fake_nws_rpc_port = yarp.Port()
        self.client_fake_nws_rpc_port.open("/fake_nws_rpc")  # Name of the local port

        if not yarp.Network.connect("/fake_nws_rpc", "/fake_robot_nws/rpc"):
            print("Error connecting to /fake_robot_nws/rpc port")
              
        self.config_path = rf.check("config", yarp.Value("")).asString()
        if not self.config_path:
            print("Error: config file path is missing")
            return False

        self._input_image_port = yarp.BufferedPortImageRgb()
        imageInPortName = '/agent/image:i'
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
        tool_module = importlib.import_module(self.config['tool_module'])
        tools = {n: f for n, f in inspect.getmembers(tool_module) if inspect.isfunction(f)}

        self.function_resolver = tools
        with open('/app/LLM4planning/code/robot_tools.json', 'r') as openfile:
             self.tool_descriptions = json.load(openfile)

        with open("/app/LLM4planning/code/robot_state_logfile.txt", "a") as log_file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f'{current_time} - Robot started up\n')
        return True
               
                               

    def _query_llm(self, messages, tool_choice: Union[Literal["none", "auto"]] = "auto"):
        response = ""
        response = self.azureOpenAI_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p = self.top_p,
            max_tokens = self.max_length,
            messages=messages,
            tools=self.tool_descriptions,
            tool_choice=tool_choice,
        )
        return response

    
    def updateModule(self):
        
        bottle = self.agent_text_port.read(False)
        text_input = ""
        if bottle is not None:
            for i in range(bottle.size()):
               message = bottle.get(i).asString()  # Assuming messages are strings
               text_input+=message + " "
            bottle.clear()

        skip_human = False
        skip_obs = False
        skip_intState = False

        if text_input == "":
            skip_human = True
        else:
            print("💬 Human: "+ text_input)
            text_input = "💬 Human: "+ text_input
            self.messages.append({"role": "user", "content": text_input})

        bottle = self.observer_text_port.read(False)
        obs_fb_input = ""
        if bottle is not None:
           for i in range(bottle.size()):
               message = bottle.get(i).asString()  # Assuming messages are strings
               obs_fb_input+=message + " "
           bottle.clear()
        obs_fb_input = obs_fb_input.strip()
        
        if obs_fb_input == 'No significant changes in the scene.' or obs_fb_input == "":
            skip_obs = True
        else:
            print("👁️ Observer: "+ obs_fb_input)
            obs_fb_input = "👁️ Observer: "+ obs_fb_input
            #msg = text_input + "\n" + obs_fb_input
            self.messages.append({"role": "user", "content": obs_fb_input})

        bottle = self.intState_text_port.read(False)
        intState_input = ""
        if bottle is not None:
           for i in range(bottle.size()):
               message = bottle.get(i).asString()  # Assuming messages are strings
               intState_input+=message + " "
           bottle.clear()
        intState_input = intState_input.strip()

        if intState_input == 'Nothing is running' or intState_input == 'Nothing is running.' or intState_input == "":
            skip_intState = True
        else:
            print("🔎 Internal state: "+ intState_input)
            intState_input = "🔎 Internal state: "+ intState_input
            self.messages.append({"role": "user", "content": intState_input})

        if any([not(skip_human), not(skip_obs), not(skip_intState)]):
        
            chatGPT_answer = False
            while not chatGPT_answer:
                try:
                    response = self._query_llm(self.messages)
                    chatGPT_answer = True
                except Exception as e:
                    print(f'Error: {e}')
            
            self.messages.append(response.choices[0].message)

            if (response.choices[0].message.content is not None):
                bottle_answer = response.choices[0].message.content
                print("🤖💭 ergoCub: " + bottle_answer +'\n')
            else:
                bottle_answer = ""
                
            if response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls
                actions_ = [tool_calls]
                for tcs in actions_:
                    if not tcs:
                        continue
                    for tc in tcs:
                        function_call = tc.function
                        func = function_call.name
                        # invoke functions
                        bot = self.client_fake_nws_rpc_port.prepare()
                        bot.clear()
                        bot.addString(function_call)
                        self.client_fake_nws_rpc_port.write()
                        
                        fcn_state= 'function invoked'
                        self.messages.append(
                            {
                                "role": "tool",
                                "name": func,
                                "content": fcn_state,
                                "tool_call_id": tc.id,
                            }
                        )
                
            bot = self.agent_output_port.prepare()
            bot.clear()
            bot.addString(bottle_answer)
            self.agent_output_port.write()
    
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
        self.client_fake_nws_rpc_port.close()
        self.client_emotion_rpc_port.close()
        self.agent_output_port.close()
        return True
    
    
    def interruptModule(self):
        self.agent_text_port.interrupt()
        self.client_fake_nws_rpc_port.interrupt()
        #self.client_observer_rpc_port.interrupt()
        self.client_emotion_rpc_port.interruption()
        self.agent_output_port()
        return True
    
#########################################333

if __name__ == '__main__':
    
    yarp.Network.init()

    mod = Planner()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
