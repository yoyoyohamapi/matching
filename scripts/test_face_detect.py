import cv2
import os
import sys

dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
cascadesPath = os.path.join(dirname, 'cascades/haarcascade_frontalface_default.xml')
faceCascade = cv2.CascadeClassifier(cascadesPath)

faces = [
    '../faces/1.jpg',
    '../faces/2.jpg',
    '../faces/3.jpg',
    '../faces/4.jpg'
]

for idx, face in enumerate(faces):
    image = cv2.imread(face)
    dst = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) > 0:
        for (x,y,w,h) in faces:
            cv2.rectangle(dst, (x,y), (x+w, x+h), color=(0,255,0), thickness=5)
    cv2.imwrite('../faces/%d_result.jpg'%(idx+1), dst)
