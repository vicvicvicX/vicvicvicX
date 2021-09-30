import config
from binance.client import Client
from binance.enums import *
import time
import datetime
import numpy as np
import sys


client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = 'ADAEUR'
#quantityOrders = 0.0013
quantityOrders = 0.0039
pl = 0;    #perdidas y ganancias
pcompra = 0
pventa = 0
hayorden = False
iteracion =0
original_stdout = sys.stdout
aciertos=0
fallos=0
hitmiss=0


def tendencia():
    x = []
    y = []
    sum = 0
    ma50_i = 0

    resp = False

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "18 hour ago UTC")

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

def _ma50_():

    ma50_local = 0
    sum = 0

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "15 hour ago UTC")

    if (len(klines)==60):
        for i in range (10,60):
            sum = sum + float(klines[i][4])
        ma50_local = sum / 50

    return ma50_local

def marcadetiempo():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")    

def mibalance():
    #mostramos mi balance de la moneda
    b_btc=client.get_asset_balance(asset='BTC')
    b_ada=client.get_asset_balance(asset='ADA')
    b_eth=client.get_asset_balance(asset='ETH')
    b_eur=client.get_asset_balance(asset='EUR')

    #impresion    
    print (marcadetiempo() + '-' + 'Balance:')
    print('   ' + b_btc['asset']+ ' ' + b_btc['free'])
    print('   ' + b_ada['asset']+ ' ' + b_ada['free'])
    print('   ' + b_eth['asset']+ ' ' + b_eth['free'])
    print('   ' + b_eur['asset']+ ' ' + b_eur['free'])
    return 0

def misOrders():
    #mostramos mis orders
    ordersEURBTC = client.get_open_orders(symbol='BTCEUR')
    ordersEURADA = client.get_open_orders(symbol='ADAEUR')
    ordersEURETH = client.get_open_orders(symbol='ETHEUR')

    print (marcadetiempo() + '-' + 'Orders:')
    print(ordersEURBTC)
    print(ordersEURADA)
    print(ordersEURETH)
    #print('   ' + ordersEURBTC)
    #print('   ' + tradesEURADA)
    #print('   ' + tradesEURETH)
    return 0

def impTrade(tradesEURADA):
    numtrades = 1
    for elem in tradesEURADA:
        print('   ' + 'ordernumber:' + str(numtrades))
        print('   ' +'   ' + 'symbol:' + elem['symbol'])
        print('   ' +'   ' + 'id:' + str(elem['id']))
        print('   ' +'   ' + 'orderid:' + str(elem['orderId']))
        print('   ' +'   ' + 'price:' + str(elem['price']))
        print('   ' +'   ' + 'qty:' + str(elem['qty']))
        print('   ' +'   ' + 'isBuyer:' + str(elem['isBuyer']))
        print('   ' +'    ---')
        numtrades=numtrades+1


def misTrades():
    #mostramos mis trades
    tradesEURBTC = client.get_my_trades(symbol='BTCEUR')
    tradesEURADA = client.get_my_trades(symbol='ADAEUR')
    tradesEURETH = client.get_my_trades(symbol='ETHEUR')

    print (marcadetiempo() + '-' + 'Trades:')
    impTrade(tradesEURBTC)
    impTrade(tradesEURADA)
    impTrade(tradesEURETH)
    #print('   ' + ordersEURBTC)
    #print('   ' + tradesEURADA)
    #print('   ' + tradesEURETH)
    return 0

def miPL():
    print (marcadetiempo() + '-' + 'P&L:')
    print('   ' + 'P&L= ' + str(pl))    
    print('   ' + 'compras= ' + str(aciertos + fallos))
    print('   ' + 'ventas= ' + str(aciertos + fallos))
    print('   ' + 'aciertos= ' + str(aciertos))
    print('   ' + 'fallos= ' + str(fallos))
    if (aciertos+fallos==0):
        print('   ' + 'hitmiss= ' + str('N.A.') )
    else:        
        print('   ' + 'hitmiss= ' + str(aciertos/(aciertos+fallos)))
    return 0


### BEGIN PP
#comienzo del programa principal. 



mibalance()
miPL()
misOrders()
misTrades()

#cambio de la salida estandar
with open(marcadetiempo() + ".log", 'w') as f:
    sys.stdout = f # Change the standard output to the file we created.

    mibalance()
    miPL()
    misOrders()
    misTrades()



    # Esto se ejecuta SIEMPRE, while siempre
    while 1:

        iteracion = iteracion +1

        #cogemos la tendencia
        ma50 = _ma50_()
        if (ma50 == 0): continue

        #get price
        list_of_tickers = client.get_all_tickers()
        for tick_2 in list_of_tickers:
            if tick_2['symbol'] == symbolTicker:
                symbolPrice = float(tick_2['price'])
        # get price

        tend = tendencia()

        print(marcadetiempo() + '-' + '*********')
        print("***** " + symbolTicker + " *******")
        print("iteracion:" + str(iteracion))
        print("Actual MA50 " + str(round(ma50,2)))
        print("Actual Price " + str(round(symbolPrice,2)))
        print("Price to Buy " + str(round(ma50*0.995,2)))
        print("tendencia alcista " + str(tend))
        miPL()
        print (marcadetiempo() + '-' + '*********')

        sys.stdout = original_stdout
        print(marcadetiempo() + '-' + '*********')
        print("***** " + symbolTicker + " *******")
        print("iteracion:" + str(iteracion))
        print("Actual MA50 " + str(round(ma50,2)))
        print("Actual Price " + str(round(symbolPrice,2)))
        print("Price to Buy " + str(round(ma50*0.995,2)))
        print("tendencia alcista " + str(tend))
        miPL()
        print (marcadetiempo() + '-' + '*********')

        sys.stdout = f

        

        #orders = client.get_open_orders(symbolTicker)

        #si hay órdenes abiertas, no se hace nada, puesto que se tienen que cerrar sólas (20% de ganancia y cierro)
        if (hayorden):
            print("HAY ORDENES ASÍ QUE ESPERAMOS A LA SIGUIENTE ITERACIÓN")        
        
            #si sube más de un 4% vendemos y recogemos ganancias
            if (symbolPrice> ma50*1.04):
                print("VENDEMOS TOMANDO BENEFICIOS!")
                pventa = symbolPrice
                pl = pl + (pventa-pcompra)
                miPL()
                hayorden=False
                aciertos= aciertos+1

            #si baja más de un 5% vendemos y minimizamos pérdidas
            if (symbolPrice< ma50*0.995):
                pventa = symbolPrice
                print("VENDEMOS MINIMIZANDO PERDIDAS!")
                pl = pl + (pventa-pcompra)
                miPL()
                hayorden=False
                fallos = fallos +1


        else:#NO HAY ÓRDENES
            if (not tend):
                print ("TENDENCIA BAJISTA")
            else:
                print ("TENDENCIA ALCISTA")

                #si estamos por debajo de la tendencia alcista, compramos
                if (symbolPrice < ma50*0.996):
                    hayorden=True
                    print ("COMPRA!!")
                    print ("BUY SIGNAL at price " + str(symbolPrice))
                    pcompra = symbolPrice
                    

        time.sleep(10)
"""



        #METEMOS ORDEN DE VENTA, LIMITADA , AL PRECIO COMPRADO POR 0.2, CON UN STOP LOSS DEL 5% Y STOP LIMIT PRICE DEL 4%
        orderOCO = client.order_oco_sell(
            symbol = symbolTicker,
            quantity = quantityOrders,
            price = round(symbolPrice*1.02,2),
            stopPrice = round(symbolPrice*0.995,2),
            stopLimitPrice = round(symbolPrice*0.994,2),
            stopLimitTimeInForce = 'GTC'
        )
        time.sleep(20)
"""