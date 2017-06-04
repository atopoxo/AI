#encoding=utf-8
'''
Created on 2017/06/03
@author: crystal
'''

from Strategy import StrategyDisturb
from Tkconstants import CURRENT

class DecisionTreePredictNode:
    def __init__(self, criteriaIndex = -1, judgeValue = None, nodes = None, results = None):
        self.criteriaIndex = criteriaIndex
        self.judgeValue = judgeValue
        self.nodes = nodes
        self.results = results
        
    def modified_classify(self, observation, node):
        if node.results != None:
            return node.results
        else:
            value = observation[node.criteriaIndex]
            if value == None:
                totalCount = 0
                counts = []
                results = []
                for currentNode in node.nodes:
                    result = self.modified_classify(observation, currentNode)
                    results.append(result)
                    count = sum(result.values())
                    counts.append(count)
                    totalCount += count
                    
                probabilities = []
                for count in counts:
                    probabilities.append(float(count) / totalCount)
                
                index = 0
                values = {}
                for result in results:
                    probability = probabilities[index]
                    index += 1
                    for key, value in result.items():
                        values.setdefault(key, 0)
                        values[key] += value * probability
                return values
            else:
                branch = self.get_branch(value, node)
                return self.modified_classify(observation, branch)
        
    def classify(self, observation, node):
        if node.results != None:
            return node.results
        else:
            value = observation[node.criteriaIndex]
            branch = self.get_branch(value, node)
            return self.classify(observation, branch)
        
    def get_tree(self, rows, scoreFunction = StrategyDisturb.get_entropy):
        length = len(rows)
        if length == 0:
            return DecisionTreePredictNode()
        
        score           = scoreFunction(rows, self.get_unique_counts)
        bestGain        = 0.0
        bestScore       = 0.0
        bestCriteria    = None
        bestSets        = None
        columnCount     = len(rows[0]) - 1
        
        for column in range(0, columnCount):
            columnValues = {}
            for row in rows:
                columnValues[row[column]] = 1
            for value in columnValues.keys():
                sets = self.divide_function(rows, column, value)
                gain = score
                flag = True
                for set in sets:
                    setLength = len(set)
                    flag = flag and (setLength > 0)
                    probability = float(setLength) / length
                    gain -= probability * scoreFunction(set, self.get_unique_counts)
                if gain > bestGain and flag:
                    bestGain = gain
                    bestCriteria = (column, value)
                    bestSets = sets
                    
        if bestGain > 0:
            branches = [self.get_tree(bestSet, scoreFunction) for bestSet in bestSets]
            return DecisionTreePredictNode(criteriaIndex = bestCriteria[0], judgeValue = bestCriteria[1], nodes = branches)
        else:
            return DecisionTreePredictNode(results = self.get_unique_counts(rows))
     
    def prune(self, node, threshold = 0.1, scoreFunction = StrategyDisturb.get_entropy): 
        for currentNode in node.nodes:
            if currentNode.results == None:
                self.prune(currentNode, threshold)
                
        flag = True
        for currentNode in node.nodes:
            flag = flag and (currentNode.results != None)
            
        if flag == True:
            totalResults= []
            disturbedSum = 0
            for currentNode in node.nodes:
                newResults = []
                for value, count in currentNode.results.items():
                    newResults += [[value]] * count
                totalResults += newResults
                disturbedSum += scoreFunction(newResults, self.get_unique_counts)
                
            delta = scoreFunction(totalResults, self.get_unique_counts) - disturbedSum / 2
            if delta < threshold:
                node.results = self.get_unique_counts(totalResults)
    
    def get_branch(self, value, node):
        branch = None
        if isinstance(value, int) or isinstance(value, float):
            if value >= node.judgeValue:
                branch = node.nodes[0]
            else:
                branch = node.nodes[1]
        else:
            if value == node.judgeValue:
                branch = node.nodes[0]
            else:
                branch = node.nodes[1]
        return branch
                   
    def divide_function(self, rows, column, value):
        return self.divide_to_numerical_and_noun(rows, column, value)
        
    def divide_to_numerical_and_noun(self, rows, column, value):
        split_function = None
        if isinstance(value, int) or isinstance(value, float):
            split_function = lambda row:row[column] >= value
        else:
            split_function = lambda row:row[column] == value
            
        trueSet = [row for row in rows if split_function(row)]
        falseSet = [row for row in rows if not split_function(row)]
        
        return [trueSet, falseSet]
    
    def get_unique_counts(self, rows):
        result = {}
        for row in rows:
            value = row[len(row) - 1]
            result.setdefault(value, 0)
            result[value] += 1
        return result