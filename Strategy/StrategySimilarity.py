#encoding=utf-8
'''
Created on 2017/04/30
@author: crystal
'''
from math import sqrt
from win32con import NULL

def get_euclid_correlation(values, key1, key2):
    value       = 0
    sameValues  = get_common_prefers(values, key1, key2)
    
    if len(sameValues) == 0:
        return value

    sumOfSquares = sum([pow(values[key1][item] - values[key2][item], 2) for item in sameValues])
    value = 1./(1 + sqrt(sumOfSquares))
    
    return value

def get_pearson_correlation(param1 = None, param2 = None, param3 = None):
    if param1 == None:
        return
    
    if type(param1) == dict:
        return get_pearson_correlation_table(param1, param2, param3)
    else:
        return get_pearson_correlation_array(param1, param2)
    
def get_pearson_correlation_table(values, key1, key2):
    value       = 0
    sameValues  = get_common_prefers(values, key1, key2)
    
    n = len(sameValues)
    if n == 0:
        return value
    
    sum1 = sum([values[key1][item] for item in sameValues])
    sum2 = sum([values[key2][item] for item in sameValues])
    
    sumSquare1 = sum([pow(values[key1][item], 2) for item in sameValues])
    sumSquare2 = sum([pow(values[key2][item], 2) for item in sameValues])
    
    multiplySum = sum(values[key1][item] * values[key2][item] for item in sameValues)
    
    numerator   = multiplySum - (sum1 * sum2 / n)
    denominator = sqrt((sumSquare1 - pow(sum1, 2) / n) * (sumSquare2 - pow(sum2, 2) / n))
    
    if denominator == 0:
        return value
    
    value = numerator / denominator
    
    return value

def get_pearson_correlation_array(values1, values2):
    result  = 0
    n       = len(values1)
    
    if n != len(values2):
        return result

    sum1 = sum(values1)
    sum2 = sum(values2)
    
    sumSquare1 = sum([pow(value, 2) for value in values1])
    sumSquare2 = sum([pow(value, 2) for value in values2])
    
    multiplySum = sum(values1[i] * values2[i] for i in range(n))
    
    numerator   = multiplySum - (sum1 * sum2 / n)
    denominator = sqrt((sumSquare1 - pow(sum1, 2) / n) * (sumSquare2 - pow(sum2, 2) / n))
    
    if denominator == 0:
        return result
    
    result = numerator / denominator
    
    return result

def get_tanimoto_correlation(param1 = None, param2 = None, param3 = None):
    if param1 == None:
        return
    
    if type(param1) == dict:
        return get_tanimoto_correlation_table(param1, param2, param3)
    else:
        return get_tanimoto_correlation_array(param1, param2)
    
def get_tanimoto_correlation_table(values, key1, key2):
    sameValues  = get_common_prefers(values, key1, key2)
    commonLen   = len(sameValues)
    len1        = len(values[key1])
    len2        = len(values[key2])
    
    result = float(commonLen) / (len1 + len2 - commonLen)
    
    return result

def get_tanimoto_correlation_array(values1, values2):
    result  = 0
    length  = len(values1)
    if length != len(values2):
        return result

    count1  = 0
    count2  = 0
    same    = 0
    
    for i in range(length):
        if values1[i] != 0:
            count1 += 1
        if values2[i] != 0:
            count2 += 1
        if values1[i] != 0 and values2[i] != 0:
            same += 1
            
    result = float(same) / (count1 + count2 - same)
    
    return result

def get_cosine_correlation(values, key1, key2):
    value       = 0
    sameValues  = get_common_prefers(values, key1, key2)
    
    multipySum = sum(values[key1][item] * values[key2][item] for item in sameValues)
    
    sum1Square = sum([pow(values[key1][item], 2) for item in sameValues])
    sum2Square = sum([pow(values[key2][item], 2) for item in sameValues])
    
    numerator   = multipySum
    denominator = sqrt(sum1Square) * sqrt(sum2Square)
    
    if denominator == 0:
        return value
    
    value = numerator / denominator
    
    return value

def get_common_prefers(values, key1, key2):
    sameValues  = []    
    for key in values[key1]:
        if key in values[key2]:
            sameValues.append(key)
            
    return sameValues