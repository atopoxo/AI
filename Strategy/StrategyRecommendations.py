#encoding=utf-8
'''
Created on 2017/04/25
@author: crystal
'''
from StrategySimilarity import *

def top_matches(prefers, person, n = 5, similarity = get_pearson_correlation):
    scores = [(similarity(prefers, person, other), other) for other in prefers if other != person]
    scores.sort()
    scores.reverse()
        
    return scores[0:n]

def get_recommendations(prefers, person, n = 5, similarity = get_pearson_correlation):
    similarityValues    = {}
    totalValues         = {}
    
    for other in prefers:
        if other == person:
            continue
        
        similarityValue = similarity(prefers, person, other)
        if similarityValue <= 0:
            continue
        
        for item in prefers[other]:
            if item in prefers[person]:
                continue
            similarityValues.setdefault(item, 0)
            similarityValues[item] += similarityValue;
            totalValues.setdefault(item, 0)
            totalValues[item] += prefers[other][item] * similarityValue
            
    rankings = [(totalValues[item] / similarityValues[item], item) for item in totalValues.keys()]
    rankings.sort()
    rankings.reverse()
        
    length = min(n, len(rankings))
    return rankings[0:length]

def transform_prefers(prefers):
    result = {}
    for person in prefers:
        for item in prefers[person]:
            result.setdefault(item, {})
            result[item][person] = prefers[person][item]
            
    return result

def calculate_similar_items(prefers, n = 10, similarity = get_euclid_correlation):
    result      = {}
    itemPrefers = transform_prefers(prefers)
    length      = len(itemPrefers)
    count       = 0
    
    for item in itemPrefers:
        count += 1
        if count % 100 == 0:
            print "%d / %d" % (count, length)
            
        scores = top_matches(itemPrefers, item, n, similarity)
        result[item] = scores
    
    return result

def get_recommend_items(prefers, matchItems, user):
    userRatings     = prefers[user]
    scores          = {}
    totalSimilarity = {} 
    rankings        = []
    
    for (item, rating) in userRatings.items():
        for (similar, matchItem) in matchItems[item]:
            if matchItem in userRatings:
                continue
            
            scores.setdefault(matchItem, 0)
            scores[matchItem] += similar * rating
            
            totalSimilarity.setdefault(matchItem, 0)
            totalSimilarity[matchItem] += similar
            
    for item, score in scores.items():
        if totalSimilarity[item] == 0:
            value = 0
        else:
            value = score / totalSimilarity[item]
        rankings.append((value, item))
    
    rankings.sort()
    rankings.reverse()
    
    return rankings