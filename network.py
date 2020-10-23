import numpy as np
from game import *
from settings import *
import random
import math

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

class Genetic:

    ACTIONS = [
        Game.TURN_RIGHT,
        Game.TURN_LEFT,
        Game.ACCELERATE,
        Game.BRAKE,
        Game.IDLE
    ]

    def __init__(self):

        # creates a random network
        self.network = self.generate_rnetwork(2+Car.VISION_LINES, 6, len(Genetic.ACTIONS))
    
    def generate_rnetwork(self, input_size, hidden_size, output_size):

        # hidden_size is the number of perceptrons per layer
        # Each perceptron is a vector containing '#input_size' values

        # The +1 is for a bias weight
        hidden_layer1 = np.array([[random.uniform(-1,1) for _ in range(input_size + 1)] for _ in range(hidden_size)])
        hidden_layer2 = np.array([[random.uniform(-1,1) for _ in range(hidden_size + 1)] for _ in range(hidden_size)])
        output_layer = np.array([[random.uniform(-1,1) for _ in range(hidden_size + 1)] for _ in range(output_size)])

        return [hidden_layer1, hidden_layer2, output_layer]

    def get_move(self, car):
        
        input_vector = self.get_state(car)
        hidden_layer1, hidden_layer2, output_layer = self.network

        # Forwards propagation
        # Tanh is the activation function
        # A bias is a weight that is not dependent on the input

        # Use dot product to get the output of perceptrons from the input to the hiddenlayer1
        hidden_result1 = np.array([
            math.tanh(np.dot(input_vector, hidden_layer1[i])) \
                for i in range(hidden_layer1.shape[0])] + [1]) # [1] is added as a bias

        # Use dot product to get the output of perceptrons from hiddenresult 1 to the hiddenlayer2
        hidden_result2 = np.array([
            math.tanh(np.dot(hidden_result1, hidden_layer2[i])) \
                for i in range(hidden_layer2.shape[0])] + [1]) # [1] is added as a bias
        
        # Use dot product to get the output of perceptrons from hiddenresult 3 to the output layer
        output_result = np.array([
            math.tanh(np.dot(hidden_result2, output_layer[i])) \
                for i in range(output_layer.shape[0])])

        max_index = np.argmax(output_result)
        return Genetic.ACTIONS[max_index]

    def get_state(self, car):
        """
        direction
        speed
        l1
        l2
        l3
        l4
        l5
        """

        input_vector = [-1 for i in range(7)]
        input_vector[0] = (car.direction % (2*pi)) / (2*pi)
        input_vector[1] = car.speed / Car.MAX_SPEED

        index = 2
        for i, p in enumerate(car.calculate_vision()):
            p1, p2 = p
            x1, y1 = p1
            if car.vision_intersections[i] == []: 
                x2, y2 = p2
            else:
                x2, y2 = car.vision_intersections[i][0]

            input_vector[index] = hypot(x1-x2, y1-y2)/Car.VISION_DISTANCE
            index += 1

        input_vector = list(np.array(input_vector)) + [1]

        return np.array(input_vector)

class Population:

    def __init__(self, pop_size, generations, lifespan, mutation_chance=0.1, mutation_rate=0.1, network_type=Genetic):

        self.pop_size = pop_size
        self.population = [network_type() for i in range(pop_size)]
        self.generations = generations
        self.current_generation = 1
        self.lifespan = lifespan * 60 # in seconds

        self.mutation_chance = mutation_chance
        self.mutation_rate = mutation_rate

        self.network_type = network_type

        self.best_by_generation = []
    
    def crossover(self, pool, total_children):
        children = []

        for i in range(total_children):
            parentA = random.choice(pool)
            parentB = random.choice(pool)

            mid = random.randint(0, len(parentA.network[0]))
            hidden_layer1 = np.array( list(parentA.network[0][:mid]) + list(parentB.network[0][mid:]) )

            mid = random.randint(0, len(parentA.network[1]))
            hidden_layer2 = np.array( list(parentA.network[1][:mid]) + list(parentB.network[1][mid:]) )

            
            child = self.network_type()

            child.network[0] = hidden_layer1
            child.network[1] = hidden_layer2

            children.append(child)

        return children
    
    def mutate(self, pool):

        chance = self.mutation_chance
        rate = self.mutation_rate

        # Mutation on all layers except last
        for entity in pool:
            for layer in entity.network[:1]:

                for i in range(len(layer)):
                    if random.random() < chance:
                        layer[i] += np.random.uniform(-1,1) * rate

        return pool
    
    def evaluate(self, cars):
        for car in cars:
            fitness = 0

            if car.time_alive < 20:
                fitness -= 99999

            fitness -= car.time_alive//10
            for b in car.checkpoints:
                if b:
                    fitness += 30
            if car.checkpoints[-1]:
                fitness += 300
            car.fitness = fitness

    def train_network(self, networks):

        cars = [Car((0,0), 20) for i in range(len(self.population))]
        g = Game(cars, "map_data.json")
        
        while g.timer < self.lifespan and any([x.alive for x in g.cars]):
            for i, car in enumerate(g.cars):
                move = self.population[i].get_move(car)
                g.controller(i, move)
            g.update()

        self.evaluate(g.cars)
        
        zipped = list(zip(networks, g.cars))
        return sorted(zipped, key=lambda x: x[1].fitness)[::-1]
    
    def train_generation(self):

        nets = self.train_network(self.population)
        top_score = nets[0][1].fitness
        print("Best Score: ", top_score)
        self.population = [y[0] for y in nets]

        # Take top 25%
        top_25 = self.population[:len(self.population)//4]
        top_25_children = self.crossover(top_25, len(self.population)//2)
        randoms = [self.network_type() for i in  range(self.pop_size-len(top_25)-len(top_25_children))]


        # Now mutate all of these 
        a = self.mutate(top_25)
        b = self.mutate(top_25_children)
        c = self.mutate(randoms)
        self.population = a+b+c

        # Elitism: Also include the highest performing network, unmodified
        self.population.insert(0,top_25[0])
        self.population = self.population[:-1]

        # Done with 1 generation
        # Return score of the best performing network
        return top_score
    
    def train(self):
        for i in range(self.generations):
            print("Gen:",self.current_generation)
            top_score = self.train_generation()
            self.best_by_generation.append((self.population[0], top_score))
            self.current_generation += 1