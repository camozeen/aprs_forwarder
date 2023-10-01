import flask
import json

app = flask.Flask(__name__, instance_relative_config=True)

@app.route('/', methods=['POST'])
def data():
    print(flask.request.get_json())
    return json.dumps({ 'message': 'ok' })

