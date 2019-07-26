from picamera import PiCamera
import time

cam = PiCamera()
cam.start_preview()
time.sleep(5)
cam.stop_preview()
