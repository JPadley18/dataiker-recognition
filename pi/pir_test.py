from gpiozero import MotionSensor
import time

sensor = MotionSensor()

while True:
	if sensor.motion_detected:
		print("Motion Detected")
	else:
		print("No Motion Detected")

	time.sleep(1)
