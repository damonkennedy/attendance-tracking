<h1>Attendance Tracking System</h1>
<br>
<h2>Steps to get the program running</h2>
<ol>
  <li>Download files</li>
  <li>Edit script</li>
  <li>Install Nginx webserver</li>
  <li>Create database and tables</li>
  <li>Identify student ID</li>
  <li>Add students to the database</li>
  <li>Create cron entry</li>
</ol>
<br>
<h2>Details to to each of the needed steps</h2>
  
1. Download the "attendance.py" and the "read.py" scripts from this link 

2. Inside of the attendance.py script edit the email address that the report will be sent to

3. Install Nginx webserver on your pi by using the instructions from here<br> https://pimylifeup.com/raspberry-pi-nginx/  

4. Create the database my installing SQLite. To install issue the following command "sudo apt-get -y sqlite". <br>
   Create the tables by issuing the following commands <br>"sqlite3 attendance.db"<br>
   "CREATE TABLE students(student_id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL);"<br>
   "CREATE TABLE attendance(id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, session_id INTEGER, date DATETIME, FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE ON UPDATE NO ACTION);"

5. To populate the student information you must know the ID number of the badge associated with the student. Use the "read.py" script to determine the ID you will be using for a student.

6. Add students to the database using the following INSERT statement after you are in the database editor.<br>
   "sqlite3 attendance.db"<br>
   "INSERT INTO students (student_id, first_name, last_name) VALUES (1000, 'Test', 'Students');"

7. Add the following line to the end of the cron file to start the script on boot. Be sure to adjust to where your working directory is.<br>
   "sudo crontab -e"<br>
   "@reboot python3 /home/pi/Project/attendance.py >> /home/pi/logs/attendance.log"
