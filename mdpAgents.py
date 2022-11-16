from pacman import Directions
from game import Agent
import mapAgents
import api
import random
import game
import util

#Rewards
R_FOOD = 10
R_WALLS = None
R_CAP = 5
R_GHOST = -1000
R_G_NEIGH = -500
R_PAC = -15
R_EMPTY = 0
T_VALUE = 500

#Interface
class MDP:
#     #""" Return all states of this MDP """
#     def get_states(self):
        #return all possible states as (x,y) coordinates

#     #""" Return all actions with non-zero probability from this state """
    def get_actions(self, state):
        #all legal actions for the current state
        return state.getLegalPacmanActions()

#     """ Return the discount factor for this MDP """
    def get_discount_factor(self):
        discount_factor = 0.9
        return discount_factor

#    Return the initial state of this MDP
    def get_initial_state(state):
        return api.whereAmI(state)

#Return all non-zero probability transitions for this action
# from this state, as a list of (next_state, probability) pairs
    def get_transitions(self, state, action):
        transitions = []

        # Probabilities
        straight = api.directionProb
        noise = 0.5*(1 - api.directionProb)

        (x, y) = api.whereAmI(state) #initial state

        if action == Directions.NORTH:
            transitions += self.valid_add(state, (x, y + 1), straight) #goes up as intented
            transitions += self.valid_add(state, (x - 1, y), noise) #goes left
            transitions += self.valid_add(state, (x + 1, y), noise)
            transitions += self.valid_add(state, (x, y-1), 0.0)  

        elif action == Directions.SOUTH:
            transitions += self.valid_add(state, (x, y - 1), straight)
            transitions += self.valid_add(state, (x - 1, y), noise)
            transitions += self.valid_add(state, (x + 1, y), noise)

        elif action == Directions.RIGHT:
            transitions += self.valid_add(state, (x + 1, y), straight)
            transitions += self.valid_add(state, (x, y - 1), noise)
            transitions += self.valid_add(state, (x, y + 1), noise)

        elif action == Directions.LEFT:
            transitions += self.valid_add(state, (x - 1, y), straight)
            transitions += self.valid_add(state, (x, y - 1), noise)
            transitions += self.valid_add(state, (x, y + 1), noise)

        return transitions
    
    #when wall in place there will be some probability of staying in the same state
    def valid_add(self, state, new_state, probability):

        if new_state not in MDP.get_states(self):
            return [(api.whereAmI(state), probability)]

        return [(new_state, probability)]
     

#""" Return the reward for transitioning from state to nextState via action
# return numeric reward for this state given some action
    def get_reward(self, state, action, new_state):
        reward = 0.0
        #here modify to assign to reward whatever value appropriate
        
        if state in self.get_goal_states().keys():
            reward = self.get_goal_states().get(state) 
        else:
            reward = self.action_cost #if state not in goal states assign some reward
        return reward



# initialize the values:
# Values is the length of how many states we've got
#like an additional external array V = [0, 0, 0 ... 0s]
#pi = [None, none, none , .... nones] size of states, same as values stores best policies
class ValueIteration:

    def value_iteration(self, max_iterations=100, theta=0.001):

        for i in range(max_iterations):
            delta = 0.0
            new_values = dict([(s, 0) for s in mdp.states]) #initialize values for each state assign zero
            for state in self.mdp.get_states():
                max_val = 0 #initialise max value to zero
                #for each state, compute value for each legal action
                for action in self.mdp.get_actions(state):
                    # Calculate the state value when certain action is taken
                    for (new_state, probability) in self.mdp.get_transitions(state, action):
                        reward = self.mdp.get_reward(state, action, new_state) #direct reward for that resulting next state
                        #U1[s] = prob * (reward(s) + gamma* val_newstate)
                        new_value += probability * (reward + (_discount_factor()
                                * self.Values(new_state) #value for next state
                            )
                        )

                    # Store the value for best action so far
                    max_val = max(max_val, new_value)

                    #update best policy
                    if Values(state) < new_value:
                        pi[state] = get_actions[action] #store action with highest value
                #update value with highest value
                new_values[state] = max_val
                #update max difference
                delta = max(delta, abs(values[s] - new_value[s]))
            #update (extr. vals function)
            values = new_values

            # Terminate if the value function has converged
            if delta < theta:
                return i


#write code to perform action based on the optimal policy





class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"


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
