import requests
import os
import io

user_name = "iotScrapeTest@gmail.com"
password = "sadsadsad"




def send_user_info(username, password):
    upload_url = "http://localhost:5000" + '/upload/userinfo'

    file = io.StringIO()
    file.write(username+'\n')
    file.write(password)
    file.seek(0)
    response = requests.post(upload_url, files={'file': file})

    print(response.text)



    
send_user_info(user_name, password)