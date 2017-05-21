# -*- coding: UTF-8 –*-
'''
Created on 2017/4/25
@author: crystal
'''

from Data.DataRecommendations import critics
from Strategy import StrategyRecommendations
from Strategy import StrategySimilarity
from Strategy import StrategyGenerateFeeds
from Strategy import StrategyCluster
from Strategy import StrategyScale
from Strategy import StrategyOptimization
from Skill import SkillSearchEngine
from API import sheet
from API import pydelicious
from API import DownLoadZeboData
from API import DrawImage
import os
from NNs import NNsSearchNet
from Strategy.StrategyOptimization import schedule_cost

def print_tuple_table(values):
    column = [""]
    length = 0
    for key in values:
        for value in values[key]:
            if value[1] not in column:
                length = max(len(value[1]), length)
                column.append(value[1])
    
    length += 5
    for value in column:
        print value.rjust(length),
    print ""
       
    for key in values:
        print key.rjust(length),
        for value in column:
            if value == "":
                continue
            flag = False
            for item in values[key]:
                if item[1] == value:
                    print "%+*.3f" % (length, item[0]),
                    flag = True
                    break
            if flag == False:
                print "*".rjust(length),
        print ""
    
def load_movie_lens(path = 'I:/SVN/Repository/AI/Data/ml-100k'):
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title
        
    prefers = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefers.setdefault(user, {})
        prefers[user][movies[movieid]] = float(rating)
        
    return prefers
    
def Test():
    '''print get_euclid_correlation(critics, 'Lisa Rose', 'Gene Seymour')
    print get_pearson_correlation(critics, 'Lisa Rose', 'Gene Seymour')
    print top_matches(critics, 'Toby', n = 3)
    print get_recommendations(critics, 'Toby', n = 5)
    movies = StrategyRecommendations.transform_prefers(critics)
    print StrategyRecommendations.top_matches(movies, 'Superman Returns')
    print pydelicious.get_popular('programing')
    print_tuple_table(StrategyRecommendations.calculate_similar_items(critics))
    result = StrategyRecommendations.calculate_similar_items(critics)
    print StrategyRecommendations.get_recommend_items(critics, result, 'Toby')
    prefers = load_movie_lens()
    print StrategyRecommendations.get_recommendations(prefers, '87')[0:30]
    itemSimilar = StrategyRecommendations.calculate_similar_items(prefers, 50, StrategySimilarity.get_pearson_correlation)
    print StrategyRecommendations.get_recommend_items(prefers, itemSimilar, '87')[0:30]
    '''
    '''
    localPath = "I:/SVN/Repository/AI/Data"
    StrategyGenerateFeeds.generate_blog_words_statistics(localPath + "/feedlist.txt", localPath + "/blogdata1.txt")
    blogNames, words, data = sheet.read_sheet('I:/SVN/Repository/AI/Data/blogdata1.txt')
    rotateData = StrategyCluster.rotate_matrix(data)
    cluster = StrategyCluster.cluster_statistics(data, similarity = StrategySimilarity.get_pearson_correlation)
    StrategyCluster.draw_dendrogram(cluster, words, 'I:/SVN/Repository/AI/Data/blogCluster.jpg')
    blogNames, words, data = sheet.read_sheet('I:/SVN/Repository/AI/Data/blogdata.txt')
    k = 10
    cluster = StrategyCluster.k_cluster(data, similarity = StrategySimilarity.get_pearson_correlation, k = k)
    count = 0
    for i in range(k):
        count += len(cluster[i])
        print "The " + str(i + 1) + "th cluster!"
        print [blogNames[id] for id in cluster[i]]
        
    print count
    '''
    '''
    DownLoadZeboData.generate_data_from_zebo()
    print "Download finished!"
    '''
    '''
    wants, people, data = sheet.read_sheet('I:/SVN/Repository/AI/Data/zebo.txt')
    cluster = StrategyCluster.hierarchical_cluster(data, similarity = StrategySimilarity.get_tanimoto_correlation)
    StrategyCluster.draw_dendrogram(cluster, wants, 'I:/SVN/Repository/AI/Data/blogCluster.jpg')
    '''
    '''
    blognames, words, data = sheet.read_sheet('I:/SVN/Repository/AI/Data/blogdata.txt')
    coords = StrategyScale.multidimensional_scaling(data)
    print "Get coords finished!"
    DrawImage.draw_two_demension(coords, blognames, jpeg = 'I:/SVN/Repository/AI/Data/blogs2d.jpg')
    '''
    '''
    crawler = SkillSearchEngine.Crawler('searchindex.db')
    pages = ["http://stackoverflow.com/questions/36778189/beautifulsoup-returns-an-empty-string"]
    crawler.crawl(pages)
    '''
    '''
    e = SkillSearchEngine.Searcher('searchindex.db')
    e.output_query('python beautifulsoup', length = 10)
    '''
    '''
    crawler = SkillSearchEngine.Crawler('searchindex.db')
    crawler.calculate_page_rank()
    '''
    '''
    mynet = NNsSearchNet.SearchNet('NeuralNetworks.db')
    
    wWorld = 1
    wBank = 2
    wRiver = 3
    inputIdList = [wWorld, wBank, wRiver]
    uWorldBank = 11
    uRiver = 12
    uEarth = 13
    outputIdList = [uWorldBank, uRiver, uEarth]
    '''
    '''
    mynet.train_correlation([wWorld, wBank], outputIdList, uWorldBank)
    print mynet.get_correlation([wWorld, wBank], outputIdList)
    '''
    '''
    for i in range(30):
        mynet.train_correlation([wWorld, wBank], outputIdList, uWorldBank)
        mynet.train_correlation([wRiver, wBank], outputIdList, uRiver)
        mynet.train_correlation([wWorld], outputIdList, uEarth)
        
    print mynet.get_correlation([wWorld, wBank], outputIdList)
    print mynet.get_correlation([wRiver, wBank], outputIdList)
    print mynet.get_correlation([wBank], outputIdList)
    '''
    flights = StrategyOptimization.read_file('I:/SVN/Repository/AI/Data/schedule.txt')
    plans = {
        "Seymour" : [("BOS", "LGA"), ("LGA", "BOS")], 
        "Franny" : [("DAL", "LGA"), ("LGA", "DAL")], 
        "Zooey" : [("CAK", "LGA"), ("LGA", "CAK")], 
        "Walt" : [("MIA", "LGA"), ("LGA", "MIA")], 
        "Buddy" : [("ORD", "LGA"), ("LGA", "ORD")], 
        "Les" : [("OMA", "LGA"), ("LGA", "OMA")]
    }
    print "random_optimize"
    cost, solution = StrategyOptimization.random_optimize(flights, plans, StrategyOptimization.schedule_cost)
    print cost
    print solution
    StrategyOptimization.print_schedule(flights, plans, solution)
    
    print "hill_climb_optimize"
    cost, solution = StrategyOptimization.hill_climb_optimize(flights, plans, StrategyOptimization.schedule_cost)
    print cost
    print solution
    StrategyOptimization.print_schedule(flights, plans, solution)
    
    print "annealing_optimize"
    cost, solution = StrategyOptimization.annealing_optimize(flights, plans, StrategyOptimization.schedule_cost, temperature = 10000.0, cool = 0.99, step = 2)
    print cost
    print solution
    StrategyOptimization.print_schedule(flights, plans, solution)
    
    print "genetic_optimize"
    cost, solution = StrategyOptimization.genetic_optimize(flights, plans, StrategyOptimization.schedule_cost, populationSize = 100, elite = 0.2, mutateProbability = 0.2, step = 1, times = 100)
    print cost
    print solution
    StrategyOptimization.print_schedule(flights, plans, solution)
    
    print "Finished!"

if __name__ == '__main__':
    Test()