import pygame
import os
import sys
import time
import random
import shutil
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
# prevPin = 15
# nextPin = 28
# likePin = 21
# modePin = 12
# powerPin = 5 # Special pin that can start Pi from halted state

# Connect grounded pins to pull up resistor keeps them HIGH until pressed
# GPIO.setup(prevPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(nextPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(likePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(modePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(powerPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Button presses will be detected in the background:
# GPIO.add_event_detect(prevPin, GPIO.RISING)
# GPIO.add_event_detect(nextPin, GPIO.RISING)
# GPIO.add_event_detect(likePin, GPIO.RISING)
# GPIO.add_event_detect(modePin, GPIO.RISING)
# GPIO.add_event_detect(powerPin, GPIO.RISING)
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
url =  "http://131.155.184.82:5000" #needs to be the servers IP

def send_like(url, txt_path):
    upload_url = url + '/upload'

    file = {'file': open(txt_path, 'rb')}
    response = requests.post(url, files=file)

    print(response.text)

    

def get_posts(url):
    # Get the zip file from the server
    response = requests.get(url)
    zip_file = BytesIO(response.content)

    # Extract the contents of the zip file to a directory
    extract_path = os.path.dirname(os.path.realpath(__file__)) + "/Posts"
    with zipfile.ZipFile(zip_file) as archive:
        archive.extractall(extract_path)

get_posts(url)

# Write initial folder state
filenames = os.listdir(folderpath)
images = []
for filename in filenames:
    if filename.endswith(".jpg"):
        images.append(filename)

# Text writing prep
def show_text( msg, x=WIDTH//2, y=HEIGHT//2, color=defaultColour ):
    global screen
    text = font.render( msg, True, color, (0, 0, 0))
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
        images = random.shuffle(images)
        current_image_iteration = 0

    # Pick a picture from the list and display that
    #TODO: Then also take the text and write it over top

    img = pygame.image.load(folderpath + images[current_image_iteration])
    try:
        with open(folderpath + images[current_image_iteration][:-4] +  ".txt", 'r') as file:
            txt = file.readline().strip('\n')
    except:
        print("Loading text file failed")
        txt = ""
    current_image_iteration += 1
    if current_image_iteration == len(images):
        current_image_iteration = 0

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
    while timer < waitTime:
        if GPIO.event_detected(prevPin):
            # Show previous picture
            current_image_iteration -= 1
            if current_image_iteration == -1:
                current_image_iteration = len(images) - 1
            timer = 0
        elif GPIO.event_detected(nextPin):
            current_image_iteration += 1
            if current_image_iteration == len(images):
                current_image_iteration = 0
            timer = waitTime
        elif GPIO.event_detected(likePin):
            # Do the liking thing
            # Add current picture to a separate "liked" folder
            # Send liked image's text to server
            # Include the liked folder in image sources
            timenow = str(floor(time.time()))
            shutil.copy(folderpath + images[current_image_iteration], folderpath + "like" + timenow + ".jpg")
            try:
                shutil.copy(folderpath + images[current_image_iteration][:-4] + ".txt", folderpath + "like" + timenow + ".txt")
            except FileNotFoundError:
                print("Text file for liked picture not found")
            print("Picture liked")
        elif GPIO.event_detected(modePin):
            # Do the mode thing: speed change or text/no text
            print("Changing mode")
        elif GPIO.event_detected(powerPin):
            print("Attempting system shutdown")
            running = False
            timer = waitTime
            os.system("shutdown -h now")
            pygame.quit()
            sys.exit()
        time.sleep(0.5)
        timer += 0.5