#encoding=utf-8
'''
Created on 2017/05/21
@author: crystal
'''

import random
import math

def random_optimize(boundaries, costFunction, times = 1000, bIsSmallBest = True):
    best            = -1
    bestSolution    = None
    
    for i in range(times):
        solution = [random.randint(boundaries[i][0], boundaries[i][1]) for i in range(len(boundaries))]
        cost = costFunction(solution)
        
        if best == -1:
            best = cost
        
        if bIsSmallBest:
            if best > cost:
                best = cost
                bestSolution = solution
        else:
            if best < cost:
                best = cost
                bestSolution = solution
    
    return best, bestSolution

def hill_climb_optimize(boundaries, costFunction, step = 1, bIsSmallBest = True):
    best        = -1
    solution    = [random.randint(boundaries[i][0], boundaries[i][1]) for i in range(len(boundaries))]
    
    while True:
        neighbors = []
        for i in range(len(boundaries)):
            if solution[i] - step >= boundaries[i][0]:
                neighbors.append(solution[0:i] + [solution[i] - step] + solution[i + 1:])
            if solution[i] + step <= boundaries[i][1]:
                neighbors.append(solution[0:i] + [solution[i] + step] + solution[i + 1:])
                    
        currentCost = costFunction(solution)
        best = currentCost
        
        for i in range(len(neighbors)):
            cost = costFunction(neighbors[i])
            if bIsSmallBest:
                if cost < best:
                    cost = best
                    solution = neighbors[i]
            else:
                if cost > best:
                    cost = best
                    solution = neighbors[i]
                    
        if best == currentCost:
            break
        
    return best, solution

def annealing_optimize(boundaries, costFunction, temperature = 10000.0, cool = 0.95, step = 1, bIsSmallBest = True):
    eps         = 0.1
    bestCost    = -1
    maxIndex    = len(boundaries) - 1
    solution    = [random.randint(boundaries[i][0], boundaries[i][1]) for i in range(len(boundaries))]
    
    while temperature > eps:
        index = random.randint(0, maxIndex)
        direction = random.randint(-step, step)
         
        newSolution = solution[:]
        newSolution[index] += direction
        newSolution[index] = max(boundaries[index][0], newSolution[index])
        newSolution[index] = min(newSolution[index], boundaries[index][1])
         
        bestCost = costFunction(solution)
        newCost = costFunction(newSolution)
        
        if bIsSmallBest:
            if newCost < bestCost or random.random() < pow(math.e, -(newCost - bestCost) / temperature):
                bestCost = newCost
                solution = newSolution
        else:
            if newCost > bestCost or random.random() < pow(math.e, -(bestCost - newCost) / temperature):
                bestCost = newCost
                solution = newSolution
                
        temperature *= cool
    
    return bestCost, solution

def genetic_optimize(boundaries, costFunction, populationSize = 50, elite = 0.2, mutateProbability = 0.2, step = 1, times = 100):
    def mutate(genes):
        index = random.randint(0, len(boundaries) - 1)
        if random.random() < 0.5:
            if genes[index] - step >= boundaries[index][0]:
                return genes[0:index] + [genes[index] - step] + genes[index + 1:]
            else:
                return genes
        else:
            if genes[index] + step <= boundaries[index][1]:
                return genes[0:index] + [genes[index] + step] + genes[index + 1:]
            else:
                return genes
    
    def crossover(genesA, genesB):
        index = random.randint(1, len(boundaries) - 1)
        return genesA[0:index] + genesB[index:]
    
    population = []
    for i in range(populationSize):
        genes = [random.randint(boundaries[i][0], boundaries[i][1]) for i in range(len(boundaries))]
        population.append(genes)
    
    eliteCount = int(elite * populationSize)
    
    for i in range(times):
        scores = [(costFunction(genes), genes) for genes in population]
        scores.sort()
        rankList = [genes for (score, genes) in scores]
        
        population = rankList[0:eliteCount]
        
        while len(population) < populationSize:
            if random.random() < mutateProbability:
                index = random.randint(0, eliteCount)
                population.append(mutate(rankList[index]))
            else:
                indexA = random.randint(0, eliteCount)
                indexB = random.randint(0, eliteCount)
                while indexA == indexB:
                    indexB = random.randint(0, eliteCount)
                population.append(crossover(rankList[indexA], rankList[indexB]))
        
    return scores[0][0], scores[0][1]