
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

        return True            

    def action_outcome(self, success_rate=0.8):
        return "Success" if random.random() < success_rate else "Failure"

    # def respond(self, command, reply):
    #     action = command.get(0).asString()
    #     print(action)
    #     print(f"Received command action '{action}'.")
    #     if action=='take':
    #         sleeping_time = 3
    #         success_rate = 0.8
    #     elif action=='pour':
    #         sleeping_time = 8
    #         success_rate = 0.7
    #     elif action=='move':
    #         sleeping_time = 5
    #         success_rate = 0.9
    #     elif action=='wave':
    #         sleeping_time = 2
    #         success_rate = 0.95     
    #     elif action=='shake':
    #         sleeping_time = 3
    #         success_rate = 0.95
    #     elif action=='t_pose':
    #         sleeping_time = 7
    #         success_rate = 0.7
    #     elif action=='ready':   
    #         sleeping_time = 2
    #         success_rate = 0.95
    #     time.sleep(sleeping_time)
    #     response = self.action_outcome(success_rate)
    #     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     msg = f"[{current_time}] Command action '{action}' ended with outcome: {response}."
    #     print(msg)
    #     # Open the log file in append mode
    #     with open("/home/carmela/dev_iit/development/LLM4chatting/robot_state_logfile.txt", "a") as log_file:
    #         log_file.write(msg)
    #     return True

    

    def handle_action(self, action, reply):
        try:

            action_map = {
                'take': (3, 0.8),
                'pour': (8, 0.7),
                'move': (5, 0.9),
                'wave': (2, 0.95),
                'shake': (3, 0.95),
                't_pose': (7, 0.7),
                'ready': (2, 0.95),
                'neutral': (0.5, 0.99),   
                'happy': (0.5, 0.99),
                'alert': (0.5, 0.99),
                'shy': (0.5, 0.99),
            }

            if action in action_map:
                sleeping_time, success_rate = action_map[action]
            else:
                msg = f"Unknown action '{action}', ignoring command."
                print(msg)
                # Send the result back asynchronously
                reply.clear()
                reply.addString(msg)
                self.port.reply(reply)  # Send the reply back
                return False  # Exit early if unknown command

            time.sleep(sleeping_time)
            response = self.action_outcome(success_rate)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{current_time}] Command action '{action}' ended with outcome: {response}."
            print(msg)

            reply.clear()
            reply.addString(f"Command action '{action}' ended with outcome: {response}")
            self.fake_nws_rpc_port.reply(reply)  # Send the reply back

            log_file_path = "/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt"
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
        action = command.get(0).asString()
        print(f"Received command action: {action}")
        
        # Handle different actions asynchronously using threads
        threading.Thread(target=self.handle_action, args=(action, reply)).start()
        
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
