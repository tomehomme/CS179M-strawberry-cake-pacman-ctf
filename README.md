# Team strawberry-cake pacman-ctf
## Team Members - Paris Hom and Osvaldo Moreno Ornelas
## Python3 version of UC Berkeley's CS 188 Pacman Capture the Flag project

### Original Licensing Agreement (which also extends to this version)
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

### This version attribution
This version (cshelton/pacman-ctf github repo) was modified by Christian
Shelton (cshelton@cs.ucr.edu) on June 23, 2020 to run under Python 3.


## Agents Stragety
The agents have an aggressive stragety. For the Ghost agent the class used is DefensiveReflexAgent. In this class, we -------- .
The Pacman agent uses OffensiveReflexAgent. In this class, we always try to seek for the
closest food. When eating we keep a counter. When the counter reaches 4, we go back and 
dump the food back to base. If the pacman is killed while carrying 5 orbs, the Pacman goes
back to the lace the orbs were dumped. Also, the pacman remembers the decisions that have been made and when deciding where to go, it tries to go to a better direction then it did last time, rather than making a random decision.

### Decision to persue this stragety
We decided to use this stragety because we wanted to make the Ghost a good keeper of the food while the pacman launch an offensive that took an small amount of risks. 


### How the work was divided

Paris worked on the ghost agent while Osvaldo worked on the pacman. Paris helped Osvaldo in the development of the pacman.

#### How well the agent works

**Ghost:** Ghost is capable of --

**Pacman:**  Pacman retrieves the food as expected. Pacman makes decisions based on a bank. The decisions are not as smart or dynamic as expected, there is still work to do in that aspect. Pacman "dances" around ghost if there is one always trying to block. It is a work in progress to make pacman flank the ghost.

#### Leassons learned from the iteration

**To Change:** Pacman's decision making algorith into something more dynamic and self-learning. The ghost --

**To Keep:** The way the food is retrieved and brought back. The food dumped to go back and get it back if it is higher than a set limit. Ghost --
