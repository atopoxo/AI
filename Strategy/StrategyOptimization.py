#encoding=utf-8
'''
Created on 2017/05/17
@author: crystal
'''

import time
import random
import math
import copy

def read_file(filePath):
    flights = {}
    for line in file(filePath):
        origin, destination, depart, arrive, price = line.strip().split(',')
        flights.setdefault((origin, destination), [])
        flights[(origin, destination)].append((depart, arrive, int(price)))
        
    return flights

def print_schedule(flights, plans, solution):
    for name in solution:
        print '%10s:' % name
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            print '%20s %5s %6s %5s-%5s $%3s' % (origin, '-->', destination, recorder[0], recorder[1], recorder[2])
    
def random_optimize(flights, plans, costFunction, times = 1000, bIsSmallBest = True):
    best = -1
    bestSolution = None
    
    randomValues = {}
    for name in plans:
        randomValues[name] = []
        for i in range(len(plans[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            maxValue = len(flights[(origin, destination)])
            randomValues[name].append((0, maxValue - 1))
            
    for i in range(times):
        solution = {}
        for name in plans:
            solution[name] = []
            for i in range(len(plans[name])):
                solution[name].append(random.randint(randomValues[name][i][0], randomValues[name][i][1]))
        
        cost = costFunction(flights, plans, solution)
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

def hill_climb_optimize(flights, plans, costFunction, bIsSmallBest = True):
    best = -1
    
    randomValues = {}
    for name in plans:
        randomValues[name] = []
        for i in range(len(plans[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            maxValue = len(flights[(origin, destination)])
            randomValues[name].append((0, maxValue - 1))
            
    solution = {}
    for name in plans:
        solution[name] = []
        for i in range(len(plans[name])):
            solution[name].append(random.randint(randomValues[name][i][0], randomValues[name][i][1]))
            
    while True:
        neighbors = []
        for name in solution:
            for i in range(len(solution[name])):
                if solution[name][i] > randomValues[name][i][0]:
                    neighbor = copy.deepcopy(solution)
                    neighbor[name][i] -= 1
                    neighbors.append(neighbor)
                if solution[name][i] < randomValues[name][i][1]:
                    neighbor = copy.deepcopy(solution)
                    neighbor[name][i] += 1
                    neighbors.append(neighbor)
                    
        currentCost = costFunction(flights, plans, solution)
        best = currentCost
        
        for i in range(len(neighbors)):
            cost = costFunction(flights, plans, neighbors[i])
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
 
def annealing_optimize(flights, plans, costFunction, temperature = 10000.0, cool = 0.95, step = 1, bIsSmallBest = True):
    eps = 0.1
    nameCount = 0
    maxPlanCount = 0
    names = []
    plansCount = {}
    bestCost = 0
    
    randomValues = {}
    for name in plans:
        names.append(name)
        nameCount += 1
        randomValues[name] = []
        plansCount[name] = len(plans[name])
        for i in range(plansCount[name]):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            maxValue = len(flights[(origin, destination)])
            randomValues[name].append((0, maxValue - 1))
    
    solution = {}
    for name in plans:
        solution[name] = []
        for i in range(len(plans[name])):
            solution[name].append(random.randint(randomValues[name][i][0], randomValues[name][i][1]))

    while temperature > eps:
        nameIndex = random.randint(0, nameCount - 1)
        name = names[nameIndex]
        planIndex = random.randint(0, plansCount[name] - 1)
        
        newSolution = copy.deepcopy(solution)
        direction = random.randint(-step, step)
        newSolution[name][planIndex] += direction
        newSolution[name][planIndex] = max(newSolution[name][planIndex], randomValues[name][planIndex][0])
        newSolution[name][planIndex] = min(newSolution[name][planIndex], randomValues[name][planIndex][1])
        
        bestCost = costFunction(flights, plans, solution)
        newCost = costFunction(flights, plans, newSolution)
        
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

def genetic_optimize(flights, plans, costFunction, populationSize = 50, elite = 0.2, mutateProbability = 0.2, step = 1, times = 100):
    def mutate(genes, boundaries):
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
    def crossover(genesA, genesB, boundaries):
        index = random.randint(1, len(boundaries) - 1)
        return genesA[0:index] + genesB[index:]
    
    boundaries = []
    for name in plans:
        for i in range(len(plans[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            maxValue = len(flights[(origin, destination)])
            boundaries.append((0, maxValue - 1))
            
    population = []
    for i in range(populationSize):
        genes = [random.randint(boundaries[i][0], boundaries[i][1]) for i in range(len(boundaries))]
        population.append(genes)
        
    eliteCount = int(elite * populationSize)
    
    for i in range(times):
        scores = [(costFunction(flights, plans, genes), genes) for genes in population]
        scores.sort()
        rankList = [genes for (score, genes) in scores]
        
        population = rankList[0:eliteCount]
        
        while len(population) < populationSize:
            if random.random() < mutateProbability:
                index = random.randint(0, eliteCount)
                population.append(mutate(rankList[index], boundaries))
            else:
                indexA = random.randint(0, eliteCount)
                indexB = random.randint(0, eliteCount)
                while indexA == indexB:
                    indexB = random.randint(0, eliteCount)
                population.append(crossover(rankList[indexA], rankList[indexB], boundaries))
    
    ways = scores[0][1]
    solution = {}
    index = 0
    for name in plans:
        solution[name] = {}
        for i in range(len(plans[name])):
            solution[name][i] = ways[index]
            index += 1
                
    return scores[0][0], solution
    
def schedule_cost(flights, plans, solution):
    if type(solution) == dict:
        return schedule_cost_dict(flights, plans, solution)
    else:
        return schedule_cost_vector(flights, plans, solution)
        
def schedule_cost_dict(flights, plans, solution):
    totalPrice = 0
    totalWaitTime = 0
    earliestLeave = 24 * 60
    latestArrival = 0

    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            totalPrice += recorder[2]
            
            if (i & 1) == 0:
                landTime = get_minutes(recorder[1])
                latestArrival = max(latestArrival, landTime)
            else:
                takeOffTime = get_minutes(recorder[0])
                earliestLeave = min(earliestLeave, takeOffTime)
    
    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            if (i & 1) == 0:
                totalWaitTime += latestArrival - get_minutes(recorder[1])
            else:
                totalWaitTime += get_minutes(recorder[0]) - earliestLeave
                
    if latestArrival > earliestLeave:
        totalPrice += 50
        
    return totalPrice + totalWaitTime

def schedule_cost_vector(flights, plans, ways):
    totalPrice = 0
    totalWaitTime = 0
    earliestLeave = 24 * 60
    latestArrival = 0
    index = 0
    
    solution = {}
    for name in plans:
        solution[name] = {}
        for i in range(len(plans[name])):
            solution[name][i] = ways[index]
            index += 1

    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            totalPrice += recorder[2]
            
            if (i & 1) == 0:
                landTime = get_minutes(recorder[1])
                latestArrival = max(latestArrival, landTime)
            else:
                takeOffTime = get_minutes(recorder[0])
                earliestLeave = min(earliestLeave, takeOffTime)
    
    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            if (i & 1) == 0:
                totalWaitTime += latestArrival - get_minutes(recorder[1])
            else:
                totalWaitTime += get_minutes(recorder[0]) - earliestLeave
                
    if latestArrival > earliestLeave:
        totalPrice += 50
        
    return totalPrice + totalWaitTime
            
def get_minutes(currentTime):
    formatTime = time.strptime(currentTime, '%H:%M')
    seconds = formatTime[3] * 50 + formatTime[4]
    return seconds