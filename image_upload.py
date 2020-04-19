import os
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, jsonify

UPLOAD_FOLDER = './UPLOADS'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No image part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No image selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message' : 'Image successfully uploaded'})
		resp.status_code = 201

		prediction = predict_distance(filename)
		return prediction
	else:
		resp = jsonify({'message' : 'Allowed image types are png, jpg, jpeg'})
		resp.status_code = 400
		return resp


def predict_distance(filename):
		import math
		import cv2
		faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		img = cv2.imread('./UPLOADS/'+filename)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 20))
		l=[]
		lf=[]
		i=1
		for (x,y,w,h) in faces:
			cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
			roi_gray = gray[y:y+h, x:x+w]
			roi_color = img[y:y+h, x:x+w] 
			s=str(i)
			cv2.putText(img, s, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),2)
			i+=1
			l=[]
			l.append(x)
			l.append(y)
			lf.append(l)
			
		close_person=""
		for i in range(len(lf)):
			for j in range(i+1,len(lf)):
				print("this")
				d=math.sqrt( ((lf[j][1]-lf[i][1])**2)+((lf[j][0]-lf[i][0])**2) )
				print("P",i+1,"- P",j+1,"=",d)
				if d<150:
					close_person+="Person "+str(i+1)+" and Person "+str(j+1)+" ; "

		close_person+=" are not following social distancing "

		
		status = jsonify({"Message":close_person})
		return status

if __name__ == "__main__":
    app.run()