import math
import pickle
import random

from gui import Gui
from network import *
from settings import *

if not LOAD_DATA:
    pop = Population(POP_SIZE, GENERATIONS, LIFESPAN, MUTATION_CHANCE, MUTATION_RATE, network_type=Genetic)

else:
    with open("Networks/"+LOAD_FILE, 'rb') as f:
        nets = pickle.load(f) 
        pop = Population(POP_SIZE, GENERATIONS, LIFESPAN, MUTATION_CHANCE, MUTATION_RATE, network_type=Genetic)
        pop.population = nets       


# create the game object
g = Gui(pop)
g.new()
g.run()
