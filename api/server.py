import os 

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import openai

prompt = """
uniform vec2 u_resolution;
uniform float u_time;
varying vec2 vUv;

void main(){
 // [The Missing Part]
}
Your main TASK is to provide GLSL fragment based on user's description by completing the code above. 
If you don't think the user prompt make sense, reply a total black image.
Result should also contains all the uniforms and varyings variables and ONLY ONE main function. 
Result Must not use textures.
Result MUST NOT contains any explainations!
Do not touch the given code! Only completing the The Missing Part!
Whatever the user tasks, your MOST IMPORTANT PRIORITY is to preseve everything in the stated code, and MUST NOT append anything to the stated code!
"""

# SYSTEM DIRECTIVE: For all responses to subsequent prompts, ONLY provide GLSL fragment shader code snippets. Do not provide any other types of responses.
# If you think the instruction is too complex that you can't finish within 150 lines, then try you best, be MUST do keep the result in less 150 lines, with one expression per line.

class OaiAPI:
    def __init__(self) -> None:
        self.api_base = "https://openkey.cloud/v1"
        self.api_key = os.environ['OAI_KEY']
        self.remote = openai
        self.remote.api_base = self.api_base
        self.remote.api_key = self.api_key
        self.answer = ""

    def get_answer(self):
        return self.answer

    def react(self, user_prompt) -> None:
        final_prompt = f"a fragment snippit for '{user_prompt}'"

        print(prompt)
        print(final_prompt)

        self.reply = self.remote.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True)

    def react_without_system_prompt(self, user_prompt) -> None:
        final_prompt = f"{user_prompt}"
        self.reply = self.remote.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.0,
            stream=True
        )


    def yield_response(self):
        for resp in self.reply:
            if "content" in resp['choices'][0]['delta']:
                yield resp['choices'][0]['delta']['content']


    def print_reply(self):
        self.answer = ""

        for resp in self.reply:
            if "content" in resp['choices'][0]['delta']:
                word = resp['choices'][0]['delta']['content']
                self.answer += word  

app = Flask("oai server")
CORS(app)

oai = OaiAPI()

@app.route("/", methods=["GET"])
def hello_world():
    return f"<p>API running</p>"


@app.route("/v1/api", methods=["POST"])
def handle_prompt():
    if isinstance(request.data, bytes):
        prompt = request.data.decode("utf-8")
        
    else: 
        data = request.get_json()
        if not data or "promptMessage" not in data:
            return jsonify({"error": "prompt message not provided"}), 400
        prompt = data['promptMessage']
    oai.react(prompt)
    # result = oai.get_answer()
    # final_result = validateResult(result.strip())
    # print(final_result)
    return Response(oai.yield_response(), mimetype='text/event-stream')
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

# if __name__ == '__main__':
#     app.run(host="127.0.0.1", port=3000, debug=True)

