#!/usr/bin/env python3

import platform
import sys
import yaml
import time
import yarp

from pathlib import Path
# from mutual-gaze-classifier-demo import mutualgaze-classifier
# import whisper



def do_response_action(action, client_port, manipulation_port) -> str:
#def do_response_action(action) -> str:
    """
    Run the most appropriate action during human-robot interaction. You can be 'ready' [home posture-DEFAULT], 'wave' [wave your harm to say hello], 'shake' [shake hand to introduce yourself], 't_pose' [to assume a t-pose]. 
    To call this function, you have to specify which action you want to do.

    Available actions: ready [default], wave, shake, t_pose

    :return: Result message.
    """
   
    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    #if action is not 'ready':
    # Add a command to the request bottle (you can modify this as needed)
    request.addString(f'{action}')  # Action

    # Send the RPC command and receive the response
    client_port.write(request, response)
    result = response.toString()
    # if result == 'Problema'or 'Capito':
    #     result = 'done'
    # print(f"Response: Action {action} result: {result}")

    check_act = False
    while check_act:
        print('Sono qui')
        manipulation_port.write('is_finished', response)
        #result = response.toString()
        if result=='[ok]':
            check_act = True
        print(result)

    time.sleep(5)
    # Add a command to the request bottle (you can modify this as needed)
    request2 = yarp.Bottle()
    response2 = yarp.Bottle()

    request2.addString('home')  # Back home
    client_port.write(request2, response2)

    # # Send the RPC command and receive the response
    # client_port.write(request, response)
    # result = response.toString()
    # if result == 'Problema'or 'Capito':
    #     result = 'Fatto'
    # print(f"Response: Action 'ready' result: {result}")

    if not result:
        return "Action running"
    return result


def apply_emotion(emotion, client_port, manipulation_port) -> str:
#def apply_emotion(emotion) -> str:
    """
    Run the most appropriate emotion on ergoCub's face during human-robot interaction. You can smile, be puzzled, be unhappy. 
    To call this function, you have to specify which emotion you want to act.

    Available emotions: neutral [default], happy, alert, shy
    
    :return: Result message.
    """
   
    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString("setEmotion")  # Command
    request.addString(f'{emotion}')  # Emotion


    # Send the RPC command and receive the response
    client_port.write(request, response)
    result = response.toString()

    # Print the response
    print(f"Response: {result}")

    time.sleep(10)

    # # Check if any action is running, I keep the emotion and then I go back to neutral
    # check_act = False
    # while check_act:
    #     manipulation_port.write('is_finished', response)
    #     #result = response.toString()
    #     if result=='[ok]':
    #         check_act = True

    # # Add a command to the request bottle (you can modify this as needed)
    # request2 = yarp.Bottle()
    # response2 = yarp.Bottle()

    # request2.addString("setEmotion")  # Command
    # request2.addString("neutral")  # Emotion
    # client_port.write(request2, response2)

    if not result:
        return "Emotion running"
    return result



#def speak(text, speak_port) -> str:
def speak(text) -> str:
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

    result =f'Text {text} sent.'

    # Print the response
    print(f"Response: {result}")

    if not result:
        return "Speaking"
    return result


#def get_action(action_port) -> str:
def get_action() -> str:
    """
    Get the human action during human-robot interaction.

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

    result =f'The person is waving.'

    # Print the response
    print(f"Response: {result}")

    if not result:
        return "Checking"
    return result



#def look_obj_around(client_obj_det_rpc_port, client_gaze_rpc_port, client_obj_dets_port, object) -> str:
def look_obj_around(client_obj_det_rpc_port, client_obj_dets_port, object) -> str:

    """
    It allows ergoCub detecting the objects in the scene during human-robot interaction. 

    :return: It returns objects, confidence, and x,y positions in the image plane.
    """
   
    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    # Add a command to the request bottle (you can modify this as needed)
    request.addString("get_bbox")  # Command
    request.addString(f'{object}')  # Action

    # Send the RPC command and receive the response
    client_obj_det_rpc_port.write(request, response)
    result = response.toString()

    time.sleep(0.5)

    # # Create a request bottle and a response bottle
    # request = yarp.Bottle()
    # response = yarp.Bottle()

    # # Add a command to the request bottle (you can modify this as needed)
    # request.addString("look_at")  # Command
    # request.addFloat64(f'{object}')  # Position

    # # Send the RPC command and receive the response
    # client_gaze_rpc_port.write(request, response)
    # result = response.toString()

    detection = []
    received_bboxes = client_obj_dets_port.read()
    if received_bboxes:

            print(f'# Boxes: {received_bboxes.size()}')

            if received_bboxes.size()==0:
                print(f"Sorry, I do not see the object you look for.")
                detection.append(f"Sorry, I do not see the object you look for.")
            else:
                for i in range(0, received_bboxes.size()):

                    print(f'Box idx: {i+1}')
                    bboxe_btl = received_bboxes.get(i).asList()

                    x1y1x2y2 = bboxe_btl.get(0).asList()
                    x1y1x2y2_list= []
                    for i in range(0, x1y1x2y2.size()):
                        x1y1x2y2_list.append(int(x1y1x2y2.get(i).asFloat64()))
                    
                    centroid = bboxe_btl.get(1).asList()
                    centroid_list= []
                    for i in range(0, centroid.size()):
                        centroid_list.append(int(centroid.get(i).asInt64()))

                    label = bboxe_btl.get(2).asString()
                    conf = bboxe_btl.get(3).asFloat64()

                    print(f"I see {label} with confidence score {conf} in position {centroid_list} in the image plane.")
                    detection.append(f"I see {label} with confidence score {conf} in position {centroid} in the image plane.")
                    
                    
    result = ''.join(detection)

    if not result:
        return "Checking"
    return result
