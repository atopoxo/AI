#encoding=utf-8
'''
Created on 2017/05/05
@author: crystal
'''

import Image
import ImageDraw

def draw_dendrogram(cluster, labels, jpeg = 'clusters.jpg'):
    height  = get_height(cluster) * 20
    width   = 1200
    depth   = get_depth(cluster)
    scale   = float(width - 150) / depth * 0.8

    picture = Image.new('RGB', (width, height), (255, 255, 255))
    draw    = ImageDraw.Draw(picture)
    
    draw.line((0, height / 2, 10, height / 2), fill = (255, 0, 0))
    
    draw_node(draw, cluster, 10, (height / 2), scale, labels)
    
    picture.save(jpeg, 'JPEG')

def get_height(cluster):
    if cluster.left == None and cluster.right == None:
        return 1
    
    return get_height(cluster.left) + get_height(cluster.right)

def get_depth(cluster):
    if cluster.left == None and cluster.right == None:
        return 0
    
    return max(get_depth(cluster.left), get_depth(cluster.right)) + cluster.distance

def draw_node(draw, cluster, x, y, scale, labels):
    if cluster.id < 0:
        heightLeft  = get_height(cluster.left) * 20
        heightRight = get_height(cluster.right) * 20
        top         = y - (heightLeft + heightRight) / 2
        bottom      = y + (heightLeft + heightRight) / 2
        lineLength  = cluster.distance * scale
        
        draw.line((x, top + heightLeft / 2, x, bottom - heightRight / 2), fill = (255, 0, 0))
        draw.line((x, top + heightLeft / 2, x + lineLength, top + heightLeft / 2), fill = (255, 0, 0))
        draw.line((x, bottom - heightRight / 2, x + lineLength, bottom - heightRight / 2), fill = (255, 0, 0))
        
        draw_node(draw, cluster.left, x + lineLength, top + heightLeft / 2, scale, labels)
        draw_node(draw, cluster.right, x + lineLength, bottom - heightRight / 2, scale, labels)
    else:
        draw.text((x + 5, y - 7), labels[cluster.id], (0, 0, 0))
    
def print_cluster(cluster, labels = None, n = 0):
    for i in range(n):
        print ' ',
    
    if cluster.id < 0:
        print '-'
    else:
        if labels == None:
            print cluster.id
        else:
            print labels[cluster.id]
    
    if cluster.left != None:
        print_cluster(cluster.left, labels = labels, n = n + 1)
    if cluster.right != None:
        print_cluster(cluster.right, labels = labels, n = n + 1)
        
def draw_two_demension(data, labels, jpeg = 'drawTwoDemension.jpg'):
    picture = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw    = ImageDraw.Draw(picture)
    
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    picture.save(jpeg, 'JPEG')
    
def draw_social_networks(solution, people, links, jpeg = 'socialNetworks.jpg'):
    picture = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw.Draw(picture)
    
    positions = dict([(people[i], (solution[i * 2], solution[i * 2 + 1])) for i in range(0, len(people))])
    
    for (a, b) in links:
        draw.line((positions[a], positions[b]), fill = (255, 0, 0))
        
    for name, position in positions.items():
        draw.text(position, name, (0, 0, 0))
        
    picture.save(jpeg, 'JPEG')