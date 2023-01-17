from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
from easyprocess import EasyProcess
from selenium.webdriver.common.action_chains import ActionChains

import time
import datetime
import traceback
import logging
import unicodedata


import urllib.request
import os

developmentMode = 1
EXPLICIT_WAIT_TIME = 10 #seconds
DISPLAY_RATIO = 4/3 #4:3
SCREEN_WIDTH = 600
SCREEN_HEIGHT = SCREEN_WIDTH / DISPLAY_RATIO
image_reference_dict = {}
image_reference_nr = 1

def main():
    # #Virtual display for chromium to work
    # display = Display(visible=developmentMode, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
    # display.start()

    # options = Options()
    # #specify browser is chromium instead of chrome
    # options.BinaryLocation = "/usr/bin/chromium-browser"
    # #using custom chromedriver for raspi
    # driverPath = "/usr/bin/chromedriver"
    chrome_options = Options()

    chrome_options.add_experimental_option("detach", True)
    # chrome_options.add_argument("--headless")

    #start the driver
    driver = webdriver.Chrome(ChromeDriverManager().install() ,options=chrome_options)#service=Service(driverPath)), options = options)
    driver.get("https://www.instagram.com/")
    printdev(('Instagram'))

    #accept Cookies
    cookie_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
    EC.presence_of_element_located(
        (By.XPATH, "//button[text()='Allow essential and optional cookies']")))
    cookie_btn.click()
    printdev(("cookies accepted"))


    #Login sequence
    __user_name = "iotScrapeTest@gmail.com"
    __password = "sadsadsad"

    username_input = driver.find_element(By.NAME, "username")
    username_input.clear()
    username_input.send_keys(__user_name)\

    password_input = driver.find_element(By.NAME, "password")
    password_input.clear()
    password_input.send_keys(__password)

    submit_button = driver.find_element(By.XPATH, "//div[text()='Log in']")
    submit_button.click()

    #Reject saving info for safety purposes
    not_now_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Not Now']")))
    not_now_btn.click()

    #Reject saving info for safety purposes
    try:
        not_now_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[text()='Not Now']")))
        not_now_btn.click()
    except Exception:
        printdev(('2nd popup exception'))
   

    #Go to the account page
    profile_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located((By.XPATH,
         "//div[@class='x1n2onr6']")))
    profile_btn.click()

    #Go to the following list
    following_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located((By.XPATH,
         "//div[text() = ' following']")))
    following_btn.click()
    
    #Get all the people following as a list
    following_div = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located((By.XPATH,
         "//div[@class= '_aano']")))
    
    #scroll following list
    vertical_ordinate = 100
    for i in range(10):
        print(vertical_ordinate)
        driver.execute_script("arguments[0].scrollTop = arguments[1]", following_div, vertical_ordinate)
        vertical_ordinate += 250
        time.sleep(0.4)
    
    #get the div with all following people
    following_list = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.XPATH,
        "//div[@class = '_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p  _ab9- _aba8 _abcm']")))

    #get the url to the main page of the people in a list
    following_url_list = []

    for account in following_list:
        account_link = account.find_element(By.XPATH, ".//a").get_attribute("href")
        following_url_list.append(account_link)

    #keep track of all posts in a dictionary with key as the link to the users account page
    # and values a list of tuples of source link of the post and a link to the post
    posts = {}

    #iterate over all account urls in following list
    for url in following_url_list:
        #go to the main page of the following account
        driver.get(url)

        current_user_posts = []

        #TODO: scroll to the bottom before getting all triple pics
        #get the div for triple pics
        triple_pic_divs = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.XPATH,
        "//div[@class = '_aabd _aa8k _aanf']")))

        #iterate over all triple pics (TODO: only last posted 3 pictures right now)
        i = 0
        for post in triple_pic_divs:
            # for post in triplet_elements:
            #get the source of the image
            pic_source = post.find_element(By.XPATH, ".//img").get_attribute("src")
            #get the url of the image for future reference (like liking)
            post_link = post.find_element(By.XPATH, ".//a").get_attribute("href")
            #append the tuple to the list
            current_user_posts.append((pic_source, post_link))
            i += 1
            if i == 3:
                break
        
        #add the posts to the dictionary
        posts.update({url : current_user_posts})

    
    #download all images in the dictionary
    printdev(("downloading photos"))
    for triplet in posts:
        process_list(posts[triplet], driver)

    #reset image reference nr to 1
    global image_reference_nr
    image_reference_nr = 1

    



#downloads all the pictures in a list and saves the instagram url to txt file
#list item format = (image source url, image instagram url)
def process_list(list, driver):
    global image_reference_dict
    global image_reference_nr

    for post in list:
        #TODO: idk if line below is necessary
        # image_reference_dict.update({image_reference_nr : post[1]})
        download_image(post[0], image_reference_nr)
        get_post_description(driver, post[1], image_reference_nr)
        image_reference_nr += 1

#uses the driver and visits the url of the post to get the description of the post
def get_post_description(driver, url, image_name):
    driver.get(url)

    try:
        description_span = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH,
            "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/div/li/div/div/div[2]/div[1]/span")))
        description = description_span.text
    except:
        description = ""

    save_description(image_name, description, url)


def save_description(file_name, description, post_url):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = dir_path + "/posts"
    description_clean = unicodedata.normalize('NFKD', description).encode('ascii', 'ignore').decode('utf-8')
    description_clean = description_clean.replace("\n", "")
    with open(full_path +"/" + str(file_name) + ".txt", "w") as file:
        file.write(description_clean + "\n" + post_url)
    


#downloads the image in the given url and names it image_name
def download_image(url, image_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = dir_path + "\posts\\" + str(image_name) + ".jpg"
    urllib.request.urlretrieve(url, full_path)
    
def like_post(driver, url):
    driver.get(url)

    #get the picture on link
    picture_div = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/section[1]/span[1]/button/div[2]/span")))
    
    time.sleep(1)

    picture_div.click()


#printing function which disables with development mode bool
def printdev(tuple):
    if developmentMode:
        print(tuple)

main()

