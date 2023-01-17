import pygame
import os
import sys
import time
import random

import requests
from io import BytesIO
import zipfile

# import RPi.GPIO as GPIO
from pygame.locals import *


pygame.init()
# GPIO.setmode(GPIO.BOARD)
running = True

# Config constants
folderpath = os.path.dirname(os.path.realpath(__file__)) + "/Posts/"
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

def get_posts():
    # Get the zip file from the server
    url = "http://172.20.10.12:5000" #needs to be the servers IP
    response = requests.get(url)
    zip_file = BytesIO(response.content)

    # Extract the contents of the zip file to a directory
    extract_path = os.path.dirname(os.path.realpath(__file__)) + "/Posts"
    with zipfile.ZipFile(zip_file) as archive:
        archive.extractall(extract_path)

#get_posts()

# Write initial folder state
filenames = os.listdir(folderpath)
images = []
for filename in filenames:
    if filename.endswith(".jpg"):
        images.append(filename)

# Text writing prep
def show_text( msg, x=WIDTH//2, y=HEIGHT//2, color=defaultColour ):
    global screen
    text = font.render( msg, True, color, (0, 0, 0, 255))
    screen.blit(text, ( x, y ) )

print("Starting loop")

current_image_iteration = 0

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
        for filename in filenames:
            if filename.endswith(".jpg"):
                images.append(filename)
        
        current_image_iteration = 0

    # Pick a picture from the list and display that
    #TODO: Then also take the text and write it over top

    img = pygame.image.load(folderpath + images[current_image_iteration])
    with open(folderpath + images[current_image_iteration][:-4] +  ".txt", 'r') as file:
        txt = file.readline().strip('\n')
    current_image_iteration += 1

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
    
    show_text(txt, 35, 900)
    pygame.display.flip()
    
    timer = 0
    # Use sleep for testing without buttons
    while timer < waitTime:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Attempting exit")
                running = False
                timer = waitTime
                pygame.quit()
                sys.exit()
        time.sleep(0.5)
        timer += 0.5

    # Wait loop when using buttons
    # while timer < waitTime:
    #     if prevPushed:
    #         # Show previous picture
    #         timer = 0
    #     elif nextPushed:
    #         timer = waitTime
    #     time.sleep(0.5)
    #     timer += 0.5