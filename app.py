from flask import Flask
import pygame

app = Flask(__name__)

@app.route('/')
def home():
    return "Traffic Simulation Running 🚦"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
