# Racing Game & Deep Genetic Network
---
## Game Content
- This project is a simple racing game that implements a neural network to have agents automatically race around the track. This project itself is split up into 3 parts: the map builder, gui/game, and deep neural network.
- ### Key Design Features
    - **Object Orient Programming (OOP)** for all abstractable features. The Deep Neural Network, Gui and Game are all built as classes for abstraction and ease of implementation.
        - Deep Neural Network Classes: `Genetic`, `Population`
        - Game & Gui: `Gui`, `Game`, `Car`
    - **Car Mechanics**: The car objects each have their own physics mechanics that allow the "front wheels" to rotate and move similar to a real car. The cars also each have "vision lines" that protrude from its center. These "vision lines" interact with the edges of the track and allow the car to know how close it is from the edge of the track.
    - **Map Builder**: The map builder was tricky to design at first. It allows you to place down points to form 2 separate polygons - one inside of the other. Eventually, the area in between both polygons is used as the track. The map builder also allows the user to place down checkpoints - these are extremely important for the cars' fitness functions. The checkpoints are created by placing a point where the user clicks, and then uses simple form of 2d ray tracing (similar to a car's vision) to determine a line between both polygons.
    - **File Reading/Writer**: In order to save data, such as created maps and high-scoring neural networks, I used the libraries `pickle` and `json`. The `pickle` library is used to save objects; in this project I used this to save the numpy objects of the neural networks. The `json` libray is used to save dictionaries; in this project I used this to save map (track) states.
    - The game itself is not designed to run with a GUI active 100% of the time. I created the game so that it could run independently as its own environment and updates as called. However, by design, it is also easy to implement a GUI with the `Game` class (as implemented in the `GUI` class).

## Neural Network
- In order to create a playable agent for this game, I decided to develop a neural network. This neural network contains perceptrons, layers, and forwards propagation.
- ### Network Structure
    - 7 (+ 1 bias) input values
    - 2 Hidden layers, each with (default) 6 perceptrons
    - 1 output layer with 5 values (each representing an action)
- ### Forward Propagation
    - Used to make the prediction for the next action
    - `tanh()` used as the activation function

## Deep Genetic Algorithm
- The Genetic Algorithm is implemented in the `Population` class which keeps track of networks (through `Genetic` objects) and their respective car objects. The `Population` class is responsible for training the neural networks via gentic algorithm - utilizing evaluation, mutation, and crossover.
- ### Training Process
    - **Evaluation**: The score of each individual neural network and car pair, is calculated in the `Population.evaluate()` method. This is the sum of a weighted value for the car's time alive and weighted values for how many checkpoinst the car reached.
    - **Mutation**: Makes random changes to a list of neural networks through the `Population.mutate(pool)` method. The method goes through each weight value in a neural network's layer and according to a mutation rate and mutation chance value, the weight value is adjusted.
    - **Crossover**: Takes a list of networks and randomly combine two networks together *n* times through the `Population.crossover(pool, total_children)`.


## Learning Resources
- The concept and code for this project was developed 100% by myself.
These are the links to resources that I used to learn about physics, neural networks and genetic algorithms, 
as well efficiency with the numpy library for creating neural networks
- [Coding Challenge #29: Smart Rockets in p5.js](https://www.youtube.com/watch?v=bGz7mv2vD6g)
- [Snake AI | Genetic Algorithm | Python](https://www.youtube.com/watch?v=SGxVaptD9Ug&list=LL&index=1&t=746s)
- [The Number of Hidden Layers](https://www.heatonresearch.com/2017/06/01/hidden-layers.html#:~:text=The%20number%20of%20hidden%20neurons,size%20of%20the%20input%20layer.)
- [Create a Simple Neural Network in Python from Scratch](https://www.youtube.com/watch?v=kft1AJ9WVDk&t=653s)
- [Simple 2D car steering physics in games](http://engineeringdotnet.blogspot.com/2010/04/simple-2d-car-physics-in-games.html)