#encoding=utf-8
'''
Created on 2017/05/21
@author: crystal
'''

import random
import math

def print_solution(prefers, dorms, solution):
    slots = []
    for i in range(len(dorms)):
        slots += [i, i]
    
    for i in range(len(solution)):
        index = int(solution[i])
        dorm = dorms[slots[index]]
        
        print prefers[i][0], dorm
        del slots[index]
        
def dorm_cost(prefers, dorms, solution):
    cost = 0
    slots = []
    for i in range(len(dorms)):
        slots += [i, i]
    
    for i in range(len(solution)):
        index = int(solution[i])
        dorm = dorms[slots[index]]
        prefer = prefers[i][1]
        if prefer[0] == dorm:
            cost += 0
        elif prefer[1] == dorm:
            cost += 1
        else:
            cost += 3
        del slots[index]
        
    return cost
        