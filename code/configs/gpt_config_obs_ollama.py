import json

data= {"model_name": "hsp-Vocalinteraction_gpt4o",
       "endpoint": "https://iitlines-swecentral1.openai.azure.com/",
       "api_version":"2023-03-15-preview",
       "temperature": 0.01,
       "top_p": 0.01,
       "max_length": 300,
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


with open('./configs/gpt_config_obs_ollama.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)