import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "do_response_action",
            "description": "Run the most appropriate action during human-robot interaction. You can be 'ready' [home posture-DEFAULT], 'wave' [wave your harm to say hello], 'shake' [shake hand to introduce yourself], 't_pose' [to assume a t-pose], 'take' [take an object], 'pour' [pour a liquid object], 'move' [move an object]. .. To call this function, you have to specify which action you want to do.",
            "parameters": {
				"type": "object",
				"properties": {
                    "action": {
                        "type": "string", 
                        "description": "The name of the action to run. The action must be coherent with the interaction. Available values: ready [default], wave, shake, t_pose, take, pour, move.",
                        },
					"object": {
                        "type": "string", 
                        "description": "The name of the object to run the action on. The object must be coherent with the interaction.",
                        },
                    },
                "required": ["action"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_emotion",
            "description": "Run the most appropriate emotion on ergoCub's face during human-robot interaction. You can smile, be puzzled, be unhappy. To call this function, you have to specify which emotion you want to act.",
            "parameters": {
                "type": "object",
                "properties": {
                    "emotion": {
                        "type": "string",
                        "description": "The name of the emotion to act. The emotion must be coherent with the interaction. Available values: neutral [default], happy, alert, shy.",
                    },
                },
                "required": ["emotion"],
            },
        }
    },
	{
        "type": "function",
        "function": {
            "name": "get_action",
            "description": "Get the human action during human-robot interaction."
        }
    },   
	{
        "type": "function",
        "function": {
            "name": "look_obj_around",
            "description": "It allows ergoCub detecting the objects in the scene during human-robot interaction. It returns objects, condifence, and x,y positions in the image plane.",
        }
    },
	{
		"type": "function",
        "function": {
            "name": "feedback_from_env",
            "description": "It allows ergoCub to collect a feedback on the state of the scene during human-robot interaction.  It returns info on environment, people and objects.",
        } 
    },
	{
		"type": "function",
        "function": {
            "name": "speak",
            "description": "It allows ergoCub speaking during human-robot interaction. To call this function, you have to the text to say. I returns result message.",
        }		
    },
]



with open("fake_robot_tools.json", "w") as outfile:
	json.dump(tools, outfile)