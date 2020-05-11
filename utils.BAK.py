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
from datetime import datetime


rut_col = (428, 453, 477, 500, 525, 550, 573, 595, 620, 665)
rut_row = ([142, 165, 190, 212, 235, 260, 283, 307, 330, 355, 377])

resp_col = [[57, 80, 103, 125, 148], 
           [230, 253, 272, 295, 312], 
           [403, 425, 448, 467, 487], 
           [580, 597, 617, 643, 667]]
resp_row = [422, 445, 468, 495, 520, 545, 570, 595, 620, 645, 670, 695, 720, 
           745, 770, 795, 820, 845, 870, 895]

def brightness_contrast(input_img, brightness = 0, contrast = 0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

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

def readB64(save_path, base64_string):
    sbuf = BytesIO()
    dec = decode_base64(base64_string)
    sbuf.write(dec)
    pimg = Image.open(sbuf)
    img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
    cv2.imwrite("1_original_Image.jpg", img)
    return img

def guardarImagen(imgbase64):
    fh = open("imageToSave3.png", "wb")
    fh.write(imgbase64)
    fh.close()

def detectDocument(image):
    image = cv2.imread("1_original_Image.jpg")
    screenCnt = False
    size = 500
    ratio = image.shape[0] / size
    orig = image.copy()

    image = imutils.resize(image, height = size)
    image2 = brightness_contrast(image, -50, 50) 

    
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    #POR RODRIGO

    kernel = np.ones((2,2), np.uint8)
    edged = gray.copy()

    gray = cv2.GaussianBlur(gray, (3, 3), 0)


    #gray = cv2.GaussianBlur(gray, (5, 5), 0)
    #gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #        cv2.THRESH_BINARY,11,2)
    #edged = cv2.adaptiveThreshold(edged,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            #cv2.THRESH_BINARY,11,2)

    #POR RODRIGO
    edged = cv2.GaussianBlur(edged, (5, 5), 0)
    edged = cv2.Canny(edged, 75, 200)
     
    cnts = cv2.findContours(edged.copy(), 
                            cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[2] if imutils.is_cv2() else cnts[1]
    #POR RODRIGO  29 ABRIL 2019.
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
    #ret3,gray = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #cv2.imwrite("5_threshold_Image.jpg", gray)

    #erosion = cv2.erode(gray, kernel, iterations=1)
    #cv2.imwrite("bordes.jpg", edged)
    dst = cv2.warpPerspective(gray, 
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
        if np.average(arr) - min(arr) > 5.5:
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
    def __init__(self, img, points, nPregunta):
        self.img = img
        self.row = points[0]
        self.cols = points[1]
        self.nPregunta = nPregunta


    def getAnswer(self, type, debug = False):
        if type == '2':
            return 'N'
        arr = []
        minimo = 100 #El valor 80 es un aporoximado, generalmente los numeros altos estan cerca de este rango
        maximo = 0
        for col in self.cols:
            promedio = self.avg(col)
            arr.append(promedio)
            if promedio <= minimo :
                minimo = promedio
            if  promedio >= maximo :
                maximo = promedio
        # Establecí el valor 63 pues en la mayoria de los casos de respuestas sin marcar bordea al rederdor de los 70 y en los casos menosres bordeaba los 64, mientras que el mayor de los casos de preguntas marcadas era 62, por eso escugi el 63 como punto medio
        #if np.average(arr) - min(arr) > 10:
        nMarcadas = 0
        for fila in arr:
            # intermedio = (maximo / 2) + (minimo / 2 )
            # if intermedio > fila :
            if np.average(arr) - min(arr) > 10:
                result = self.types[type][np.argmin(arr)]
                cv2.circle(self.img, (self.cols[np.argmin(arr)], self.row), 7, (0,255,0), 2)
                nMarcadas = nMarcadas + 1
            else:
                result = 'N'

            # archivo = open('avg.txt','a')
            # archivo.write('avg_'+ str(self.nPregunta) + '__' + str(fila) +'        marcadas: '+ str(nMarcadas) +'   intermedio:  '+ str(intermedio) + '         fila:'+ str(fila) +'\n')
            # archivo.write('_________________________________\n')
        #if (max(arr) + min(arr) / 2 )  10:
        #result = self.types[type][np.argmin(arr)]
        #cv2.circle(self.img, (self.cols[np.argmin(arr)], self.row), 7, (0,255,0), 1)
        #else:
        #result = 'N'
        # DESCOMENTAR ESTA LINEA DE ABAJO PARA PROBAR: IMPRIME LA IMAGEN PROCESADA, PARA VISUALIZAR COMO LA ESTA RECIBIENDO EL SERVIDOR 
        cv2.imwrite("respuestas.jpg", self.img)
        return result

    def avg(self, col):

        #CREAR SUBMAT
        kernel = np.ones((1,1), np.uint8)
        x = self.row-5
        x2 = self.row + 7
        y = self.cols[0] - 13
        y2 = self.cols[len(self.cols)-1]+11
        subImg = self.img [x:x2, y:y2]
        ret3,subImg = cv2.threshold(subImg,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        subImg = cv2.erode(subImg, kernel, iterations=1)
        self.img[x:x2, y:y2] = subImg

        # cv2.imwrite("fragmento_" + str(col) + "_" + str(self.nPregunta) +".jpg", subImg)

        circle_img = np.zeros((self.img.shape[0],self.img.shape[1]), np.uint8)
        cv2.circle(circle_img,(col,self.row),7,(255,255,255),-1)
        #cv2.imwrite("circulo" + str(col) + "_" + str(self.nPregunta) +".jpg", circle_img)

        rgb = cv2.mean(self.img, mask=circle_img)[::-1]
        return (rgb[1] + rgb[2] + rgb[3]) / 3
