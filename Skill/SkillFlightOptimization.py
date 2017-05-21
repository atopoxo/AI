#encoding=utf-8
'''
Created on 2017/05/17
@author: crystal
'''

import time
import copy
from Strategy import StrategyOptimization

class FlightOptimization:
    def __init__(self, plans):
        self.plans = plans
        
    def __del__(self):
        pass
        
    def read_flights_data(self, filePath):
        flights = {}
        for line in file(filePath):
            origin, destination, depart, arrive, price = line.strip().split(',')
            flights.setdefault((origin, destination), [])
            flights[(origin, destination)].append((depart, arrive, int(price)))
            
        self.flights = flights
    
    def print_schedule(self, solution):
        for name in solution:
            print '%10s:' % name
            for i in range(len(solution[name])):
                origin = self.plans[name][i][0]
                destination = self.plans[name][i][1]
                recorder = self.flights[(origin, destination)][solution[name][i]]
                print '%20s %5s %6s %5s-%5s $%3s' % (origin, '-->', destination, recorder[0], recorder[1], recorder[2])
        
    def flight_random_optimize(self):
        boundires = []
        for name in self.plans:
            for i in range(len(self.plans[name])):
                maxValue = len(self.flights[(self.plans[name][i][0], self.plans[name][i][1])])
                boundires.append((0, maxValue - 1))
        
        cost, solution = StrategyOptimization.random_optimize(boundires, self.flight_schedule_cost, times = 1000, bIsSmallBest = True)
        
        finalSolution = self.transform_to_flight_solution(solution)
        
        return cost, finalSolution
    
    def flight_hill_climb_optimize(self):
        boundires = []
        for name in self.plans:
            for i in range(len(self.plans[name])):
                maxValue = len(self.flights[(self.plans[name][i][0], self.plans[name][i][1])])
                boundires.append((0, maxValue - 1))
        
        cost, solution = StrategyOptimization.hill_climb_optimize(boundires, self.flight_schedule_cost, step = 1, bIsSmallBest = True)
        
        finalSolution = self.transform_to_flight_solution(solution)
        
        return cost, finalSolution
    
    def flight_annealing_optimize(self):
        boundires = []
        for name in self.plans:
            for i in range(len(self.plans[name])):
                maxValue = len(self.flights[(self.plans[name][i][0], self.plans[name][i][1])])
                boundires.append((0, maxValue - 1))
        
        cost, solution = StrategyOptimization.annealing_optimize(boundires, self.flight_schedule_cost, temperature = 10000.0, cool = 0.95, step = 1, bIsSmallBest = True)
        
        finalSolution = self.transform_to_flight_solution(solution)
        
        return cost, finalSolution
                
    def flight_genetic_optimize(self):
        boundires = []
        for name in self.plans:
            for i in range(len(self.plans[name])):
                maxValue = len(self.flights[(self.plans[name][i][0], self.plans[name][i][1])])
                boundires.append((0, maxValue - 1))
        
        cost, solution = StrategyOptimization.genetic_optimize(boundires, self.flight_schedule_cost, populationSize = 50, elite = 0.2, mutateProbability = 0.2, step = 1, times = 100)
        
        finalSolution = self.transform_to_flight_solution(solution)
        
        return cost, finalSolution
    
    def transform_to_flight_solution(self, solution):
        finalSolution = {}
        index = 0
        for name in self.plans:
            finalSolution[name] = {}
            for i in range(len(self.plans[name])):
                finalSolution[name][i] = solution[index]
                index += 1
                
        return finalSolution
        
    def flight_schedule_cost(self, solution):
        if type(solution) == dict:
            return self.schedule_cost_dict(self.flights, self.plans, solution)
        else:
            return self.schedule_cost_vector(self.flights, self.plans, solution)
            
    def schedule_cost_dict(self, flights, plans, solution):
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
                    landTime = self.get_minutes(recorder[1])
                    latestArrival = max(latestArrival, landTime)
                else:
                    takeOffTime = self.get_minutes(recorder[0])
                    earliestLeave = min(earliestLeave, takeOffTime)
        
        for name in solution:
            for i in range(len(solution[name])):
                origin = plans[name][i][0]
                destination = plans[name][i][1]
                recorder = flights[(origin, destination)][solution[name][i]]
                
                if (i & 1) == 0:
                    totalWaitTime += latestArrival - self.get_minutes(recorder[1])
                else:
                    totalWaitTime += self.get_minutes(recorder[0]) - earliestLeave
                    
        if latestArrival > earliestLeave:
            totalPrice += 50
            
        return totalPrice + totalWaitTime
    
    def schedule_cost_vector(self, flights, plans, ways):
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
                    landTime = self.get_minutes(recorder[1])
                    latestArrival = max(latestArrival, landTime)
                else:
                    takeOffTime = self.get_minutes(recorder[0])
                    earliestLeave = min(earliestLeave, takeOffTime)
        
        for name in solution:
            for i in range(len(solution[name])):
                origin = plans[name][i][0]
                destination = plans[name][i][1]
                recorder = flights[(origin, destination)][solution[name][i]]
                
                if (i & 1) == 0:
                    totalWaitTime += latestArrival - self.get_minutes(recorder[1])
                else:
                    totalWaitTime += self.get_minutes(recorder[0]) - earliestLeave
                    
        if latestArrival > earliestLeave:
            totalPrice += 50
            
        return totalPrice + totalWaitTime
                
    def get_minutes(self, currentTime):
        formatTime = time.strptime(currentTime, '%H:%M')
        seconds = formatTime[3] * 50 + formatTime[4]
        return seconds