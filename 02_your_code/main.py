import datetime
import json
import typer
import requests

app = typer.Typer()
""" la liberia typer minimiza la duplicación de código. 
Múltiples características de cada declaración de parámetros. Menos Bugs"""

@app.command()
def upgrade(id: str, plan: str):
  """ Funcion que se ejecuta cuando se pasa el parametro upgrade"""
  try:
    response = requests.get(f'http://localhost:8010/api/v1/customerdata/{id}/')
    print(f'http://localhost:8010/api/v1/customerdata/{id}/')
    print(response)
    customer = response.json()
    #print(customer)
    res = validation(customer)
    if res == 0:
      print('the program will finish executing')
    else:
      data = customer['data']
      infobae = validation_upgrade(data, plan)
      if type(infobae) != int and infobae != None:
        customer['data']=infobae
        api_url = 'http://localhost:8010/api/v1/customerdata/' + str(customer['id'])+'/'
        print(api_url)
        respons = requests.put(api_url, json = customer)
        print(respons)
      else:
        print('')
  except requests.ConnectionError:
    print(f'there is no information with the id: {id}')



@app.command()
def downgrade(id: str, plan: str):
  """ Funcion que se ejecuta cuando se pasa el parametro downgrade"""
  try:
    response = requests.get(f'http://localhost:8010/api/v1/customerdata/{id}/')
    print(f'http://localhost:8010/api/v1/customerdata/{id}/')
    print(response)
    customer = response.json()
    #print(customer)
    res = validation(customer)
    if res == 0:
      print('se terminara de ejecutar el programa')
    else:
      data = customer['data']
      infobae = validation_downgrade(data, plan)
      if type(infobae) != int and infobae != None:
        customer['data']=infobae
        respo = json.dumps(customer)
        print(respo)
        print(type(respo))
        api_url = 'http://localhost:8010/api/v1/customerdata/' + str(customer['id'])+'/'
        print(api_url)
        respons = requests.put(api_url, json = customer)
        print(respons)
      else:
        print('the program will finish executing')
  except requests.ConnectionError:
    print(f'no hay informacion con el id: {id}')

def validation(custom):
  """se vaida que exosta el id del plan al que se le desea cambiar 
  el estado del plan, comparando con el listado de costumerdata"""
  try:
    response = requests.get(f'http://localhost:8010/api/v1/customerdata/')
    customer = response.json()
    try:
      for i in customer['results']:
        if custom['id']==i['id']:
          print("existe el id: %(s)s" % {'s':custom['id']})
          return 1
    except KeyError:
      print('the ID does not exist or is badly formated')
      return 0
  except requests.ConnectionError:
    print(f'no hay informacion en la url')
    return 0

def validation_upgrade(data, plan):
  """se valida que los casos de mejordo del plan se sean aceptado,
  de lo contrario se termina la ejecucion."""
  if plan == 'free' or plan == 'basic' or plan == 'premium':
    if data['SUBSCRIPTION']=='premium' or plan=='free':
      message_reachble()
      return -1
    if data['SUBSCRIPTION']=='basic' and plan=='basic':
      message_reachble()
      return -1
    infot = validate_plan_upgrade(data, plan)
    return infot
  else:
    print('other unknown error')
    return 0

def validation_downgrade(data, plan):
  """se valida que los casos de degradado del plan se sean aceptado,
  de lo contrario se termina la ejecucion."""
  if plan == 'free' or plan == 'basic' or plan == 'premium':
    if(data['SUBSCRIPTION']=='free' or plan=='premium'):
      message_reachble()
      print("0 %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
      return -1
    if data['SUBSCRIPTION']=='basic' and plan=='basic':
      message_reachble()
      print("0 %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
      return -1
    info = validate_plan_downgrade(data, plan)
    return info
  else:
    print('other unknown error')
    return 0

def message_reachble():
  """se declara de manera global un mensaje de donde se aclara
  que no se puede alcanzar l suscribcion"""
  print('the target subscription level is not reachable')

""" valida cada uno de los criterios de aceptacion recibidos, teniendo 
en cuenta la suscribcion actual y el plan al que se le desea mejorar"""
def validate_plan_upgrade(data, plan):
  if(data['SUBSCRIPTION']=='free' and plan=='basic'):
    print("1 Upgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
    datos = to_basic(data['ENABLED_FEATURES'])

    modify_data(data, 'Upgrade', datos, plan)
    return data
  if(data['SUBSCRIPTION']=='free' and plan=='premium'):
    print("2 Upgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
    datos = to_premium(data['ENABLED_FEATURES'])

    modify_data(data, 'Upgrade', datos, plan)
    return data
  if(data['SUBSCRIPTION']=='basic' and plan=='premium'):
      print("3 Upgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
      datos = to_premium(data['ENABLED_FEATURES'])

      modify_data(data, 'Upgrade', datos, plan)
      return data

""" Valida cada uno de los criterios de aceptacion recibidos, teniendo 
en cuenta la suscribcion actual y el plan al que se le desea degradar"""
def validate_plan_downgrade(data, plan):
  if(data['SUBSCRIPTION']=='premium' and plan=='basic'):
    print("1 Downgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
    datos = to_basic(data['ENABLED_FEATURES'])

    modify_data(data, 'Downgrade', datos, plan)
    return data
  if(data['SUBSCRIPTION']=='premium' and plan=='free'):
    print("2 Downgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
    datos = to_free(data['ENABLED_FEATURES'])

    modify_data(data, 'Downgrade', datos, plan)
    return data
  if(data['SUBSCRIPTION']=='basic' and plan=='premium'):
      print("3 Upgrade %(d)s -> %(b)s" % {'d':data['SUBSCRIPTION'], 'b': plan})
      datos = to_free(data["ENABLED_FEATURES"])

      modify_data(data, 'Downgrade', datos, plan)
      return data


def to_free(key):
  """Función que recibe como parametro data['ENABLED_FEATURES'] 
  y cambia las caracteristicas a free"""
  key["CERTIFICATES_INSTRUCTOR_GENERATION"]=False
  key["ENABLE_COURSEWARE_SEARCH"]=False
  key["ENABLE_EDXNOTES"]=False
  key["ENABLE_DASHBOARD_SEARCH"]=False
  key["INSTRUCTOR_BACKGROUND_TASKS"]=False
  key["ENABLE_COURSE_DISCOVERY"]=False
  return(key)


def to_basic(key):
  """Función que recibe como parametro data['ENABLED_FEATURES'] 
  y cambia las caracteristicas a basic"""
  key["CERTIFICATES_INSTRUCTOR_GENERATION"]=False
  key["ENABLE_COURSEWARE_SEARCH"]=False
  key["ENABLE_EDXNOTES"]=True
  key["ENABLE_DASHBOARD_SEARCH"]=False
  key["INSTRUCTOR_BACKGROUND_TASKS"]=False
  key["ENABLE_COURSE_DISCOVERY"]=False
  return(key)

def to_premium(key):
  """Función que recibe como parametro data['ENABLED_FEATURES']
  y cambia las caracteristicas a preium"""
  key["CERTIFICATES_INSTRUCTOR_GENERATION"]=True
  key["ENABLE_COURSEWARE_SEARCH"]|=True
  key["ENABLE_EDXNOTES"]=True
  key["ENABLE_DASHBOARD_SEARCH"]=True
  key["INSTRUCTOR_BACKGROUND_TASKS"]=False
  key["ENABLE_COURSE_DISCOVERY"]=False
  return(key)

def modify_data(data, case, datos, plan):
  """Se valida el tipo de movimiento y se agrega la fecha n la que se realiza"""
  now = datetime.datetime.now()
  date = now.strftime("%Y-%m-%d %H:%M:%S")
  data['ENABLED_FEATURES']=datos
  data['SUBSCRIPTION']=plan
  if case == 'Upgrade':
    data["UPGRADE_DATE"] = date
  else:
    data["DOWNGRADE_DATE"] = date

"""Permite ejecutar código cuando el archivo se ejecuta como un script"""
if __name__ == "__main__":
  app()
