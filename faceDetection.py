import cv2
import time
import datetime
import json
import threading

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

open('data/log.json', 'w').close()
with open('data/log.json','r+') as f:
    dummyDicto={"dummy":{"date": "dummyDate","time": "dummyTime"}}
    json.dump(dummyDicto,f)


subject = "Someone is at your door!"
body ="Hi User, this is your smart door bell camera system. \n someone was detected at your doorbell!!\n we encourage you to check the recordings using the app!. Below is the image of the detected person:"
sender_email = "smartdoorbell.hackrevolution@outlook.com"
receiver_email = "osamabahamaid@gmail.com"
password ="helloWorld123@"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails
context= ssl.create_default_context()


jsonIndex=1
#Sending Email to the user
def sendEmail():
    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "capture.png"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)
    text = message.as_string()

    with smtplib.SMTP("smtp.outlook.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


#Doing Json Entry of every detected face

def doEntry(dayAndTime):
   # currentTime=datetime.datetime.now().strftime("%H:%M")
    global jsonIndex

    dicToAppend={f"{jsonIndex}":{"date":f"{dayAndTime[0]}","time":f"{dayAndTime[1]}"}}
    jsonIndex +=1
    newJsonEnd=","+json.dumps(dicToAppend)[1:-1]+"}\n"

    with open("data/log.json","r+") as f:
        f.seek(0,2)
        index=f.tell()

        while not f.read().startswith('}'):
            index-=1
            f.seek(index)
        f.seek(index)
        f.write(newJsonEnd)

    # sendMeEmail=threading.Thread(target=sendEmail)
    # sendMeEmail.start()
#Capturing video from webcam


cap=cv2.VideoCapture(0)

#Loading the cascade classifier for detection of faces and bodies

faceCascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
bodyCascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

#Set-up variables for recording functionality

detection = False
isTimerStarted=False
noDetectionTime=None
dayAndTime=[]
#Recording module of OpenCv

frameSize=(int(cap.get(3)),int(cap.get(4)))
videoFormat=cv2.VideoWriter_fourcc(*"mp4v")

while True:
    #Getting the current frame

    flag,frame=cap.read()

    #Converting to a gray image for processing

    grayFrame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    #Detecting faces

    faces=faceCascade.detectMultiScale(grayFrame,1.1,5)
    bodies=bodyCascade.detectMultiScale(grayFrame,1.1,5)

    #Checking for a recognized face


    #Recording video when a face is detected

    if len(faces) > 0:
        if detection:
            isTimerStarted=False

        else:
            detection=True
            currentDay = datetime.datetime.now().strftime("%d-%m-%Y")
            currentTime = datetime.datetime.now().strftime("%H-%M-%S")
            dayAndTime.clear()
            dayAndTime.append(currentDay)
            dayAndTime.append(currentTime)
            videoRecord = cv2.VideoWriter(f"data/{dayAndTime[0]}--{dayAndTime[1]}.mp4", videoFormat, 20, frameSize)
            cv2.imwrite("capture.png", frame)
    elif detection:
        if isTimerStarted:
            if time.time()-noDetectionTime > 1:
                detection =False
                isTimerStarted=False
                videoRecord.release()
                doEntry(dayAndTime)
        else:
            isTimerStarted=True
            noDetectionTime=time.time()
    if detection:
        videoRecord.write(frame)




    # if cv2.waitKey(1)==ord('q'):
    #     open('log.json', 'w').close()
    #     with open('log.json','r+') as f:
    #         dummyDicto={"dummy":{"date": "dummyDate","time": "dummyTime"}}
    #         f.write(dummyDicto)


# Releasing resourses
cap.release()

cv2.destroyAllWindows()