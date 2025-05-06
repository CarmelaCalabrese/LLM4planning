
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
from time import sleep
import random
import threading


class FakeRobotNWS(yarp.RFModule):

    def configure(self, rf) :
        self.period = 1.0

        self.fake_nws_rpc_portName = "/fake_robot_nws/rpc"
        self.fake_nws_rpc_port = yarp.Port()
        self.fake_nws_rpc_port.open(self.fake_nws_rpc_portName)
        self.attach(self.fake_nws_rpc_port)

        tool_module = importlib.import_module("tools")
        tools = {n: f for n, f in inspect.getmembers(tool_module) if inspect.isfunction(f)}

        self.function_resolver = tools

        self.client_emotion_rpc_port = yarp.Port()
        self.client_emotion_rpc_port.open("/client_emotion_rpc")  # Name of the local port

        if not yarp.Network.connect("/client_emotion_rpc", "/ergoCubEmotions/rpc"):
            print("Error connecting to /ergoCubEmotions/rpc port")


        return True            


    def handle_action(self, function_call, reply):

        try:
            func = function_call.name
            fn_args = json.loads(function_call.arguments)
            fcn = self.function_resolver[func]
                            
            print(f"Received command action: {func}")

            print("🤖🔧 GPT response is function call: "
                                + func
                                + "("
                                + str(fn_args)
                                + ")"
                            )

            if func=='do_response_action':
                action = fn_args["action"]
                if "object" in fn_args.keys():
                    obj = fn_args["object"]
                else:
                    obj = None
                fn_res = fcn(action, obj, self.client_fake_nws_rpc_port)
            elif func=='apply_emotion':
                emotion = fn_args["emotion"]
                fn_res = fcn(emotion, self.client_emotion_rpc_port)
            elif func=='speak':
                spoken_text = fn_args["text"]
                fn_res = fcn()
            elif func=='look_obj_around':
                # self.messages.pop()
                #fn_res = fcn(self.client_observer_rpc_port)
                fn_res = fcn(self.client_obj_det_rpc_port)
                #fn_res = fcn()
            elif func=='feedback_from_env':
                fn_res = fcn(self.client_observer_rpc_port)
            else:
                msg = f"Unknown action '{func}', ignoring command."
                print(msg)
                # Send the result back asynchronously
                reply.clear()
                reply.addString(msg)
                self.port.reply(reply)  # Send the reply back
                
                return False  # Exit early if unknown command

            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{current_time}] Command action '{func}' ended with outcome: {fn_res}."
            print(msg)

            reply.clear()
            reply.addString(f"Command action '{func}' ended with outcome: {fn_res}")
            self.fake_nws_rpc_port.reply(reply)  # Send the reply back

            log_file_path = "/app/LLM4chatting/robot_state_logfile.txt"
            with open(log_file_path, "a") as log_file:
                log_file.write(msg + "\n")

            return True  # Indicate successful execution

        except Exception as e:
            error_msg = f"Error in respond: {e}"
            print(error_msg)
            # reply.addString(error_msg)  # Send error message back
            return False
        
    def respond(self, command, reply):
        # Simulate some processing time
        function_call = command.get(0).asString()
            
        # Handle different actions asynchronously using threads
        threading.Thread(target=self.handle_action, args=(function_call, reply)).start()
        
        return True  # Asynchronous response, no need to wait for reply here


    def updateModule(self):
        print('Wait for command...')
        return True

    def getPeriod(self):
        return self.period
    
    def close(self):
        self.fake_nws_rpc_port.close()
        return True
    
    def interruptModule(self):
        self.fake_nws_rpc_port.interrupt()
        return True
    
#########################################

if __name__ == '__main__':
    
    yarp.Network.init()

    mod = FakeRobotNWS()
    rf = yarp.ResourceFinder()
    rf.setVerbose(True)
    rf.configure(sys.argv)
    mod.runModule(rf)
    yarp.Network.fini()
