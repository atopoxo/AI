#encoding=utf-8
'''
Created on 2017/05/22
@author: crystal
'''

import re
import math
from unicodedata import category

class DocFilter:
    def __init__(self):
        self.features = {}
        self.categories = {}
        self.thresholds = {}
        self.get_features = self.get_words
    
    def train(self, doc, category):
        features = self.get_features(doc)
        for feature in features:
            self.increase_feature(feature, category)
        self.increate_category(category)
    
    def classify(self, doc, default = None):
        probalities = {}
        max = 0.0
        bestCategory = None
        
        for category in self.categories:
            probalities[category] = self.get_category_in_doc_probability(doc, category)
            if probalities[category] > max:
                max = probalities[category]
                bestCategory = category
        
        for category in self.categories:
            if category == bestCategory:
                continue
            if probalities[category] * self.get_threshold(bestCategory) > probalities[bestCategory]:
                return default
        return bestCategory
        
    #Pr(A|B) = Pr(B|A) x Pr(A) / Pr(B) --use set to clarify
    def get_category_in_doc_probability(self, doc, category):
        docInCategoryProbability = self.get_doc_in_category_probability(doc, category)
        categoryProbability = float(self.get_category(category)) / self.get_categories()
        docProbability = 1
        return docInCategoryProbability * categoryProbability / docProbability
        
    def get_doc_in_category_probability(self, doc, category):
        features = self.get_features(doc)
        probability = 1
        for feature in features:
            probability *= self.weighted_probability(feature, category, self.get_probability)
        return probability
    
    def weighted_probability(self, feature, category, probabilityFunction, weight = 1.0, assumedProbability = 0.5):
        basicProbability = probabilityFunction(feature, category)
        featureTotalCount = sum([self.get_feature(feature, category) for category in self.categories.keys()])
        probability = float(((weight * assumedProbability) + (featureTotalCount * basicProbability))) / (weight + featureTotalCount)
        return probability
        
    def get_probability(self, feature, category):
        if self.get_category(category) == 0:
            return 0.0
        else:
            return float(self.get_feature(feature, category)) / self.get_category(category)
        
    def get_words(self, doc):
        splitter = re.compile('\\W*')
        #splite the words from doc which i not a letter
        words = [word.lower() for word in splitter.split(doc) if len(word) > 2 and len(word) < 20]
        return dict([(word, 1) for word in words])
    
    def get_threshold(self, category):
        if category not in self.thresholds:
            return 1.0
        else:
            return self.thresholds[category]
    
    def set_threshold(self, category, value):
        self.thresholds[category] = float(value)
    
    def increase_feature(self, feature, category):
        self.features.setdefault(feature, {})
        self.features[feature].setdefault(category, 0)
        self.features[feature][category] += 1
        
    def increate_category(self, category):
        self.categories.setdefault(category, 0)
        self.categories[category] += 1
    
    def get_feature(self, feature, category):
        if feature in self.features and category in self.features[feature]:
            return self.features[feature][category]
        else:
            return 0
        
    def get_category(self, category):
        if category in self.categories:
            return self.categories[category]
        else:
            return 0
        
    def get_categories(self):
        return sum(self.categories.values())
    
    