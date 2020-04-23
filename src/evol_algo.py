from deap import base, creator, tools
from collections import namedtuple
import random
from numpy import sqrt, inf


class EvolutionaryAlgorithm:

    def __init__(self, startpoint, endpoint, obstacle_pointlist):
        self.xytuple = namedtuple('xytuple', ['x', 'y'])
        self.possible = [self.xytuple(int(x), int(y)) for x in range(500) for y in range(450)]  # possible locations
        self.startpoint = startpoint
        self.endpoint = endpoint
        self.obstacle_pointlist = obstacle_pointlist
        self.obstacles = [(obstacle.x, obstacle.y) for obstacle in self.obstacle_pointlist]
        self.toolbox = base.Toolbox()

    def register(self):
        """REGISTERING GENES"""
        creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
        creator.create('Individual', list, fitness=creator.FitnessMin)
        self.toolbox.register('position', random.choice, self.possible)
        self.toolbox.register('first', lambda x: x, self.startpoint)
        self.toolbox.register('last', lambda x: x, self.endpoint)
        """INDIVIDUAL"""
        self.toolbox.register('individual', tools.initCycle, creator.Individual,
                              (self.toolbox.first, self.toolbox.position, self.toolbox.position,
                               self.toolbox.position, self.toolbox.position, self.toolbox.last), n=1)
        """POPULATION"""
        self.toolbox.register('population', tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register('evaluate', self.distance)
        self.toolbox.decorate('evaluate', tools.DeltaPenalty(self.validate, inf))
        self.toolbox.register('mate', tools.cxTwoPoint)  # crossover operator
        self.toolbox.register('mutate', tools.mutShuffleIndexes, indpb=0.5)  # mutation operator
        self.toolbox.register('select', tools.selTournament, tournsize=3)  # selecting 3 best individuals from batch

    @staticmethod
    def distance(individual):
        d = 0
        for i in range(1, len(individual)):
            gene2, gene1 = individual[i], individual[i - 1]
            d += sqrt((gene2.x-gene1.x)**2+(gene2.y-gene1.y)**2)
        return d,

    @staticmethod
    def create_pathpoints(individual):
        pathpoints = []
        for i in range(1, len(individual)):
            x0, y0 = individual[i - 1].x, individual[i - 1].y
            x1, y1 = individual[i].x, individual[i].y
            if abs(x0-x1) < abs(y0-y1):  # reverse x with y
                if y0 != y1:
                    if x0 != x1:
                        a = 1/((y0 - y1) / (x0 - x1))
                        b = x0 - a * y0
                    else:
                        a = 0
                        b = x0 - a * y0
                    for y in range(min(y0, y1), max(y0, y1) + 1):
                        x = int(a * y + b)
                        pathpoints.append((x, y))
                else:
                    a = 0
                    b = y0
                    for x in range(min(x0, x1), max(x0, x1) + 1):
                        y = int(b)
                        pathpoints.append((x, y))
            else:
                if x0 != x1:
                    if y0 != y1:
                        a = (y0 - y1) / (x0 - x1)
                        b = y0 - a * x0
                    else:
                        a = 0
                        b = y0 - a * x0
                    for x in range(min(x0, x1), max(x0, x1) + 1):
                        y = int(a * x + b)
                        pathpoints.append((x, y))
                    for y in range(min(y0, y1), max(y0, y1)):
                        x = int(y - b / a)
                        pathpoints.append((x, y))
                else:
                    a = 0
                    b = x0
                    for y in range(min(y0, y1), max(y0, y1) + 1):
                        x = int(b)
                        pathpoints.append((x, y))
        return pathpoints

    def validate(self, individual):
        if individual[0] == self.startpoint:
            if individual[-1] == self.endpoint:
                pathpoints = self.create_pathpoints(individual)
                invalid = list(filter(set(pathpoints).__contains__, set(self.obstacles)))
                return len(invalid) == 0

    def ea(self, progress_callback, cxpb=0.3, mutpb=0.3, gen=20):
        init_pb = (cxpb, mutpb)
        s = 0  # success of mutation
        best_register = []
        pop = self.toolbox.population(n=10000)
        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        fits = [ind.fitness.values[0] for ind in pop]
        g = 0
        m = 0
        while g < gen:
            # A new generation
            g += 1
            # Select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # Clone the selected individuals (making offspring independent from their parents)
            offspring = list(map(self.toolbox.clone, offspring))
            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # cross two individuals with probability CXPB
                if random.random() < cxpb:
                    self.toolbox.mate(child1, child2)
                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values
            mutants = []
            for mutant in offspring:
                # mutate an individual with probability MUTPB
                if random.random() < mutpb:
                    mutated = True
                    mutants.append(mutant)
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            if mutated:
                m += 1
                mutants_fits = map(self.toolbox.evaluate, mutants)
                if len(best_register) != 0:
                    if min(mutants_fits) < best_register[-1].fitness.values[0]:
                        s += 1
                mutated = False
            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            # The population is entirely replaced by the offspring
            pop[:] = offspring
            # Emit callback
            fits = [ind.fitness.values[0] for ind in pop]
            progress_callback.emit((tools.selBest(pop, 1)[0], g, min(fits)))  # to gui
            if min(fits) == inf:
                cxpb, mutpb = 0, 1
                if len(best_register) != 0:
                    pop = [random.choice(best_register) for i in range(len(pop))]
                    cxpb, mutpb = init_pb
            else:
                best_register.append(tools.selBest(pop, 1)[0])
                ps = s/m  # prob of success
                if m % 5 == 0:
                    if ps > 1/5:
                        mutpb *= 1.5
                    elif ps < 1/5:
                        mutpb *= 0.9
                    m = 0
                    s = 0
        best_ind = tools.selBest(pop, 1)[0]
        return best_ind
