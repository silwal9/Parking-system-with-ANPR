
import cv2
import pytesseract
import argparse
import numpy as np
import imutils


def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract.exe'


def readtxt(orig):
            frame = imutils.resize(orig, width=600)
            ratio = orig.shape[1] / float(frame.shape[1])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # Noise reduction
            edged = cv2.Canny(bfilter, 30, 200)  # Edge detection

            keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(keypoints)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            location = None
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 10, True)
                if len(approx) == 4:
                    location = approx
                    break
            mask = np.zeros(gray.shape, np.uint8)
            try:
                new_image = cv2.drawContours(mask, [location], 0, 255, -1)
                new_image = cv2.bitwise_and(gray, gray, mask=mask)
                (x, y) = np.where(mask == 255)
                (x1, y1) = (np.min(x), np.min(y))
                (x2, y2) = (np.max(x), np.max(y))
                cropped_image = gray[x1:x2 + 1, y1:y2 + 1]
                cropped_image = cv2.bilateralFilter(cropped_image, 11, 17, 17)  # Noise reduction
                kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
                cropped_image = cv2.filter2D(cropped_image, ddepth=-1, kernel=kernel)
                cropped_image= imutils.resize(cropped_image,height=50)
                #cv2.imshow('Frame',cropped_image)
                key = cv2.waitKey(30)
                alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                options = "-c tessedit_char_whitelist={}".format(alphanumeric)
                options += " --psm {}".format(13)  # set
                kernel = np.ones((1, 1), np.uint8)

                reader = pytesseract.image_to_string(cropped_image, config=options)
                result = reader
                text = cleanup_text(result)
                font = cv2.FONT_HERSHEY_SIMPLEX
                res = cv2.putText(frame, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font,
                                  fontScale=1,
                                  color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                res = cv2.rectangle(frame, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
                print(text)
                return res,text
            except:
                print("error")
                return frame,0


