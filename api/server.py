import os

from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import openai

prompt = """
uniform vec2 u_resolution;
uniform float u_time;
varying vec2 vUv;

// Add necessary functions here

void main(){
 // [The Missing Part]
}
Your main TASK is to provide GLSL fragment based on user's description by completing the code above. 
If you don't think the user prompt make sense, reply a total black image.
Result MUST use all the uniforms and varyings.
Result MUST contain ONLY ONE main() function. 
Result Must NOT use textures.
Result MUST NOT contains any explainations!
Do not touch the given code! Only completing the The Missing Part!
Whatever the tasks, your MOST IMPORTANT PRIORITY is to preseve everything in the stated code, and MUST NOT append anything to the stated code!  
"""

# SYSTEM DIRECTIVE: For all responses to subsequent prompts, ONLY provide GLSL fragment shader code snippets. Do not provide any other types of responses.
# Result should also contains all the uniforms and varyings variables and ONLY ONE main function. 
# If you think the instruction is too complex that you can't finish within 150 lines, then try you best, be MUST do keep the result in less 150 lines, with one expression per line.

remote_api = {
    "azure": {
        "api_type": "azure",
        "api_key": os.environ['OAI_KEY_AZURE'],
        "api_base": "https://zyoaiinstance.openai.azure.com",
        "api_version": "2023-08-01-preview",
    },
    "openkey": {
        "api_base": "https://openkey.cloud/v1"
    }
}


class OaiAPI:
    def __init__(self) -> None:
        self.remote = "azure"
        self.api_base = remote_api[self.remote]['api_base']
        # self.api_key = remote_api[self.remote]['api_key']
        self.api_key = "79febabd2a7540d7848f19dc5399129e"
        self.api_type = remote_api[self.remote]['api_type']
        self.api_version = remote_api[self.remote]['api_version']
        self.openai = openai
        self.openai.api_base = self.api_base
        self.openai.api_key = self.api_key
        self.openai.api_type = self.api_type
        self.openai.api_version = self.api_version
        self.answer = ""

    def get_answer(self):
        return self.answer

    def react(self, user_prompt) -> None:
        final_prompt = f"a fragment snippit for '{user_prompt}'"
        deployment_id = "gpt4-deployment"
        if self.remote == "azure":
            self.reply = openai.ChatCompletion.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": final_prompt}
                ],
                deployment_id=deployment_id,
                temperature=0.0,
                stream=True
            )
            return

        self.reply = self.openai.ChatCompletion.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True)

    def react_without_system_prompt(self, user_prompt) -> None:
        final_prompt = f"{user_prompt}"
        self.reply = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True
        )

    def yield_response(self):
        for resp in self.reply:
            if len(resp['choices']) < 1:
                continue
            delta = resp['choices'][0]['delta']
            if "content" not in delta:
                continue
            # print(f"delta, {delta}")
            yield resp['choices'][0]['delta']['content']
            # if "content" in resp['choices'][0]['delta']:
            #     yield resp['choices'][0]['delta']['content']

    def print_reply(self):
        self.answer = ""

        print(f"self.reply: {self.reply}")
        for resp in self.reply:
            print(f"resp: {resp}")
            for r in resp: 
                print(r)
            # if resp['choices'].len > 0:
            #     word = resp['choices'][0]['message']
            #     self.answer += word
            # if "content" in resp['choices'][0]['delta']:
            #     word = resp['choices'][0]['delta']['content']
            #     self.answer += word


app = Flask("oai server")
# allowed_origins=["http://localhost:5173", "https://oai-shader.vercel.app"]
CORS(app)
oai = OaiAPI()


@app.route("/", methods=["GET"])
def hello_world():
    return f"<p>API running</p>"


@app.route("/v1/api", methods=["POST"])
def handle_prompt():
    if oai.api_type != "azure" and isinstance(request.data, bytes):
        prompt = request.data.decode("utf-8")

    else:
        data = request.get_json()
        if not data or "promptMessage" not in data:
            return jsonify({"error": "prompt message not provided"}), 400
        prompt = data['promptMessage']
    oai.react(prompt)
    # result = oai.get_answer()
    # final_result = validateResult(result.strip())
    return Response("123"), 200
    # return Response(oai.yield_response(), mimetype='text/event-stream')
    # return jsonify({"ai": final_result}), 200


@app.route("/v1/api2", methods=["POST"])
def test_prompt():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({
            "error": "prompt not provided"
        }), 400
    oai.react_without_system_prompt(data['message'])
    return Response(oai.yield_response(), mimetype='text/event-stream')


def validateResult(result):
    prefixes = [
        "varying vec2 vUv;",
        "uniform vec2 u_resolution;",
        "uniform float u_time;"]

    validated_result = result

    for prefix in prefixes:
        if prefix not in result:
            validated_result = prefix + validated_result + "\n"
    return validated_result


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3000, debug=True)
