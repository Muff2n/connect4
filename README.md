# Intro
Using reinforcement learning to train an agent to play Connect4 as well as it can. I use a recursive neural network as a value approximator which also outputs a policy of the likely best move in a position. This is combined with a Monte Carlo Marcov Chain tree search to plan the best move.

This repo is a self-project to learn about reinforcement learning. I hope that other people might also be able to learn from my work. I welcome constructive criticism on absolutely anything from how I could have improved the Machine Learning, python programming, project layout, etc.

# Installation
$ pip install XXX

Alternatively checkout the repo and include the path to project base in your PYTHONPATH. If you checkout the repo you will also have all the misc scripts that I have used, in XXX/scripts. Be warned that these were Hacked (with a capital H) together. If you use this approach you will need to call the XXX/main.py script directly when running.

# Usage
$ XXX -m [mode] [mode options]

There are two modes that can be used:
To play a game vs the AI use
$ XXX -m game [-n network_file -s simulations]
The default simulations is 800, this is the number of positions the AI will analyise before making a move.
If a network file is not provided, a pre-trained one provided in 'XXX/data/example_net.pth' is used. If you change any of the network parapers specified in 'XXX/utils.py' you will need to train your own.

To run a self-play training loop use:
$ XXX -m training [-c config.py]

Create a config for youself following the example of XXX/data/example_config.py. You will need to specify a working directory, everything else will use the default values found in XXX/neural/config.py

Playing a game will run the network on the CPU - typically fast enough. The training loop will make use of a Cuda enabled GPU, and can use multiple processes.

# Acknowledgements
This project is a re-implementation of Deepmind's paper [A general reinforcement learning algorithm that
masters chess, shogi and Go through self-play](https://deepmind.com/documents/260/alphazero_preprint.pdf).

Another resource that has covered this that I found useful was [an Oracle blog on medium](https://medium.com/oracledevs/lessons-from-implementing-alphazero-7e36e9054191). This is what I used as a rough guide to follow in selecting Connect4 as a reasonable game, and a few of the changes.

Other useful resources are:
* [PascalPons' Github](https://github.com/PascalPons/connect4/tree/a0fcfe9e4eacd6194da8ae138a8e554f381be9e0) for having an efficient computational solution for Connect4. I really wish I had seen this before I wrote my own (inferior) implementation.
* [John's Connect Four Playground](https://tromp.github.io/c4/c4.html).
* [The dataset I used for evaluation](http://archive.ics.uci.edu/ml/datasets/connect-4).
* [A lecture series by David Silver on Reinforcement Learning](http://www0.cs.ucl.ac.uk/staff/d.silver/web/Teaching.html).

Finally I should acknowledge the less glamarous but probably most imporant role that StackOverflow has played.

# Conventions
A position is scored 1 if it is a win for the first player to move in a game of Connect4 ('player_o') and value 0 if the second player will win ('player_x'). Game tree nodes store the absolute position evaluation, but when querying the node for the value, it will return the relative value to the player querying (i.e. a value of 1 means the player to move will win).

# Notes
I differ from Deepmind's paper in the following ways:
* My training is offline, it runs after a cycle of training games. All the games from the previous max (20, gen/2) generations are used.
* I 'cheat' and augment my training data with positions reflected in the vertical axis, using the symmetrical nature of connect4.
* I don't use parallel MCTS, relying instead on parallelising the gameplay.
* I select moves based upon value, rather than visit count.
** During the exploration moves at the start, I select proportional to the squared value of possible moves, rather than softmax of visit counts.
* Lots of parameters are different from their suggested values (it is a different game afterall).

User vs AI gameplay has not been optimised in any way; the point of this project is the training process. This functionality has been included for fun.

# Training
The evaluation datasets are found in 'XXX/data'. The 8ply file has all the positions from the YYY. I use the RMSE of the position values outputted from my model compared to the theoretical values.

Because the network also outputs move probabilities, I generated a 7ply dataset where I solve using the 8ply dataset, and label the 'weak' correct moves. Weak because any move the leads to a theoretically winning position is counted as correct, even if it is not the fastest win available. The evaluation loop also tests on this and as well as the RMSE of the values, it finds the Cross Entropy Loss of the network policy.

Here is an example training run with the default parameters used:
![8ply](./example_training.pdf)
