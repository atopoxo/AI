#encoding=utf-8
'''
Created on 2017/05/22
@author: crystal
'''

import re
import math
from sqlite3 import dbapi2 as sqlite
from Strategy import StrategyProbability
from unicodedata import category

class DocFilter:
    def __init__(self):
        self.features = {}
        self.categories = {}
        self.get_features = self.get_words
        self.naiveBayes = StrategyProbability.NaiveBayes(self.get_features, self.get_categories, self.weighted_probability, self.get_category_probability)
        self.fisher = StrategyProbability.Fisher(self.get_features, self.get_categories, self.get_feature_probability, self.get_feature_total_count)
    
    def set_db(self, dbFile):
        self.connection = sqlite.connect(dbFile)
        self.connection.execute('create table if not exists feature_count(feature, category, count)')
        self.connection.execute('create table if not exists category_count(category, count)')
    
    def train(self, doc, category):
        features = self.get_features(doc)
        for feature in features:
            self.increase_feature(feature, category)
        self.increate_category(category)
        self.connection.commit()
        
    def classify(self, item, id = 0, default = None):
        if id == 0:
            return self.naiveBayes.classify(item, default)
        else:
            return self.fisher.classify(item, default)
    
    def weighted_probability(self, feature, category, weight = 1.0, assumedProbability = 0.5):
        basicProbability = self.get_feature_probability(feature, category)
        featureTotalCount = sum([self.get_feature_count(feature, currentCategory) for currentCategory in self.get_categories()])
        return float(((weight * assumedProbability) + (featureTotalCount * basicProbability))) / (weight + featureTotalCount)
        
    def get_words(self, doc):
        splitter = re.compile('\\W*')
        #splite the words from doc which i not a letter
        words = [word.lower() for word in splitter.split(doc) if len(word) > 2 and len(word) < 20]
        return dict([(word, 1) for word in words])

    def get_feature_total_count(self, feature):
        res = self.connection.execute('select sum(count) from feature_count where feature = "%s"' % (feature)).fetchone()
        if res == None:
            return 0
        else:
            return float(res[0])
    
    def get_feature_probability(self, feature, category):
        if self.get_category_count(category) == 0:
            return 0.0
        else:
            return float(self.get_feature_count(feature, category)) / self.get_category_count(category)
           
    def increase_feature(self, feature, category):
        count = self.get_feature_count(feature, category)
        if count == 0:
            self.connection.execute("insert into feature_count values('%s', '%s', 1)" % (feature, category))
        else:
            self.connection.execute("update feature_count set count = %d where feature = '%s' and category = '%s'" % (count + 1, feature, category))
        
    def get_feature_count(self, feature, category):
        res = self.connection.execute('select count from feature_count where feature = "%s" and category = "%s"' % (feature, category)).fetchone()
        if res == None:
            return 0
        else:
            return float(res[0])
    
    def get_category_total_count(self):
        res = self.connection.execute('select sum(count) from category_count').fetchone()
        if res == None:
            return 0
        else:
            return res[0]
        
    def get_categories(self):
        res = self.connection.execute('select category from category_count')
        return [currentRes[0] for currentRes in res]
    
    def get_category_probability(self, category):
        categoryValue = self.get_category_count(category)
        if categoryValue == 0:
            return 0.0
        else:
            return float(categoryValue) / self.get_category_total_count()
    
    def increate_category(self, category):
        count = self.get_category_count(category)
        if count == 0:
            self.connection.execute("insert into category_count values('%s', 1)" % (category))
        else:
            self.connection.execute("update category_count set count = %d where category = '%s'" % (count + 1, category))
            
    def get_category_count(self, category):
        res = self.connection.execute('select count from category_count where category = "%s"' % (category)).fetchone()
        if res == None:
            return 0;
        else:
            return float(res[0])