#encoding=utf-8
'''
Created on 2017/05/01
@author: crystal
'''
def read_sheet(filePath):
    lines = [line for line in file(filePath)]
    
    columnNames = lines[0].strip().split('\t')[1:]
    
    rowNames    = []
    data        = []
    for line in lines[1:]:
        items = line.strip().split('\t')
        rowNames.append(items[0])
        data.append([float(value) for value in items[1:]])
        
    return rowNames, columnNames, data