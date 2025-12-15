import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Be-Bot API Home Page"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    param = data.get('param', '')

    return jsonify({'your param': param})

if __name__ == '__main__':
    app.run()
