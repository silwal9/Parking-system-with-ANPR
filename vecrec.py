import cv2
import imutils
# Method 2
validVehiles = []


def vecrec(prev, cap):
    vehile = 0
    nxt=imutils.resize(prev.copy(), height=600)

    framer = imutils.resize(cap.copy(), height=600)
    frame = framer
    # extract the foreground mask
    fgMask = cv2.absdiff(nxt, framer)
    fgMask=cv2.cvtColor(fgMask,cv2.COLOR_BGR2GRAY)

    _, thresh= cv2.threshold(fgMask,50,255, cv2.THRESH_BINARY)

    #prev=framer

    # draw the reference traffic lines
    cv2.line(frame, (0, 300), (1000, 300), (0, 0, 255), 2)  # RED Line
    cv2.line(frame, (0, 200), (1000, 200), (0, 255, 0), 1)  # GREEN Offset ABOVE
    cv2.line(frame, (0, 360), (1000,360), (0, 255, 0), 1)  # GREEN Offset BELOW

    # extract the contours
    #contours, _ = cv2.findContours(fgMask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    gray = fgMask

    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # Noise reduction
    edged = cv2.Canny(bfilter, 30, 200)  # Edge detection

    contours,_ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        if cv2.contourArea(c)>100:
            continue

        x, y, w, h = cv2.boundingRect(c)

        # ignore the small contours in size
        visibleVehile = (w > 30) and (h > 30)
        if not visibleVehile:
            continue

        # remove the distraction on the road; consider only the objects on ROAD
        if y > 200:
            # draw the bounding rectangle for all contours
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            xMid = int((x + (x + w)) / 2)
            yMid = int((y + (y + h)) / 2)
            cv2.circle(frame, (xMid, yMid), 5, (0, 0, 255), 5)

            # add all valid vehiles into List Array
            validVehiles.append((xMid, yMid))
            #             cv2.waitKey(0) # debugging purpose

            for (vX, vY) in validVehiles:
                if 200 < vY < 500:  # adjust this for the frame jumping
                    vehile += 1
                    validVehiles.remove((vX, vY))

                    # debugging purpose
                    #cv2.putText(frame, 'Y : {}'.format(yMid), (x, y-20), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2)

    # show the thresh and original video
    mask= imutils.resize(edged, height=600)

    #cv2.putText(frame, 'Motion threshold: {}'.format(vehile), (0, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    #cv2.imshow('Original Video', frame)

    return vehile




