"""
Inside your Raspberry Pi OS: Setup a virtual environment
$ sudo apt-get install python3-venv
$ python3 -m venv YOUR_ENVIRONMENT_NAME
$ source bin/activate // in folder
Install and upgrade camera
$ sudo apt-get update
$ sudo apt-get install python3-picamera
$ sudo apt-get upgrade
# Install Python modules
$ sudo pip3 install deepface
"""

import RPi.GPIO as GPIO
import time
from subprocess import call
import picamera
from deepface import DeepFace
from deepface.basemodels import VGGFace
import re


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    pir_pin = 7
    GPIO.setup(pir_pin, GPIO.IN)


def setup_face_recognition():
    return VGGFace.loadModel()


def check_motion(pir_pin):
    return GPIO.input(pir_pin) == 1


def switch_screen(on):
    call(["/usr/bin/vcgencmd", "display_power", "1" if on else "0"])


def take_photo(camera):
    time.sleep(0.5)
    camera.capture("database/c_shot.jpg", resize=(320, 240))


def recognize_face(model):
    df = DeepFace.find(img_path="database/c_shot.jpg", db_path="database", model=model)
    if df.shape[0] > 0:
        identity = df.iloc[0]["identity"]
        identity = identity.split("/")[-1].replace(".jpg", "")
        identity = re.sub("[0-9]", "", identity)
        return identity
    return None


def update_environment(identity):
    call(["ENVIRONMENT FOR MIRROR", "npm", "run", "start"])


def main():
    time_cycle = 15
    current_identity = "Michl"
    setup_gpio()
    model = setup_face_recognition()
    camera = picamera.PiCamera()
    try:
        while True:
            start_time = time.time()
            motion_detected = check_motion(pir_pin)
            switch_screen(motion_detected)
            if motion_detected:
                take_photo(camera)
                identity = recognize_face(model)
                if identity and identity.casefold() != current_identity.casefold():
                    current_identity = identity
                    update_environment(identity)
            time.sleep(time_cycle - (time.time() - start_time))
    except Exception as e:
        print(f"Encountered error {e}")
        GPIO.cleanup()
