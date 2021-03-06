#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import sys, os

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__))

import bottle
from bottle import route, request, response, run, BaseRequest, static_file, template
from utils import *
import cv2
import imutils
from datetime import datetime
import re
import codecs
import json

BaseRequest.MEMFILE_MAX = 4096 * 4096

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        response.set_header('Access-Control-Allow-Origin','*')
        response.set_header('Access-Control-Allow-Methods','GET, POST, PUT, OPTIONS')
        response.set_header('Access-Control-Allow-Headers','Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token')

        if bottle.request.method != 'OPTIONS':
            return fn(*args, **kwargs)

    return _enable_cors

@route('/')
def index():
    return '<h1>Pagina raiz</h1>'


@route('/inicio')
def inicio():
    return '<h1>Pagina inicio</h1>'


@route('/image')
def imagen():
    return template('imagen')


@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./')


@route('/', method=['OPTIONS', 'POST'])
@enable_cors
def do_upload():
    startTime = datetime.now()
    debug = False
    save_path = "/tmp/planillas/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    upload = request.files.get('planilla')
    upload64 = request.json

    if upload is not None and upload64 is None:
        upload = request.files.get('planilla')
        preguntas = json.loads(request.forms.get("preguntas"))
        name, ext = os.path.splitext(upload.filename)
        if ext.lower() not in ('.png', '.jpg', '.jpeg'):
            return {"error":"Extensión de archivo no permitida", "data":{}}
        upload.save(save_path)
        image = cv2.imread(save_path + upload.filename)
        img = detectDocument(image)
        if isinstance(img, bool) == True:
            return {"error":"La imagen no se detectó correctamente", "data":{}}
        img2 = detectDocument(img)
        if isinstance(img2, bool) == False:
            img = img2
        os.remove(save_path + upload.filename)
    elif upload is None and isinstance(upload64, dict):
        preguntas = upload64['preguntas']
        image = readB64(save_path, upload64['planilla'])
        img = detectDocument(image)
        if isinstance(img, bool) == True:
            return {"error":"La imagen no se detectó correctamente", "data":{}}
        img2 = detectDocument(img)
        if isinstance(img2, bool) == False:
            img = img2
			    
    if isinstance(img, bool) == True:
        return {"error":"La imagen no se detectó correctamente", "data":{}}

    rut = ''
    # for xx in rut_col:
    #     a = Rut(img, [rut_row, xx])
    #     r = a.getRut('rut', debug)
    #     if str(xx) == str(rut_col[-1]) and str(r) != '':
    #         rut = rut + '-'
    #     rut = rut + str(r)

    questions = len(preguntas)
    i = 1
    result = {'error':'', 'data':{'rut':rut,'respuestas':[]}}

    # LIMPIAR ARCHIVO
    archivo = open('avg.txt','w')
    archivo.close()
    for xx in resp_col:
        if i > questions:
            break
        for yy in resp_row:
            if i > questions:
                break
            val = preguntas[i - 1]
            tipo = str(val['id_tipo_pregunta'])
            correcta = getCorrecta(val['resp'])
            correcta = correcta if int(tipo) > 1 else correcta.replace('A', 'V').replace('B', 'F')
            
            b = Respuesta(img, [yy, xx], i)
            opcion = b.getAnswer(tipo, debug)
            vacia = 1 if opcion == 'VACIO' else 0
            nula = 1 if opcion == 'NULO' else 0
            opcion = 'N' if opcion == 'VACIO' else opcion
            opcion = 'N' if opcion == 'NULO' else opcion
            puntajeObtenido = val['puntaje'] if opcion == correcta else 0
            asignada = 1
            if int(tipo) == 2:
                correcta = ''
                puntajeObtenido = 0
                asignada = 0
            d = {
                "numero_pregunta":i,
                "id_tipo_pregunta":tipo,
                "tipo_pregunta":tipo,
                "opcion": opcion,
                "puntaje": val['puntaje'],
                "puntajeObtenido": puntajeObtenido,
                "alternativa_correcta":correcta,
                "id_pregunta": val["id"],
                #"descripcion": val['descripcion'],
                "asignada": asignada,
                #"resp": val['resp'], 
                "nula": nula,
                "vacia" : vacia
            }
            result['data']['respuestas'].append(d)
            i = i + 1
    endTime = datetime.now()
    if debug == True:
        cv2.imshow("Scanned", imutils.resize(img, height = 698))
        cv2.waitKey(0)
    result["execution_time"] = str(endTime - startTime)
    # archivo = open('avg.txt','w')
    # archivo.write(str(upload64['planilla']))
    # archivo.write(str(upload64['preguntas']))
    # archivo.close()
    return result


@route('/debug', method=['OPTIONS', 'POST'])
@enable_cors
def do_upload_debug():
    
    return 'hola'
#run(host='170.239.85.159', port=8282)
#run(host='0.0.0.0', port=8080, debug=True)
application = bottle.default_app()
