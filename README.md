# DataIker Recognition Project

Welcome to the DataIker Recognition project.

## Getting Started

This guide will walk you through all the neccessary steps to set up your own instance of this project.

### The Hardware

This project uses a [Raspberry Pi 4 Model B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) (for ours, we used the 2GB model) with the [Raspberry Pi Camera Module V2](https://www.raspberrypi.org/products/camera-module-v2/) and a [HC-SR501 PIR Motion Sensor](https://thepihut.com/products/pir-infrared-motion-sensor-hc-sr501).

You may also want to purchase a [MicroSD Card with NOOBS pre-installed](https://thepihut.com/collections/raspberry-pi-sd-cards-and-adapters/products/noobs-preinstalled-sd-card). If you would rather buy a blank SD Card, follow [this guide](https://www.raspberrypi.org/documentation/installation/noobs.md) on how to set it up yourself.

### Setting Up the Hardware

First, you will need to set up the Pi itself. [This guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/4) will walk you through the setup process with NOOBS.

#### Installing the FaceRecognition Software

You will need to install the `pi` folder of this repo on the Pi. Copy the files over to the Pi into `/home/pi/Documents/`. The `pi` folder should noiw be located in `/home/pi/Documents/dataiker-recognition/pi`. Open up the Pi's terminal and `cd` to that folder. Run `sudo chmod -x setup.sh` and then `sudo ./setup.sh` in order to install all requirements for the project.

Now that the Pi is up and running, you will need to connect the Camera and Motion Sensor. Before you do this, make sure that the Pi is __**off**__. Setup for the Camera module can be found [here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/2).

#### Setting Up the PIR

In order to set up the PIR, you will need three Female-to-Female jumper connectors. Looking at the bottom of the sensor module, the pins may or may not be labelled. In the case that they are labelled, you should see VCC, OUT and GND. In case they aren't labelled, the VCC will be the pin next to the Protection Diode. Check the diagram below to help you find the diode:

![Wiring Diagram](https://lastminuteengineers.com/wp-content/uploads/2018/06/PIR-Sensor-Pinout-with-Jumper-Setting-Sensitivity-Time-Adjustment-BISS0001-IC-Labeling-Diagram.png)

Now that you know which pins are which, you will need to connect them to the GPIO pins on the Pi.

![Pi GPIO Diagram](https://img.purch.com/gpio-pi4-final-png/w/755/aHR0cDovL21lZGlhLmJlc3RvZm1pY3JvLmNvbS9VL00vODQzNTAyL29yaWdpbmFsL0dQSU8tUGk0LUZpbmFsLnBuZw==)

Connect VCC to pin 2, OUT to pin 11 and GND to pin 6. Now you can power the Pi back on.

Once you have connected the components, run `camera_test.py` to test the camera. A five-second preview from the camera should appear. Next, run `pir_test.py` to test the motion sensor. You should see a feed of messages either reading `No Motion Detected` or `Motion Detected`. These messages should change accordingly when there is motion near the sensor. If the feed does not change, try adjusting the sensitivity potentiometer with a screwdriver on the side of the module. Once the sensor is working, you can power the Pi on again.

### Setting Up the Software

You will now need to set up the `motionsensor.py` script as a `systemd` service that will run on startup of the Pi. This will later allow you to completely disconnect displays from the Pi and still be confident that the program will start as soon as you run it. `cd` to the `pi` folder and run `sudo chmod -x service_setup.sh` and `sudo ./service_setup.sh` to set up this service.

__**NOTE: This will only work if you have placed the `pi` folder at `/home/pi/Documents/dataiker-recognition/pi`**__.

Now you will need to set up your AWS credentials and other core project settings. Run `sudo cp .env.example .env` and then `sudo nano .env` to start modifying the file. Replace all of the placeholders with the relevant information.

| Setting          | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `KEY_ID`         | Your AWS S3 Key ID                                           |
| `KEY_SECRET`     | Your AWS S3 Key Secret                                       |
| `BUCKET_NAME`    | The name of your S3 Bucket                                   |
| `DIRECTORY_ROOT` | The bucket directory where the images will be stored         |
| `MODEL_ENDPOINT` | The address of the DSS API node endpoint that the machine learning model will be deployed on. You can add this later once you have trained and deployed the model. |
| `RUN_MODE`       | The mode to run the program in. `upload` will upload images of faces to the S3 bucket for later labelling, and `label` will use `MODEL_ENDPOINT` to attempt to recognise faces that it sees. Until you have set up a trained model, this should be set to `upload`. |

Now run `sudo reboot` to reboot the Pi. Once the Pi has booted, the Facial Recognition software should be running. You can use a web browser to look at a live feed from the motion camera at `[Raspberry Pi local IP]:5000`. Any faces that are detected will be sent into the S3 Bucket under the specified directory. Now you will need to set up a webapp to label them.

### DSS Webapp

You will first need to create a new DSS project.