import math
import pickle
import random

from gui import Gui
from network import *
from settings import *

if not LOAD_DATA:
    pop = Population(POP_SIZE, GENERATIONS, LIFESPAN, MUTATION_CHANCE, MUTATION_RATE, network_type=Genetic)
    '''
    pop.train()

    nets = pop.population[:5]
    name = str(input("Network name save: "))
    name = name.strip()+'.pickle'
    if name == ".pickle":
        name = "Networks/net_data.pickle"

    if "-" not in name:
        with open("Networks/"+name, 'wb') as f:
            pickle.dump(nets, f, protocol=pickle.HIGHEST_PROTOCOL)
            print("> Networks saved!")
    '''
else:
    with open("Networks/"+LOAD_FILE, 'rb') as f:
        nets = pickle.load(f)        


# create the game object
g = Gui(pop)
g.new()
g.run()
