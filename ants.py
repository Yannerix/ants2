# Pygame шаблон - скелет для нового проекта Pygame
import pygame
import random
import numpy as np
import sys
from scipy import spatial


WIDTH = 500
HEIGHT = 500
FPS = 1
# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MIN = 10000000000
random.seed()



class Ant:
    def __init__(self, currentVert, memory, distance):
        self.memory = memory
        self.currentVert = currentVert
        self.distance = distance

currentIteration = 1
num_points = 50 # количество вершин
reserveFeromon = 20
p = 0.64
alpha = 0.5
beta = 5
bestTravel = []
vertices = (np.random.randint(500, size=(num_points, 2)))  # генерация рандомных вершин

# вычисление матрицы расстояний между вершин
matrixDistance = spatial.distance.cdist(vertices, vertices, metric='euclidean')

#создаём матрицу феромонов
feromons = np.ones((num_points, num_points))/2

#создаём список муравьёв
ants = [Ant(i, [i], 0) for i in range(num_points)]



matrixWish = np.ones((num_points, num_points))*20



def updateWish():
    global matrixWish, matrixDistance
    for i in range(num_points):
        for j in range(num_points):
            if j == i:
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
        for i in range(len(ant.memory) - 1):
            feromons[ant.memory[i]][ant.memory[i + 1]] += reserveFeromon/ant.distance

def info():
    global currentIteration, bestTravel, MIN
    mini = 1000000000
    bestT = []
    for ant in ants:
        if ant.distance < mini:
            mini = ant.distance
            a = ant.memory
            bestT = ant.memory
            """
    if mini < MIN:
        print(f"На итерации №{currentIteration} кратчайший путь составил {mini}")
        bestTravel = bestT
        print(bestTravel)
        MIN = mini
        """
    bestTravel = bestT
    MIN = mini
    currentIteration += 1

def updateAnts():
    global ants
    for ant in ants:
        ant.currentVert = ant.memory[-1]
        ant.memory = [ant.currentVert]
        ant.distance = 0
    
    
    
                
def antTravel(ant):
    #пока муравей не пройдёт все точки
    while len(ant.memory) != num_points:
        numberOfNextVertices = choiceWay(ant) #выбираем путь
        ant.memory.append(numberOfNextVertices)
        ant.currentVert = numberOfNextVertices
        ant.distance += matrixDistance[ant.memory[-2]][ant.memory[-1]]
        
        
def choiceWay(ant):
    #считаем сумму всех желаний
    sumOfWish = 0
    for i in range(num_points):
        if not i in ant.memory:
            sumOfWish += matrixWish[ant.currentVert][i]
    #Теперь работаем со случайным числом от 0 до 1 и вероятностью захотеть пойти туда-то:
    randomValue = random.random()
    probabilities = []
    for i in range(num_points):
        if not i in ant.memory:
            probabilities.append(matrixWish[ant.currentVert][i] / sumOfWish)
            if sum(probabilities) > randomValue:
                return i
    return num_points - 1
    

def find():
    updateWish()
    allAntsTravel()
    feromonUpdate()
    info()
    updateAnts()


# Создаем игру и окно
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
    find()
    FPS = 30
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if i != j:
                pygame.draw.line(screen, RED, vertices[i], vertices[j], 1)
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
    for v in vertices:
        pygame.draw.circle(screen, GREEN, 
                   v, 5)
        #string = str(k)
        #text = font.render(string, True, (0, 0, 100))
        #place = (v[0],  v[1] + 10)
        #screen.blit(text, place)
        #k += 1
        
    for i in range(len(bestTravel) - 1):
        pygame.draw.line(screen, BLUE, vertices[bestTravel[i]], vertices[bestTravel[i + 1]], 1)

    pygame.display.flip()
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            find()

pygame.quit()
