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



def do_response_action(action, object, fake_nws_rpc_port) -> str:
#def do_response_action(action) -> str:
    """
    Run the most appropriate action during human-robot interaction. You can be 'ready' [home posture-DEFAULT], 'wave' [wave your harm to say hello], 'shake' [shake hand to introduce yourself], 't_pose' [to assume a t-pose],'take' [take an object], 'pour' [pour a liquid object], 'move' [move an object]. 
    To call this function, you have to specify which action you want to do.

    Available actions: ready [default], wave, shake, t_pose, pour, move

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
    if object:
        request.addString(f'{object}')

    # Send the RPC command and receive the response
    fake_nws_rpc_port.write(request)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{current_time}] Command action '{action}' sent."
    print(msg)

    # Open the log file in append mode
    with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt", "a") as log_file:
        log_file.write(msg)

    return "Command sent."


def apply_emotion(emotion, fake_nws_rpc_port) -> str:
#def apply_emotion(emotion) -> str:
    """
    Run the most appropriate emotion on ergoCub's face during human-robot interaction. You can smile, be puzzled, be unhappy. 
    To call this function, you have to specify which emotion you want to act.

    Available emotions: neutral [default], happy, alert, shy
    
    :return: Result message.
    """
   
    #result = input(f"Result of {emotion}: ")
    #print(f"Response: Action {emotion} result: {result}")
    
    ########################
    # Fake RPC to have async control
    # Create a request bottle and a response bottle
    request = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString(f'{emotion}')  # Action

    # Send the RPC command and receive the response
    fake_nws_rpc_port.write(request)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{current_time}] Command action '{emotion}' sent."
    print(msg)

    # Open the log file in append mode
    with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt", "a") as log_file:
        log_file.write(msg)

    return "Command sent."


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


def look_obj_around(client_port) -> str:
#def look_obj_around() -> str:
#def look_obj_around() -> str:
    """
    It allows ergoCub detecting the objects in the scene during human-robot interaction. 

    :return: It returns objects, condifence, and x,y positions in the image plane.
    """

    # obj_name = input(f"obj: ")
    # conf = input(f"conf: ")

    # result= f"I see {obj_name} with confidence score {conf}. "
    # print(result)

    # # Create a request bottle and a response bottle
    # request = yarp.Bottle()
    # response = yarp.Bottle()

    # print(f"Chiedo alla porta: {client_port}")

    # # Add a command to the request bottle (you can modify this as needed)
    # request.addString("get_obj")  # Command

    # client_port.write(request, response)
    # result = response.toString()

    # return result


    # client_obj_det_port = yarp.Port()
    # client_obj_det_port.open("/yarpYolo/where_coords:i")  # Name of the local port

    # if not yarp.Network.connect("/yarpYolo/where_coords:o", "/yarpYolo/where_coords:i"):
    #         print("Error connecting to /server port")
    # else:
    #      print('connesso')

    client_obj_det_port = yarp.BufferedPortBottle()
    client_obj_det_portName = "/yarpYolo/where_coords:i" 
    client_obj_det_port.open(client_obj_det_portName)
    print('{:s} opened'.format(client_obj_det_portName))
    yarp.Network.connect("/yarpYolo/where_coords:o",client_obj_det_portName)

    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    print(f"Chiedo alla porta: {client_port}")

    # Add a command to the request bottle (you can modify this as needed)
    request.addString("detect")  # Command
    client_port.write(request, response)
    print(response.toString())


    detection = []
    received_bboxes = client_obj_det_port.read(True)
    if received_bboxes:

            print(f'# Boxes: {received_bboxes.size()}')

            for i in range(0, received_bboxes.size()):

                print(f'Box idx: {i+1}')
                bboxe_btl = received_bboxes.get(i).asList()
                print(bboxe_btl)

                obj_name = bboxe_btl.get(0).asString()
                conf = bboxe_btl.get(1).asFloat64()
                x = bboxe_btl.get(2).asInt32()
                y = bboxe_btl.get(3).asInt32()

                print(f"I see {obj_name} with confidence score {conf} in position {x} and {y} in the image plane. ")
                detection.append(f"I see {obj_name} with confidence score {conf} in position {x} and {y} in the image plane. ")

    result = ''.join(detection)

    if not result:
        return "Checking"
    else:
        return result


def feedback_from_env(client_port) -> str:

    """
    It allows ergoCub to collect a feedback on the state of the scene during human-robot interaction. 

    :return: It returns info on environment, people and objects.
    """

    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    print(f"Chiedo alla porta: {client_port}")

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


def grasp(graspbase_rpc_port) -> str:
    """
    Grasp an object.
    
    :return: Result message.
    """
   
    request = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString(f'execute_grasp')  # Action

    # Send the RPC command and receive the response
    graspbase_rpc_port.write(request)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{current_time}] Command action 'execute_grasp' sent."
    print(msg)

    # Open the log file in append mode
    with open("/home/ccalabrese-iit.local/dev_iit/LLM4planning/code/robot_state_logfile.txt", "a") as log_file:
        log_file.write(msg)

    return "Command sent."