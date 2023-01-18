import requests
import os


url =  "http://localhost:5000" #needs to be the servers IP
url = url + '/upload'

txt_path = os.path.dirname(os.path.realpath(__file__)) + "/Posts/1.txt"

file = {'file': open(txt_path, 'rb')}
response = requests.post(url, files=file)

print(response.text)