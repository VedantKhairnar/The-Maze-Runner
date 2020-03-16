# The-Maze-Runner
AI Assg : Use of Greedy Best First Search Traversal to find route from Source to Destination

![Snap](https://github.com/VedantKhairnar/The-Maze-Runner/blob/master/Maze.PNG)

## Greedy Best First Search Algorith
Best First Search is an instance of graph search algorithm in which a mode is selected for expansion based on evaluation function f(n). Traditionally, the node which is the lowest evaluation is selected for expansion because the evaluation meassures distance to the goal. Best first search can be implemented within general search frame work via a priority queue, a data structure that will maintain the fringe in ascending order of f values. This search algorithm serves as combination of depth first and breadth first search algorithm. Best first search algorithm is often referred greedy algorithm this is because they quickly attack the most desirable path as soon as its heuristic weight becomes the most desirable.

For our project we have given pirorities priorities to the direction of traversal top, left, bottom, right as 1, 2, 3 and 4 respectively

## Concept

Step 1: Traverse the root node

 

Step 2: Traverse any neighbour of the root node, that is maintaining a least distance from the root node and insert them in ascending order into the queue.

Step 3: Traverse any neighbour of neighbour of the root node, that is maintaining a least distance from the root node and insert them in ascending order into the queue

Step 4: This process will continue until we are getting the goal node


## Algorithm

Step 1: Place the starting node or root node into the queue.

Step 2: If the queue is empty, then stop and return failure.

Step 3: If the first element of the queue is our goal node, then stop and return success.

Step 4: Else, remove the first element from the queue. Expand it and compute the estimated goal distance for each child. Place the children in the queue in ascending order to the goal distance.

Step 5: Go to step-3

Step 6: Exit.
