#encoding=utf-8
'''
Created on 2017/05/30
@author: crystal
'''

import feedparser
import re
from SkillDocFilter import DocFilter

class FeedFilter(DocFilter):
    def __init(self):
        DocFilter.__init__(self)
    
    def read(self, feed, id = 0, default = None):
        content = feedparser.parse(feed)
        
        for entry in content['entries']:
            print
            print '-----'
            # Print the contents of the entry
            print 'Title:     '+entry['title'].encode('utf-8')
            print 'Publisher: '+entry['publisher'].encode('utf-8')
            print
            print entry['summary'].encode('utf-8')
            
            fullText = '%s\n%s\n%s' % (entry['title'], entry['publisher'], entry['summary'])
            
            print 'Guess: ' + str(self.classify(entry, id, default))
            
            category = raw_input('Enter category: ')
            self.train(entry, category)
            
    def entry_features(self, entry, length = 2):
        splitter        = re.compile('\\W*')
        titleWords      = [word.lower() for word in splitter.split(entry['title']) if len(word) > 2 and len(word) < 20]
        summaryWords    = [word.lower() for word in splitter.split(entry['summary']) if len(word) > 2 and len(word) < 20]
        features        = {}
        
        for word in titleWords:
            features['Title:' + word] = 1
        
        upperWordCount = 0
        for i in range(len(summaryWords)):
            word = summaryWords[i]
            features[word] = 1
            if word.isupper():
                upperWordCount += 1
                
            if i <= len(summaryWords) - length:
                wordGroup = ' '.join(summaryWords[i:i + length])
                features.setdefault(wordGroup, 0)
                features[wordGroup] += 1
                
        features['Publisher:' + entry['publisher']] = 1
        
        if float(upperWordCount) / len(summaryWords) > 0.3:
            features['UPPERCASE'] = 1
        
        return features