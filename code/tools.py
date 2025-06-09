#!/usr/bin/env python3

import platform
import sys
import yaml
import time
import yarp
import numpy as np
from pathlib import Path
import math
# from mutual-gaze-classifier-demo import mutualgaze-classifier
# import whisper


def quaternion_matrix(quaternion):  #Copied from https://github.com/ros/geometry/blob/noetic-devel/tf/src/tf/transformations.py#L1515
    """Return homogeneous rotation matrix from quaternion.

    >>> R = quaternion_matrix([0.06146124, 0, 0, 0.99810947])
    >>> numpy.allclose(R, rotation_matrix(0.123, (1, 0, 0)))
    True

    """
    # epsilon for testing whether a number is close to zero
    _EPS = np.finfo(float).eps * 4.0

    q = np.array(quaternion[:4], dtype=np.float64, copy=True)
    nq = np.dot(q, q)
    if nq < _EPS:
        return np.identity(4)
    q *= math.sqrt(2.0 / nq)
    q = np.outer(q, q)
    return np.array((
        (1.0-q[1, 1]-q[2, 2],     q[0, 1]-q[2, 3],     q[0, 2]+q[1, 3], 0.0),
        (    q[0, 1]+q[2, 3], 1.0-q[0, 0]-q[2, 2],     q[1, 2]-q[0, 3], 0.0),
        (    q[0, 2]-q[1, 3],     q[1, 2]+q[0, 3], 1.0-q[0, 0]-q[1, 1], 0.0),
        (                0.0,                 0.0,                 0.0, 1.0)
        ), dtype=np.float64)


def axis_angle_matrix(pose, axis, angle):
    """Return homogeneous rotation matrix from pose, axis, angle."""
    rx = axis[0]
    ry = axis[1]
    rz = axis[2]

    cosine = math.cos(angle)
    sine = math.sin(angle)

    return np.array((
        (rx^2*(1-cosine)+cosine,     rx*ry*(1-cosine)-rz*sine,     rx*rz*(1-cosine)+ry*sine, pose[0]),
        (rx*ry*(1-cosine)+rz*sine,   ry^2*(1-cosine)+cosine,    ry*rz*(1-cosine)-rx*sine, pose[1]),
        (rx*rz*(1-cosine)-ry*sine,   ry*rz*(1-cosine)+rx*sine,  rz^2*(1-cosine)+cosine, pose[2]),
        (                0.0,                 0.0,                 0.0, 1.0)
        ), dtype=np.float64)



def camera2root (vec, pose, axis, angle):
    # Point in camera frame (x, y, z)
    p_cam = np.array([vec, 1.0])  # homogeneous coordinates

    #T_cam_to_root = quaternion_matrix(quaternion)    # Homogeneous transformation matrix (4x4) from camera to root
    T_cam_to_root = axis_angle_matrix(pose, axis, angle)    # Homogeneous transformation matrix (4x4) from camera to root
    
    # Transform the point
    p_root_homogeneous = T_cam_to_root @ p_cam

    # Extract the 3D coordinates
    p_root = p_root_homogeneous[:3]

    print("Point in root frame:", p_root)
    return p_root




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
   
    ## Move head around
    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    #yarp rpc /GazeController
    #look_at: point the camera to a 3D point in the robot frame

    # Add a command to the request bottle (you can modify this as needed)
    request.addString("look_at")  # Command
    request.addList(())  # I need to understand how to say theta head degrees on the right

    # Send the RPC command and receive the response
    client_gaze_rpc_port.write(request, response)
    result = response.toString()

    ## Look for object
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

                    u1v1u2v2 = bboxe_btl.get(0).asList()
                    u1v1u2v2_list= []
                    for i in range(0, u1v1u2v2.size()):
                        u1v1u2v2_list.append(int(u1v1u2v2.get(i).asFloat64()))
                    
                    centroid = bboxe_btl.get(1).asList()
                    centroid_list= []
                    for i in range(0, centroid.size()):
                        centroid_list.append(int(centroid.get(i).asInt64()))

                    print(centroid_list)

                    xyz = bboxe_btl.get(2).asList()
                    xyz_camera_frame_list= []
                    for i in range(0, xyz.size()):
                        xyz_camera_frame_list.append(int(xyz.get(i).asInt64()))

                    print(xyz_camera_frame_list) #in camera frame!!!!

                    label = bboxe_btl.get(3).asString()
                    conf = bboxe_btl.get(4).asFloat64()

                    print(f"I see {label} with confidence score {conf:.2f} in position {str(centroid_list)} in the image plane.")
                    detection.append(f"I see {label} with confidence score {conf:.2f} in position {str(centroid_list)} in the image plane.")
                    
                    
    result = ''.join(detection)

    if not result:
        return "Checking"
    return result


def point_at_obj_around(client_controller_port, ergocub_rs_pose, xyz_camera_frame_list) -> str:

    """

    :return: It returns objects, confidence, and x,y positions in the image plane.
    """
   
    ## Get xyz_camera_frame_list in robot frame
    #read /ergocub-rs-pose/pose:o to get camera pose in robot frame : x y z axis_x axis_y axis_z angle vector
    received_camera_pose = ergocub_rs_pose.read()
    if received_camera_pose:
            print(f'# Camera pose: {received_camera_pose.size()}')

            answer = received_camera_pose.get(0).asList()
            pose = answer[:2]
            axis = answer[3:5]
            angle = answer[6] 
            

    xyz_root_frame = camera2root(xyz_camera_frame_list, axis, angle, pose)

    ## Give command to the end effector to point at the object
    # Create a request bottle and a response bottle
    request = yarp.Bottle()
    response = yarp.Bottle()

    # # Add a command to the request bottle (you can modify this as needed)
    # request.addString("get_bbox")  # Command
    # request.addString(f'{object}')  # Action


    # time.sleep(0.5)

    if not result:
        return "Checking"
    return result