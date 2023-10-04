from flask import Flask, request, jsonify
from flask_cors import CORS
from api import OaiAPI

app = Flask("oai server")
CORS(app)

oai = OaiAPI()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/v1/api", methods=["POST", "GET"])
async def handle_prompt():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message not provided"}), 400
    print(data['message'])
    oai.react(data['message'])
    # reversed_message = data["message"][::-1]
    t = await oai.print_reply()

    result = oai.get_answer()
    final_result = validateResult(result.strip())
    print(final_result)
    return jsonify({"ai": final_result}), 200


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
    app.run(host='0.0.0.0', port=3000, debug=True)