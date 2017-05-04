#encoding=utf-8
'''
Created on 2017/05/02
@author: crystal
'''
from BeautifulSoup import BeautifulSoup
import urllib2
import re

def generate_data_from_zebo():
    chare = re.compile(r'[!-\.$]')
    dropWords = ['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']
    itemOwners = {}
    currentUerId = 0
    
    for i in range(1, 51):
        openSource = urllib2.urlopen('http://member.zebo.com/Main?event_key=USERSEARCH&wiowiw=wiw&keyword=car&page=%d' % (i))
        soup = BeautifulSoup(openSource.read())
        for td in soup('td'):
            if ('class' in dict(td.attris) and td['class'] == 'bgverdanasmall'):
                items = [re.sub(chare, '', a.contents[0].lower()).strip() for a in td('a')]
                for item in items:
                    txt = ' '.join([word for word in item.split(' ') if word not in dropWords])
                    if len(txt) < 2:
                        continue
                    itemOwners.setdefault(txt, {})
                    itemOwners[txt][currentUerId] = 1
                currentUerId += 1
                
    out = file('zebo.txt', 'w')
    out.write('Item')
    for userId in range(0, currentUerId):
        out.write('\tU%d' % userId)
    out.write('\n')
    
    for item, owners in itemOwners.items():
        if len(owners) <= 10:
            continue
        out.write(item)
        for userId in range(0, currentUerId):
            if userId in owners:
                out.write('\t1')
            else:
                out.write('\t0')
        out.wite('\n')