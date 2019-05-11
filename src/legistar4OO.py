''' legistar4OO

Created on May 7, 2019

@author: rik
'''

import json
import os
import re 
import sqlite3 as sqlite
import sys

# import requests
# import pyodata

import urllib.request

## utilities

def getDBSize(currDB):
	'''also return number of replicates 
	'''
	curs = currDB.cursor()
	stats = {}
	for tblName in DBTableSpecTbl.keys():
		sql = 'SELECT Count(*) FROM %s' % (tblName)
		curs.execute(sql)
		res = curs.fetchall()
		stats[tblName] = res[0][0]
	return stats

DBTableSpecTbl = {'municipality':
				  """CREATE TABLE IF NOT EXISTS municipality (
				  muniID	INTEGER PRIMARY KEY,
				  name      TEXT,
				  publicURL TEXT,
				  client	TEXT
				  )""",
				  'body':
				  """CREATE TABLE IF NOT EXISTS body (
				  bodyID	INTEGER PRIMARY KEY,
				  muniID    INTEGER,
				  name	TEXT,
				  contactName TEXT,
				  phone TEXT,
				  email TEXT
				  )""",
				  'event':
				  """CREATE TABLE IF NOT EXISTS event (
				  eventID INTEGER PRIMARY KEY,  
				  bodyID	INTEGER,
				  date	TEXT,
				  siteURL TEXT,
				  agendaURL	TEXT,
				  minutesURL TEXT
				  )""",
				  'eventItem':
				  """CREATE TABLE IF NOT EXISTS eventItem (
				  eitemID	INTEGER PRIMARY KEY,
				  eiEventId INTEGER,
				  agendaSequence INTEGER,
				  agendaNumber INTEGER,
				  minutesSequence INTEGER
				  )""",
				  'eiAttachment':
				  """CREATE TABLE IF NOT EXISTS eiAttachment (
				  eiaIdx INTEGER PRIMARY KEY,
				  eiaEventId INTEGER,
				  eiaItemId INTEGER,
				  matterId INTEGER,
				  eiaModDate TEXT,
				  link TEXT
				  )""",
				  'body2muni':
				   """CREATE TABLE IF NOT EXISTS body2muni (
				  b2mIdx INTEGER PRIMARY KEY,
				  bodyIdx INTEGER,
				  muniIdx INTEGER
				  )""",
				  'event2body':
				   """CREATE TABLE IF NOT EXISTS event2body (
				  e2bIdx INTEGER PRIMARY KEY,
				  eventIdx INTEGER,
				  bodyIdx INTEGER
				  )""",
				  'ei2e':
				   """CREATE TABLE IF NOT EXISTS ei2e (
				  ei2eIdx INTEGER PRIMARY KEY,
				  eiIdx INTEGER,
				  eIdx INTEGER
				  )""",
				  'eia2ei':
				   """CREATE TABLE IF NOT EXISTS eia2ei (
				  eia2eiIdx INTEGER PRIMARY KEY,
				  eiaIdx INTEGER,
				  eiIdx INTEGER
				  )""",}


def initDB(currDB):
	curs = currDB.cursor()

	for tbl in DBTableSpecTbl.keys():
		curs.execute('DROP TABLE IF EXISTS %s' % (tbl) )
		curs.execute(DBTableSpecTbl[tbl])

	# check to make sure it loaded as expected
	curs = currDB.cursor()
	curs.execute("select tbl_name from sqlite_master")
	allTblList = curs.fetchall()
	for tbl in DBTableSpecTbl.keys():
		assert (tbl,) in allTblList, "initdb: no %s table?!" % tbl

	return currDB

def postEvents(currDB,eventList):
	curs = currDB.cursor()
	ninsert = 0
	for e in eventList:
		
		try:		
			sql = 'insert into event (eventID,bodyID,date,siteURL,agendaURL,minutesURL) values(?,?,?,?,?,?)'
			valList = [e['EventId'], e['EventBodyId'], e['EventDate'],e['EventInSiteURL'],e['EventAgendaFile'],e['EventMinutesFile']]
			curs.execute(sql,tuple(valList))
			ninsert += 1
			# eventIdx = cursor.lastrowid
		except Exception as e:
			print('event', e)
			#eventIdx = -1

	print('events2db: %d/%d' % (len(eventList),ninsert))
	currDB.commit()
	
def postAllEventItems(currDB,bodyID):
	'''retrieve all eventItems associated with ALL events
	and all attachments associated with the eventItems
	'''
	
	curs = currDB.cursor()
	sql1 = '''select event.eventID from event where event.bodyID = %s''' % (bodyID)
	curs.execute(sql1)
	res = curs.fetchall()
	nEIinsert = 0
	nEIAinsert = 0
	nevent = len(res)
	for row in res:
		eid = row[0]
		eitemList = getOneEventsItems(eid)
		for eitem in eitemList:
			try:		
				sql2 = 'insert into eventItem (eitemID,eiEventID,agendaSequence,agendaNumber,minutesSequence) values(?,?,?,?,?)'
				valList = [eitem['EventItemId'], eid, eitem['EventItemAgendaSequence'],eitem['EventItemAgendaNumber'],eitem['EventItemMinutesSequence']]
				curs.execute(sql2,tuple(valList))
				nEIinsert += 1
				eiIdx = curs.lastrowid
			except Exception as e:
				print('eventItem', e)
				eiIdx = -1
				
			try:		
				sql3 = 'insert into ei2e (eiIdx,eIdx) values(?,?)'
				valList = [eiIdx,eid]
				curs.execute(sql3,tuple(valList))
			except Exception as e:
				print('ei2e', e)
				
			for attach in eitem['EventItemMatterAttachments']:
				modDate = attach['MatterAttachmentLastModifiedUtc']
				matterId = attach['MatterAttachmentId']
				link = attach['MatterAttachmentHyperlink']

				try:		
					sql4 = 'insert into eiAttachment (eiaEventId,eiaItemId,eiaModDate,matterId,link) values(?,?,?,?,?)'
					valList = [eid,eitem['EventItemId'],modDate,matterId,link]
					curs.execute(sql4,tuple(valList))
					nEIAinsert += 1
					eiaIdx = curs.lastrowid
				except Exception as e:
					print('eventItemAttach', e)
					eiaIdx = -1

				try:		
					sql5 = 'insert into eia2ei (eiaIdx,eiIdx) values(?,?)'
					valList = [eiaIdx,eiIdx]
					curs.execute(sql5,tuple(valList))
				except Exception as e:
					print('eia2ei', e)
				
					
		currDB.commit() # NB: commit after every event
		print('event %s' % eid,nEIinsert,nEIAinsert)
	print('postAllEventItems: done',nevent,nEIinsert,nEIAinsert)
				

def getEvents(bodyID,startDate):
	'''ASSUME bodyID,startDate are strings
	'''
	
	qstr = "Events?$filter=EventDate+ge+datetime'%s'+and+EventBodyId+eq+%s" % (startDate,bodyID)
	qstr1 = "Events?$filter=EventBodyId+eq+%s" % (bodyID)
	fullURL = "http://"+SERVICE_ROOT_URL+qstr1
	
	contents = urllib.request.urlopen(fullURL)
	return json.loads(contents.read())

def getOneEventsItems(eventID):
	
	# GET v1/{Client}/Events/{EventId}/EventItems?AgendaNote={AgendaNote}&MinutesNote={MinutesNote}&Attachments={Attachments}

	qstr = "Events/%s/EventItems?AgendaNote=1&MinutesNote=1&Attachments=1" % (eventID)
	fullURL = "http://"+SERVICE_ROOT_URL+qstr
	
	contents = urllib.request.urlopen(fullURL)
	return json.loads(contents.read())

def harvestEventAgenda(currDB,bodyID,pdfDir):
	'''download events' agendas
	'''
	curs = currDB.cursor()
	sql1 = '''select eventID,agendaURL from event '''
	curs.execute(sql1)
	res = curs.fetchall()
	nevent = len(res)
	nmiss = 0
	for row in res:
		eventID,url = row
		if url ==  None:
			nmiss += 1
			continue
		pdf = urllib.request.urlopen(url)
		pdfData = pdf.read()
		fname = 'agenda_%s_%05d.pdf' % (bodyID,eventID)
		with open(pdfDir+fname,'wb') as outf:
			outf.write(pdfData)
	
		print('harvestEventAgenda: ', eventID)
		
	print('harvestEventAgenda: done. NEvent=%d NMiss=%d' % (nevent,nmiss))

def harvestAttach(currDB,pdfDir):
	'''download ALL eiAttachments
	'''
	curs = currDB.cursor()
	sql1 = '''select eiaIdx,link from eiAttachment '''
	curs.execute(sql1)
	res = curs.fetchall()
	nerr = 0
	for row in res:
		eiaIdx,link = row
		try:
			pdf = urllib.request.urlopen(link)
		except Exception as e:
			print('harvestAttach',eiaIdx,link,e)
			nerr += 1
			continue
		
		pdfData = pdf.read()
		fname = 'eia_%05d.pdf' % (eiaIdx)
		with open(pdfDir+fname,'wb') as outf:
			outf.write(pdfData)
	
		print('harvestAttach: ', eiaIdx)
	print('harvestAttach: Nerr=%d / %d' % (nerr,len(res)))
	

def parseAgenda(atxt):
	''' return [(item#,topic,body)]
	'''
	
	# ASSUME items begin with item# on its own line
	items = re.split(r'^([0-9]+)$',atxt,flags=re.M)
	
	aInfoList = []
	currItemNum = None
	for item in items:
		# NB: drop preamble
		if currItemNum == None:
			currItemNum = 0
		elif re.match(r'[0-9]+',item):
			currItemNum = int(item)
		else:
			lines = item.split('\n')
			lines2 = [l.strip() for l in lines]
			lines3 = [l for l in lines if l != '']
			topic = lines3[0]
			adjournFnd = None
			for ib, l in enumerate(lines3):
				if l == 'ADJOURNMENT':
					adjournFnd = ib
					break
			if adjournFnd==None:
				body = lines3[1:]
			else:
				body = lines3[1:adjournFnd]

				
			
			aInfo = {'itemNum': currItemNum, 'topic': topic, 'body': body}
			
			aInfoList.append(aInfo)
			
	return aInfoList
	
SERVICE_ROOT_URL = 'webapi.legistar.com/v1/oakland/'	

# HACK: bootstrap of initially identified Bay Area Legistar clients
KnownLegistarClients = {'oakland': ['Oakland', 'https://oakland.legistar.com/Calendar.aspx'],
						'sanmateocounty': ['San Mateo (county)', 'https://sanmateocounty.legistar.com/Calendar.aspx'], 
						'mountainview': ['Mountain View', 'https://mountainview.legistar.com/Calendar.aspx'], 
						'cupertino': ['Cupertino', 'https://cupertino.legistar.com/Calendar.aspx'], 
						'sunnyvaleca': ['Sunnyvale. Milpitas. Palo Alto', 'https://sunnyvaleca.legistar.com/Calendar.aspx']}

def addAllMuni(currDB):
	curs = currDB.cursor()
	ninsert = 0
	for legClient,clientInfo in KnownLegistarClients.items():
		name,url = KnownLegistarClients[legClient]
		valList = [name,url,legClient]
		try:		
			sql = 'insert into municipality (name,publicURL,client) values(?,?,?)'
			curs.execute(sql,tuple(valList))
			ninsert += 1
		except Exception as e:
			print('muni', e)
		
	currDB.commit()	
	print('addAllMuni: %d/%d' % (len(KnownLegistarClients),ninsert))
		
def addBodies(currDB,legClient):

	curs = currDB.cursor()
	
	sql = '''select muniID from municipality where client="%s" ''' % (legClient)
	curs.execute(sql)
	res = curs.fetchall()
	muniIdx = res[0][0]
	
	legService = 'webapi.legistar.com/v1/' + legClient + '/'
	qstr = "Bodies" 
	fullURL = "http://" + legService + qstr
	
	contents = urllib.request.urlopen(fullURL)
	allBodies = json.loads(contents.read())

	curs = currDB.cursor()
	ninsert = 0
	for bodyInfo in allBodies:
		name = bodyInfo['BodyName']
		contactName = bodyInfo['BodyContactFullName']
		phone = bodyInfo['BodyContactPhone']
		email = bodyInfo['BodyContactEmail']
		valList = [muniIdx,name,contactName,phone,email]
		try:		
			sql = 'insert into body (muniID,name,contactName,phone,email) values(?,?,?,?,?)'
			curs.execute(sql,tuple(valList))
			bodyIdx = curs.lastrowid
			ninsert += 1
		except Exception as e:
			print('body', bodyInfo, e)

		try:		
			sql2 = 'insert into body2muni (bodyIdx,muniIdx) values(?,?)'
			valList = [bodyIdx,muniIdx]
			curs.execute(sql2,tuple(valList))
		except Exception as e:
			print('body2muni', e)
	
	currDB.commit()
	print('addBodies: %s %d/%d' % (legClient,len(allBodies),ninsert))
	
def main():

	dataDir = '/Data/c4a-Data/oakPubSafety/OakCC/'
	dbPath = dataDir + 'legistar4OO.db'
	

	initializeDB = True

	currDB = sqlite.connect(dbPath)
	
	if initializeDB:
		print('initializing DB...')
		initDB(currDB)
		
		addAllMuni(currDB)
		
		for legClient in KnownLegistarClients.keys():
			addBodies(currDB,legClient)

# 		PubSafetyBodyID = '12'
# 		CCBodyID = '230'
# 		beginDate = '2018-01-01' # '2017-01-01'
# 
# 		PSEventList = getEvents(CCBodyID,beginDate)
# 		postEvents(currDB,PSEventList)
# 		postAllEventItems(currDB,CCBodyID)
# 	
		
	sys.exit()
		
	print('Database loaded:',getDBSize(currDB))
	
	pdfDir = dataDir + 'pdfAttach/'
	if not os.path.exists(pdfDir):
		print('creating pdfAttach',pdfDir)
		os.mkdir(pdfDir)
		
	# harvestEventAgenda(currDB, CCBodyID, pdfDir)
	# harvestAttach(currDB,pdfDir)
	
	tstAgendaFile = '/Data/c4a-Data/oakPubSafety/OakCC/pdfTxt/agenda_230_08177.txt'
	tstAgendaTxt = open(tstAgendaFile).read()
	
	agendaInfoList = parseAgenda(tstAgendaTxt)
	agendaSummFile = dataDir + 'agenda_230_08177.csv'
	
	with open(agendaSummFile,'w') as outs:
		outs.write('Item#,Topic,Body\n')
		for ia, ainfo in enumerate(agendaInfoList):
			# {'itemNum': currItemNum, 'topic': topic, 'body': body}
			topic = ainfo['topic']
			if len(ainfo['body']) == 0:
				bodySnip = ''
			else:
				allBody = ' '.join(ainfo['body'])
				bodySnip = allBody[:100] + ' ... ' + allBody[-100:]
			outs.write('%d,"%s","%s"\n' % (ainfo['itemNum'],topic,bodySnip))
	
	
if __name__ == '__main__':
	main()