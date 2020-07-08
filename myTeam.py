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
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
import math
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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

# copied from baselineTeam.py
class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

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
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)



###############
# Ghost Agent #
###############
# copied from baselineTeam.py
class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  Ghost Agent that keeps our side PacMan free.
  Will try to eat opponent's PacMan by finding and going towards it.
  Will run away for the duration that it is scared/eatable.
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    # member variables
    self.numCapsules = len(self.getCapsulesYouAreDefending(gameState)) # saves how many capsules are on our side left
    self.scared = 0 # timer for how much longer to be scared for
    self.invaderDistance = [] # list of the most recent and exact coordinates of invaders
    self.middleOfBoard = tuple(map(lambda i,j: math.floor((i-j)/2), gameState.getInitialAgentPosition(1), gameState.getInitialAgentPosition(0)))
    self.target = 0 # used if there is an enemy on the map whose exact position we do not know, but has eaten food recently.

    
  def getFeatures(self, gameState, action):
    """
    Gets features of the gameState after the arg action has been made
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see (within 5 distance)
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    numEnemies = len([a for a in enemies if a.isPacman])
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    isStuck = self.isStuck(gameState,action)
    if invaders and numEnemies:
      # store the most recent distance of the invader(s)
      self.invaderDistance = invaders
    elif self.invaderDistance and numEnemies and not isStuck:
      # use the most recent distance of the invader(s)
      invaders = self.invaderDistance
    elif isStuck and numEnemies:
      eatenFood = self.guessPacManPosition(gameState,action)
      if eatenFood:
        self.target = eatenFood
        self.invaderDistance = []
    else:
      invaders = []
      self.invaderDistance = []
      self.target = 0


    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
    elif numEnemies and self.target:
      features['invaderDistance'] = self.getMazeDistance(myPos,self.target)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    # to prevent ghost from going back to the start position
    if self.red and myPos[0] == self.start[0]: features['beginning'] = 1
    elif not self.red and myPos[0] == self.start[0]: features['beginning'] = 1
    return features

  def evaluate(self, gameState, action):
      """
      Evaluate actions based on the game state and state of ghost.
      Depending on the state of the ghost, will evaluate the actions differently.
      """
      features = self.getFeatures(gameState, action)
      weights = self.getWeights(gameState, action)
      return features*weights

  def chooseAction(self,gameState):
    """
    Picks on an action that gives the highest evaluation.
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

    if (self.isScared(gameState)):
      #reduce timer for being scared
      self.scared -= 1
    
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    
    foodLeft = len(self.getFoodYouAreDefending(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction
    return random.choice(bestActions)
    
  def isStuck(self,gameState,action):
    """
    Checks to see if ghost gets stuck while trying to chase pacman
    """
    if len(self.observationHistory)>6:
      # if we do not move an average of 2 distance over 6 moves, then assume we are stuck
      oldpos3 = self.observationHistory[-3].getAgentPosition(self.index) # get the 3rd to last move
      oldpos6 = self.observationHistory[-6].getAgentPosition(self.index) # get the 6th to last move
      currPos = gameState.getAgentPosition(self.index)
      dist = self.getMazeDistance(currPos,oldpos3)
      dist += self.getMazeDistance(oldpos3,oldpos6)
      return dist/2 <= 2 # calculate the average distance and see if we moved more than 2
    return False
    
  def guessPacManPosition(self,gameState,action):
    """
    Ghost Agent will try to guess where PamMan is based on the food that are missing from the board by comparing board states
    """
    foodPositions = self.getFoodYouAreDefending(gameState).asList()
    passedGameState = self.getPreviousObservation()
    if passedGameState:
      OldFood = self.getFoodYouAreDefending(passedGameState).asList()
      # find food position that was eaten 
      foodEaten = [i for i in OldFood if i not in foodPositions]
      if foodEaten:
        return random.choice(foodEaten)
    return 0

  def getWeights(self, gameState, action):
    """
    Weights of each feature. In a normal ghost state, we will try to penalize the action that does not eat PacMan and increases distance to PacMan.
    We will also penalize the action that makes the ghost go back to its original starting position heavily.
    """
    if self.isScared(gameState):
      # When we are scared, we don't want to try to eat pacman right now, but don't want to be too far
      return {'numInvaders': 1000, 'onDefense': 100, 'invaderDistance': 0,'stop': -2,'reverse': -2, 'beginning': -400}
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10,'stop': -2,'reverse': -2, 'beginning': -400}

  def ourCapsuleEaten(self,gameState):
    """
    Helper function to see if a capsule on our side was eaten
    """
    # check if a capsule on our side was eaten
    boardCapsules = len(self.getCapsulesYouAreDefending(gameState))
    if (self.numCapsules > boardCapsules):
      print("enemy pacman ate capsule")
      self.numCapsules-=1
      return True
    return False

  def isScared(self,gameState):
    """
    Checks to see if our ghost is scared. Has a 40 move countdown to keep track of scared state
    """
    if self.scared:
      previousState = self.getPreviousObservation()
      # This is to check if ghost has been eaten, since there seems to be no function to see if an agent was eaten
      # Check if the Ghost agent teleported back to start by comparing it to its previous position
      if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), previousState.getAgentState(self.index).getPosition()) > 1:
        print("eaten")
        self.scared = 0
        return False
      else:
        return True
    if self.ourCapsuleEaten(gameState):
      # If Pacman eats a power capsule, agents on the opposing team become "scared" for the next 40 moves
      # or until they are eaten and respawn
      self.scared = 40
      return True
    return False



################
# Pacman Agent #
################
class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.scaredGhostTimers = [0,0]


  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def isCapsuleEaten(self, gameState):
    """
    Checks if a capsule was eaten by our team pacman. If it was eaten, then this function also
    sets the enemy ghosts scared timer to 40
    """
    capsule = self.getCapsules(gameState)
    previousState =self.getPreviousObservation() # get the previous observation
    if previousState:
      previousCapsules = self.getCapsules(previousState)
      if len(capsule) != len(previousCapsules):
        self.scaredGhostTimers = [40,40] # both ghost's scared timers to 40 moves
        print("our pacman ate capsule")
        return True
    else:
      return False

  def isGhostEaten(self, gameState, ghostIndex):
      """
      Checks if the ghost in arg ghostIndex was eaten yet during the scared state. 
      There is no need to check if a ghost was eaten if it already has a value of 0 in
      its scaredGhostTimer index.
      """
      if self.isScared(gameState,ghostIndex):
        ghost = self.getOpponents(gameState)[ghostIndex] # get the ghost at the arg ghostIndex
        previousObservation = self.getPreviousObservation() # get the previous observation
        if previousObservation:
          previousGhostPosition = previousObservation.getAgentPosition(ghost)
          if previousGhostPosition:
            currentGhostPosition = gameState.getAgentPosition(ghost)
            # If we cannot find the ghost anymore, or if the ghost moved more than 1 position then the ghost
            # has been eaten.
            if not currentGhostPosition or self.getMazeDistance(previousGhostPosition,currentGhostPosition) > 1:
              self.scaredGhostTimers[ghostIndex] = 0 # ghost is no longer scared after being eaten
              return True
      return False

  def chooseAction(self, gameState):
      """
      Picks among the actions with the highest Q(s,a).
      """
      actions = gameState.getLegalActions(self.index)
      self.isCapsuleEaten(gameState)
      # You can profile your evaluation time by uncommenting these lines
      # start = time.time()
      values = [self.evaluate(gameState, a) for a in actions]
      # print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

      maxValue = max(values)
      bestActions = [a for a, v in zip(actions, values) if v == maxValue]

      # decrement scaredTimers if needed.
      for i in range(len(self.scaredGhostTimers)):
        self.scaredGhostTimers[i] -=1 if self.scaredGhostTimers[i] > 0 else 0

      foodLeft = len(self.getFood(gameState).asList())

      if foodLeft <= 2:
        bestDist = 9999
        for action in actions:
          successor = self.getSuccessor(gameState, action)
          pos2 = successor.getAgentPosition(self.index)
          dist = self.getMazeDistance(self.start,pos2)
          if dist < bestDist:
            bestAction = action
            bestDist = dist
        return bestAction

      return random.choice(bestActions)

  def isScared(self, gameState, ghostIndex):
    """
    Checks if a ghost, given the arg ghostIndex is in a scared state.
    A ghost is in a scared state if it's timer is greater than 0
    """
    return self.scaredGhostTimers[ghostIndex] > 0
  


