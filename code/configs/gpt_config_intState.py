import json

data= {"model_name": "hsp-Vocalinteraction_gpt4o",
       "endpoint": "https://iitlines-swecentral1.openai.azure.com/",
       "api_version":"2023-03-15-preview",
       "temperature": 0.4,
       "top_p": 0.4,
       "max_length": 300,
       "system_prompt": ("You are a tool supervising the internal state of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad.\n"
                     "You have to provide feedback about what is currently running or which function has finished to another LLM that is a planner of Ergocub behaviour.\n"
                    "The planner will call the execution of some functions based on reasoning on the feedback that receives from another tool about the environment and on what you report/notify.\n"
                    "You will receive the actual time and a report about what is happening in the machine and from what you read, you have to understand and summarize very briefly the most updated state of the internal state of the robot in terms of running functions. \n"
                    "Provide the output in the form 'Nothing is running' or 'Function x is still running' or 'Function x has ended'. Focus on the timestamp to understand the actual status. Please, don't forget to notify that an action ended and the success/failure ONLY in the following 5seconds!")
}


with open('./configs/gpt_config_intState.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)