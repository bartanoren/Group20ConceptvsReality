import zipfile
import pathlib

from flask import Flask, make_response
import os

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

if __name__ == '__main__':
    app.run(debug=True)

