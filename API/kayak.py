#encoding=utf-8
'''
Created on 2017/05/21
@author: crystal
'''
import time
import urllib2
import xml.dom.minidom

kayakKey = ''

def create_schedule(plans, departDate):
    sid = get_kayak_session()
    flights = {}
    
    for name in plans:
        for i in range(len(plans[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            searchId = flight_search(sid, origin, destination, departDate)
            flights[(origin, destination)] = flight_search_results(sid, searchId)
            
    return flights

def get_kayak_session():
    url = 'http://www.kayak.com/k/ident/apisession?token=%s&version=1' % kayakKey
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    sid = doc.getElementsByTagName('sid')[0].firstChild.data
    return sid

def flight_search(sid, origin, destination, departDate):
    url = 'http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' % origin
    url += '&destination=%s&depart_date=%s' % (destination, departDate)
    url += '&return_date=none&depart_time=a&return_time=a'
    url += '&travelers=1&cabin=e&action=doFlights&apimode=1'
    url += '&_sid_=%s&version=1' % (sid)
    
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    searchId = doc.getElementsByTagName('searchid')[0].firstChild.data
    
    return searchId

def flight_search_results(sid, searchId):
    def parse_price(price):
        return float(price[1:].replace(',', ''))
    
    while True:
        time.sleep(2)
        
        url ='http://www.kayak.com/s/basic/flight?'
        url +='searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchId, sid)
        doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
        
        morepending = doc.getElementsByTagName('morepending')[0].firstChild
        if morepending == None or morepending.data == 'false':
            break
        
    url = 'http://www.kayak.com/s/basic/flight?'
    url += 'searchid=%s&c=999&apimode=1&_sid_=%s&version=1' % (searchId,sid)
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    
    prices = doc.getElementsByTagName('price')
    departures = doc.getElementsByTagName('depart')
    arrivals = doc.getElementsByTagName('arrive')
    
    return zip([price.firstChild.data.split(' ')[1] for price in departures],
               [price.firstChild.data.split(' ')[1] for price in arrivals],
               [parse_price(price.firstChild.data) for price in prices])