# mdpAgents.py
#
# Author: Jagoda Wojcik
# k21171248
# Value Iteration MDP Solver for pacman  
# AI Reasoning and Decision Making KCL '22
# (use pacman.py -q -n 25 -p MDPAgent -l mediumCLassic/smallGrid
# to run)


# Skeleton code: parsons/20-nov-2017
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

from pacman import Directions
from game import Agent
import api
import random
import game
import util


# Constants used in rewards assignment
FOOD = 1000
CAPSULE = 1000
GHOST = -20000
EMPTY = 100

# Discount factor used to discount future rewards
DISCOUNT_FACTOR = 0.9

class MDPAgent(Agent):
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        # Variable to store utility values for each state
        self.Values = {}
    
    # Read layout height
    # source - Practical 5 mapAgents.py AI Reasoning & Decision Making KCL
    def get_layout_height(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1
    
    # Read layout width
    #source - Practical 5 mapAgents.py AI Reasoning & Decision Making KCL
    def get_layout_width(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Return all traversable states as (x,y) coordinates list
    # Include only states that are not walls
    def get_states(self, state):        
        height = self.get_layout_height( api.corners(state))
        width = self.get_layout_width(api.corners(state))

        walls = api.walls(state)
        states = []
        for i in range(width):
            for j in range(height):
                if (i,j) not in walls:
                    states.append((i,j))
        
        return states

    # Return next state as result of taking action from the current state
    # Next state returned as a list of tuples:
    # [west (right), north (up), south (down), east (left)]
    def get_next_state(self, all_states, current_state):
        west = (current_state[0]-1, current_state[1])
        north = (current_state[0], current_state[1]+1)
        south = (current_state[0], current_state[1]-1)
        east = (current_state[0]+1, current_state[1])

        next_state = [west, north, south, east]
        
        # If state is a wall pacman bumps and stays in current
        #current state
        for a in next_state:
            if a not in all_states:
                next_state[next_state.index(a)] = current_state

        return next_state


    def get_ghost_danger_region(self, state):
        
        # It was found that for both layers +- 1 grid point from ghost
        #is enough to assign negative values to, so for both layouts:
        danger_radius = 1

        return danger_radius
    
    # Create a dictionary of direct state rewards
    def map_rewards(self, state, states):
        
        mapRewards = {}
        food = api.food(state)
        capsules = api.capsules(state)
       
        ghost_loc = []
        radius = self.get_ghost_danger_region(state)

        for g, status in api.ghostStates(state):
            if status == 0:
                ghost_loc.append(g)
                ghost_loc.append((g[0]+radius, g[1])) #one sq east
                ghost_loc.append((g[0]-radius, g[1])) #one sq west
                ghost_loc.append((g[0], g[1]+radius)) #one sq north
                ghost_loc.append((g[0], g[1]-radius)) #one sq south
            # It was found that for best win rate when ghost edible no specific
            #value will be assigned
            elif status == 1:
                pass

        
        for s in states:
            
            if s in ghost_loc:
                mapRewards[s] = GHOST  
            elif s in food:
                mapRewards[s] = FOOD 
            elif s in capsules:
                mapRewards[s] = CAPSULE 
            else:
                mapRewards[s] = EMPTY
        
        return mapRewards

    # Retrive best policy (action) for the current state and its legal action
    #based on utilities values self.Values calculated through value iteration
    def get_best_policy(self, state, current_state, legal_actions):
        
        actions_utilities_temp = []
        for action in legal_actions:
            if action == "West":
                next_state = ((current_state[0]-1),(current_state[1]))
            elif action == "East":
                next_state = ((current_state[0]+1),(current_state[1]))
            elif action == "North":
                next_state = ((current_state[0]),(current_state[1]+1))
            else: 
                action == "South"
                next_state = ((current_state[0]),(current_state[1]-1))
            actions_utilities_temp.append(self.Values[next_state])
        

        best_action_utility = max(actions_utilities_temp)
        best_policy = actions_utilities_temp.index(best_action_utility)

        return legal_actions[best_policy]

    #Heart of the coursework - Value Iteration MDP Solver
    def value_iteration(self, state, theta=0.01):
        
        states = self.get_states(state)
        rewards = self.map_rewards(state, states)
        
        new_Values = {}
        # Values is the length of how many states we've got
        for n in states:
            self.Values[n] = 0.0
            new_Values[n] = 0.0 

        #Initialize convergence list to keep track of converged states
        converged_states = []
        while len(converged_states) < len(states):
            
            for s in states:
                #initialise max expected utility value to zero
                max_exp_utility = 0.0

                exp_utilities_temp = []

                next_state = self.get_next_state(states, s)

                # Fetch utility value for surrounding states to our current state
                u_west = new_Values[next_state[0]]
                u_north = new_Values[next_state[1]]
                u_south = new_Values[next_state[2]]
                u_east = new_Values[next_state[3]]
                # Calculate expected utility value for each surrounding state
                #account for transistions P(s'|s,a)
                exp_utilities_temp.append(0.8*u_west+0.1*u_north+0.1*u_south)
                exp_utilities_temp.append(0.8*u_north+0.1*u_west+0.1*u_east)
                exp_utilities_temp.append(0.8*u_south+0.1*u_east+0.1*u_west)
                exp_utilities_temp.append(0.8*u_east+0.1*u_north+0.1*u_south)
                
                # Choose the value of highest utility for our bellman update
                max_exp_utility = max(exp_utilities_temp)              

                # Bellman update
                new_Values[s] = rewards[s] + (DISCOUNT_FACTOR * max_exp_utility)      
                
                # Update difference between calculated utility and utility from previous iteration
                delta = abs(self.Values[s] - new_Values[s])
               
                # Update values of max utility of states
                self.Values[s] = new_Values[s]
                
            # Record the state as converged, when delta<theta
            # Allows to terminate when all states converged
                if delta < theta:
                    if s not in converged_states:
                        converged_states.append(s)

    # (from skeleton) Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
       
    # (skeleton) This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        
        #clear utility values
        self.Values = {}
    

    # Run at each game clock
    def getAction(self, state):
        
        #get some information about pacman and its legal actions
        current_state = api.whereAmI(state)
        legal_actions = api.legalActions(state)

        #calculate max expected utility for each state through value iter
        self.Values = {}
        self.value_iteration(state)

        #Remove stop from legal actions
        if Directions.STOP in legal_actions:
            legal_actions.remove(Directions.STOP)
        
        #Get best policy - check what action leads to best utility
        #could've been saved in a form of dict on value iter stage, however
        #this was found to execute faster
        move = self.get_best_policy(state, current_state, legal_actions)

        return api.makeMove(move, legal_actions)