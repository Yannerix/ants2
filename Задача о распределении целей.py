# Pygame шаблон - скелет для нового проекта Pygame
import random
import numpy as np
import sys
from scipy import spatial
import pygame

WIDTH = 500
HEIGHT = 500
FPS = 1
# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MIN = 10000000000
random.seed()



class Ant:
    def __init__(self, currentVert, memory, memory_target, distance):
        self.memory = memory # Память муравья об использованном транспорте
        self.currentVert = currentVert #Транспорт, на котором находится муравей сейчас
        self.memory_target = memory_target # Память муравья о выбранных целях
        self.distance = distance #Массив с вероятностями поразить i-тую цель

currentIteration = 1
reserveFeromon = 20
p = 0.64
alpha = 0.5
beta = 5
types = 3
transports = {"tank" : 10, "ship" : 5, "gyro" : 3, "airplane" : 3}
targets = {"A" : 5, "B" : 10, "C" : 20, "D" : 15, "E" : 27, "F" : 5, "G" : 15}
COUNT_TRANSPORT = sum(transports.values())
COUNT_TARGETS = len(targets.values())
bestAnt = Ant(0, [0]*COUNT_TRANSPORT, [0]*COUNT_TRANSPORT, [0]*COUNT_TARGETS)
prob =           [[0.1, 0.7, 0.05, 0.35, 0.73, 0.11, 0.9],
                 [0.4, 0.2, 0.15, 0.75, 0.70, 0.05, 0.6],
                 [0.50, 0.60, 0.40, 0.35, 0.19, 0.8, 0.1],
                 [0.9, 0.9, 0.8, 0.05, 0.30, 0.40, 0.40]]

x_trans = np.array([50]*COUNT_TRANSPORT)
y_trans = np.linspace(50, 450, COUNT_TRANSPORT)
x_targ =  np.array([450]*COUNT_TARGETS)
y_targ =  np.linspace(50, 450, COUNT_TARGETS)

# вычисление матрицы расстояний между вершин


M = []
k = 0
for keys, val in transports.items():
    for i in range(val):
        M.append([1]*COUNT_TRANSPORT + prob[k])
    k += 1

for i in range(len(targets)):
    mas = []
    k = 0
    for val in transports.values():
        mas += [prob[k][i]]*val
        k += 1
    M.append(mas + [1]*COUNT_TARGETS)

matrixDistance = 1 - np.array(M)
print(matrixDistance)
                

#создаём матрицу феромонов
feromons = np.ones((COUNT_TRANSPORT + COUNT_TARGETS, COUNT_TRANSPORT + COUNT_TARGETS))/2


#создаём список муравьёв
ants = [Ant(i, [i], [], [1]*COUNT_TARGETS) for i in range(COUNT_TRANSPORT)]



matrixWish = np.ones((COUNT_TRANSPORT + COUNT_TARGETS, COUNT_TRANSPORT + COUNT_TARGETS))*20



def updateWish():
    global matrixWish, matrixDistance
    for i in range(COUNT_TRANSPORT + COUNT_TARGETS):
        for j in range(COUNT_TRANSPORT + COUNT_TARGETS):
            if j == i:
                matrixWish[i][j] = 0
            elif matrixDistance[i][j] == 0:
                matrixWish[i][j] = 0
            else:
                matrixWish[i][j] = feromons[i][j]**alpha/matrixDistance[i][j]**beta
                

def allAntsTravel():
    for ant in ants:
        antTravel(ant)
        

def feromonUpdate():
    global feromons
    #print(feromons)
    feromons = feromons*(1 - p)
    for ant in ants:
        k = 0
        d = 0
        for val in targets.values():
            d += ant.distance[k]*val
            k += 1
        feromons += reserveFeromon/d

def info():
    global currentIteration, bestAnt, MIN
    mini = 1000000000
    bestT = []
    for ant in ants:
        k = 0
        d = 0
        for val in targets.values():
            d += ant.distance[k]*val
            k += 1
        if d < mini:
            mini = d
            a = ant.memory
            bestT = ant.memory
    if mini < MIN:
        bestAnt = Ant(ant.currentVert, ant.memory, ant.memory_target, ant.distance)
        print(f"На итерации №{currentIteration} кратчайший путь составил {mini}")
        for i in range(len(bestAnt.memory)):
            print(bestAnt.memory[i] + 1, " -> ", bestAnt.memory_target[i] + 1)
        privod()
        MIN = mini
        
    currentIteration += 1

def privod():
    global bestAnt
    for targ in range(COUNT_TARGETS):
        z = {}
        print(f"Для цели #{targ + 1} надо выслать: ", end = "", sep = "")
        for i in range(COUNT_TRANSPORT):
            if targ == bestAnt.memory_target[i]:
                typ = translate(bestAnt.memory[i])
                try:
                    z[typ] += 1
                except KeyError:
                    z[typ] = 1
        for key, value in z.items():
            print(f"{value} {key}, ", end = "")
        print()

def translate(n):
    s = 0
    for key, value in transports.items():
        if n < s + value:
            return key
        else:
            s += value

        
                
            

def updateAnts():
    global ants
    for ant in ants:
        ant.currentVert = ant.memory[-1]
        ant.memory = [ant.currentVert]
        ant.distance = [1]*COUNT_TARGETS
        ant.memory_target = []
    
    
    
                
def antTravel(ant):
    #пока муравей не пройдётся по всему транспорту
    while len(ant.memory) != COUNT_TRANSPORT:
        numberOfNextTarget = choiceWay(ant) #выбираем цель
        ant.distance[numberOfNextTarget - COUNT_TRANSPORT] *= matrixDistance[ant.currentVert][numberOfNextTarget]
        ant.memory_target.append(numberOfNextTarget - COUNT_TRANSPORT)
        ant.currentVert = choiceNewStart(ant)
        ant.memory.append(ant.currentVert)
    numberOfNextTarget = choiceWay(ant)
    ant.distance[numberOfNextTarget - COUNT_TRANSPORT] *= matrixDistance[ant.currentVert][numberOfNextTarget]
    ant.memory_target.append(numberOfNextTarget - COUNT_TRANSPORT)
def choiceNewStart(ant):
    for i in range(COUNT_TRANSPORT):
        if not i in ant.memory:
            return i
            
        
def choiceWay(ant):
    #считаем сумму всех желаний
    sumOfWish = 0
    for i in range(COUNT_TARGETS + COUNT_TRANSPORT):
        if not i in ant.memory:
            sumOfWish += matrixWish[ant.currentVert][i]
    #Теперь работаем со случайным числом от 0 до 1 и вероятностью захотеть пойти туда-то:
    randomValue = random.random()
    probabilities = []
    for i in range(COUNT_TARGETS + COUNT_TRANSPORT):
        if not i in ant.memory:
            probabilities.append(matrixWish[ant.currentVert][i] / sumOfWish)
            if sum(probabilities) > randomValue:
                return i
    return COUNT_TARGETS + COUNT_TRANSPORT - 1
    

def find():
    updateWish()
    allAntsTravel()
    feromonUpdate()
    info()
    updateAnts()
    
    

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(WHITE)
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 20)

# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    #clock.tick(FPS)
    FPS = 100
    find()
    #for i in range(len(vertices)):
        #for j in range(i + 1, len(vertices)):
           # if i != j:
                #pygame.draw.line(screen, RED, vertices[i], vertices[j], 1)
                #желание
                #string = str(int(matrixWish[i][j]*10)/10)
                #text = font.render(string, True, (0, 100, 0))
                #place = (vertices[i][0]/2 + vertices[j][0]/2, vertices[i][1]/2 + vertices[j][1]/2)
                #screen.blit(text, place)
                #расстояние
                #string = str(int(matrixDistance[i][j]))
                #text = font.render(string, True, (0, 0, 100))
                #place = (vertices[i][0]/2 + vertices[j][0]/2, vertices[i][1]/2 + vertices[j][1]/2 + 10)
                #screen.blit(text, place)
    #k = 0            
    for i in range(COUNT_TRANSPORT):
        pygame.draw.circle(screen, GREEN, 
                   (x_trans[i], y_trans[i]), 5)
    for i in range(COUNT_TARGETS):
        pygame.draw.circle(screen, RED, 
                   (x_targ[i], y_targ[i]), 5)
    for i in range(COUNT_TRANSPORT):
        for j in range(COUNT_TARGETS):
            pygame.draw.line(screen, BLUE, (x_trans[i], y_trans[i]),(x_targ[j], y_targ[j]), 1)
    ant = bestAnt
    for i in range(len(ant.memory)):
        pygame.draw.line(screen, YELLOW, (x_trans[ant.memory[i]], y_trans[ant.memory[i]]),(x_targ[ant.memory_target[i]], y_targ[ant.memory_target[i]]), 1)
        #string = str(matrixDistance[ant.memory[i]][ant.memory_target[i] + COUNT_TRANSPORT])
        #text = font.render(string, True, (0, 0, 100))
        #place = (0.5*x_trans[ant.memory[i]] + x_targ[ant.memory_target[i]]*0.5,  y_trans[ant.memory[i]]*0.5 + y_targ[ant.memory_target[i]]*0.5)
        #screen.blit(text, place)

    pygame.display.flip()
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            find()

pygame.quit()
