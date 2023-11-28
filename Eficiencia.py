# Programa para calcular la eficiencia de produccion de las tiendas
# Modificado Agosto 9/2023 Se agrego Tienda de Ensenada
# Ago 11 se subio a Github

from __future__ import print_function
import pandas as pd
import numpy as np
import xlwt
import openpyxl
import xlsxwriter
import gspread
import pygsheets
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import timedelta
from datetime import datetime as dt

from Fun_EficienciaTest import *
import gspread
import sys
import warnings
import glob
import os
from gooey import Gooey, GooeyParser

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

credentials = ServiceAccountCredentials.from_json_keyfile_name("monitor-eficiencia-3a13458926a2.json", scopes) #access the json key you downloaded earlier 
file = gspread.authorize(credentials)# authenticate the JSON key with gspread


dfcortes = pd.read_csv(r'horasCorte.csv')
H = dfcortes["horas"].tolist()
M = dfcortes["minutos"].tolist()
tiendas = ['1','2','6','7','8','4','14','10','15','20'] # Arreglo de numeros de tiendas Tapatio
Jobs = []
hora = 0
JobStore = [[] for _ in range(len(tiendas))]
columnas = [3,13,14,16]
hojas = ['SiempreViva','Nirvana','San Bernardino','Rosamond','Rosamond','Desarme TJ','Desarme TJ','Economy','Ensenada','Natalia']
hojas2 = ['SiempreViva','Nirvana','San Bernardino','Rosamond','TDT','Economy','Ensenada','Natalia']
valor = ['Voided','New','Pickup']

@Gooey(program_name="Eficiencia Diaria Tapatio Stores")
def parse_args():
    """ Use GooeyParser to build up the arguments we will use in our script
    Save the arguments in a default json file so that we can retrieve them
    every time we run the script.
    """
    stored_args = {}
    # get the script name without the extension & use it to build up
    # the json filename
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    args_file = "{}-args.json".format(script_name)
    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)
    parser = GooeyParser(description='Actualiza reporte diario des eficiencia de Google Sheets')
    parser.add_argument('Archivo_CSV',
                        action='store',
                        default=stored_args.get('cust_file'),
                        widget='FileChooser',
                        help='Ej. JobsReport_20230317081108.csv')
    parser.add_argument('Directorio_de_salida',
                        action='store',
                        default=stored_args.get('data_directory'),
                        widget='DirChooser',
                        help="Directorio de salida de arhivo .XLSX ")
    parser.add_argument('Archivo_Corte',
                        action='store',
                        default=stored_args.get('cust_file'),
                        widget='FileChooser',
                        help='Ej. horacortesFestivos.csv')
    parser.add_argument('Fecha', help='Seleccione Fecha para generar reporte',
                        default=stored_args.get('Fecha'),
                        widget='DateChooser')
    args = parser.parse_args()
    # Store the values of the arguments so we have them next time we run
    with open(args_file, 'w') as data_file:
        # Using vars(args) returns the data as a dictionary
        json.dump(vars(args), data_file)
    return args


def inicial():
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("monitor-eficiencia-3a13458926a2.json", scopes) #access the json key you downloaded earlier 
    file = gspread.authorize(credentials)# authenticate the JSON key with gspread

    columnas = [3,13,14,16]
    tiendas = ['1','2','6','7','8','4','14','10','15','20'] # Arreglo de numeros de tiendas Tapatio
    Jobs = []
    JobStore = [[] for _ in range(len(tiendas))]
    hojas = ['SiempreViva','Nirvana','San Bernardino','Rosamond','Rosamond','Desarme TJ','Desarme TJ','Economy','Ensenada','Natalia']
    hojas2 = ['SiempreViva','Nirvana','San Bernardino','Rosamond','TDT','Economy','Ensenada','Natalia']
    valor = ['Voided','New','Pickup']

def cortes(Archivo_Corte):
    dfcortes = pd.read_csv(Archivo_Corte)
    H = dfcortes["horas"].tolist()
    M = dfcortes["minutos"].tolist()
    return H,M

#busca los trabajos de cada tienda de acuerdo a los horarios de corte
def trabajos(store,i,cortes,date,ds2,datet):
    cut = horacortes(store,cortes,date)
    Jobs.append(str(datetime.date(date)))
    Jobs.append(hojas[i])
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1])] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Pulled Finished'] < datet)] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Job Status'] == 'Pulling Part')] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[0]) & (ds2['Created'] <= cut[1]) & (ds2['Job Status'] == 'Unassigned')] )) 
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[1]) & (ds2['Created'] < datet)] ))
    Jobs.append(len(ds2[(ds2['Part Store #'] == store) & (ds2['Created'] >= cut[1]) & (ds2['Created'] < datet) & (ds2['Pulled Finished'] < datet)] ))
    JobStore[i].extend(Jobs)


def suma_stores(JobStore,st1,st2):
 for j in range(2,8):
  JobStore[st1][j] = JobStore[st1][j] + JobStore[st2][j]
 JobStore.pop(st2)
  
# Funcion Main para buscar todos los trabajos
def principal(date,nombre,H,M,directorio):
    date=dt.strptime(date, "%Y-%m-%d")
    print(date)
    ds = pd.read_csv(nombre)
    head_tail = os.path.split(nombre)
    nombre2 = head_tail[1].split('.')
    nombre3 = directorio + "\\"+ nombre2[0] + ".xlsx"
    nombre4 = directorio + "\\"+ nombre2[0] + "_Logistica.xlsx"
    ds2 = time_fix(columnas,hora,ds)
    rango_fechas(ds2,date)
    print(ds2)
    #writer = pd.ExcelWriter(nombre4, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    print("Creando archivo para Logistica", nombre4)
    ds2.to_excel(nombre4,header=True, index = False)

    print("Conectando a google sheets .....")
    ss = file.open("EficienciaReporte")
    print("Conexion exitosa")

    borra_columnas('Job Status',valor,ds2)
    #print(H[0])

    cortes,datet = fechas_corte1(date,H,M)
        
    for i in range(len(tiendas)):
     trabajos(int(tiendas[i]),i,cortes,date,ds2,datet)
     Jobs.clear()

    suma_stores(JobStore,3,4) 
    suma_stores(JobStore,4,5)

    # Actualizo reporte de eficiencia de Google Drive
    for i in range(len(hojas2)):
     hoja = ss.worksheet(str(hojas2[i]))
     print(JobStore[i]) ####
     hoja.append_row(JobStore[i])
    print("Reporte de Eficiencia en Google Sheets actualizado correctamente") 
    writer = pd.ExcelWriter(nombre3, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    print("Creando archivo", nombre3)
    ds2.to_excel(writer, sheet_name='ProduccionDiaria',header=True, index = False)
    

    while True:
        try:
            writer.close()
        except xlsxwriter.exceptions.FileCreateError as e:
            decision = input("Exception caught in workbook.close(): %s\n"
                             "Please close the file if it is open in Excel.\n"
                             "Try to write file again? [Y/n]: " % e)
            if decision != 'n':

                continue

        break

if __name__ == '__main__':
    conf = parse_args()
    H,M=cortes(conf.Archivo_Corte)
    principal(conf.Fecha,conf.Archivo_CSV,H,M,conf.Directorio_de_salida)
     