from typing import Any
import config
from binance.client import Client
from binance.enums import *
import time
import datetime
import talib
import numpy as np
import pandas as pd
import sys



import smtplib, ssl


def marcadetiempo():
    return datetime.datetime.now().strftime(" %Y/%m/%d - %H:%M:%S ")




class Mail:

    def __init__(self):
        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.sender_mail = "vicvicvicvicvicvicvicx@gmail.com"
        self.password = config.GP

    def send(self, emailto, subject, content):
        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
        service.login(self.sender_mail, self.password)               
        #result = service.sendmail(self.sender_mail, email, f"Subject: {subject}\n{content}")
        content2= f"Subject: {subject}\n" + """\
        \n\n Estado de las cotizaciones de interes definidas en 'alertsConf.txt':\n        
        \n \n""" + content  + " \n\n This message is sent from Python. \n\n"
        result = service.sendmail(self.sender_mail, emailto , content2)

        service.quit()




def getPrice(par):
    #get price
    valor=-1;
    list_of_tickers = client.get_all_tickers()
    for tick_2 in list_of_tickers:
        if tick_2['symbol'] == par:
            valor = float(tick_2['price'])
    return valor
    # get price


def tendenciaString ( symbolTicker, tipo):
    if (tipo=="L"):
        resultado = tendenciaLargo (symbolTicker)
    else:
        if (tipo=="M"):
            resultado = tendenciaMedio (symbolTicker)
        else:
            resultado = tendenciaCorto (symbolTicker)

    if (resultado):
        return "SUBE"
    else:
        return "BAJA"


def tendenciaCorto( symbolTicker ):
    return tendencia(  symbolTicker,  Client.KLINE_INTERVAL_15MINUTE, "18 hour ago UTC")    

def tendenciaMedio( symbolTicker ):
    return tendencia(  symbolTicker, Client.KLINE_INTERVAL_1HOUR, "1 week ago UTC")    

def tendenciaLargo( symbolTicker ):    
    return tendencia(  symbolTicker, Client.KLINE_INTERVAL_1DAY, "1 month ago UTC")    

def tendencia( symbolTicker, intervaloVelas, inicioVelas ):
    x = []
    y = []
    sum = 0
    ma50_i = 0

    resp = False

    #tendencia desde hace 18 horas cada 15 minutos
    #klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "18 hour ago UTC")
    klines = client.get_historical_klines(symbolTicker, intervaloVelas, inicioVelas)

    if (len(klines) != 72):
        return False
    for i in range (56,72):
        for j in range (i-50,i):
          sum = sum + float(klines[i][4])
        ma50_i = round(sum / 50,2)
        sum = 0
        x.append(i)
        y.append(float(ma50_i))

    modelo = np.polyfit(x,y,1)
    if (modelo[0]>0):
        resp = True

    return resp

#método que lanza el correo con la alerta
def lanzaCorreoAlerta(par, sisube, cantUmbral, precAct):
    content = ""

    subject= "Alerta de precio " + par + "  " + marcadetiempo()
    if (sisube == True):
        ssisube = " ha superado el "
    else:
        ssisube = " ha bajado del "    

    content = "- El par: '" + par + "' vale:'" + str(precAct) + "' y " + ssisube+ " umbral:'" + str(cantUmbral) +"'. Accion recomendada."

    #ahora ya tenemos la posibilidad de mandar el correo. Tenemos la cadena a mandar
    mail = Mail()
    mail.send("vcampanario@protonmail.com", subject, content)


# método que devuelve el rsi del par dado
def rsi(par):    
    RSI_N = 14

    klines = client.get_historical_klines(par, Client.KLINE_INTERVAL_30MINUTE, '{} hours ago UTC'.format((RSI_N + 3) // 2))
    closings = np.asarray(klines, dtype=float)[-RSI_N - 1:, 4]

    diffs = np.diff(closings)
    ups = diffs.clip(min=0)
    downs = diffs.clip(max=0)    
    
    float_data = [float(x) for x in diffs]
    np_float_data = np.array(float_data)
    rsi = talib.RSI(np_float_data, RSI_N)       
    
    return rsi



def lanzaCorreoReporte():
    #en ese caso mandamos el correo
    content=""   
    
    #recorremos el listado de pares de interés
    for x in pares:
        tendL = tendenciaString (x, "L")   #tomamos la tendencia de las últimas 18 horas
        tendC = tendenciaString(x, "C")
        tendM = tendenciaString(x, "M")
        precio = getPrice(x)            # tomamos el precio actual
        # construimos una línea para el contenido
        line = "- " + x + ": "+ str(round(precio,2)) + " ; CORTO:'" + tendC +"'; MEDIO: '"+ tendM + "'; LARGO:'" + tendL +"'; RSI:'" + rsi(x) + "'."
        #imprimimos esta línea
        print(line)
        #la añadimos al contenido del correo que vamos a mandar
        content=content + "" + line + "\n"
        


    subject= "Alerta de tendencias de Bitcoin " + marcadetiempo()
    #ahora ya tenemos la posibilidad de mandar el correo. Tenemos la cadena a mandar
    mail = Mail()
    print("subject: "+ subject)
    print("content: "+ content)
    mail.send("vcampanario@protonmail.com", subject, content)

    
#creamos esta función, que en la línea que le pasamos, escribe un "SI" en la 5º columna
def actualizax (numlinea,lista):
    #contador de linea
    i=0

    #copiamos el contenido de la lista en una nueva
    newContent_list = []
    #print("Entramos en 'actualizax'. El contenido de lista es el siguiente")
    #print(lista)
    #print("fin del contenido de lista")

    #recorremos la lista
    for x in lista:        

        i=i+1
        #print ("iteracion: " + str(i))
        #print ("newContent_list:'" + str(newContent_list) + "'")

        #si hemos llegado a la línea en custión
        if (i==numlinea):
            linea = x.split(';')
            newContent_list.append(linea[0] + ";" +  linea[1] +  ";" +  linea[2] + ";" +  linea[3] + ";SI")         
        else:
            newContent_list.append(x)            

    return newContent_list


#esta función escribe la lista en fichero
def escribeEnFichero(nombrefichero,listap):

    #escribimos en el mismo fichero tras el cambio
    fic = open(nombrefichero, "w")
    fic.writelines("%s\n" % s for s in listap)
    fic.close()



#lectura del fichero de configuración
def lecturaFicheroConfig(nombreFichero):
    # leemos el fichero con las alertas
    my_file = open(nombreFichero, "r")
    # este método no me gustó
    #content_list = my_file.readlines()
    content = my_file.read()
    content_list = content.splitlines()

    #cerramos el fichero
    my_file.close()

    return content_list

#obtencion lista de pares
def obtenerListaPares(listaContent: Any):
    # obtenemos una lista de pares de interes
    pares={}
    # pares es la lista de interés    
    lista = []
    #recorremos la lista de líneas entera leida de fichero
    for x in listaContent:
        #primera linea, dividimos por campos
        linea = x.split(';')
        #el elemento sera el primer elemento de la lista
        elemento = linea[1]
        if elemento not in pares:
            lista.append(elemento)

    #imprimios la lista de pares
    #print(lista)

    #imprimios la lista de interés de pares diferentes
    pares = set(lista)
    #print(pares)

    return pares



#####################
### BEGIN PP
#####################
#comienzo del programa principal. 

#inicializamos la varaiable de la última ejecución del correo
ejecutado = False
ultimaejecucion = datetime.datetime.now()

#esperamos 2 segundos
time.sleep(2)

# leemos la configuracion binance
client = Client(config.API_KEY, config.API_SECRET, tld='com')

#cada 5 minutos ejecutamos nuestro bucle principal
# Esto se ejecuta SIEMPRE, while siempre
while 1:

    #lectura de configuración y montaje content_list
    content_list=lecturaFicheroConfig("alertsConf.txt")

    pares = {}
    pares = obtenerListaPares(content_list)


    #REVISIÓN CORREO TENDENCIAS
    # si es la primera ejecución, se lanza el coreo de reporte de tendencias
    if ejecutado == False:

        #lanzamos el correo
        lanzaCorreoReporte()
        print("correo mandado")        


        ejecutado = True
    else:        
        # no es la primera ejecucion, calculamos la diferencia
        #print ("diferencia: " + str((datetime.datetime.now() - ultimaejecucion).total_seconds()))

        #si la diferencia es mayor que 12 horas (43200 segs). 1 hora 3600 segs
        if ((datetime.datetime.now() - ultimaejecucion).total_seconds() >= 43200):

            #lanzamos el correo con el reporte de tendencias
            lanzaCorreoReporte()
            print("correo mandado")            

            #anotamos la ultima ejecucion
            ultimaejecucion = datetime.datetime.now()


    numlinea=0
    #REVISIÓN ALERTAS
    #ahora en el bucle principal recorremos toda la lista
    for x in content_list:

        #incrementamos el numlinea 
        numlinea=numlinea+1        

        #primera linea, dividimos por campos
        linea = x.split(';')

        #tomamos si se ha ejecutado o no
        ejecutadoONo = linea[4] == 'SI'

        #sí no se ha ejecutado
        if ejecutadoONo == False:
            #tomamos el par
            par = linea[1]
            #tomamos la cantidad umbral
            cantUmbral = linea[2]
            #vemos si lo activamos en la subida (si no en la bajada)
            sisube = linea[3] == 'S'
            #tomamos el precio actual del mercado del par
            precAct = getPrice(par)

            #print("Leido: par:'" + par + "', cantUmbral='"+cantUmbral +"', sisube='" + str(sisube) + "', precAct='"+ str(precAct) + "'")

            #si sube
            if (sisube==True):
                #comparamos precio mayor que umbral, entonces lanzamos la alerta
                if (precAct>float(cantUmbral)):                    
                    print("hay que lanzar alerta de subida par:" + par + " cant umbral " + cantUmbral)
                    lanzaCorreoAlerta(par, sisube, cantUmbral, precAct)
                    #cambiamos la información de esa línea en memoria. Hay que hacerlo tb en el content_list y finalmente en fichero
                    linea[4] = 'SI'
                    #actualizariamos la posicion en el el content_list en la línea acordada
                    content_list = actualizax (numlinea,content_list)
                    #escribimos esto mismo en fichero, para que la próxima vez estas alertas no se ejecuten
                    escribeEnFichero("alertsConf.txt",content_list)

            else: #si baja
                #comparamos precio menor que umbral, entonces lanzamos la alerta
                if (precAct<float(cantUmbral)):   
                    print("hay que lanzar alerta de bajada par:" + par + " cant umbral " + cantUmbral)           
                    lanzaCorreoAlerta(par, sisube, cantUmbral, precAct)
                    #cambiamos la información de esa línea en memoria. Hay que hacerlo tb en el content_list y finalmente en fichero
                    linea[4] = 'SI'
                    #actualizariamos la posicion en el el content_list en la línea acordada
                    content_list = actualizax (numlinea,content_list)
                    #escribimos esto mismo en fichero, para que la próxima vez estas alertas no se ejecuten
                    escribeEnFichero("alertsConf.txt",content_list)
    
    #cada 5 minutos seguimos
    print("ahora: '" + marcadetiempo() + "")
    print("dormimos 5 minutos...")
    time.sleep(300)
