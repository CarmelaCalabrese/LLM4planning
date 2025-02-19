
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


class LLMchat(yarp.RFModule):

    def configure(self, rf) :
        self.period = 1/30

        self.agent_text_portName = "/agent/text:i"
        self.agent_text_port = yarp.BufferedPortBottle()
        self.agent_text_port.open(self.agent_text_portName)

        self.agent_output_portName = "/agent/text:o"
        self.agent_output_port = yarp.BufferedPortBottle()
        self.agent_output_port.open(self.agent_output_portName)

        self.observer_text_portName = "/observer/text:i"
        self.observer_text_port = yarp.BufferedPortBottle()
        self.observer_text_port.open(self.observer_text_portName)
 
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
        with open('/home/carmela/dev_iit/development/LLM4chatting/code/fake_robot_tools.json', 'r') as openfile:
             self.tool_descriptions = json.load(openfile)
             #print(self.tool_descriptions)


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
            tools=self.tool_descriptions,
            tool_choice=tool_choice,
        )
        return response

    
    def updateModule(self):
        
        bottle = self.agent_text_port.read()
        text_input = ""
        if bottle is not None:
           for i in range(bottle.size()):
               message = bottle.get(i).asString()  # Assuming messages are strings
               text_input+=message + " "
        bottle.clear()

        skip_human = False

        if text_input == "":
            skip_human = True

        if not skip_human:
            print("💬 Human: "+ text_input)
            text_input = "💬 Human: "+ text_input
            # self.messages.append({"role": "user", "content": text_input})

        bottle = self.observer_text_port.read()
        obs_fb_input = ""
        if bottle is not None:
           for i in range(bottle.size()):
               message = bottle.get(i).asString()  # Assuming messages are strings
               obs_fb_input+=message + " "
        bottle.clear()

        print("👁️ Observer: "+ obs_fb_input)
        obs_fb_input = "👁️ Observer: "+ obs_fb_input
        msg = text_input + "\n" + obs_fb_input

        self.messages.append({"role": "user", "content": msg})


        print('Ora chiedo a LLM')
        response = self._query_llm(self.messages)
        self.messages.append(response.choices[0].message)

        # run with function calls as long as necessary
        while response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            actions_ = [tool_calls]
            for tcs in actions_:
                if not tcs:
                    continue
                for tc in tcs:
                    function_call = tc.function
                    # invoke functions
                    func = function_call.name
                    fn_args = json.loads(function_call.arguments)
                    print("🤖🔧 GPT response is function call: "
                        + func
                        + "("
                        + str(fn_args)
                        + ")"
                    )

                    fcn = self.function_resolver[func]
                    done = False
                    if func=='do_response_action':
                        action = fn_args["action"]
                        #fn_res = fcn(action, self.client_action_rpc_port, self.manipulation_rpc_port)
                        fn_res = fcn(action)
                        done = True
                    elif func=='apply_emotion':
                        emotion = fn_args["emotion"]
                        #fn_res = fcn(emotion, self.client_emotion_rpc_port)
                        fn_res = fcn(emotion)
                        done = True
                    elif func=='speak':
                        spoken_text = fn_args["text"]
                        #fn_res = fcn(emotion, client_emotion_rpc_port)
                        fn_res = fcn(spoken_text)
                        done = True
                    elif func=='look_obj_around':
                        # self.messages.pop()
                        #fn_res = fcn(self.client_obj_dets_port)
                        fn_res = fcn()
                        done = True
                        # received_image = self._input_image_port.read()
                        # self._in_buf_image.copy(received_image)   
                        # frame = self._in_buf_array
                        # img=Image.fromarray(np.uint8(frame)).convert('RGB')
                        # buffered = BytesIO()
                        # img.save(buffered, format='png')
                        # print('Sto encodando l immagine')
                        # base64_image = self.encode_image(buffered.getvalue())
                        # print('Encoding terminato')
                        # self.messages.append({"role": "user", "content":[
                        #     {"type": "text", "text": f"{text_input}"},
                        #     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        # ]})
                    else:
                        fn_res = fcn(**fn_args)
                        done = True
                    
                    if done: 
                        print("🔧 Function result is: " + fn_res)
                        self.messages.append(
                            {
                                "role": "tool",
                                "name": func,
                                "content": fn_res,
                                "tool_call_id": tc.id,
                            }
                        )
            start_time = time.time()
            print('sto chiedendo a LLM')
            response = self._query_llm(self.messages)        
            end_time = time.time()
            print(f'Answer time:{end_time-start_time}')    
            self.messages.append(response.choices[0].message)

            if (response.choices[0].message.content is not None):
                bottle_answer = response.choices[0].message.content
            else:
                bottle_answer = ""
            print("🤖💭 ergoCub: " + bottle_answer +'\n')

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

    mod = LLMchat()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
