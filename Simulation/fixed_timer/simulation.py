# FIXED TIMER SIMULATION
# Each lane gets 15s green + 3s yellow
# Statistics of vehicles and timers shown on screen

import random
import time
import threading
import pygame
import sys
import os

# Default values of signal times
defaultRed = 150
defaultYellow = 3
defaultGreen = 15
defaultMinimum = 15
defaultMaximum = 15

signals = []
noOfSignals = 4
simTime = 300       # total simulation time
L = 0 # Global variable for cycle length
global script_dir
script_dir = os.path.dirname(os.path.abspath(__file__))
timeElapsed = 0

currentGreen = 0   # Indicates which signal is green
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0   # Indicates whether yellow signal is on or off 

# Vehicle speeds
speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'rickshaw':2, 'bike':2.5}  

# Coordinates of start
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 
            'down': {0:[], 1:[], 2:[], 'crossed':0}, 
            'left': {0:[], 1:[], 2:[], 'crossed':0}, 
            'up': {0:[], 1:[], 2:[], 'crossed':0}}

vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'rickshaw', 4:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]
vehicleCountTexts = ["0", "0", "0", "0"]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
rotationAngle = 3

# Gap between vehicles
gap = 15    
gap2 = 15   

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = os.path.join(script_dir, "images", direction, vehicleClass + ".png")
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        # Positioning logic
        if(direction=='right'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='left'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction=='down'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='up'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def move(self):
        # Only keeping simplified move logic (same as before)
        if self.direction=='right':
            if(self.crossed==0 and self.x+self.currentImage.get_rect().width>stopLines[self.direction]):   
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if((self.x+self.currentImage.get_rect().width<=self.stop or self.crossed == 1 or (currentGreen==0 and currentYellow==0)) and 
               (self.index==0 or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2))):                
                self.x += self.speed  
        elif self.direction=='down':
            if(self.crossed==0 and self.y+self.currentImage.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if((self.y+self.currentImage.get_rect().height<=self.stop or self.crossed == 1 or (currentGreen==1 and currentYellow==0)) and 
               (self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2))):                
                self.y += self.speed
        elif self.direction=='left':
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and 
               (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + gap2))):                
                self.x -= self.speed  
        elif self.direction=='up':
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if((self.y>=self.stop or self.crossed == 1 or (currentGreen==3 and currentYellow==0)) and 
               (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + gap2))):                
                self.y -= self.speed

# Initialization of signals
def initialize():
    for i in range(noOfSignals):
        ts = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
        signals.append(ts)
    repeat()

# Fixed-time setTime function
def setTime():
    global L
    L = 15 * noOfSignals
    for i in range(noOfSignals):
        signals[i].green = 15

def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green>0):
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 1
    for i in range(0,3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow>0):
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0
    setTime()
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    currentGreen = nextGreen 
    nextGreen = (currentGreen+1)%noOfSignals    
    signals[nextGreen].red = signals[currentGreen].yellow+signals[currentGreen].green    
    repeat()     

def printStatus():                                                                                           
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                print(" GREEN TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
            else:
                print("YELLOW TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
        else:
            print("   RED TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
    print()

def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
                signals[i].totalGreenTime+=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,4)
        lane_number = random.randint(0,2)
        will_turn = 0
        direction_number = random.randint(0,3)
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)

def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane',i+1,':',vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ',totalVehicles)
            print('Total time passed: ',timeElapsed)
            print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
            os._exit(1)
    

class Main:
    thread4 = threading.Thread(name="simulationTime",target=simulationTime, args=()) 
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization",target=initialize, args=())    
    thread2.daemon = True
    thread2.start()

    # Colours 
    global black, white
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    background = pygame.image.load(os.path.join(script_dir, 'images', 'mod_int.png'))

    global screen
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'red.png'))
    yellowSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'yellow.png'))
    greenSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'green.png'))
    global font
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background,(0,0))   

        for i in range(0,noOfSignals):  
            if(i==currentGreen):
                if(currentYellow==1):
                    screen.blit(yellowSignal, signalCoods[i])
                    signals[i].signalText = signals[i].yellow if signals[i].yellow>0 else "STOP"
                else:
                    screen.blit(greenSignal, signalCoods[i])
                    signals[i].signalText = signals[i].green if signals[i].green>0 else "SLOW"
            else: 
                screen.blit(redSignal, signalCoods[i])
                signals[i].signalText = str(signals[i].red)

        signalTexts = ["","","",""]
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i]) 
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i],vehicleCountCoods[i])

        fixedTimerText = font.render("Fixed Timer: 15s each lane", True, black, white)
        screen.blit(fixedTimerText,(1100,25))

        timeElapsedText = font.render(("Time Elapsed: "+str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText,(1100,50))

        cycleLengthText = font.render(("Cycle Length (L): "+str(L)), True, black, white)
        screen.blit(cycleLengthText,(1100,75)) 

        def displayStatistics():
            totalVehicles = 0
            for i in range(noOfSignals):
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            stats_text = f"Total Vehicles Passed: {totalVehicles}"
            stats_surface = font.render(stats_text, True, black, white)
            screen.blit(stats_surface, (1100, 100))

        displayStatistics()

        for vehicle in simulation:  
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()

Main()
