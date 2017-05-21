#encoding=utf-8
'''
Created on 2017/05/21
@author: crystal
'''

import math
from Strategy import StrategyOptimization

class SocialNetworksOptimization:
    def __init__(self, people, links):
         self.people = people
         self.links = links
         
    def social_networks_random_optimize(self):
        boundires = [(10, 370)] * (len(self.people) * 2)
        
        cost, solution = StrategyOptimization.random_optimize(boundires, self.cross_count, times = 1000, bIsSmallBest = True)
        
        return cost, solution
        
    def cross_count(self, values):
        totalCount  = 0
        positions   = dict([(self.people[i], (values[i * 2], values[i * 2 + 1])) for i in range(0, len(self.people))])
        linkCount   = len(self.links)
        
        for i in range(linkCount):
            for j in range(i + 1, linkCount):
                (x1, y1), (x2, y2) = positions[self.links[i][0]], positions[self.links[i][1]]
                (x3, y3), (x4, y4) = positions[self.links[j][0]], positions[self.links[j][1]]
                
                distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
                if distance < 50:
                    totalCount += (1.0 - (distance / 50.0))
                
                denominator = (x2 - x1) * (y4 - y3) - (x4 - x3) * (y2 - y1)
                if denominator == 0:
                    continue
                
                numeratorA = float(((x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3))) / denominator
                numeratorB = float(((x2 - x1) * (y1 - y3) - (x1 - x3) * (y2 - y1))) / denominator
                
                if numeratorA > 0 and numeratorA < 1 and numeratorB > 0 and numeratorB < 1:
                    totalCount += 1
                    
        return totalCount