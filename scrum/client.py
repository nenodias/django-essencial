# *-* coding: utf-8 *-*
import datetime
import requests, pprint

usuario = 'nenodias'
senha = '123'

autorizacao = (usuario, senha)

#Metodo para validar retorno
def valida_response(response):
	if response.status_code >= 200 and response.status_code <=207:
		return True
	raise Exception('Erro atualização retornou status:%s \nmensagem: %s'%(response.status_code, response.json()))

#Pegando urls da api
response = requests.get('http://localhost:8000/api/')
api = response.json()

#Inserindo Sprint
today = datetime.date.today()
two_weeks = datetime.timedelta(days=14)

data = {"name":"Current Sprint","end":today+two_weeks}

response = requests.post(api['sprints'], data=data, auth=autorizacao)
valida_response(response)
sprint = response.json()

#Inserindo Task
data = {"name":"Current Task", "sprint": sprint['id']}
response = requests.post(api['tasks'], data=data, auth=autorizacao)
valida_response(response)
task = response.json()

#Atualizando task
task['assigned'] = usuario
task['status'] = 2
task['started'] = today
response = requests.put(task['links']['self'], data=data, auth=autorizacao)
valida_response(response)
task = response.json()
