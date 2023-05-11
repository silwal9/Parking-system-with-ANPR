from imutils.video import VideoStream
from imutils.perspective import four_point_transform
from pytesseract import Output

import sqlite3
import cv2
import pytesseract
import argparse
import numpy as np
import imutils
from imutils import paths


def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def detect_blur_fft(image, size=60, thresh=10, vis=False):
    # grab the dimensions of the image and use the dimensions to
    # derive the center (x, y)-coordinates
    (h, w) = image.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))
    fft = np.fft.fft2(image)
    fftShift = np.fft.fftshift(fft)
    fftShift[cY - size:cY + size, cX - size:cX + size] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)
    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)
    return (mean, mean <= thresh)


pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ACER\AppData\Local\Tesseract-OCR\tesseract.exe'
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
                help="path to input directory of images")
ap.add_argument("-c", "--video", type=int, default=-1,
                help="whether using video or image")
ap.add_argument("-p", "--psm", type=int, default=7,
                help="default PSM mode for OCR'ing license plates")
ap.add_argument("-d", "--debug", type=int, default=-1,
                help="whether or not to show additional visualizations")
args = vars(ap.parse_args())

print("[INFO] opening video file...")
# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture("vid3f.mp4")
# Dataset/Test/image4.jpg


# count frames:
frameno = 0
# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video file")

# Read until video is completed
while (cap.isOpened()):

    # Capture frame-by-frame
    ret, orig = cap.read()
    if ret == True:
        frameno = frameno + 1
        frametext = "Frame. no: ({:.4f})"
        frametext = frametext.format(frameno)
        # frame = imutils.resize(orig, width=600)
        frame = orig
        ratio = orig.shape[1] / float(frame.shape[1])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (mean, blurry) = detect_blur_fft(gray, thresh=15)
        # draw whether or not the frame is blurry
        color = (0, 0, 255) if blurry else (0, 255, 0)
        text = "Blurry ({:.4f})" if blurry else "Not Blurry ({:.4f})"
        text = text.format(mean)
        cv2.putText(frame, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2)
        cv2.putText(frame, frametext, (250, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2)

        if not blurry:

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

                '''
                #skew correction:
                gray = cv2.bitwise_not(cropped_image)
                # threshold the image, setting all foreground pixels to
                # 255 and all background pixels to 0
                thresh = cv2.threshold(gray, 0, 255,
                                       cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

                coords = np.column_stack(np.where(thresh > 0))
                angle = cv2.minAreaRect(coords)[-1]
                # the `cv2.minAreaRect` function returns values in the
                # range [-90, 0); as the rectangle rotates clockwise the
                # returned angle trends to 0 -- in this special case we
                # need to add 90 degrees to the angle
                if angle < -45:
                    angle = -(90 + angle)
                # otherwise, just take the inverse of the angle to make
                # it positive
                else:
                    angle = -angle
                    # rotate the image to deskew it
                    (h, w) = image.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(cropped_image, M, (w, h),
                                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    # draw the correction angle on the image so we can validate it
                    cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle),
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # show the output image
                    print("[INFO] angle: {:.3f}".format(angle))
                    cv2.imshow("Input", cropped_image)
                    cv2.waitKey(0)
                    cv2.imshow("Rotated", rotated)
                    cv2.waitKey(0)
                '''

                alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
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
                cv2.imshow('Frame', frame)
            except:
                print("error")

        # Press Q on keyboard to exit
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break
    else:
        break

# When everything done, release
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()