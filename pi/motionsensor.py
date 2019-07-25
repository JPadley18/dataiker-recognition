from gpiozero import MotionSensor
from picamera import PiCamera
from picamera.array import PiRGBArray
from dotenv import load_dotenv
from datetime import datetime
import sys
import io
import time
import os
import base64
import requests
import json

import numpy as np
import cv2
import boto3

# Load .env options
load_dotenv()

# AWS Credentials
KEY_ID = os.getenv("KEY_ID")
KEY_SECRET = os.getenv("KEY_SECRET")
BUCKET_NAME = os.getenv("BUCKET_NAME")
DIRECTORY_ROOT = os.getenv("DIRECTORY_ROOT")

# Machine Learning API backend
AI_ENDPOINT = os.getenv("MODEL_ENDPOINT")

# Load the operation mode
mode = os.getenv("RUN_MODE")

# Relative Path to face cascade data
cascPath = "data/haarcascade_frontalface_default.xml"
# Declare the face classifier
faceCascade = cv2.CascadeClassifier(cascPath)

# Connect to S3
session = boto3.Session(
	aws_access_key_id=KEY_ID,
	aws_secret_access_key=KEY_SECRET
)
s3 = session.resource('s3')

CHANNEL = "FaceDetector"
MSG_MOTION = "motion"
MSG_RECOG = "recognised"
MSG_IDLE = "idle"

# Register motion sensor
sensor = MotionSensor(17)
# Register  and setup the camera
camera = PiCamera()
camera.resolution = (3280, 2464)
camera.shutter_speed = 10000
camera.rotation = 180
raw_cap = PiRGBArray(camera)

def add_to_json(timestamp, label):
	if not os.path.exists("history.json"):
		file = open("history.json", "w+")
		file.close()
		js = []
	else:
		with open("history.json", "r+") as file:
			try:
				js = json.loads(file.read())
				today = datetime.now()
				midnight = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
				js = [x for x in js if x['time'] > time.mktime(midnight.timetuple())]
			except json.decoder.JSONDecodeError:
				js = []

	with open("history.json", "w") as file:
		new_js = {
			"time": timestamp,
			"label": label
		}
		js.append(new_js)
		json.dump(js, file)

# Keep checking for motion
triggered = False
while True:
	if sensor.motion_detected:
		# Take a picture and write it to a stream
		print("Detected a new motion event")
		sys.stdout.flush()
		camera.capture(raw_cap, format='bgr')
		img = raw_cap.array

		# Find all faces in the image
		faces = faceCascade.detectMultiScale(
			img,
			scaleFactor=1.2,
			minNeighbors=5
		)

		# Extract the image data for all faces
		images = [img[y:y+h, x:x+w] for (x, y, w, h) in faces]

		print("{} faces detected".format(len(images)))
		sys.stdout.flush()

		# Upload all detected faces to S3
		for i, data in enumerate(images):
			filename = "{}-motion-{}.jpg".format(str(datetime.now()).replace(".", ":"), i).replace(" ", "-")

			if mode == "upload":
				# Re-encode the image for upload
				encoded = cv2.imencode('.jpg', data)[1].tostring()
				s3.Bucket(BUCKET_NAME).put_object(Key=DIRECTORY_ROOT + filename, Body=encoded)
			elif mode == "label":
				encoded = base64.b64encode(cv2.imencode('.jpg', data)[1].tostring()).decode("utf-8")
				data = {
					"features": {
						"img_b64": encoded
					}
				}

				response = requests.post(AI_ENDPOINT, data=json.dumps(data))
				label = list(response.json()['response'].keys())[0]
				print("I can see {}".format(label))
				if label != "non-human":
					add_to_json(time.time(), label)
			else:
				raise ValueError("'{}' is not a valid operation mode".format(mode))

		# Clear the buffer
		raw_cap.truncate(0)

		# Set the flag to prevent repeat captures
		triggered = True
	else:
		print("Sensor is inactive")
		sys.stdout.flush()
		# On no motion detected, reset the flag
		triggered = False

	if not triggered:
		time.sleep(1)
