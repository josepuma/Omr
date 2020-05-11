import cv2
import imutils
from imutils import perspective
import numpy as np
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO
from base64 import b64decode
from PIL import Image
from skimage import img_as_ubyte

rut_col = (428, 453, 477, 500, 525, 550, 573, 595, 620, 665)
rut_row = ([142, 165, 190, 212, 235, 260, 283, 307, 330, 355, 377])

resp_col = [[57, 80, 103, 125, 148], 
           [230, 253, 272, 295, 312], 
           [403, 425, 448, 467, 487], 
           [580, 597, 617, 643, 667]]
resp_row = [422, 445, 468, 495, 520, 545, 570, 595, 620, 645, 670, 695, 720, 
           745, 770, 795, 820, 845, 870, 895]

def decode_base64(data):
    if '=' in data:
        data = data[:data.index('=')]
    missing_padding = len(data) % 4
    if missing_padding == 1:
        data += 'A=='
    elif missing_padding == 2:
        data += '=='
    elif missing_padding == 3:
        data += '='
    return b64decode(data)

def readB64(base64_string):
    sbuf = BytesIO()
    dec = decode_base64(base64_string)
    sbuf.write(dec)
    pimg = Image.open(sbuf)
    #print type(np.array(pimg))
    img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
    return img

def detectDocument(image):
    screenCnt = False
    size = 600
    ratio = image.shape[0] / size
    orig = image.copy()
    image = imutils.resize(image, height = size)
     
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    #POR RODRIGO
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    #gray = cv2.GaussianBlur(gray, (5, 5), 0)
    #gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #        cv2.THRESH_BINARY,11,2)
    
    #POR RODRIGO
    edged = cv2.Canny(gray, 75, 200)
     
    cnts = cv2.findContours(edged.copy(), 
                            cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
     
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
     
        if len(approx) == 4:
            screenCnt = approx
            break
    if isinstance(screenCnt, bool) == True:
        return False
    pts1 = perspective.order_points(np.float32([screenCnt[0][0], 
                                               screenCnt[1][0], 
                                               screenCnt[2][0], 
                                               screenCnt[3][0]]))
    pts2 = np.float32([[0,0], [698,0], [698,923], [0,923]])

    #POR RODRIGO
    #dst = cv2.warpPerspective(image, 
    #                          cv2.getPerspectiveTransform(pts1,pts2), 
    #                          (698,923))
    kernel = np.ones((2,2), np.uint8)
    ret3,gray = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    erosion = cv2.erode(gray, kernel, iterations=1)
    
    dst = cv2.warpPerspective(erosion, 
                              cv2.getPerspectiveTransform(pts1,pts2), 
                              (698,923))
    #POR RODRIGO
    return dst

def getCorrecta(opt):
    i = 0
    while i < len(opt):
        if opt[i]['estado'] == 1:
            return opt[i]['respuesta']
        i += 1
    return 'N'

class Rut:
    rut = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'K']
    def __init__(self, img, points):
        self.img = img
        self.cols = points[0]
        self.row = points[1]

    def getRut(self, type, debug = False):
        arr = []
        for col in self.cols:
            arr.append(self.avg(col))
        if np.average(arr) - min(arr) > 5:
            result = str(self.rut[np.argmin(arr)])
            if debug == True:
                cv2.circle(self.img, 
                           (self.row, self.cols[np.argmin(arr)]), 
                           10, (0,255,0), 1)
        else:
            result = ''
        return result

    def avg(self, col):
        circle_img = np.zeros((self.img.shape[0],self.img.shape[1]), np.uint8)
        cv2.circle(circle_img,(self.row, col),10,(255,255,255),-1)
        rgb = cv2.mean(self.img, mask=circle_img)[::-1]
        return (rgb[1] + rgb[2] + rgb[3]) / 3

class Respuesta:
    types = {
            '3':['A', 'B', 'C', 'D', 'E'],
            '1':['V', 'F', 'N', 'N', 'N']}
    def __init__(self, img, points):
        self.img = img
        self.row = points[0]
        self.cols = points[1]

    def getAnswer(self, type, debug = False):
        if type == '2':
            return 'N'
        arr = []
        for col in self.cols:
            arr.append(self.avg(col))
        if np.average(arr) - min(arr) > 5:
            result = self.types[type][np.argmin(arr)]
            if debug == True:
                cv2.circle(self.img, (self.cols[np.argmin(arr)], self.row), 10, (0,255,0), 1)
        else:
            print (arr)
            print (str(int(np.average(arr))) + ' - ' + str(int(min(arr))) + ' = ' + str(int(np.average(arr) - min(arr))))
            result = 'N'
        return result

    def avg(self, col):
        circle_img = np.zeros((self.img.shape[0],self.img.shape[1]), np.uint8)
        cv2.circle(circle_img,(col,self.row),10,(255,255,255),-1)
        rgb = cv2.mean(self.img, mask=circle_img)[::-1]
        return (rgb[1] + rgb[2] + rgb[3]) / 3