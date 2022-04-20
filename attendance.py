# Attendance Tracking System
# Script to log student attendance within database
# Send report to professor of past attendance

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from gpiozero import LED
import I2C_LCD_driver
import sqlite3
from datetime import datetime
import csv

# Define Devices
reader = SimpleMFRC522()
led = LED(17, active_high = False)
blue_led = LED(27, active_high = False)
thelcd = I2C_LCD_driver.lcd()
professorID = 290781925910
rows = [['Student ID','First Name','Last Name','Date']]

#Establish connection with database
conn = sqlite3.connect('/home/pi/Project/attendance.db')
print("Databased opened")

def log_student():
	global id
	global session
	# Add student login to the database
	insert_statement = "INSERT INTO attendance (student_id, session_id, date) VALUES ("+str(id)+","+str(session)+",datetime('now'));"
	conn.execute(insert_statement)
	conn.commit()
	# Get student name that signed in to display
	select_statement = "SELECT first_name FROM students WHERE student_id="+str(id)
	student_name = conn.execute(select_statement)
	for row in student_name:
		first_name = row[0]
	print(first_name + " has been signed in")
	thelcd.lcd_clear()
	thelcd.lcd_display_string(first_name,1)
	thelcd.lcd_display_string("Signed in",2)
	led.on()
	time.sleep(3)
	# Clear message and LED
	led.off()
	thelcd.lcd_clear()

def send_report():
	global session
	import smtplib
	import subprocess
	import urllib.request

        # Configuration parameters
	gmail_user = "damonkennedypi@gmail.com"
	gmail_password = "dkennedy2"
	to = ['damonkennedy0@gmail.com']

	# This makes sure the network is up by trying to access google.com
	try:
		urllib.request.urlopen("http://www.google.com").close()
	except urllib.request.URLError:
		print("Network not up yet")
		time.sleep(1)
	else:
		print("Network connected")

	# Get the IP address, hostname and create the email message parameters.
	subject = 'Attendance Report'
	sent_from = gmail_user
	ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
	hostname = subprocess.getoutput('hostname')
	print(ip)
	tostr = ", ".join(to)
	body = "Your most recent attendance report has been generated. Download the report using the following link. http://"+ip+"/files/"+session+".csv   To view past attendance reports visit the archive at http://"+ip

	# Create the email message.
	email_text = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (sent_from, tostr, subject, body)

	# Try and send it. It will print out an error message if it can't be se$
	# most likely a firewall issue.

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com',465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text)
		server.close()
		print("Email sent!")
	except:
		print("Something went wrong")




def create_report():
	global rows
	# Search database for students within current session
	select_statement = "SELECT students.student_id, students.first_name, students.last_name,  attendance.date  FROM students INNER JOIN attendance ON students.student_id=attendance.student_id WHERE attendance.session_id="+str(session)
	student_name = conn.execute(select_statement)
	# Pull information into list
	for row in student_name:
		rows.append([row[0],row[1],row[2],row[3]])
	# Export to CSV and store on webserver
	file_name = "/var/www/html/files/"+str(session)+".csv"
	with open(file_name,"w") as output:
		writer = csv.writer(output)
		writer.writerows(rows)
	rows = [['Student ID','First Name','Last Name','Date and Time']]
	# Send report/CSV to professor
	send_report()

# Wait for pi to boot before allowing attendance sessions
thelcd.lcd_display_string("System booting",1)
time.sleep(30)
thelcd.lcd_clear()

while True:
	try:
		# Scan Badge
		id, text = reader.read()

		# Check for professor
		if id == professorID:
			# Create session id using current time
			now = datetime.now()
			session = now.strftime("%m%d%Y%H%M%S")
			# Start session
			print("Attendance will start being recorded")
			thelcd.lcd_display_string("Attendance",1)
			thelcd.lcd_display_string("Recording",2)
			blue_led.on()
			# Change ID from the professor so next loop starts
			id = 1
			time.sleep(2)
			# Esure there is a student
			while id != professorID:
				thelcd.lcd_clear()
				thelcd.lcd_display_string("Scan Badge",1)
				try:
					# Scan Badge
					id, text = reader.read()
				finally:
					pass
				# Check that it is a student and log entry
				if id != professorID:
					log_student()
			# Professor has now scanned their badge and session is complete
			print("Attendance session complete")
			thelcd.lcd_display_string("Attendance",1)
			thelcd.lcd_display_string("Complete",2)
			blue_led.off()
			# Create and send report to the assigned email
			create_report()
			time.sleep(5)
		else:
			print("Professor has not started the attendance session")
	finally:
		GPIO.cleanup()
