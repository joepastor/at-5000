#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Joe - jlopez.mail@gmail.com

from conexion import *
from time import strftime,localtime
import os
import time
import subprocess

# INICIALIZACION
llamados=0
inicio=830
fin=2030
# Opciones de primero : celular, red
primero="red"

# CONFIGURACION
dummy=1
if len(sys.argv)>1:
	if sys.argv[1]=="start":
		dummy=0
teldummy=1540727071
diroutgoing="/var/spool/asterisk/outgoing/"
dirapp="/root/at-5000"
dirwww="/var/www/html"

if dummy==1:
	diroutgoing="/var/spool/asterisk/probandollamadas/"

def enproceso(extension):
	if len(os.listdir(diroutgoing)) > 0:
		if extension==1101:
			extension_enproceso=1152
		else:
			extension_enproceso=extension
		os.system("grep 'Extension: %s' %s* | wc -l > %s/enproceso" % (extension_enproceso,diroutgoing,dirapp))
		inp=open("%s/enproceso" % dirapp,"r")
		for linea in inp.readlines():
			enproceso=int(linea)
		inp.close()
		os.system("rm %s/enproceso" % dirapp)
		return enproceso
	else:
		return 0

def agentesconectados(extension):
	os.system("/usr/sbin/asterisk -rx 'queue show %s' | grep 'dynamic' | grep -v 'Unavailable' -c > %s/cantidadagentes" % (extension,dirapp))
	inp=open("%s/cantidadagentes" % dirapp,"r")
	for linea in inp.readlines():
		agentes=int(linea)
	inp.close()
	os.system("rm %s/cantidadagentes" % dirapp)
	return agentes

def agenteslibres(extension):
	os.system("/usr/sbin/asterisk -rx 'queue show %s' | grep 'Not in use' -c > %s/agenteslibres" % (extension,dirapp))
	inp=open("%s/agenteslibres" % dirapp,"r")
	for linea in inp.readlines():
		agentes=int(linea)
	inp.close()
	os.system("rm %s/agenteslibres" % dirapp)
	return agentes

def agentesocupados(extension):
	os.system("/usr/sbin/asterisk -rx 'queue show %s' | grep 'In use' -c > %s/agentesocupados" % (extension,dirapp))
	inp=open("%s/agentesocupados" % dirapp,"r")
	for linea in inp.readlines():
		agentes=int(linea)
	inp.close()
	os.system("rm %s/agentesocupados" % dirapp)
	return agentes

if dummy==1:
	os.system("rm %s* " % diroutgoing)
while True:
	#hora="%s%s" % (localtime()[3],localtime()[4])
	hora=int(strftime("%H%M",localtime()))
	#hora=int(hora)
	ts=strftime("%D %T %a",localtime())

	session.execute("select at5000exigencia from parametros")
	exigencia=session.fetchone()

	html="<meta http-equiv=refresh content=1><body topmargin=0 leftmargin=0 rightmargin=0 bottommargin=0><table border=0 width=100% cellpadding=0 cellspacing=1><tr align=center><td>Actualizacion</td><td>Extension</td><td>Agentes</td><td>Libres</td><td>Hablando</td><td>Exigencia</td><td>Discando</td><td>Llamadas Realizadas</td><td>Base Disponible</td></tr>"

	logfile=open("%s/logs/at5000-%s.log" % (dirapp,strftime("%Y%m%d")),"a")

	session.execute("""select extension,count(*) as base from at5000 where llamar<=date_FORMAT(now(),"%Y%m%d") and llamado=0 group by 1""")
	rstcolas=session.fetchall()
	for extension,base in rstcolas:
		print "Conectados: %s" % agentesconectados(1101)
		print "En proceso: %s" % enproceso(1101)
		print "Exigencia: %s" % exigencia[0]
		print "Llamar a %i clientes:" % (agentesconectados(1101)*exigencia[0]/100)

		disponibles=agentesconectados(extension)*exigencia[0]/100
		disponibles=disponibles-enproceso(extension)

		log="%s | Extension %s - Agentes Conectados %s Libres %s Hablando %s Exigencia %s%% Llamadas en proceso %s Llamadas realizadas %s Base Disponible %s\n" % (ts,extension,agentesconectados(extension),agenteslibres(extension),agentesocupados(extension),exigencia[0],enproceso(extension),llamados,base)
		if dummy==1:
			print log
		logfile.write(log)
		html+="<tr align=center bgcolor=darkgrey><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s%%</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (ts,extension,agentesconectados(extension),agenteslibres(extension),agentesocupados(extension),exigencia[0],enproceso(extension)-agentesocupados(extension),llamados,base)
		if hora >= inicio and hora <= fin and localtime()[6] >= 0 and localtime()[6]<=4:
			if disponibles>0:
				sql="""select dpclinumero,dpapellido,dpnombres,dpptelefono,dppcelular,id from datospersonales right join at5000 on cliente=dpclinumero where llamar<=date_FORMAT(now(),"%%Y%%m%%d") and extension=%s and llamado=false limit %s""" % (extension,disponibles)
				session.execute(sql)
				recordset = session.fetchall()
				for dpclinumero,dpapellido,dpnombres,dpptelefono,dppcelular,id in recordset:
					if primero=="celular":
						if dppcelular<>"":
							telefono=dppcelular
							canal="Telular2-Out"
						else:
							if dpptelefono<>"":
								telefono=dpptelefono
								canal="Telmex-Out"
					else:
						if dpptelefono<>"":
							telefono=dpptelefono
							canal="Telmex-Out"
						else:
							if dppcelular<>"":
								telefono=dppcelular
								canal="Telular2-Out"
		
					if dummy==1:
						telefono=teldummy
						extension=6000
					if telefono<>"":
						call=""
						call+="Channel: SIP/%s/%s\n" % (canal,telefono)
						call+="MaxRetries: 0\n"
						call+="RetryTime: 300\n"
						call+="WaitTime: 20\n"
						call+="Context: from-internal\n"
						print extension
						if extension == 1101:
							call+="Extension: 1152\n"
						else:
							call+="Extension: %s\n" % extension
						call+="Priority: 1\n"
						call+="CallerID: '%s-%s %s' <%s>\n" % (dpclinumero,dpnombres,dpapellido,telefono)
						call+="Archive: Yes\n"
						f=open("%s%s.call"%(diroutgoing,dpclinumero),"w")
				        	f.write(call)
		                	        f.close()
						os.system("chmod 777 %s%s.call"%(diroutgoing,dpclinumero))
						if dummy==0:
							session.execute("update at5000 set llamado=true,timestamp=now() where id=%s" % id)
							db.commit()
						log="-"*168
						log+=" "*40+"%s Llamando a %s %s (%s)- Telefono %s - Extension %s\n" %(ts,dpnombres,dpapellido,dpclinumero,telefono,extension)
						log+="-"*168
						log+="\n"
						if dummy==1:
							print log
						logfile.write(log)
						llamados=llamados+1
		else:
			#log="*"*40+"FUERA DE HORARIO"+"*"*40
			#log+="\n"
			if dummy==1:
				print log
			#logfile.write(log)
	logfile.close()
	html+="</table>"
	fhtml=open("%s/estado.html" % dirwww,"w")
	fhtml.write(html)
	fhtml.close()
	time.sleep(1)
