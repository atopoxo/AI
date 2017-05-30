#encoding=utf-8
'''
Created on 2017/05/29
@author: crystal
'''

import math

class NaiveBayes:
    def __init__(self, get_features, get_assumptions, get_feature_probability, get_assumption_probability):
        self.get_features = get_features
        self.get_assumptions = get_assumptions
        self.get_feature_probability = get_feature_probability
        self.get_assumption_probability = get_assumption_probability
        self.thresholds = {}
    
    def classify(self, item, default = None):
        probabilities     = {}
        max             = 0.0
        bestAssumption  = None
        assumptions     = self.get_assumptions()
        
        for assumption in assumptions:
            probabilities[assumption] = self.get_posterior_probability(item, assumption)
            if probabilities[assumption] > max:
                max = probabilities[assumption]
                bestAssumption = assumption
        
        for assumption in assumptions:
            if assumption == bestAssumption:
                continue
            if probabilities[assumption] * self.get_threshold(bestAssumption) > probabilities[bestAssumption]:
                return default
        return bestAssumption
    
    #Pr(A|B) = Pr(B|A) x Pr(A) / Pr(B) --use set to clarify
    def get_posterior_probability(self, item, assumption):
        conditionProbability = self.get_condition_probability(item, assumption)
        priorProbability = self.get_prior_probability(assumption)
        return conditionProbability * priorProbability
    
    def get_prior_probability(self, assumption):
        return self.get_assumption_probability(assumption)
    
    def get_condition_probability(self, item, assumption):
        features = self.get_features(item)
        probability = 1.0
        for feature in features:
            probability *= self.get_feature_probability(feature, assumption)
        return probability
    
    def get_threshold(self, assumption):
        if assumption not in self.thresholds:
            return 1.0
        else:
            return self.thresholds[assumption]
    
    def set_threshold(self, assumption, value):
        self.thresholds[assumption] = float(value)

class Fisher:
    def __init__(self, get_features, get_assumptions, get_probability, get_feature_count):
        self.get_features = get_features
        self.get_assumptions = get_assumptions
        self.get_probability = get_probability
        self.get_feature_count = get_feature_count
        self.minimums = {}
        
    def classify(self, item, default = None):
        bestAssumption  = default
        max             = 0.0
        assumptions     = self.get_assumptions()
        
        for assumption in assumptions:
            probability = self.get_fisher_probability(item, assumption)
            if probability > max and probability > self.get_minimum(assumption):
                max = probability
                bestAssumption = assumption
                
        return bestAssumption
        
    def get_fisher_probability(self, item, assumption):
        probability = 1.0
        features    = self.get_features(item)
        
        for feature in features:
            probability *= self.weighted_probability(feature, assumption)
            
        featureScore = -2 * math.log(probability)
        
        return self.invchi2(featureScore, len(features) * 2)
            
    def weighted_probability(self, feature, assumption, weight = 1.0, assumedProbability = 0.5):
        basicProbability = self.get_feature_probability(feature, assumption)
        featureCount = self.get_feature_count(feature)
        probability = float(((weight * assumedProbability) + (featureCount * basicProbability))) / (weight + featureCount)
        return probability
        
    def get_feature_probability(self, feature, assumption):
        eps = 1e-8
        probability = self.get_probability(feature, assumption)
        if probability <= eps:
            return 0.0
        
        probabilitySum = sum([self.get_probability(feature, currentAssumption) for currentAssumption in self.get_assumptions()])
        return float(probability) / probabilitySum
    
    def invchi2(self, chi, df):
        m       = chi / 2.0
        sum     = math.exp(-m)
        term    = sum
        
        for i in range(1, df / 2):
            term *= m / i
            sum += term
            
        return min(sum, 1.0)
    
    def set_minimum(self, assumption, value):
        self.minimums[assumption] = value
        
    def get_minimum(self, assumption):
        if assumption not in self.minimums:
            return 0
        else:
            return self.minimums[assumption]