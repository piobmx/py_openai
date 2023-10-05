from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from oai import OaiAPI

app = Flask("oai server")
CORS(app)

oai = OaiAPI()

@app.route("/", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"


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

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3000, debug=True)

