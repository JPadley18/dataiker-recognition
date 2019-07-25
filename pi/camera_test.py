from picamera import picamera
import time

cam = PiCamera()
cam.start_preview()
time.sleep(5)
cam.stop_preview()
