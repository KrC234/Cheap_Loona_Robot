import cv2

class CamaraStream:
    def __init__(self,url):
        self.url = url
        self.cap = cv2.VideoCapture(0)

    def grab_frame(self):
        success, image = self.cap.read()
        image = cv2.flip(image,1)
        return success, image
    
    def release(self):
        self.cap.release