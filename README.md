# Path Finding

## Algorithm
Developed path finding algorithm is based on [genetic algorithms](https://towardsdatascience.com/introduction-to-genetic-algorithms-including-example-code-e396e98d8bf3).
Initial mutation and crossover probabilities are set up as 0.3 (30%). With every 5th mutation the probability of mutating is adjusted
in accordance with [1/5-th rule](https://hal.inria.fr/inria-00430515/document). Function to be optimised is a distance between points. 
Distance is given by Euclidean distance formula. Punishment function - if no valid path is found: distance=inf. Valid path is a path that does not
cross the obstacles.
## GUI
Based on PyQt5. In main window, user can define start and end points. The environment can be modified by drawing lines which will be
considered by algorithm as obstacles. Run button launches thread (genetic algorithm). With every iteration (algorithm's generation) progress
callback is emited to main window. The signal contains information about current generation and best found distance. After the end of algorithm,
the messagebox with with best path found pops up. The main window draws the best path as well automatically.
## Example
### Run app
![img1](https://github.com/MarcinKurylo/Path_Finding/blob/master/img/AG_1.png)
### Define start and end points
![img2](https://github.com/MarcinKurylo/Path_Finding/blob/master/img/AG_3.png)
![img3](https://github.com/MarcinKurylo/Path_Finding/blob/master/img/AG_4.png)
### Draw obstacles
![img4](https://github.com/MarcinKurylo/Path_Finding/blob/master/img/AG_5.png)
### Results
![img5](https://github.com/MarcinKurylo/Path_Finding/blob/master/img/AG_6.png)
