from pygame import Color

WIDTH = 800
HEIGHT = 800
TITLE = "Car Racing"
FPS = 60


MAP = "tight_track.json"

COLORS = {
    'background' : Color("#121212"),
    'white' : Color("#FFFFFF"),
    "grass" : Color("#3aba4d"),
    "track" : Color("#878787"),
    "red" : Color("#ff4545")
}

LOAD_DATA = False
LOAD_FILE = "workingtwo.pickle"

# Car settings
CAR_SIZE = 20

# Neural Network Settings
HIDDEN_PERCEPTRONS = 4

# Genetic Algorithm Settings
POP_SIZE = 30
GENERATIONS = 15
LIFESPAN = 20 #in seconds
MUTATION_CHANCE = 0.35
MUTATION_RATE = 0.35