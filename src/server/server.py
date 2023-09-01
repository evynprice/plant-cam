# server.py Flask webserver to view plant images and create videos
# Version 1.0, Sep 1, 2023
# plant-cam
# by Evyn Price me@evynprice.com
# _____________________________________________________________________________
#

from flask import Flask, request
from flask import render_template
import os
from datetime import datetime
from flask_bootstrap import Bootstrap4
from werkzeug.utils import secure_filename

app = Flask(__name__)
bootstrap = Bootstrap4(app)

def allowedFile(filename):
    allowedExtensions = {'jpg', 'png', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedExtensions

def fetchImage():
    imgDir = "./static"
    imgPath = os.path.join(imgDir, "proxy-image.jpg")
    return imgPath

@app.route("/")
def index_page():
    timestamp = datetime.now().strftime("%Y%m%d:%H%M%S")
    timestamp = datetime.now().strftime("%m-%d-%Y %H:%M")
    imgPath = fetchImage()
    return render_template('index/index.html', timestamp=timestamp, image=imgPath)

@app.route("/images")
def images_page():
    return render_template('images/index.html')

@app.route("/videos")
def videos_page():
    return render_template('videos/index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # Check if the post request has a file
        if 'file' not in request.files:
            return render_template('upload/response.html', alertType="danger", error="Invalid File: No file part.")
        file = request.files['file']
        # If user does not select file, browser will also submit an empty part without filename
        if file.filename == '':
            return render_template('upload/response.html', alertType="danger", error="Invalid File: No file was selected.")
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('./static', filename))
            return render_template('upload/response.html', alertType="success", error="Successfully uploaded file.")
        else:
            return render_template('upload/response.html', alertType="danger", error="Invalid File: Invalid file type.")
    elif request.method == 'GET':
        return render_template('upload/index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)