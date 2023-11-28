# Programa para calcular la eficiencia de produccion de las tiendas
# Modificado Agosto 9/2023 Se agrego Tienda de Ensenada

from datetime import datetime, timedelta
import pandas as pd

USAstores = [1,2,3,5,6,7,8]
DesarmeTJ = [4,14]
Economy = 10
Ensenada = 15
Natalia = 20

def fechas_corte1(date,H,M):
 # Convierte argumento de entrada a fecha, y calculo fechas de cortes
 datey = date - timedelta(days=1) # Ayer
 datet = date + timedelta(days=1) # Mañana
 dateS = date - timedelta(days=2) # Sabado
 dateF = date - timedelta(days=3)
 
 # Arreglo de fechas de cortes de tiendas Tapatio
 cortes = [ datey + timedelta(hours = H[0])+ timedelta(minutes = M[0]),  #0 Stores USA stores
            date + timedelta(hours = H[1])+ timedelta(minutes = M[1]),   #1 Stores USA stores
            datey + timedelta(hours = H[2])+ timedelta(minutes = M[2]),  #2
            date + timedelta(hours = H[3])+ timedelta(minutes = M[3]),   #3 Stores USA stores
            datey + timedelta(hours = H[4])+ timedelta(minutes = M[4]), #4 Stores 4,14
            date + timedelta(hours = H[5]) + timedelta(minutes= M[5]),  #5 Stores 4,14
            datey + timedelta(hours = H[6])+ timedelta(minutes = M[6]),  #6 Store 10
            date + timedelta(hours = H[7])+ timedelta(minutes = M[7]),   #7 Store 10
            dateS + timedelta(hours = H[8])+ timedelta(minutes = M[8]),  #8 Stores USA stores
            dateF + timedelta(hours = H[9])+ timedelta(minutes = M[9]), #9 Stores 4,14
            dateS + timedelta(hours = H[10])+ timedelta(minutes = M[10]),  #10 Store 10
            date + timedelta(hours = H[11]) + timedelta(minutes= M[11]),  #11 Stores 4,14  Sabado todo el dia en
            datey + timedelta(hours = H[0])+ timedelta(minutes = M[0]),  #12 Tap 15 Ensenada
            date + timedelta(hours = H[1])+ timedelta(minutes = M[1]),   #13 Tap 15 Enesenada
            dateS + timedelta(hours = H[12])+ timedelta(minutes = M[12]),  #14 Tap 15 Ensenada
            dateF + timedelta(hours = H[13])+ timedelta(minutes = M[13]),  #15 Tap 20 Lalos
            date + timedelta(hours = H[14])+ timedelta(minutes = M[14]),   #16 Tap 20 Lalos
            dateS + timedelta(hours = H[15])+ timedelta(minutes = M[15]),  #17 Tap 20 Lalos
            datey + timedelta(hours = H[13])+ timedelta(minutes = M[13])  #18 Tap 20 Lalos

          ]
 cortes = pd.to_datetime(cortes)
 return cortes,datet

def time_fix(col,h,ds):
 # Sumo o resto horas para arreglar hora de reporte de Produccion
 for i in range(len(col)):
     n = int(col[i])
     ds.iloc[:, n] = pd.to_datetime(ds.iloc[:,n])+ timedelta(hours=h)
 ds3 = ds.copy()
 return ds3

def borra_columnas(col,value,ds2):
    # Borro los registros que no se ocupan del reporte de produccion
    for i in range(len(value)):
     indexDeleted = ds2[ds2[col] == value[i]].index
     ds2.drop(indexDeleted,inplace=True)
    indexDeleted = ds2[ds2['Part Price'] <  0].index #borro regresos de dinero (retornos)
    ds2.drop(indexDeleted,inplace=True)


def rango_fechas(df,date):
    #print(date)
    #print(df['Created'].min())
    #print(df['Created'].max())
    if date <= df['Created'].min() or date >= df['Created'].max():
        print("La fecha no se encuentra en el rango de fechas del archivo")
        print("[",df['Created'].min()," - ", df['Created'].max(),"]")
        exit()
    
# Selecciona los horarios de corte de acuerdo a la tienda    
def hora_cortes(store,cortes,date):
    j=0
    if date.weekday() == 0:  # (0 lunes)  

        if store in USAstores: #range(1,3) or store in range(6,9):
            cuts = [cortes[8],cortes[1]]

        elif store in DesarmeTJ:#(store == 14 or  store == 4):
            cuts = [cortes[9],cortes[5]]

        elif store == Economy:
            cuts = [cortes[10],cortes[7]]

        elif store == Ensenada:
            cuts = [cortes[14],cortes[1]]

        elif store == 20:
            cuts = [cortes[15],cortes[16]]  
       
    elif date.weekday() == 5:      # 5 SABADO

        #print(store)
        if store in USAstores: # range(1,3) or store in range(6,9):
            cuts = [cortes[0],cortes[3]]
        elif store in DesarmeTJ:#  (store == 14 or  store == 4):  
            cuts = [cortes[4],cortes[11]]  
        elif store == Economy:
            cuts = [cortes[6],cortes[7]]
        elif store == Ensenada:
            cuts = [cortes[14],cortes[14]] 
        elif store == Natalia:
            cuts = [cortes[18],cortes[11]]       
    else : #(1 martes) (2 miercoles) (3 jueves) (4 vienres) (5 sabado)
        if store in USAstores:#range(1,3) or store in range(6,9):
            cuts = [cortes[0],cortes[1]]
        elif store in DesarmeTJ:#s(store == 14 or  store == 4):
            cuts = [cortes[4],cortes[5]]
        elif store == Economy:
            cuts = [cortes[6],cortes[7]]
        elif store == Ensenada:
            cuts = [cortes[0],cortes[1]]
        elif store == Natalia:
            cuts = [cortes[18],cortes[16]]          
    return cuts

#busca los trabajos de cada tienda de acuerdo a los horarios de corte
def trabajos1(ds2,store,i,cortes,date,Jobs,JobStore,hojas,datet):
    cut = hora_cortes(store,cortes,date)
    Jobs.append(str(datetime.date(date)))
    Jobs.append(hojas[i])
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1])] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Pulled Finished'] < datet)] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Job Status'] == 'Pulling Part')] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Job Status'] == 'Unassigned')] )) 
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[1]) & (ds2['Created'] < datet)] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[1]) & (ds2['Created'] < datet) & (ds2['Pulled Finished'] < datet)] ))
    JobStore[i].extend(Jobs)




