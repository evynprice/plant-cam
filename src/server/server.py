# server.py Flask webserver to view plant images and create videos
# Version 1.0, Sep 1, 2023
# plant-cam
# by Evyn Price me@evynprice.com
# _____________________________________________________________________________
#

import os
import glob
import re
import ffmpeg
from flask import Flask, request
from flask import render_template
from datetime import datetime
from flask_bootstrap import Bootstrap4
from werkzeug.utils import secure_filename

START_WEEK = datetime(2023, 8, 21)

app = Flask(__name__, static_url_path='/static')
bootstrap = Bootstrap4(app)

def allowedFile(filename):
    allowedExtensions = {'jpg', 'png', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedExtensions

def fetchLatestImage():
    imageDirs = glob.glob('./static/uploads/*/*/*')
    if(len(imageDirs) == 0):
        return ''
    latestFile = ''
    while('.' not in latestFile[1:]):
        latestFile = max(imageDirs, key=os.path.getctime)
        imageDirs.pop(imageDirs.index(latestFile))
    return latestFile[1:]

def pushVideo(path):
    path = path.split('/')
    path = path[3:]
    tempPath = './temp'

    # all video
    allImages = glob.glob('./static/uploads/**/*.png', recursive=True)
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    if not os.path.exists("./static/videos/all"):
        os.makedirs("./static/videos/all")

    for file in allImages:
        fileName = file.split('/')
        fileName = fileName[len(fileName) - 1]
        os.popen(f'cp {file} ./temp/{fileName}')

    if os.path.exists("./static/videos/all/all.mp4"):
        os.remove("./static/videos/all/all.mp4")
    
    (
    ffmpeg
    .input(f'./temp/*.png', pattern_type='glob', framerate=12)
    .output("./static/videos/all/all.mp4")
    .run()
    )
    if os.path.exists("./temp"):
        for file in glob.glob('./temp/*'):
            os.remove(file)

    # Weekly video
    weekImages = glob.glob(f'./static/uploads/{path[0]}/**/*.png', recursive=True)
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    if not os.path.exists(f"./static/videos/{path[0]}"):
        os.makedirs(f"./static/videos/{path[0]}")

    for file in weekImages:
        fileName = file.split('/')
        fileName = fileName[len(fileName) - 1]
        os.popen(f'cp {file} ./temp/{fileName}')

    if os.path.exists(f"./static/videos/{path[0]}/{path[0]}.mp4"):
        os.remove(f"./static/videos/{path[0]}/{path[0]}.mp4")
    
    (
    ffmpeg
    .input(f'./temp/*.png', pattern_type='glob', framerate=6)
    .output(f"./static/videos/{path[0]}/{path[0]}.mp4")
    .run()
    )
    if os.path.exists("./temp"):
        for file in glob.glob('./temp/*'):
            os.remove(file)

    # Daily video
    uploadPath = f'./static/videos/{path[0]}/'
    if not os.path.exists(uploadPath):
        os.makedirs(uploadPath)
    if os.path.exists(uploadPath + f"{path[1]}.mp4"):
        os.remove(uploadPath + f"{path[1]}.mp4")
    (
    ffmpeg
    .input(f'./static/uploads/{path[0]}/{path[1]}/*.png', pattern_type='glob', framerate=2)
    .output(uploadPath + f"{path[1]}.mp4")
    .run()
    )

@app.route("/")
def index_page():
    imgPath = fetchLatestImage()
    imgName = imgPath.split('/')
    imgName = imgName[len(imgName)-1].split('.')
    imgName = imgName[0]
    return render_template('index/index.html', timestamp=imgName, image=imgPath)

@app.route("/images")
def images_page():
    return imagessubdir_page('', '')

@app.route("/images/<dir1>")
def imagesdir_page(dir1):
    return imagessubdir_page(dir1, '')

@app.route("/images/<dir1>/<dir2>")
def imagessubdir_page(dir1, dir2):
    if(dir1 == ''):
        dirContents = glob.glob('./static/uploads/*')
        parent = '/'
    elif(dir2 == ''):
        dirContents = glob.glob(f'./static/uploads/{dir1}/*')
        parent = f'/{dir1}'
    else:
        dirContents = glob.glob(f'./static/uploads/{dir1}/{dir2}/*')
        parent = f'/{dir1}/{dir2}'
    images = False
    for file in dirContents:
        if('.' in file[1:]):
            images = True
            break
    files = []
    if(images):
        for file in dirContents:
            file = str(file).split('/')
            file = file[len(file)-1]
            files.append(file)
        return render_template('images/images.html', parent=parent, imgs=files)
    else:
        for file in dirContents:
            file = file.split('/')
            file = file[3:]
            file = "/".join(file)
            files.append(file)
        return render_template('images/index.html', parent=parent, dirs=files)
    
@app.route("/videos")
def videos_page():
    return videossubdir_page('', '')

@app.route("/videos/<dir1>")
def videosdir_page(dir1):
    return videossubdir_page(dir1, '')

@app.route("/videos/<dir1>/<dir2>")
def videossubdir_page(dir1, dir2):
    if(dir1 == ''):
        dirContents = glob.glob('./static/videos/*')
        parent = '/'
    elif(dir2 == ''):
        dirContents = glob.glob(f'./static/videos/{dir1}/*')
        parent = f'/{dir1}'
    else:
        dirContents = glob.glob(f'./static/videos/{dir1}/{dir2}/*')
        parent = f'/{dir1}/{dir2}'
    videos = False
    for file in dirContents:
        if('.' in file[1:]):
            videos = True
            break
    files = []
    if(videos):
        for file in dirContents:
            file = str(file).split('/')
            file = file[len(file)-1]
            files.append(file)
        return render_template('videos/videos.html', parent=parent, videos=files)
    else:
        for file in dirContents:
            file = file.split('/')
            file = file[3:]
            file = "/".join(file)
            files.append(file)
        return render_template('videos/index.html', parent=parent, dirs=files)
    

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

            currenttime = datetime.now()
            timestamp = currenttime.strftime("%Y-%m-%d")
            weekNum = int((currenttime - START_WEEK).days / 7)
            week = "week-" + str(weekNum)
            path = "./static/uploads/" + week + "/" + timestamp + "/"
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path, filename))
            pushVideo(path + filename)
            return render_template('upload/response.html', alertType="success", error="Successfully uploaded file.")
        else:
            return render_template('upload/response.html', alertType="danger", error="Invalid File: Invalid file type.")
    elif request.method == 'GET':
        return render_template('upload/index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)