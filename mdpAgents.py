# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import mapAgents
import api
import random
import game
import util


R_FOOD = 10
R_WALLS = None
R_CAP = 5
R_GHOST = -1000
R_G_NEIGH = -500
R_PAC = -15
R_EMPTY = 0
T_VALUE = 500



class MDPAgent(Agent):

    def getHeight(self, corners):
        #save the highest corners[][1] coord as a height
        self.height = -1
        for i in range(len(corners)):
            if corners[i][1] > self.height:
                self.height = corners[i][1]
        self.height = self.height+1
        return self.height

    def getWidth(self, corners):
        #save the highest corners[][0] coord as a height
        self.width = -1
        for i in range(len(corners)):
            if corners[i][0] > self.width:
                self.width = corners[i][0]
        self.width = self.width+1
        return self.width

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
      


    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        
        
    def initialStatesMap(self, state):
        width = self.getWidth(api.corners(state))
        height = self.getHeight(api.corners(state))

        #initialise with zeros where empty, alternative to np.zeros
        #results in a list of lists = 2D array
        statesMap = [[0 for x in range(width)] for y in range(height)]
        
        #retrive information on the environment
        food = api.food(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)
        walls = api.walls(state)

        #Append the 2D array with information on environment
        for i in food:
            statesMap[i[0]][i[1]]= R_FOOD
        for i in capsules:
            statesMap[i[0]][i[1]] = R_CAP
        for i in ghosts:
            statesMap[i[0]][i[1]] = R_GHOST
        for i in walls:
            statesMap[i[0]][i[1]] = R_WALLS
        
        
        return statesMap

    def updateMap(self, state, oldStatesMap):
        
        statesMap = oldStatesMap
        food = api.food(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)

        for i in food:
            statesMap[i[0]][i[1]]= R_FOOD
        for i in capsules:
            statesMap[i[0]][i[1]] = R_CAP
        for i in ghosts:
            statesMap[i[0]][i[1]] = R_GHOST

        return statesMap

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
       
       
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)


    def get_transitions(self, state, action):
        transitions = []

        if state == self.TERMINAL:
            if action == self.TERMINATE:
                return [(self.TERMINAL, 1.0)]
            else:
                return []

    def value_iteration(self, max_iterations=100, theta=0.001):

        for i in range(max_iterations):
            delta = 0.0
            new_values = # here initial values
            for state in self.mdp.get_states(): #here go my states
                qtable = QTable() # here save calculated values
                for action in self.mdp.get_actions(state):
                    # Calculate the value of Q(s,a)
                    new_value = 0.0
                    #"" get_transitions - Return all non-zero probability transitions for this action
        #from this state, as a list of (state, probability) pairs
                    for (new_state, probability) in self.mdp.get_transitions( #
                        state, action
                    ):
                        reward = self.mdp.get_reward(state, action, new_state) #Return the reward for transitioning from state to nextState via action
                        new_value += probability * (
                            reward
                            + (
                                self.mdp.get_discount_factor()
                                * self.values.get_value(new_state)
                            )
                        )

                    qtable.update(state, action, new_value)

                # V(s) = max_a Q(sa)
                (_, max_q) = qtable.get_max_q(state, self.mdp.get_actions(state))
                delta = max(delta, abs(self.values.get_value(state) - max_q))
                new_values.update(state, max_q)

            self.values.merge(new_values)

            # Terminate if the value function has converged
            if delta < theta:
                return i

