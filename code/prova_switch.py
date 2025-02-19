from openai import OpenAI, AzureOpenAI
import os

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)


if __name__ == '__main__':
    messages=[
    {"role": "system", "content": "You are a helpful assistant."},]
    question=""
    model = "llama3.2:1b"

    while True:
        question = input("You: ")
        if question == "exit":
            break
        elif question == "":
            continue
        elif question == "clear":
            messages = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            continue
        elif question == "history":
            for message in messages:
                print(f"{message['role']}: {message['content']}")
            continue
        elif question == "undo":
            messages.pop()
            continue
        elif question == "switch_azure":
            client = AzureOpenAI(
            azure_endpoint = "https://iitlines-swecentral1.openai.azure.com/", 
            api_key=os.getenv("AZURE_API_KEY"),
            api_version="2023-03-15-preview"
            )
            model = "hsp-Vocalinteraction_gpt4o"
            continue
        elif question == "switch_ollama":
            client = OpenAI(
                base_url = 'http://localhost:11434/v1',
                api_key='ollama', # required, but unused
                )
            model = "llama3.2:b1"
            continue
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

        print(response.choices[0].message.content)