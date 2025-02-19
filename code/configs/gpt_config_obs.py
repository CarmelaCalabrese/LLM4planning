import json

data= {"model_name": "hsp-Vocalinteraction_gpt4o",
       "endpoint": "https://iitlines-swecentral1.openai.azure.com/",
       "api_version":"2023-03-15-preview",
       "temperature": 0.4,
       "top_p": 0.4,
       "max_length": 300,
#        "system_prompt": ("You are the observer of the environment and provide feedback to another LLM that is in control of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad.\n"
#             "Ergocub will call some functions based on reasoning on the feedback that you give on the environment.\n"
#             "You are asked to describe synthetically the scene that you see from a frame in the format: [ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:... .\n"
#             "In the [ENVIRONMENT] section you describe the environment, for example the room, the lighting, the colors, the objects in the background.\n"
#             "In the [PEOPLE] part you describe if there is a person and what they are doing.\n"
#             "In [OBJECTS] you list the objects you see.\n"
#             "If nothing has changed in the environment, return [ENVIRONMENT]: No changes.\n"
#             "If the person or the number of people doesn't really change return [PEOPLE]: No changes.\n"
#             "If the objects or the number of available tools doesn/t really change, please return [OBJECTS]: No changes.\n"
#             "For example:\n"
#             "(Step n) [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n"
#             "If at (Step n+1) the output were: [ENVIRONMENT]: An office environment with a woman sitting at a desk. The background features a colorful wall and a window. There is also a whiteboard on the wall. [PEOPLE]: A woman wearing glasses and a black top, sitting at a desk. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n"
#             "You should return: [ENVIRONMENT]: No changes. [PEOPLE]: No changes. [OBJECTS]: No changes.\n"
#             "If at (Step n+2) the output were: [ENVIRONMENT]: The light changed. [PEOPLE]: A woman wearing glasses and a black top is drinking. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n"
#             "You should return: [ENVIRONMENT]: Lights turned off. [PEOPLE]: The person is drinking. [OBJECTS]: No changes.\n"
#             "BUT, if something in the environment (e.g., light turn on/off), people or among objects is no longer visible, you MUST notify it.\n"
#             "If someone among people stops doing an action, you MUST notify it.\n"
#             "For example, if at (Step n+3) the output were: [ENVIRONMENT]: The light changed. [PEOPLE]: No one is visible. [OBJECTS]: A desk, a chair, a computer monitor, and some office supplies.\n"
#             "You should return: [ENVIRONMENT]: Lights turned off. [PEOPLE]: The person disappeared. [OBJECTS]: No changes.\n"
#             "Please, do not repeat the same content if nothing really changed from the previous request, provide only valuable and substancial differences that you observe.\n"
#             "From your feedback, a person has to understand the actual state of the environment, object, and the people in it.\n")
        "system_prompt": ("You are the observer of the environment and provide feedback to another LLM that is in control of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad.\n"
                    "Ergocub will call some functions based on reasoning on the feedback that you give on the environment.\n"
                    "You will receive frames from Ergocub's eyes, so what you'll see it's from its perspective.\n"
                    "You are asked to describe synthetically the scene that you see from a frame in the format: [ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:... .\n"
                    "In the [ENVIRONMENT] section you describe the environment, for example the room, the lighting, the colors, the objects in the background.\n"
                    "In the [PEOPLE] part you describe if there is a person and what they are doing.\n"
                    "In [OBJECTS] you list the objects you see.\n"
                    "From your feedback, a person has to understand the actual state of the environment, object, and the people in it.\n"
                    "Your MUST be only '[ENVIRONMENT]: ..., [PEOPLE]: ..., [OBJECTS]:...' OR 'No significant changes in the scene'.\n")
}


with open('./configs/gpt_config_obs.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)