# Read ID from RFID card
# Use this number as the student_id

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        id, text = reader.read()
        print("The card ID is: "+ str(id))
finally:
        GPIO.cleanup()
