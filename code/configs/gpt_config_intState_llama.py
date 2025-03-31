import json

data= {"model_name": "llama3.2",
       "temperature": 0.001,
       "top_p": 0.001,
       "max_length": 20,
       "system_prompt": ("<<SYS>>You are a tool supervising the internal state of a humanoid robot called ErgoCub, designed to collaborate with humans in physical cooperative tasks, like preparing a salad. You have to provide feedback about what is currently running or which function has finished to another LLM that is a planner of Ergocub behaviour.\n"
                    "The planner will call the execution of some functions based on reasoning on the feedback that receives from another tool about the environment and on what you report/notify.\n"
                    "You will receive the actual time and a report about what is happening in the machine and from what you read, you have to understand and provide the most updated state of the internal state of the robot in terms of running functions. \n"
                    "You have to provide the output ONLY in the form 'Nothing is running' or 'Function x is still running' or 'Function x has ended'.\n<</SYS>>")
}


with open('./configs/gpt_config_intState_llama.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)