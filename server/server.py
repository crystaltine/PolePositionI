# Simple flask server

from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Routes
@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello World'})

app.run(port=5000, debug=True)