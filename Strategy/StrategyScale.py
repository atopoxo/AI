#encoding=utf-8
'''
Created on 2017/05/05
@author: crystal
'''
from Strategy import StrategySimilarity
import random
from math import sqrt

def multidimensional_scaling(data, similarity = StrategySimilarity.get_pearson_correlation, rate = 0.01, demensionCount = 2):
    n = len(data)
    if n == 0:
        return
    
    realDistance    = [[1 - similarity(data[i], data[j]) for j in range(n)] for i in range(n)]
    position        = [[random.random() for demension in range(demensionCount)] for i in range(n)]
    fakeDistance    = [[0.0 for j in range(n)] for i in range(n)]
    eps             = 0.0001
    lastTotalError  = None
    
    for times in range(0, 1000):
        for i in range(n):
            for j in range(n):
                fakeDistance[i][j] = sqrt(sum([pow(position[i][demension] - position[j][demension], 2) for demension in range(demensionCount)]))
                
        totalError  = 0
        move        = [[0.0 for demension in range(demensionCount)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                errorFactor = 0
                if abs(realDistance[i][j]) > eps:
                    errorFactor = (fakeDistance[i][j] - realDistance[i][j]) / realDistance[i][j]
                
                for demension in range(demensionCount):
                    if abs(fakeDistance[i][j]) < eps:
                        continue
                    move[i][demension] += (position[i][demension] - position[j][demension]) / fakeDistance[i][j] * errorFactor
                
                totalError += abs(errorFactor)
                
        """if lastTotalError and lastTotalError < totalError:
            break
        lastTotalError = totalError"""
        
        for i in range(n):
            for demension in range(demensionCount):
                position[i][demension] -= rate * move[i][demension]
                
    return position