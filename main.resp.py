#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import os
import bottle
from bottle import route, request, response, run, BaseRequest
from utils import *
import cv2s
import imutils
from datetime import datetime
import re
import codecs

BaseRequest.MEMFILE_MAX = 4096 * 4096

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            return fn(*args, **kwargs)

    return _enable_cors

@route('/')
def index():
    return '<h1>Root Page</h1>'

@route('/inicio')
def inicio():
    return '<h1>Inicio</h1>'

@route('/', method=['OPTIONS', 'POST'])
@enable_cors
def do_upload():
    startTime = datetime.now()
    debug = True
    save_path = "/tmp/planillas/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    upload = request.files.get('planilla')
    upload64 = request.json

    if upload is not None and upload64 is None:
        upload = request.files.get('planilla')
        name, ext = os.path.splitext(upload.filename)
        if ext.lower() not in ('.png', '.jpg', '.jpeg'):
            return {"error":"Extensión de archivo no permitida", "data":{}}
        upload.save(save_path)
        image = cv2.imread(save_path + upload.filename)
        img = detectDocument(image)
        os.remove(save_path + upload.filename)
    elif upload is None and isinstance(upload64, dict):
        preguntas = upload64['preguntas']
        #return {"preguntas":preguntas[0]}
        image = readB64(upload64['planilla'])
        img = detectDocument(image)

    if isinstance(img, bool) == True:
        return {"error":"La imagen no se detectó correctamente", "data":{}}

    rut = ''
    for xx in rut_col:
        a = Rut(img, [rut_row, xx])
        r = a.getRut('rut', debug)
        if str(xx) == str(rut_col[-1]) and str(r) != '':
            rut = rut + '-'
        rut = rut + str(r)

    questions = len(preguntas)
    i = 1
    result = {'error':'', 'data':{'rut':rut,'respuestas':[]}}
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
            if int(tipo) == 2:
                correcta = ''
            b = Respuesta(img, [yy, xx])
            opcion = b.getAnswer(tipo, debug)
            d = {
                "numero_pregunta":i,
                "id_tipo_pregunta":tipo,
                "tipo_pregunta":tipo,
                "opcion": opcion,
                "puntaje": val['puntaje'] if opcion == correcta else 0,
                "alternativa_correcta":correcta,
                "descripcion": val['descripcion'],
                "resp": val['resp']
            }
            result['data']['respuestas'].append(d)
            i = i + 1
    endTime = datetime.now()
    if debug == True:
        cv2.imshow("Scanned", imutils.resize(img, height = 698))
        cv2.waitKey(0)
    result["execution_time"] = str(endTime - startTime)
    return result

run(host='0.0.0.0', port=8282)