import cv2
import numpy as np
from tracker import*
import cvzone
import time
import csv
import pymysql
import schedule
import subprocess

# Параметры подключения к БД
host = '127.0.0.1'
port = 3306
user = 'mysql'
password = 'mysql'
database = 'twobd'
#rtsp://admin:admin@192.168.1.38:554/11
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=140)
video_capture = cv2.VideoCapture("rtsp://admin:02272001kir@192.168.1.51:554")

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        point = [x, y]
        print(point)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)
tracker = Tracker()

area2 = [(261, 11), (331, 13), (461, 486), (401, 484)]
area1 = [(193, 9), (252, 13), (390, 490), (332, 486)]

er = {}
counter1 = []
ex = {}
counter2 = []

def send_data():
    subprocess.run(["python", "sender.py"])

while True:

    ret, frame = video_capture.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1028, 500))

    mask = bg_subtractor.apply(frame)
    _, mask = cv2.threshold(mask, 245, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    list = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1500:
           x, y, w, h = cv2.boundingRect(cnt)
           list.append([x, y, w, h])

    bbox_idx = tracker.update(list)

    for bbox in bbox_idx:
        x1, y1, x2, y2, id = bbox
        cx = int(x1 + x1 + x2) // 2
        cy = int(y1 + y1 + y2) // 2
        result = cv2.pointPolygonTest(np.array(area1, np.int32), ((cx, cy)), False)

        if result >= 0:
            er[id] = (cx, cy)
            con = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

            with con.cursor() as cursor:
                in_time = time.strftime("%Y-%m-%d/%H:%M:%S")
                cursor.execute("INSERT INTO users(move_in, in_time) VALUES (%s, %s)", (Enter, in_time))
                con.commit()

        if id in er:
            result1 = cv2.pointPolygonTest(np.array(area2, np.int32), ((cx, cy)), False)

            if result1 >= 0:
                cv2.rectangle(frame, (x1, y1), (x2 + x1, y2 + y1), (0, 255, 0), 3)
                cvzone.putTextRect(frame, f'{id}', (cx, cy), 2, 2)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                if counter1.count(id) == 0:
                    counter1.append(id)

        result2 = cv2.pointPolygonTest(np.array(area2, np.int32), ((cx, cy)), False)

        if result2 >= 0:
            ex[id] = (cx, cy)
            con = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

            with con.cursor() as cursor:
                out_time = time.strftime("%Y-%m-%d/%H:%M:%S")
                cursor.execute("INSERT INTO users(move_out, out_time) VALUES (%s, %s)", (Enter, out_time))
                con.commit()

        if id in ex:
            result3 = cv2.pointPolygonTest(np.array(area1, np.int32), ((cx, cy)), False)

            if result3 >= 0:
                cv2.rectangle(frame, (x1, y1), (x2 + x1, y2 + y1), (0, 0, 255), 3)
                cvzone.putTextRect(frame, f'{id}', (cx, cy), 2, 2)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                if counter2.count(id) == 0:
                    counter2.append(id)

    cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 0, 255), 2)
    cv2.polylines(frame, [np.array(area2, np.int32)], True, (0, 0, 255), 2)

    Enter = len(counter1)
    Exit = len(counter2)
    
    cvzone.putTextRect(frame, f'ENTER: {Enter}', (50, 60), 2, 2)
    cvzone.putTextRect(frame, f'EXIT: {Exit}', (50, 130), 2, 2)

    cv2.imshow('RGB', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

    # Запуск программы sender.py каждый новый месяц
    if time.strftime("%d") == '01' and time.strftime("%H:%M") == '00:00':
        send_data()

video_capture.release()
cv2.destroyAllWindows()