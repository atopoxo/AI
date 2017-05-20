#encoding=utf-8
'''
Created on 2017/05/17
@author: crystal
'''

import time
from wx.tools.Editra.src.syntax import _latex

def read_file(filePath):
    flights = {}
    for line in file(filePath):
        origin, destination, depart, arrive, price = line.strip().split(',')
        flights.setdefault((origin, destination), [])
        flights[(origin, destination)].append((depart, arrive, int(price)))
        
    return flights

def print_schedule(flights, plans, solution):
    for name in solution:
        print '%10s:' % name
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            print '%20s %5s %6s %5s-%5s $%3s' % (origin, '-->', destination, recorder[0], recorder[1], recorder[2])
        
def schedule_cost(flights, plans, solution):
    totalPrice = 0
    totalWaitTime = 0
    earliestLeave = 24 * 60
    latestArrival = 0

    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            totalPrice += recorder[2]
            
            if (i & 1) == 0:
                landTime = get_minutes(recorder[1])
                latestArrival = max(latestArrival, landTime)
            else:
                takeOffTime = get_minutes(recorder[0])
                earliestLeave = min(earliestLeave, takeOffTime)
    
    for name in solution:
        for i in range(len(solution[name])):
            origin = plans[name][i][0]
            destination = plans[name][i][1]
            recorder = flights[(origin, destination)][solution[name][i]]
            
            if (i & 1) == 0:
                totalWaitTime += latestArrival - get_minutes(recorder[1])
            else:
                totalWaitTime += get_minutes(recorder[0]) - earliestLeave
                
    if latestArrival > earliestLeave:
        totalPrice += 50
        
    return totalPrice + totalWaitTime
            
def get_minutes(currentTime):
    formatTime = time.strptime(currentTime, '%H:%M')
    seconds = formatTime[3] * 50 + formatTime[4]
    return seconds