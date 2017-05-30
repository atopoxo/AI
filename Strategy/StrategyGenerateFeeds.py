#encoding=utf-8
'''
Created on 2017/04/30
@author: crystal
'''
import feedparser
import re

def get_words_count(url):
    source      = feedparser.parse(url)
    database    = {}
    
    for entry in source.entries:
        if 'summary' in entry:
            summary = entry.summary
        else:
            summary = entry.description
        
        words = get_words(entry.title + ' ' + summary)
        for word in words:
            database.setdefault(word, 0)
            database[word] += 1
    
    print "Sucess parse " + url
    
    return source.feed.title, database

def get_words(html):
    txt = re.compile(r'<[^>]+>').sub('', html)
    
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    
    lowerCaseWords = [word.lower() for word in words if word != '']
    
    return lowerCaseWords

def generate_blog_words_statistics(listFilePath = 'feedlist.txt', outputFilePath = 'blogdata.txt'):
    blogApprearanceCount    = {}
    wordsCount              = {}
    feedList                = [line for line in file(listFilePath)]
    wordList                = []
    length                  = len(feedList)
    
    for url in feedList:
        try:
            title, database = get_words_count(url)
            wordsCount[title] = database
            
            for word, count in database.items():
                blogApprearanceCount.setdefault(word, 0)
                if count > 1:
                    blogApprearanceCount[word] += 1
        except:
            print 'Failed to parse feed %s' % url
            
    for word, count in blogApprearanceCount.items():
        factor = float(count) / length
        if factor > 0.1 and factor < 0.5:
            wordList.append(word)
            
    outputFile = file(outputFilePath, 'w')
    
    outputFile.write('Blog')
    for word in wordList:
        outputFile.write('\t%s' % word)
    outputFile.write('\n')
    
    for blog, database in wordsCount.items():
        outputFile.write(blog)
        for word in wordList:
            if word in database:
                outputFile.write('\t%d' % database[word])
            else:
                outputFile.write('\t0')
        outputFile.write('\n')