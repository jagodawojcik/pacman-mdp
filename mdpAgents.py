from pacman import Directions
from game import Agent
from mapAgents import Grid
import api
import random
import game
import util

#Rewards
FOOD = 100
CAPS = 400
GHOST = -15000
EMPTY = -5
GAMMA = 0.9

class MDPAgent(Agent):
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        self.Values = {}
        self.Policy = {}

        
    def get_layout_height(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

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

    # Return next states as result of taking action from the current state
    # Next state resturned as a list of tuples [west, north, south, east]
    def get_next_state(self, all_states, current_state):
        west = (current_state[0]-1, current_state[1])
        north = (current_state[0], current_state[1]+1)
        south = (current_state[0], current_state[1]-1)
        east = (current_state[0]+1, current_state[1])

        next_state = [west, north, south, east]
        
        #if state is a wall, assign current state to next state
        for a in next_state:
            if a not in all_states:
                next_state[next_state.index(a)] = current_state

        return next_state

    #Return all non-zero probability transitions for this action
    # from this state, as a list of (next_state, probability) pairs
    # tested and works
    #def get_transitions(self, state, current_state, action):

    
    # creates a dictionary of direct state rewards
    def map_rewards(self, state, states):
         
        mapRewards = {}
        food = api.food(state)
        capsules = api.capsules(state)
        #"state" is 1 if the relevant ghost is scared/edible, and 0
        # otherwise.

        ghost_loc = []
        for g, status in api.ghostStates(state):
            if status == 0:
                ghost_loc.append(g)
                ghost_loc.append((g[0]+1, g[1])) #one sq east
                ghost_loc.append((g[0]-1, g[1])) #one sq west
                ghost_loc.append((g[0], g[1]+1)) #one sq north
                ghost_loc.append((g[0], g[1]-1)) #one sq south
                ghost_loc.append((g[0]+1, g[1]+1)) #one sq east
                ghost_loc.append((g[0]-1, g[1]-1)) #one sq west
                ghost_loc.append((g[0]+1, g[1]-1)) #one sq north
                ghost_loc.append((g[0]-1, g[1]+1)) #one sq south
                ghost_loc.append((g[0]+2, g[1])) #one sq east
                ghost_loc.append((g[0]-2, g[1])) #one sq west
                ghost_loc.append((g[0], g[1]+2)) #one sq north
                ghost_loc.append((g[0], g[1]-2)) #one sq south
                ghost_loc.append((g[0]+2, g[1]+2)) #one sq east
                ghost_loc.append((g[0]-2, g[1]-2)) #one sq west
                ghost_loc.append((g[0]+2, g[1]-2)) #one sq north
                ghost_loc.append((g[0]-2, g[1]+2)) #one sq south
            elif status == 1:
                capsules.append(g)


        for s in states:
            if s in ghost_loc:
                mapRewards[s] = GHOST
            elif s in food:
                mapRewards[s] = FOOD
            elif s in capsules:
                mapRewards[s] = CAPS
            else:
                mapRewards[s] = EMPTY

        return mapRewards


    def value_iteration(self, state, theta=0.001):
        
        
        states = self.get_states(state)
        rewards = self.map_rewards(state, states)
        new_Values = {}
        # Values is the length of how many states we've got
        for n in states:
            self.Values[n] = 0.0
            self.Policy[n] = None
            new_Values[n] = 0.0 
    
        convered_states = []
        while len(convered_states) < len(states):
            
            #initialize values for each state assign zero
            
            for s in states:
                max_val = 0.0 #initialise max value to zero
                Utility = []

                next_state = self.get_next_state(states, s)

                #Calculate expected unitility value for each transition

                r_west = new_Values[next_state[0]]
                r_north = new_Values[next_state[1]]
                r_south = new_Values[next_state[2]]
                r_east = new_Values[next_state[3]]
                Utility.append(0.8*r_west+0.1*r_north+0.1*r_south)
                Utility.append(0.8*r_north+0.1*r_west+0.1*r_east)
                Utility.append(0.8*r_south+0.1*r_east+0.1*r_west)
                Utility.append(0.8*r_east+0.1*r_north+0.1*r_south)
                

                max_val = max(Utility)
                max_index = str(Utility.index(max_val))                

                # if max_index == '0':
                #     self.Policy[s] = Directions.WEST
                # elif max_index == '1':
                #     self.Policy[s] = Directions.NORTH
                # elif max_index == '2':
                #     self.Policy[s] = Directions.SOUTH
                # elif max_index == '3':
                #     self.Policy[s] = Directions.EAST

                
                #bellman update
                new_Values[s] = rewards[s] + (GAMMA * max_val)      
                
                
                #update max difference
                delta = abs(self.Values[s] - new_Values[s])
               
                #Update values for states
                self.Values[s] = new_Values[s]
                
 
            # Record the state as converged, when delta<theta
            # Allows to terminate when states converged
                if delta < theta:
                    if s not in convered_states:
                        convered_states.append(s)


    # (skeleton) Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        #map rewards
        # get rewards to be tested

    # (skeleton) This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        self.Values = {}
        self.Policy = {}

    # Run at each game clock
    def getAction(self, state):
        
        #print 'Game iter'
        
        current_state = api.whereAmI(state)
        legal = api.legalActions(state)
        self.value_iteration(state)

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        actionUtil = []
        for action in legal:
            if action == "West":
                newState = ((current_state[0]-1),(current_state[1]))
            elif action == "East":
                newState = ((current_state[0]+1),(current_state[1]))
            elif action == "North":
                newState = ((current_state[0]),(current_state[1]+1))
            else: 
                action == "South"
                newState = ((current_state[0]),(current_state[1]-1))
            actionUtil.append(self.Values[newState])
        
        """ 
        Identify the action with max util from the value iteration. 
        As numpy is not allowed to be used for project purpose, below method is used to 
        identify the index of action with maximum utility (argmax).
        """
        maxActionUtil = max(actionUtil)
        policy = legal[actionUtil.index(maxActionUtil)]


        # print 'State I am in:'
        # print current_state
        # print 'Action I take'
        # print self.Policy[current_state]

    


        return api.makeMove(policy, legal)


