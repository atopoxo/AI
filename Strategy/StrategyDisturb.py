#encoding=utf-8
'''
Created on 2017/06/03
@author: crystal
'''

from math import log

def get_gini_impurity(rows, getCountsFunction):
    total       = len(rows)
    counts      = getCountsFunction(rows)
    impurity    = 0
    
    for i in counts:
        probabilityA = float(counts[i]) / total
        for j in counts:
            if i == j:
                continue
            probabilityB = float(counts[j]) / total
            impurity += probabilityA * probabilityB
            
    return impurity

def get_entropy(rows, getCountsFunction):
    log2    = lambda x: log(x) / log(2)
    counts  = getCountsFunction(rows)
    total   = len(rows)
    value   = 0.0
    
    for key in counts.keys():
        probability = float(counts[key]) / total
        value -= probability * log2(probability)
        
    return value