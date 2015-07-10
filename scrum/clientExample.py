# *-* coding: utf-8 *-*
import requests as r
import json

cabecalho = {"Accept":"application/json", "Content-Type":"application/json"}

dados = {"username":"nenodias","password":"123"}
json_retorno = None

sessao = r.session()
requisicao = r.Request(url="http://localhost:8000/api/token/",method="post", headers=cabecalho, data=json.dumps(dados))
requisicao_preparada = requisicao.prepare()
retorno = sessao.send(requisicao_preparada)
if retorno.headers['Content-Type'] == "application/json":
	json_retorno = json.loads(retorno.text)
	cabecalho['Authorization'] = 'Token %s'%(json_retorno.get('token'))
	requisicao = r.Request(url="http://localhost:8000/api/users/",method="get", headers=cabecalho)
	requisicao_preparada = requisicao.prepare()
	retorno = sessao.send(requisicao_preparada)
	print(retorno.text)



with open('saida.html','w') as arquivo:
	arquivo.write(retorno.text.encode('iso-8859-1'))
	arquivo.flush()