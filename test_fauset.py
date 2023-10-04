import openai


openai.api_base = "https://openkey.cloud/v1"
openai.api_key = "sk-jIdDi9srkUoVlqVRIo0KQXu9eT6NMIf6t2FYZMQ2QU6eLGMg"

for resp in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "write a shader code that creates a green circle"}
        ],
        stream=True):
    if 'content' in resp.choices[0].delta:
        print(resp.choices[0].delta.content, end="", flush=True)
