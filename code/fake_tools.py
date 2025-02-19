#!/usr/bin/env python3

import platform
import sys
import yaml
import time
import yarp
from datetime import datetime   
from pathlib import Path
# from mutual-gaze-classifier-demo import mutualgaze-classifier
# import whisper



def do_response_action(action, fake_nws_rpc_port) -> str:
#def do_response_action(action) -> str:
    """
    Run the most appropriate action during human-robot interaction. You can be 'ready' [home posture-DEFAULT], 'wave' [wave your harm to say hello], 'shake' [shake hand to introduce yourself], 't_pose' [to assume a t-pose],'take' [take an object], 'pour' [pour a liquid object], 'move' [move an object]. 
    To call this function, you have to specify which action you want to do.

    Available actions: ready [default], wave, shake, t_pose, take, pour, move

    :return: Result message.
    """
   
    # result = input(f"Result of {action}: ")
    # print(f"Response: Action {action} result: {result}")

    ########################
    # Fake RPC to have async control
    # Create a request bottle and a response bottle
    request = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString(f'{action}')  # Action

    # Send the RPC command and receive the response
    fake_nws_rpc_port.write(request)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{current_time}] Command action '{action}' sent."
    print(msg)

    # Open the log file in append mode
    with open("/home/carmela/dev_iit/development/LLM4chatting/robot_state_logfile.txt", "a") as log_file:
        log_file.write(msg)

    return "Command sent."


def apply_emotion(emotion) -> str:
#def apply_emotion(emotion) -> str:
    """
    Run the most appropriate emotion on ergoCub's face during human-robot interaction. You can smile, be puzzled, be unhappy. 
    To call this function, you have to specify which emotion you want to act.

    Available emotions: neutral [default], happy, alert, shy
    
    :return: Result message.
    """
   
    result = input(f"Result of {emotion}: ")
    print(f"Response: Action {emotion} result: {result}")

    return result



#def get_action(action_port) -> str:
def get_action() -> str:
    """
    Get the human action during human-robot interaction.

    :return: Result message.
    """
    
    result = input(f"The person is ")
    print(f"Response: Action recognition result: {result}")


    result =f'The person is {result}'

    # Print the response
    print(f"Response: {result}")

    return result


#def look_obj_around(client_port) -> str:
def look_obj_around() -> str:
#def look_obj_around() -> str:
    """
    It allows ergoCub detecting the objects in the scene during human-robot interaction. 

    :return: It returns objects, condifence, and x,y positions in the image plane.
    """

    obj_name = input(f"obj: ")
    conf = input(f"conf: ")

    result= f"I see {obj_name} with confidence score {conf}. "
    print(result)

    return result



def feedback_from_env(client_port) -> str:

    """
    It allows ergoCub to collect a feedback on the state of the scene during human-robot interaction. 

    :return: It returns info on environment, people and objects.
    """

    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString("get_resume")  # Command

    client_port.write(request, response)
    result = response.toString()

    return result


def speak() -> str:
    """
    It allows ergoCub speaking during human-robot interaction. 
    To call this function, you have to the text to say.

    :return: Result message.
    """
   
    # # Create a request bottle and a response bottle
    # request = yarp.Bottle()
    # response = yarp.Bottle()

    # # Add a command to the request bottle (you can modify this as needed)
    # request.addString("command_name")  # Command
    # request.addString(f'{action}')  # Action

    # # Send the RPC command and receive the response
    # client_port.write(request, response)
    # result = response.toString()

    result =f'Text sent.'

    # Print the response
    print(f"Response: {result}")

    if not result:
        return "Speaking"
    return result
