#encoding=utf-8
'''
Created on 2017/05/01
@author: crystal
'''
from Strategy import StrategySimilarity
import random

class cluster:
    def __init__(self, vector, left = None, right = None, distance = 0.0, id = None):
        self.left       = left
        self.right      = right
        self.vector     = vector
        self.id         = id
        self.distance   = distance
        
def k_cluster(values, similarity = StrategySimilarity.get_pearson_correlation, k = 4):
    lastBestMatches = None
    
    itemCount = len(values)
    if itemCount <= 0:
        return lastBestMatches
    
    vectorLength = len(values[0])
    if vectorLength <= 0:
        return lastBestMatches
    
    ranges = [(min([items[i] for items in values]), max([items[i] for items in values])) for i in range(vectorLength)]
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(vectorLength)] for j in range(k)]

    for count in range(100):
        print 'Iteration %d' % (count + 1)
        
        bestMatches = [[] for i in range(k)]
        for id in range(itemCount):
            vector      = values[id]
            bestMatchId = 0
            for i in range(k):
                if get_distance(clusters[i], vector, similarity) < get_distance(clusters[bestMatchId], vector, similarity):
                    bestMatchId = i
            bestMatches[bestMatchId].append(id)
        if bestMatches == lastBestMatches:
            break
        lastBestMatches = bestMatches
        
        for i in range(k):
            if len(bestMatches[i]) <= 0:
                continue
            vectorAverages = [0.0] * vectorLength
            currentItemCount = len(bestMatches[i])
            for id in bestMatches[i]:
                for j in range(vectorLength):
                    vectorAverages[j] += values[id][j]
            for j in range(vectorLength):
                vectorAverages[j] /= currentItemCount
            clusters[i] = vectorAverages
    
    return lastBestMatches
    
def hierarchical_cluster(values, similarity = StrategySimilarity.get_pearson_correlation):
    distances           = {}
    currentClusterId    = -1
    
    clusters = [cluster(values[i], id = i) for i in range(len(values))]

    while len(clusters) > 1:
        vectorLength    = len(clusters[0].vector)
        closestPair     = (0, 1)
        closest         = get_distance(clusters[0].vector, clusters[1].vector, similarity)
        
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if (clusters[i].id, clusters[j].id) not in distances:
                    distances[(clusters[i].id, clusters[j].id)] = get_distance(clusters[i].vector, clusters[j].vector, similarity)
                    
                if distances[(clusters[i].id, clusters[j].id)] < closest:
                    closest = distances[(clusters[i].id, clusters[j].id)]
                    closestPair = (i, j)
        
        mergeVector = [(clusters[closestPair[0]].vector[i] + clusters[closestPair[1]].vector[i]) / 2.0 for i in range(vectorLength)]
        
        newCluster = cluster(mergeVector, left = clusters[closestPair[0]], right = clusters[closestPair[1]], distance = closest, id = currentClusterId)
        
        currentClusterId -= 1
        
        del clusters[closestPair[1]]
        del clusters[closestPair[0]]
        clusters.append(newCluster)
        
    return clusters[0]

def rotate_matrix(matrix):
    newMatrix   = []
    rowCount    = len(matrix)
    
    if rowCount == 0:
        return newMatrix
    
    columnCount = len(matrix[0])
    if columnCount == 0:
        return newMatrix
    
    for i in range(columnCount):
        newRow = [matrix[j][i] for j in range(rowCount)]
        newMatrix.append(newRow)
        
    return newMatrix

def get_distance(values1, values2, similarity = StrategySimilarity.get_pearson_correlation):
    return 1.0 - similarity(values1, values2)