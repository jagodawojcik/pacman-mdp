from pacman import Directions
from game import Agent
from mapAgents import Grid
import api
import random
import game
import util

#Rewards
FOOD = 50
CAPS = 25
GHOST = -1000
EMPTY = -5


class MDPAgent(Agent):
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    def makeMap(self, state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        map = Grid(width, height)
        return map

    def get_states(self, state):

        #return all possible states as (x,y) coordinates
        # this is states that are not walls
        # checked on small grid and runs correctly
        
        height = self.getLayoutHeight( api.corners(state))
        width = self.getLayoutWidth(api.corners(state))

        walls = api.walls(state)
        states = []
        for i in range(width):
            for j in range(height):
                if (i,j) not in walls:
                    states.append((i,j))
        
        return states

#     #""" Return all legal for the state """
    #tested and works as intended
    def get_actions(self, states, current_state):
        legal_actions = []

        (x, y) = current_state
        if ((x+1),y) in states:
            legal_actions.append(Directions.EAST)
        if ((x-1),y) in states:
            legal_actions.append(Directions.WEST)
        if (x, (y-1)) in states:
            legal_actions.append(Directions.SOUTH)
        if (x, (y+1)) in states:
            legal_actions.append(Directions.NORTH)

        return legal_actions

#     """ Return the discount factor for this MDP """
    def get_discount_factor(self):
        discount_factor = 0.9
        return discount_factor

#    Return the initial state of this MDP
    def get_initial_state(state):
        return api.whereAmI(state)

#Return all non-zero probability transitions for this action
# from this state, as a list of (next_state, probability) pairs
# tested and works
    def get_transitions(self, state, current_state, action):
        transitions = []

        # Probabilities
        straight = api.directionProb
        noise = 0.1

        #(x, y) = api.whereAmI(state) #initial state
        (x, y) = current_state
        
        if action == Directions.NORTH:
            transitions += self.valid_add(state,(x,y), (x, y + 1), straight) 
            transitions += self.valid_add(state,(x,y), (x - 1, y), noise) 
            transitions += self.valid_add(state,(x,y), (x + 1, y), noise)
            transitions += self.valid_add(state,(x,y), (x, y-1), 0.0)  

        elif action == Directions.SOUTH:
            transitions += self.valid_add(state,(x,y), (x, y - 1), straight)
            transitions += self.valid_add(state,(x,y), (x - 1, y), noise)
            transitions += self.valid_add(state,(x,y), (x + 1, y), noise)
            transitions += self.valid_add(state,(x,y), (x, y+1), 0.0)  

        elif action == Directions.EAST:
            transitions += self.valid_add(state,(x,y), (x + 1, y), straight)
            transitions += self.valid_add(state,(x,y), (x, y - 1), noise)
            transitions += self.valid_add(state,(x,y), (x, y + 1), noise)
            transitions += self.valid_add(state,(x,y), (x-1, y), 0.0)

        elif action == Directions.WEST:
            transitions += self.valid_add(state,(x,y), (x - 1, y), straight)
            transitions += self.valid_add(state,(x,y), (x, y - 1), noise)
            transitions += self.valid_add(state,(x,y), (x, y + 1), noise)
            transitions += self.valid_add(state,(x,y), (x+1, y), 0.0)

        return transitions
    
    #when wall in place there will probability of staying in the same state
    #tested and works
    def valid_add(self, state, current_state, new_state, probability):

        if new_state not in self.get_states(state):
            return [((current_state), probability)]

        return [(new_state, probability)]
     
    # creates a dictionary of state: reward - note needs to be updated at each step
    # needs to be tested
    def map_rewards(self, state, states):
         
        mapRewards = {}
        food = api.food(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)
        walls = api.walls(state)

        for s in states:
            if s in food:
                mapRewards[s] = FOOD
            elif s in capsules:
                mapRewards[s] = CAPS
            elif s in ghosts:
                mapRewards[s] = GHOST
            else:
                mapRewards[s] = EMPTY

        return mapRewards
    
    def get_reward(self, new_state, rewards_map):

        return rewards_map[new_state]

    def extract_move(self, state, current_state, opt_policy):
        legal = api.legalActions(state)
        action = opt_policy[current_state]
        if action not in legal:
            print 'Something is wrong this action is not legal for this state'
    
        return action

    def value_iteration(self, state, max_iterations=100, theta=0.001):
        # initialize the values:
        Values = {}
        Policy = {}
        
        states = self.get_states(state)
        rewards = self.map_rewards(state, states)
        # Values is the length of how many states we've got
        for n in states:
            Values[n] = -100000.0
            Policy[n] = None

        for i in range(max_iterations):
            delta = 0.0
            #initialize values for each state assign zero
            new_Values = {}
            for m in states:
                new_Values[m] = 0.0
            
            for s in states:
                max_val = 0.0 #initialise max value to zero
                #for each state, compute value for each legal action
                for action in self.get_actions(states, s):
                    # Calculate the state value when certain action is taken
                    new_value = 0.0
                    for (new_state, probability) in self.get_transitions(state, s, action):
                        reward = self.get_reward(new_state, rewards) #direct reward for that resulting next state
                        #U1[s] = prob * (reward(s) + gamma* val_newstate)
                        new_value += probability * (reward + (self.get_discount_factor() * Values[new_state])) #value for next state
                       
                    # Store the value for best action so far
                    max_val = max(max_val, new_value)
                    #update best policy
                    if Values[s] < new_value:
                        Policy[s] = action #store action with highest value
                
                #update value with highest value
                new_Values[s] = max_val
                #update max difference
                delta = max(delta, abs(Values[s] - new_Values[s]))
            #update (extr. vals function)
            Values = new_Values

            # Terminate if the value function has converged
            if delta < theta:
                return i, Policy

        #write code to perform action based on the optimal policy
        

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        #map rewards
        # get rewards to be tested

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        i, policy = self.value_iteration(state)
        # print 'Pac at state:'
        now = api.whereAmI(state)
        legal = api.legalActions(state)
        # print 'legal actions are: '
        # print legal
        # print 'Policy at current state:'
        # print policy[api.whereAmI(state)]
        # move = self.extract_move(state, api.whereAmI(state), policy )
        # legal = api.legalActions(state)
        # Random choice between the legal options.
        return api.makeMove(policy[now], legal)
