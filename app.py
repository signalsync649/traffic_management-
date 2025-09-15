from flask import Flask, send_file
import pygame

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Traffic Simulation Running 🚦</h1><img src="/simulation">'

@app.route('/simulation')
def simulation():
    # run a single frame of pygame and save it
    pygame.init()
    screen = pygame.Surface((400, 400))
    screen.fill((0, 0, 0))  # background black
    pygame.draw.circle(screen, (255, 0, 0), (200, 200), 50)  # red circle as demo
    pygame.image.save(screen, "frame.png")
    return send_file("frame.png", mimetype='image/png')
