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


import urllib.request
import os

developmentMode = 1
EXPLICIT_WAIT_TIME = 30 #seconds
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
    not_now_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Not Now']")))
    not_now_btn.click()

    #Go to the account page
    #TODO: try to make more robust
    # profile_btn = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
    #     EC.presence_of_element_located((By.XPATH,
    #      "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[8]")))
    
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
    
    vertical_ordinate = 100
    for i in range(10):
        print(vertical_ordinate)
        driver.execute_script("arguments[0].scrollTop = arguments[1]", following_div, vertical_ordinate)
        vertical_ordinate += 250
        time.sleep(0.4)
    
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

        #iterate over all triple pics (TODO: only last posted  3 right now)
        i = 0
        for post in triple_pic_divs:

            # triplet_elements = []
            # triplet_elements.append(triplet.find_element(".//div[@class= '_aabd _aa8k _aanf'][1]"))
            # triplet_elements.append(triplet.find_element(".//div[@class= '_aabd _aa8k _aanf'][2]"))
            # triplet_elements.append(triplet.find_element(".//div[@class= '_aabd _aa8k _aanf'][3]"))

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
            #break #TODO: remove to look at all posts by the user
        
        #add the posts to the dictionary
        posts.update({url : current_user_posts})

    #close the web tab
    driver.close()
    
    #download all images in the dictionary
    for triplet in posts:
        download_list(posts[triplet])

    #TODO: implement differently later
    #reset image reference nr to 1
    global image_reference_nr
    image_reference_nr = 1



    #TODO: uncomment

    # for i in range(3):
    #     articles = get_post(driver)
    #     if articles == []:
    #         time.sleep(2)
    #         articles = get_post(driver)
            
    #     #store pictures TODO: pictures need to be stored with poster ID(sometype)
    #     picture_links = []
    #     for post in articles:
    #         try:
    #             picture_link = post.find_element(By.XPATH, ".//div[@class='_aatk']//img").get_attribute("src")
    #             printdev(("picture is: ", picture_link))
    #             download_image(picture_link)

    #             href = post.find_element(By.XPATH, ".//a").get_attribute("href")
    #             printdev(("href:  ", href))

    #             if (picture_link, href) not in picture_links:
    #                 picture_links.append((picture_link, href))
    #             else:
    #                 printdev(("Tuple already processed"))
    #         except:
    #             printdev(("Something Went wrong"))
    #         finally:
    #             printdev(("Try ended"))
    #             pass

    #     #scroll to the last picture that was processed
    #     actions = ActionChains(driver)
    #     actions.move_to_element(articles[len(articles)-1]).perform()
    #     printdev(("scroll completed"))

    #     time.sleep(2)


#downloads all the pictures in a list and saves the instagram url
#list item format = (image source url, image instagram url)
def download_list(list):
    global image_reference_dict
    global image_reference_nr

    for post in list:
        image_reference_dict.update({image_reference_nr : post[1]})
        download_image(post[0], image_reference_nr)
        image_reference_nr += 1
        


    
def download_image(url, image_name):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    full_path = dir_path + "\posts\\" + str(image_name) + ".jpg"
    urllib.request.urlretrieve(url, full_path)
    


def get_post(driver):
    #Gather posts
    #First get the div that contains all posts by class id
    post_div = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
    EC.presence_of_all_elements_located((By.XPATH, "//div[@class = '_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _abc0 _abcm']//article")))
    printdev(("post_div:  ", post_div))

    # #get all articles with posts
    # articles = post_div.find_elements(By.XPATH, ".//article")
    # printdev("articles:  ", articles)

    return post_div

#printing function which disables with development mode bool
def printdev(tuple):
    if developmentMode:
        print(tuple)

main()

