import pygame
import os
import sys
import time
import random
from pygame.locals import *

pygame.init()
running = True

# Config constants
folderpath = "/home/stijn/projects/Group20ConceptvsReality/Coding/Posts/"
WIDTH = 600
HEIGHT = 1024
font = pygame.font.SysFont(None, 25)
defaultColour = (0,0,0)

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

# Text writing prep
def show_text( msg, x=WIDTH//2, y=HEIGHT//2, color=defaultColour ):
    global screen
    text = font.render( msg, True, color)
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
    picNum = random.randint(0, len(images) - 1)
    img = pygame.image.load(folderpath + images[picNum])

    screen.fill((0,0,0))

    widthFactor = WIDTH/img.get_width()
    heightFactor = HEIGHT/img.get_height()
    if heightFactor < widthFactor:
        imgWidth = img.get_width() * heightFactor
        img = pygame.transform.smoothscale(img, (imgWidth, HEIGHT))
        xpos = WIDTH/2 - imgWidth/2
        screen.blit(img, (xpos, 0))
    else:
        imgHeight = img.get_height() * widthFactor
        img = pygame.transform.smoothscale(img, (WIDTH, imgHeight))
        ypos = HEIGHT/2 - imgHeight/2
        screen.blit(img, (0, ypos))
    
    show_text('SocialFrame', 20, 35)
    pygame.display.flip()
    time.sleep(3)