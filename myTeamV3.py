# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent2'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    return random.choice(bestActions)

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()

    # features['foodHolding'] = 1
    # features['distanceFromPacman'] = 1
    # features['distanceFromSafety'] = 1
    myPos = successor.getAgentState(self.index).getPosition()

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 1/minDistance

    nextState = successor.getAgentState(self.index)
    pos2 = successor.getAgentPosition(self.index)
    dist = self.getMazeDistance(self.start, pos2)

    currentState = gameState.getAgentState(self.index)

    features['foodOnBoard'] = nextState.numCarrying - currentState.numCarrying#len(foodList)#self.getScore(successor)
    features['distanceFromBaseIfPacmanAndCarrying'] = dist if (nextState.numCarrying > 0) else 0
    features['scoreIncrease'] = nextState.numReturned - currentState.numReturned

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['nearestInvaderIfSafe'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in invaders]) if len(invaders) > 0 else 0

    defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    # features['nearestGhostIfPacman'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in defenders]) if len(defenders) > 0 and nextState.isPacman and currentState.numCarrying > 0 else 0
    
    # if (features['nearestInvaderIfSafe'] <= 0) :
    #   features['nearestGhostIfPacman'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in defenders]) if len(defenders) > 0 and currentState.isPacman and nextState.numCarrying > 0 else 0

    x, y = gameState.getAgentState(self.index).getPosition()

    vx, vy = Actions.directionToVector(action)

    newx = int(x + vx)
    newy = int(y + vy)
    
    walls = gameState.getWalls()
    
    for ghots in defenders:
      ghostpos = ghots.getPosition()
      neighbors = Actions.getLegalNeighbors(ghostpos, walls)
      if (newx, newy) in neighbors:
        features["closeInvader"] = 1

    
    red_postions = [ gameState.getAgentPosition(x) for x in gameState.getRedTeamIndices()]
    split_dis = self.getMazeDistance(red_postions[0], red_postions[1])
    if features['nearestInvaderIfSafe'] == 0:
      features["split"] = split_dis
    
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return { 'split': -10, 'closeInvader': -10, 'distanceToFood': 1, 'foodOnBoard': 100, 'distanceFromBaseIfPacmanAndCarrying': -1, 'scoreIncrease': 1000, 'nearestInvaderIfSafe': -10}

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)

    return successor

class DummyAgent2(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    return random.choice(bestActions)

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()

    # features['foodHolding'] = 1
    # features['distanceFromPacman'] = 1
    # features['distanceFromSafety'] = 1

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 1/minDistance

    nextState = successor.getAgentState(self.index)
    pos2 = successor.getAgentPosition(self.index)
    dist = self.getMazeDistance(self.start, pos2)

    currentState = gameState.getAgentState(self.index)

    features['foodOnBoard'] = nextState.numCarrying - currentState.numCarrying#len(foodList)#self.getScore(successor)
    features['distanceFromBaseIfPacmanAndCarrying'] = dist if (nextState.numCarrying > 0) else 0
    features['scoreIncrease'] = nextState.numReturned - currentState.numReturned

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['nearestInvaderIfSafe'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in invaders]) if len(invaders) > 0 else 0

    defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    # features['nearestGhostIfPacman'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in defenders]) if len(defenders) > 0 and nextState.isPacman and currentState.numCarrying > 0 else 0
    
    # if (features['nearestInvaderIfSafe'] <= 0) :
    #   features['nearestGhostIfPacman'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in defenders]) if len(defenders) > 0 and currentState.isPacman and nextState.numCarrying > 0 else 0

    x, y = gameState.getAgentState(self.index).getPosition()

    vx, vy = Actions.directionToVector(action)

    newx = int(x + vx)
    newy = int(y + vy)
    
    walls = gameState.getWalls()

    for ghots in defenders:
      ghostpos = ghots.getPosition()
      neighbors = Actions.getLegalNeighbors(ghostpos, walls)
      if (newx, newy) in neighbors:
        features["closeInvader"] = 1

  
    
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return { 'closeInvader': -10, 'distanceToFood': 1, 'foodOnBoard': 100, 'distanceFromBaseIfPacmanAndCarrying': -1, 'scoreIncrease': 1000, 'nearestInvaderIfSafe': -10}

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)

    return successor
