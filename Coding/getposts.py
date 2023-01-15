import requests
from io import BytesIO
import zipfile
import os

# Get the zip file from the server
url = "http://localhost:5000"
response = requests.get(url)
zip_file = BytesIO(response.content)

# Extract the contents of the zip file to a directory
extract_path = os.path.dirname(os.path.realpath(__file__)) + "/ZipExtract"
with zipfile.ZipFile(zip_file) as archive:
    archive.extractall(extract_path)
