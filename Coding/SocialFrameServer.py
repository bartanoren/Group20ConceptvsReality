import zipfile
import pathlib

from flask import Flask, make_response, request
import os

import random
import string

app = Flask(__name__)

@app.route('/')
def download_file():
    #Create the zip file
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "\Posts"
    directory = pathlib.Path(dir_path)
    archive = zipfile.ZipFile(os.path.dirname(os.path.realpath(__file__)) + "\posts.zip", mode="w")
    for file_path in directory.iterdir():
        archive.write(file_path, arcname=file_path.name)
    
    archive.close()

    # Serve the file
    with open(os.path.dirname(os.path.realpath(__file__))+"\posts.zip", "rb") as f:
        data = f.read()
    response = make_response(data)
    response.headers["Content-Disposition"] = "attachment; filename=posts.zip"
    response.headers["Content-type"] = "application/zip"
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/Likes/"

    file = request.files['file']

    if file:

        # filename = ''.join(random.choices(string.ascii_letters + string.digits,
        #     k=8)) + file.filename
        # file.save(dir_path, filename)

        file_contents = file.stream.read()
        file_contents_str = file_contents.decode('utf-8')
        file_contents_str_lines = file_contents_str.split("\n")
        print(file_contents_str_lines[1])

        txt_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))+'.txt'
        with open(dir_path+txt_name, 'a') as file:
            file.write(file_contents_str_lines[1])


        return 'File: uploaded successfully'
    else:
        return 'No file was uploaded'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

