#encoding=utf-8
'''
Created on 2017/05/05
@author: crystal
'''

import re
import urllib2
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite
from bs4 import BeautifulSoup
from NNs import NNsSearchNet

ignoreWords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}

class Crawler:
    def __init__(self, dbName):
        self.dbName = dbName
        self.connection = sqlite.connect(dbName)
    
    def __del__(self):
        self.connection.close()
    
    def db_commit(self):
        self.connection.commit()
    
    def crawl(self, pages, depth = 2):
        self.check_tables()
        for i in range(depth):
            newPages = set()
            for page in pages:
                try:
                    socket = urllib2.urlopen(page)
                except:
                    print "Couldn't open %s" % page
                    continue
                
                try:
                    soup = BeautifulSoup(socket.read(), "html.parser")
                    if soup == None:
                        continue
                    self.add_index(page, soup)
                
                    links = soup('a')
                    for link in links:
                        if 'href' in dict(link.attrs):
                            url = urljoin(page, link['href'])
                            if url.find("'") != -1:
                                continue
                            url = url.split('#')[0]
                            if url[0:4] == 'http' and not self.is_indexed(url):
                                newPages.add(url)
                            linkText = self.get_text_from_html(link)
                            self.add_link(page, url, linkText)
                
                    self.db_commit()
                except:
                    print "Could not parse page %s" % page
            pages = newPages
        
    def calculate_page_rank(self, iterations = 20):
        try:
            count = self.connection.execute("select count(*) from sqlite_master where type = 'table' and name = 'page_rank'").fetchone()[0]
            if count <= 0:
                self.connection.execute("create table if not exists page_rank(url_id primary key, score)")   
                self.connection.execute("insert into page_rank select rowid, 1.0 from url_list") 
                self.db_commit()
        except:
            print "Initiate page_rank failed!" 
        
        for i in range(iterations):
            print "Iteration %d" % i
            
            try:
                toIdList = self.connection.execute("select rowid from url_list")
            except:
                print "Select rowid from url_list failed!"
            for (toId, ) in toIdList:
                urlPageRankScore = 0.15
                
                try:
                    fromIdList = self.connection.execute("select distinct from_id from link where to_id=%d" % toId)
                except:
                    print "Select distinct from_id from link where to_id=%d failed!" % toId
                for (fromId, ) in fromIdList:
                    try:
                        pageRankScore = self.connection.execute("select score from page_rank where url_id=%d" % fromId).fetchone()[0]
                    except:
                        print "Select score from page_rank where url_id=%d failed!" % fromId
                        
                    try:
                        linkCount = self.connection.execute("select count(*) from link where from_id=%d" % fromId).fetchone()[0]
                    except:
                        print "Select count(*) from link where from_id=%d failed!" % fromId
                        
                    urlPageRankScore += 0.85 * (float(pageRankScore) / linkCount)
                    
                    try:
                        self.connection.execute("update page_rank set score=%f where url_id=%d" % (urlPageRankScore, toId))
                    except:
                        print "Update page_rank set score=%f where url_id=%d failed!" % (urlPageRankScore, toId)
                self.db_commit()
        
    def check_tables(self):
        try:
            self.connection.execute('create table if not exists url_list(url)')
            self.connection.execute('create index if not exists I_URL on url_list(url)')
            self.connection.execute('create table if not exists word_list(word)')
            self.connection.execute('create index if not exists I_WORD on word_list(word)')
            self.connection.execute('create table if not exists word_location(url_id, word_id, location)')
            self.connection.execute('create index if not exists I_WORD_URL on word_location(word_id)')
            self.connection.execute('create table if not exists link(from_id integer, to_id integer)')
            self.connection.execute('create index if not exists I_URL_TO on link(to_id)')
            self.connection.execute('create index if not exists I_URL_FROM on link(from_id)')
            self.connection.execute('create table if not exists link_words(link_id, word_id)')
            self.db_commit()
        except:
            print "Check table failed!"
        
    def add_index(self, url, soup):
        if self.is_indexed(url):
            return
        
        print 'Indexing %s' % url
        
        text = self.get_text_from_html(soup)
        words = self.separate_words(text)
        
        urlId = self.get_entry_id('url_list', 'url', url)
        
        for i in range(len(words)):
            word = words[i]
            if word in ignoreWords:
                continue
            wordId = self.get_entry_id('word_list', 'word', word)
            try:
                self.connection.execute("insert into word_location(url_id, word_id, location) values (%d, %d, %d)" % (urlId, wordId, i))
            except:
                print "insert into word_location(url_id, word_id, location) values (%d, %d, %d) failed!" % (urlId, wordId, i)
         
    def add_link(self, urlFrom, urlTo, linkText):
        words = self.separate_words(linkText)
        fromId = self.get_entry_id('url_list', 'url', urlFrom)
        toId = self.get_entry_id('url_list', 'url', urlTo)
        if fromId == toId:
            return
        try:
            command = self.connection.execute("insert into link(from_id, to_id) values (%d, %d)" % (fromId, toId))
        except:
            print "insert into link(from_id, to_id) values (%d, %d) failed!" % (fromId, toId)  
        linkId = command.lastrowid
        
        for word in words:
            if word in ignoreWords:
                continue
            wordId = self.get_entry_id('word_list', 'word', word)
            try:
                self.connection.execute("insert into link_words(link_id, word_id) values (%d, %d)" % (linkId, wordId))
            except:
                print "insert into link_words(link_id, word_id) values (%d, %d) failed!" % (linkId, wordId)
               
    def is_indexed(self, url):
        result = False
        try:
            urls = self.connection.execute("select rowid from url_list where url='%s'" % url).fetchone()
            if urls != None:
                words = self.connection.execute('select * from word_location where url_id=%d' % urls[0]).fetchone()
                if words != None:
                    result = True
        except:
            print "select row_id from url_list error!"
            
        return result
    
    def get_text_from_html(self, soup):
        text = ''
        value = soup.string
        if value == None:
            contents = soup.contents
            for content in contents:
                temp = self.get_text_from_html(content)
                text += temp + '\n'
        else:
            text = value.strip()
        
        return text
    
    def separate_words(self, text):
        splitter = re.compile('\\W*')
        
        return [value.lower() for value in splitter.split(text) if value != '']
    
    def get_entry_id(self, table, field, value, createNew = True):
        result = None
        try:
            command = self.connection.execute("select rowid from %s where %s='%s'" % (table, field, value))
            resource = command.fetchone()
            if resource == None:
                command = self.connection.execute("insert into %s (%s) values ('%s')" % (table, field, value))
                result = command.lastrowid
            else:
                result = resource[0]
        except:
            print "select rowid from %s where %s='%s' error!" % (table, field, value)
            
        return result
            
class Searcher:
    def __init__(self, dbName):
        self.dbName = dbName
        self.connection = sqlite.connect(dbName)
        
    def __del__(self):
        self.connection.close()
    
    def query(self, queryMessage, length = 10):
        rows, wordIdList = self.get_match_rows(queryMessage)
        scores = self.get_scored_list(rows, wordIdList)
        rankedScores = sorted([(score, urlId) for (urlId, score) in scores.items()], reverse = 1)
        
        return rankedScores[0:length]
    
    def output_query(self, queryMessage, length = 10):
        rankedScores = self.query(queryMessage, length)
        for (score, urlId) in rankedScores:
            print '%f\t%s' % (score, self.get_url_name(urlId))
        
    def get_match_rows(self, query):
        fieldList = 'w0.url_id'
        tableList = ''
        clauseList = ''
        wordIdList = []
        
        words = query.split(' ')
        tableNumber = 0
        
        for word in words:
            try:
                row = self.connection.execute("select rowid from word_list where word='%s'" % word).fetchone()
            except:
                print "select rowid from word_list where word='%s' fetchone failed!" % word
            if row != None:
                wordId = row[0]
                wordIdList.append(wordId)
                
                if tableNumber > 0:
                    tableList += ','
                    clauseList += ' and '
                    clauseList += 'w%d.url_id=w%d.url_id and ' % (tableNumber - 1, tableNumber)
                fieldList += ',w%d.location' % tableNumber
                tableList += 'word_location w%d' % tableNumber
                clauseList += 'w%d.word_id=%d' % (tableNumber, wordId)
                tableNumber += 1
        
        finalQuery = 'select %s from %s where %s' % (fieldList, tableList, clauseList)
        result = self.connection.execute(finalQuery)
        rows = [row for row in result]
        
        return rows, wordIdList
        
    def get_url_name(self, id):
        try:
            result = self.connection.execute("select url from url_list where rowid=%d" % id).fetchone()[0]
        except:
            print "select url from url_list where rowid=%d fetchone failed!" % id
        
        return result
    
    def get_scored_list(self, rows, wordIdList):
        totalScores = dict([(row[0], 0) for row in rows])
        
        weights = [(1.0, self.words_frequency_score(rows)),
                   (1.0, self.words_location_score(rows)),
                   (1.0, self.words_distance_score(rows)),
                   (1.0, self.link_count_score(rows)),
                   (1.0, self.page_rank_score(rows)),
                   (1.0, self.link_text_score(rows, wordIdList)),
                   (6.0, self.train_score(rows, wordIdList))]
        
        for (weight, scores) in weights:
            for url in totalScores:
                totalScores[url] += weight * scores[url] 
                
        return totalScores
    
    def words_frequency_score(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        
        for row in rows:
            counts[row[0]] += 1
        
        return self.normalize_scores(counts)
    
    def words_location_score(self, rows):
        locations = dict([(row[0], -1) for row in rows])
        
        for row in rows:
            localDistance = sum(row[1:])
            if localDistance < locations[row[0]] or locations[row[0]] == -1:
                locations[row[0]] = localDistance
                
        return self.normalize_scores(locations, smallIsBetter = 1)
    
    def words_distance_score(self, rows):
        if len(rows[0]) <= 2:
            return dict([(row[0], 1.0) for row in rows])
        urlWordsDistance = dict([(row[0], -1) for row in rows])
        for row in rows:
            distance = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if distance < urlWordsDistance[row[0]] or urlWordsDistance[row[0]] == -1:
                urlWordsDistance[row[0]] = distance
        
        return self.normalize_scores(urlWordsDistance, smallIsBetter = 1)
    
    def link_count_score(self, rows):
        uniqueUrlIdList = set([row[0] for row in rows])
        linkCounts = dict([(urlId, self.connection.execute("select count(*) from link where to_id=%d" % urlId).fetchone()[0]) for urlId in uniqueUrlIdList])
        
        return self.normalize_scores(linkCounts)
    
    def page_rank_score(self, rows):
        try:
            count = self.connection.execute("select count(*) from sqlite_master where type = 'table' and name = 'page_rank'").fetchone()[0]
            if count <= 0:
                crawler = Crawler(self.dbName)
                crawler.calculate_page_rank(iterations = 5)
        except:
            print "Initiate page_rank failed!"
        
        try:
            pageRanks = dict([(row[0], self.connection.execute("select score from page_rank where url_id=%d" % row[0]).fetchone()[0]) for row in rows])
            return self.normalize_scores(pageRanks)
        except:
            print "Select score from page_rank execute failed!"
            
    def link_text_score(self, rows, wordIdList):
        linkScores = dict([(row[0], 0) for row in rows])
        
        for wordId in wordIdList:
            urlPairs = self.connection.execute("select link.from_id, link.to_id from link_words, link where link_words.word_id=%d and link_words.link_id=link.rowid" % wordId)
            for (fromId, toId) in urlPairs:
                if toId not in linkScores:
                    continue
                try:
                    pageRankScore = self.connection.execute("select score from page_rank where url_id=%d" % fromId).fetchone()[0]
                    linkScores[toId] += pageRankScore
                except:
                    print "Select score from page_rank where url_id=%d failed!" % fromId
        
        return self.normalize_scores(linkScores)
    
    def train_score(self, rows, wordIdList):
        currentNNsSearchNet = NNsSearchNet.SearchNet('NeuralNetworks.db')
        urlIdList = [urlId for urlId in set([row[0] for row in rows])]
        correlations = currentNNsSearchNet.get_correlation(wordIdList, urlIdList)
        scores = dict([(urlIdList[i], correlations[i]) for i in range(len(urlIdList))])
        return self.normalize_scores(scores)
    
    def normalize_scores(self, scores, smallIsBetter = 0):
        eps = 0.00001
        if smallIsBetter:
            minScore = min(scores.values())
            return dict([(urlId, float(minScore) / max(eps, score)) for (urlId, score) in scores.items()])
        else:
            maxScore = max(scores.values())
            if maxScore == 0:
                maxScore = eps
            return dict([(urlId, float(score) / maxScore) for (urlId, score) in scores.items()])
