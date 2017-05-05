#encoding=utf-8
'''
Created on 2017/05/05
@author: crystal
'''
class crawler:
    def __init__(self, dbName):
        pass
    
    def __del__(self):
        pass
    
    def db_commit(self):
        pass
    
    def get_entry_id(self, table, field, value, createNew = True):
        return None
    
    def add_index(self, url, soup):
        print 'Indexing %s' % url
        
    def get_text_from_html(self, soup):
        return None
    
    def separate_words(self, text):
        return None
    
    def is_indexed(self, url):
        return False
    
    def add_link(self, urlFrom, urlTo, linkText):
        pass
    
    def create_index_tables(self):
        pass