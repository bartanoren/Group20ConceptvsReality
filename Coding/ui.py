import pygame
import os
import sys
import time
import math
import random
import io
import shutil
import requests
from io import BytesIO
import zipfile

import RPi.GPIO as GPIO
from pygame.locals import *


pygame.init()
clock = pygame.time.Clock()
GPIO.setmode(GPIO.BOARD)
running = True

# Config constants
folderpath = os.path.dirname(os.path.realpath(__file__)) + "/Posts/"
WIDTH = 600
HEIGHT = 1024
waitTime = 3 # time in seconds that an image is shown
clockMode = False
font = pygame.font.SysFont(None, 25)
largeFont = pygame.font.SysFont(None, 100)
defaultColour = (255,255,255)
prevPin = 15
nextPin = 29
likePin = 21
modePin = 12
powerPin = 5 # Special pin that can start Pi from halted state

# Connect grounded pins to pull up resistor keeps them HIGH until pressed
GPIO.setup(prevPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(nextPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(likePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(modePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(powerPin, GPIO.IN) # No pullup assignment necessary since apparently there is a physical pull up resistor
# Button presses will be detected in the background:
GPIO.add_event_detect(prevPin, GPIO.RISING)
GPIO.add_event_detect(nextPin, GPIO.RISING)
GPIO.add_event_detect(likePin, GPIO.RISING)
GPIO.add_event_detect(modePin, GPIO.RISING)
GPIO.add_event_detect(powerPin, GPIO.RISING)

print(pygame.display.list_modes())
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

url =  "http://131.155.184.82:5000" #needs to be the servers IP

def send_like(url, txt_path):
    upload_url = url + '/upload'

    file = {'file': open(txt_path, 'rb')}
    response = requests.post(upload_url, files=file)

    print(response.text)

def send_user_info(url, username, password):
    upload_url = url+ '/upload/userinfo'

    file = io.StringIO()
    file.write(username+'\n')
    file.write(password)
    file.seek(0)
    
    response = requests.post(upload_url, files={'file': file})

    print(response.text)

    

def get_posts(url):
    # Get the zip file from the server
    response = requests.get(url)
    zip_file = BytesIO(response.content)

    # Extract the contents of the zip file to a directory
    extract_path = os.path.dirname(os.path.realpath(__file__)) + "/Posts"
    with zipfile.ZipFile(zip_file) as archive:
        archive.extractall(extract_path)

# get_posts(url)

# Write initial folder state
filenames = os.listdir(folderpath)
images = []
for filename in filenames:
    if filename.endswith(".jpg"):
        images.append(filename)
random.shuffle(images)

# Text writing prep
def show_large_text( msg, x=WIDTH//2, y=HEIGHT//2, color=defaultColour ):
    global screen
    text = largeFont.render( msg, True, color, (0, 0, 0))
    screen.blit(text, ( x, y ) )

def renderTextCenteredAt(text, font, colour, y, x=WIDTH/2, screen=screen, allowed_width=WIDTH-20):
    # first, split the text into words
    words = text.split()

    # now, construct lines out of these words
    lines = []
    while len(words) > 0:
        # get as many words as will fit within allowed_width
        line_words = []
        while len(words) > 0:
            line_words.append(words.pop(0))
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > allowed_width:
                break

        # add a line consisting of those words
        line = ' '.join(line_words)
        lines.append(line)

    # now we've split our text into lines that fit into the width, actually
    # render them

    # we'll render each line below the last, so we need to keep track of
    # the cumulative height of the lines we've rendered so far
    y_offset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2
        ty = y + y_offset

        font_surface = font.render(line, True, colour, (0,0,0))
        screen.blit(font_surface, (tx, ty))

        y_offset += fh
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
        random.shuffle(images)
        current_image_iteration = 0

    # Pick a picture from the list and display that

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
    
    renderTextCenteredAt(txt, font, defaultColour, 900)
    pygame.display.flip()
    
    timer = 0
    # Use sleep for testing without buttons
#     while timer < waitTime:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 print("Attempting exit")
#                 running = False
#                 timer = waitTime
#                 pygame.quit()
#                 sys.exit()
#         time.sleep(0.5)
#         timer += 0.5

    # Wait loop when using buttons
    while timer < waitTime:
        if GPIO.event_detected(prevPin):
            # Show previous picture
            print("Showing previous picture")
            current_image_iteration -= 2
            if current_image_iteration == -1:
                current_image_iteration = len(images) - 1
            timer = waitTime
        elif GPIO.event_detected(nextPin):
            print("Showing next picture")
            timer = waitTime
        elif GPIO.event_detected(likePin):
            # Do the liking thing
            # Add current picture to a separate "liked" folder
            # Send liked image's text to server
            # Include the liked folder in image sources
            if not images[current_image_iteration].__contains__("like"):
                timenow = str(math.floor(time.time()))
                shutil.copy(folderpath + images[current_image_iteration], folderpath + "like" + timenow + ".jpg")
                try:
                    txtPath = folderpath + images[current_image_iteration][:-4] + ".txt"
                    shutil.copy(txtPath, folderpath + "like" + timenow + ".txt")
                    send_like(url, txtPath)
                except FileNotFoundError:
                    print("Text file for liked picture not found")
                show_large_text("Liked", 10, 10)
                print("Picture liked")
            else:
                # Remove the liked instance of this picture
                print("Unliking picture")
                os.remove(folderpath + images[current_image_iteration])
                try:
                    os.remove(folderpath + images[current_image_iteration][:-4] + "txt")
                except:
                    print("No txt file to delete for unliking")
                show_large_text("Unliked", 280, 400)
                
        elif GPIO.event_detected(modePin):
            # Do the mode thing: speed change or text/no text
            if clockMode:
                timer = waitTime #End timer so image is drawn again
                current_image_iteration -= 1 #Prevent it from choosing the next image
            clockMode = not clockMode
            print("Changing mode")
        elif GPIO.event_detected(powerPin):
            print("Attempting system shutdown")
            running = False
            timer = waitTime
#             os.system("shutdown -h now")
            pygame.quit()
            sys.exit()

        if clockMode:
            show_large_text(time.strftime("%H:%M:%S"), 160, 100)
            pygame.display.flip()
        clock.tick(2) # Number means loop iterations per second
        timer += 0.5