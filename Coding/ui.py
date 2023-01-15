import pygame
import os
import sys
import time
import random
# import RPi.GPIO as GPIO
from pygame.locals import *

pygame.init()
# GPIO.setmode(GPIO.BOARD)
running = True

# Config constants
folderpath = "/home/stijn/projects/Group20ConceptvsReality/Coding/Posts/"
WIDTH = 600
HEIGHT = 1024
waitTime = 3 # time in seconds that an image is shown
font = pygame.font.SysFont(None, 25)
defaultColour = (255,255,255)
# prevPin = 
# nextPin = 
# likePin = 
# modePin = 
# powerPin = 

screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

# Write initial folder state
filenames = os.listdir(folderpath)
images = []
texts = []
for filename in filenames:
    if filename.endswith(".txt"):
        texts.append(filename)
    if filename.endswith(".jpg"):
        images.append(filename)

# Write dummy history so that later we can update the history more easily
picNum = random.randint(0, len(images) - 1)
imgHistory = [images[picNum]]
picNum = random.randint(0, len(images) - 1)
imgHistory.append(images[picNum])
picNum = random.randint(0, len(images) - 1)
imgHistory.append(images[picNum])
picNum = random.randint(0, len(images) - 1)
imgHistory.append(images[picNum])

# Text writing prep
def show_text( msg, x=WIDTH//2, y=HEIGHT//2, color=defaultColour ):
    global screen
    text = font.render( msg, True, color, (0, 0, 0))
    screen.blit(text, ( x, y ) )

print("Starting loop")

# Main display loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Attempting exit")
            running = False
            pygame.quit()
            sys.exit()

    # Iterate through folder writing list of filenames if anything changed
    newFilenames = os.listdir(folderpath)
    if newFilenames != filenames:
        filenames = newFilenames
        images = []
        texts = []
        for filename in filenames:
            if filename.endswith(".txt"):
                texts.append(filename)
            if filename.endswith(".jpg"):
                images.append(filename)

    # Pick a picture from the list and display that
    #TODO: Then also take the text and write it over top

    # Make sure images aren't repeated too quickly
    noNewImg = True
    while noNewImg:
        picNum = random.randint(0, len(images) - 1)
        if imgHistory.count(images[picNum]) == 0:
            del imgHistory[0]
            imgHistory.append(images[picNum])
            img = pygame.image.load(folderpath + images[picNum])
            noNewImg = False

    screen.fill((0,0,0)) # Clear background
    # Scale and write pictures to screen
    widthFactor = WIDTH/img.get_width()
    heightFactor = HEIGHT/img.get_height()
    if heightFactor < widthFactor:
        imgWidth = round(img.get_width() * heightFactor)
        img = pygame.transform.smoothscale(img, (imgWidth, HEIGHT))
        xpos = round(WIDTH/2 - imgWidth/2)
        screen.blit(img, (xpos, 0))
    else:
        imgHeight = round(img.get_height() * widthFactor)
        img = pygame.transform.smoothscale(img, (WIDTH, imgHeight))
        ypos = round(HEIGHT/2 - imgHeight/2)
        screen.blit(img, (0, ypos))

    show_text('SocialFrame', 20, 35)
    pygame.display.flip()
    
    # Use sleep for testing without buttons
    time.sleep(waitTime)

    # Wait loop when using buttons
    # timer = 0
    # while timer < waitTime:
    #     if prevPushed:
    #         # Show previous picture
    #         timer = 0
    #     elif nextPushed:
    #         timer = waitTime
    #     time.sleep(0.5)
    #     timer += 0.5