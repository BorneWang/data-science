
import cv2


class KCF_tracker():
    def __init__(self,last_img,boxes,src):
        self.src = src
        self.tracker = cv2.MultiTracker_create()
        framePath = self.src + '/' + last_img + '.png'
        image = cv2.imread(framePath)
        im_w = image.shape[1] 
        im_h = image.shape[0]
        for bbox in boxes:
            box = [bbox[0]*im_w,bbox[1]*im_h,bbox[2]*im_w,bbox[3]*im_h]
            ok = self.tracker.add(cv2.TrackerMIL_create(), image, box)
        
    def Update(self,now_img):
        framePath = self.src + '/' + now_img + '.png'
        image = cv2.imread(framePath)
        im_w = image.shape[1]
        im_h = image.shape[0]
        ok, boxes = self.tracker.update(image)
        conv_boxes = []
        for bbox in boxes:
            box = [bbox[0]*im_w,bbox[1]*im_h,bbox[2]*im_w,bbox[3]*im_h]
            conv_boxes.append(box)
        return boxes














'''
cv2.namedWindow("tracking")
camera = cv2.VideoCapture(0)
tracker = cv2.MultiTracker_create()
init_once = False

ok, image=camera.read()
if not ok:
    print('Failed to read video')
    exit()

bbox1 = cv2.selectROI('tracking', image)
bbox2 = cv2.selectROI('tracking', image)
bbox3 = cv2.selectROI('tracking', image)

while camera.isOpened():
    ok, image=camera.read()
    if not ok:
        print 'no image to read'
        break

    if not init_once:
        ok = tracker.add(cv2.TrackerMIL_create(), image, bbox1)
        ok = tracker.add(cv2.TrackerMIL_create(), image, bbox2)
        ok = tracker.add(cv2.TrackerMIL_create(), image, bbox3)
        init_once = True

    ok, boxes = tracker.update(image)
    print ok, boxes

    for newbox in boxes:
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        cv2.rectangle(image, p1, p2, (200,0,0))

    cv2.imshow('tracking', image)
    k = cv2.waitKey(1)
    if k == 27 : break # esc pressed
'''