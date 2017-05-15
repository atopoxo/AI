#encoding=utf-8
'''
Created on 2017/05/14
@author: crystal
'''

from math import tanh
from sqlite3 import dbapi2 as sqlite

class SearchNet:
    def __init__(self, dbName):
        self.dbName = dbName
        self.connection = sqlite.connect(dbName)
        
    def __del__(self):
        self.connection.close()
        
    def db_commit(self):
        self.connection.commit()
    
    def get_correlation(self, inputIdList, outputIdList):
        self.check_tables()
        self.setup_network(inputIdList, outputIdList)
        return self.feed_forward()
    
    def train_correlation(self, inputIdList, outputIdList, selectedOutputId):
        self.check_tables()
        self.check_inner_node(inputIdList, outputIdList)
        self.setup_network(inputIdList, outputIdList)
        self.feed_forward()
        targets = [0.0] * len(outputIdList)
        targets[outputIdList.index(selectedOutputId)] = 1.0
        self.back_propagate(targets)
        self.update_db()
    
    def check_tables(self):
        try:
            self.connection.execute("create table if not exists input(from_id, to_id, strength)")
            self.connection.execute("create table if not exists inner(inner_id)")
            self.connection.execute("create table if not exists output(from_id, to_id, strength)")
            self.db_commit()
        except:
            print "Initiate SearchNet data base failed!"
            
    def check_inner_node(self, inputIdList, outputIdList):
        inputIdListCount = len(inputIdList)
        if inputIdListCount <= 0 or inputIdListCount > 3:
            return None
        
        innerId = ' '.join(sorted([str(inputId) for inputId in inputIdList]))
        try:
            rowIdList = self.connection.execute("select rowid from inner where inner_id='%s'" % innerId).fetchone()
        except:
            print "Select rowid from inner where inner_id='%s' failed!" % innerId
        if rowIdList == None:
            try:
                command = self.connection.execute("insert into inner (inner_id) values('%s')" % innerId)
                rowId = command.lastrowid
                for inputId in inputIdList:
                    self.set_strength(inputId, rowId, self.INPUT_LAYER, 1.0 / inputIdListCount)
                for outputId in outputIdList:
                    self.set_strength(rowId, outputId, self.OUTPUT_LAYER, 0.1)
                self.db_commit()
            except:
                print "Set strength failed!"
    
    def setup_network(self, inputIdList, outputIdList):
        self.inputIdList = inputIdList
        self.innerIdList = self.get_inner_id_list(inputIdList, outputIdList)
        self.outputIdList = outputIdList
        
        self.inputSignal = [1.0] * len(self.inputIdList)
        self.innerSignal = [1.0] * len(self.innerIdList)
        self.outputSignal = [1.0] * len(self.outputIdList)
        
        self.inputWeights = [[self.get_strength(fromId, toId, self.INPUT_LAYER) for toId in self.innerIdList] for fromId in self.inputIdList]
        self.outputWeights = [[self.get_strength(fromId, toId, self.OUTPUT_LAYER) for toId in self.outputIdList] for fromId in self.innerIdList]
    
    def feed_forward(self):
        inputLength     = len(self.inputIdList)
        innerLength     = len(self.innerIdList)
        outputLength    = len(self.outputIdList)
        
        for i in range(inputLength):
            self.inputSignal[i] = 1.0
            
        for j in range(innerLength):
            sum = 0.0
            for i in range(inputLength):
                sum += self.inputSignal[i] * self.inputWeights[i][j]
            self.innerSignal[j] = tanh(sum)
            
        for j in range(outputLength):
            sum = 0.0
            for i in range(innerLength):
                sum += self.innerSignal[i] * self.outputWeights[i][j]
            self.outputSignal[j] = tanh(sum)
            
        return self.outputSignal
    
    def back_propagate(self, targets, ratio = 0.5):
        inputLength     = len(self.inputIdList)
        innerLength     = len(self.innerIdList)
        outputLength    = len(self.outputIdList)
        
        outputDeltas = [0.0] * outputLength
        for i in range(outputLength):
            error = targets[i] - self.outputSignal[i]
            outputDeltas[i] = self.dtanh(self.outputSignal[i]) * error
            
        innerDeltas = [0.0] * innerLength
        for i in range(innerLength):
            error = 0.0
            for j in range(outputLength):
                error += outputDeltas[j] * self.outputWeights[i][j]
            innerDeltas[i] = self.dtanh(self.innerSignal[i]) * error
            
        for i in range(innerLength):
            for j in range(outputLength):
                change = outputDeltas[j] * self.innerSignal[i]
                self.outputWeights[i][j] += ratio * change
                
        for i in range(inputLength):
            for j in range(innerLength):
                change = innerDeltas[j] * self.inputSignal[i]
                self.inputWeights[i][j] += ratio * change
    
    def update_db(self):
        inputLength     = len(self.inputIdList)
        innerLength     = len(self.innerIdList)
        outputLength    = len(self.outputIdList)
        
        for i in range(inputLength):
            for j in range(innerLength):
                self.set_strength(self.inputIdList[i], self.innerIdList[j], self.INPUT_LAYER, self.inputWeights[i][j])
                
        for i in range(innerLength):
            for j in range(outputLength):
                self.set_strength(self.innerIdList[i], self.outputIdList[j], self.OUTPUT_LAYER, self.outputWeights[i][j])
                
        self.db_commit()
        
    def get_inner_id_list(self, wordIdList, urlIdList):
        nodes = {}
        
        for wordId in wordIdList:
            innerNodes = self.connection.execute("select to_id from input where from_id=%d" % wordId)
            for innerNode in innerNodes:
                nodes[innerNode[0]] = 1
        
        for urlId in urlIdList:
            innerNodes = self.connection.execute("select from_id from output where to_id=%d" % urlId)
            for innerNode in innerNodes:
                nodes[innerNode[0]] = 1
        
        return nodes.keys()
    
    def get_strength(self, fromId, toId, layer):
        table = self.layerMap[layer]
        try:
            strengthList = self.connection.execute("select strength from %s where from_id=%d and to_id=%d" % (table, fromId, toId)).fetchone()
            if strengthList == None:
                return self.layerStrengthMap[layer]
            else:
                return strengthList[0]
        except:
            print "Select strength from %s where from_id=%d and to_id=%d failed!" % (table, fromId, toId)
        
    def set_strength(self, fromId, toId, layer, strength):
        table = self.layerMap[layer]
        try:
            rowIdList = self.connection.execute("select rowid from %s where from_id=%d and to_id=%d" % (table, fromId, toId)).fetchone()
            if rowIdList == None:
                try:
                    self.connection.execute("insert into %s (from_id, to_id, strength) values(%d, %d, %f)" % (table, fromId, toId, strength))
                except:
                    print "Insert into %s (from_id, to_id, strength) values(%d, %d, %f) failed!" % (table, fromId, toId, strength)
            else:
                rowId = rowIdList[0]
                try:
                    self.connection.execute("update %s set strength=%f where rowid=%d" % (table, strength, rowId))
                except:
                    print "Update %s set strength=%f where rowid=%d failed!" % (table, strength, rowId)
        except:
            print "Select rowid from %s where from_id=%d and to_id=%d failed!" % (table, fromId, toId)
            
    def dtanh(self, value):
        return 1.0 - value * value
            
    INPUT_LAYER     = 0
    INNER_LAYER     = 1
    OUTPUT_LAYER    = 2
    
    layerMap = {
        INPUT_LAYER : 'input',
        OUTPUT_LAYER : 'output'
    }
    
    layerStrengthMap = {
        INPUT_LAYER : -0.2,
        OUTPUT_LAYER : 0
    }