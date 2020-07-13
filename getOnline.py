from bs4 import BeautifulSoup
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sqlite3
import time

def main():
	driver = opt()
	autorize(driver)
	db = sqlite3.connect('server.db')
	sql = db.cursor()
	compare(getClansArr(), getClanInfo(getClansArr()), 16, sql, db, driver)
	#printTable(sql, 'Revenant')
	#print(getAllOnline())
	clans = ['Alliance', 'AllianceA', 'AlphaCentauri', 'HauntedFamily', 'Hell', 'MonteCarlo', 'NightRobbers', 'OrdenChaos', 'ProjectTRoN', 'Revenant', 'Storm', 'TRIADA', 'TRoN', 'TheFreezed', 'TheRegents', 'ZERG']
	#getOnlineClan(getAllOnline(), nicksFromTable(sql, 'Alliance'), 'Alliance')
	playersAll = getAllOnline()
	getOnlineAllClan(playersAll, clans, sql)

def getOnlineAllClan(playersAll, clans, sql):
	players =[]
	for clan in clans:
		OneClan = getOnlineClan(playersAll, nicksFromTable(sql, clan), clan)
		players.append('[' + clan + '] Общее количество игроков: '+  str(len(OneClan)))
		players += OneClan
	return players

def getOnlineClan(playersAll, playersClan, clan):
	online = []
	for i in playersAll:
		if i[0] in playersClan:
			online.append(str('[' + clan + '] ' + i[0] + ': ' + i[1]))
			#print('[' + clan + '] ' + i[0] + ': ' + i[1])
	return online

def nicksFromTable(sql, clan): #Вывод таблицы из бд
	q = "SELECT nickname FROM {table}"
	sql.execute(q.format(table=clan))
	playersClan = []
	rows = sql.fetchall()
	for i in range(len(rows)):
		playersClan.append(str(rows[i]).split("('")[1].split("',)")[0])
	return playersClan

def getAllOnline(): #Получение онлайна со всех серверов
	urlMain = 'https://forum.minecraft-galaxy.ru/main/'
	reqMain = requests.get(urlMain)
	soupMain = BeautifulSoup(reqMain.content, 'lxml')
	online = soupMain.find_all('span', {'style':'color: yellow;'})
	serverName = soupMain.find('table', {'class':'servers-list'}).find_all('a')
	pCount = soupMain.find('table', {'class':'servers-list'}).find_all('tr')
	playersCount = pCount[len(pCount)-1].find('td').next_element.split('line: ')[1]
	playersAll = []
	for i in range(len(online)):
		if online[i].next_element !='0':
			id = online[i].find_parent('div', {'class':'spoler'}).find_all('div')[2]
			idOnline = str(id).split('online-')[1].split('">')[0]
		
			playersAll += getOnline(idOnline, serverName[i*2].next_element)
	return playersAll
	
def getOnline(id, serverName): #Получение списка игроков онлайн на заданном сервере
	urlMain = 'https://forum.minecraft-galaxy.ru/main/' + id + '/online'
	reqMain = requests.get(urlMain)
	soupMain = BeautifulSoup(reqMain.content, 'lxml')
	onlineServer = soupMain.find('body').next_element
	online = len(str(onlineServer).split('login'))-1
	worlds = str(onlineServer.text).split(']}, {')
	nickServer = [0] * int(online)
	for i in range(int(online)):
		nickServer[i] = [0] * 2
	rangeNicks = 0
	for world in worlds:
		nicks = ''
		nameWorld = serverName + '[' + world.split('"name":"')[1].split('", "b')[0]+']'
		players = world.split('}, {')[0].split('users":[')[1].split('},{')
		for a in players:
			try:
				nicks += a.split('"login":"')[1].split('","g')[0] + ' '
			except:
				t = 'null'
		massiv = nicks.split()
		for i in range(rangeNicks, rangeNicks + len(massiv)):
			nickServer[i][0] = massiv[i-rangeNicks]
			nickServer[i][1] = nameWorld
		rangeNicks += len(massiv) 
		massiv = []
	return nickServer

def getClansArr(): #Получение прошлого кoличества игроков в кланах
	file = open('clans.txt', 'r').readlines()
	count = sum(1 for line in file)
	clan = [0] * count
	for i in range(count):
		clan[i] = [0] * 3
	for i in range(count):
		clan[i][0] = file[i].split('|')[0]
		clan[i][1] = file[i].split('|')[1]
		clan[i][2] = file[i].split('|')[2].split('\n')[0]
	return clan

def getClanInfo(clan): #Получение текущего количества игроков в кланах
	array = []
	for i in range(16):
		array.append(clan[i][0])
	clanNew = [0] * 60
	for i in range(60):
		clanNew[i] = [0] * 2
	startLen = 1
	len = 21
	urlsClan = ['https://forum.minecraft-galaxy.ru/clans/', 'https://forum.minecraft-galaxy.ru/clans/0/1', 'https://forum.minecraft-galaxy.ru/clans/0/2']
	for j in range(0, 3):
		reqClan = requests.get(urlsClan[j])
		soupClan = BeautifulSoup(reqClan.content, 'lxml')
		table = soupClan.find('table', {'class':'topics clans-table'})
		trClan = table.find_all('tr')
		k = 1
		try:
			for i in range(startLen, len):
					if trClan[k].find('a').next_element in array:
						clanNew[i-1][0] = trClan[k].find('a').next_element
						clanNew[i-1][1] = trClan[k].find_all('td')[3].next_element
					k+=1
		except:
			t = 'null'
		len+=21
		startLen +=20

	while [0, 0] in clanNew:
			clanNew.remove([0, 0])
	return clanNew

def compare(clan, clanNew, count, sql, db, driver): #Сравние числа игроков в кланах
	try:
		autorize(driver)
	except:
		t = 'null'
	clan.sort()
	clanNew.sort()
	id = []
	names = []
	for i in range(count):
		if clan[i][2] != clanNew[i][1]:
			id.append(clan[i][1])
			names.append(clanNew[i][0])
			clan[i][2]=clanNew[i][1]
			try:
				nameClan = str(clan[i][0].split()[0]+clan[i][0].split()[1])
			except:
				nameClan = str(clan[i][0])
			addDataBaseClan(sql, db, nameClan, findNicknames(driver, round(int(clan[i][2])//20)+1, clan[i][2], clan[i][1]))
	#print(names)
	printToFile(clan, count)
	time.sleep(3600)
	compare(getClansArr(), getClanInfo(getClansArr()), 16, sql, db, driver)

def printToFile(clan, count): #Обновление информации в файле
	file = open('clans.txt', 'w')
	for i in range(count):
		file.write(clan[i][0]+'|'+clan[i][1]+'|'+clan[i][2]+'\n')
	file.close()

def opt(): #Настройки браузера
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	chrome_prefs = {}
	options.experimental_options["prefs"] = chrome_prefs
	chrome_prefs["profile.default_content_settings"] = {"images": 2}
	chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
	driver = webdriver.Chrome(options=options)
	return driver

def autorize(driver): #Авторизация на форуме
	driver.get('https://forum.minecraft-galaxy.ru/guilogin/')
	driver.find_element_by_name('login').send_keys('NoWayBack')
	driver.find_element_by_name('pass').send_keys('qwerty')
	driver.find_element_by_class_name("btn").click()

def memRange(driver, idClan): #Определение количества членов в клане
	driver.get('https://forum.minecraft-galaxy.ru/claninfo/' + idClan)
	members = driver.find_element_by_class_name('frame').find_element_by_tag_name('td').text
	memRange = members.split('Членов: ')[1].split('Уровень')[0]
	return memRange
def getLeader(driver, idClan): #oпределение лидера клана
	driver.get('https://forum.minecraft-galaxy.ru/claninfo/' + idClan)
	leaderF = driver.find_element_by_class_name('frame').find_element_by_tag_name('td').text
	leader = leaderF.split('Лидер: ')[1].split("\n")[0]
	return leader

def findNicknames(driver, pageRange, memRange, idClan): #Запись ников и отряда 
	players = [0] * 2
	for i in range(2):
		players[i] = [0] * (int(memRange)+1)
	for n in range(0, pageRange):
		driver.get('https://forum.minecraft-galaxy.ru/clanmembers/'+ idClan + '/' + str(n)) 
		for i in range (1, 21):
			try:
				tr = driver.find_elements_by_tag_name('tr')[i]
				players[0][i+20*n] = str(tr.find_element_by_tag_name('a').text)
				#players[1][i+20*n]=  str(tr.find_elements_by_tag_name('td')[1].text)
			except:
				t='null'
	players[0][0] = getLeader(driver, idClan)
	#players[1][0] = 'лидер'
	return players
			
def printTable(sql, clan): #Вывод таблицы из бд
	q = "SELECT * FROM {table}"
	sql.execute(q.format(table=clan))
	rows = sql.fetchall()
	for row in rows:
		print (row)
def dropTable(sql, db, clan_name):
	q = """DROP TABLE {table}"""
	sql.execute(q.format(table=clan_name))
	db.commit()

def addDataBaseClan(sql, db, user_clan, players): #Запись игроков в таблицу
	file = open('log.txt', 'a')
	qw = """CREATE TABLE IF NOT EXISTS {table} (
		nickname TEXT PRIMARY KEY
	);"""
	qwe = """SELECT nickname FROM {table} where nickname={nickname}"""
	q = """INSERT INTO {table} VALUES(?)"""
	printed = """SELECT nickname FROM {table}"""
	deleted = """DELETE FROM {table} WHERE nickname = {nickname}"""
	sql.execute(qw.format(table=user_clan))
	db.commit()
	items = sql.execute(printed.format(table=user_clan)).fetchall()
	for i in range(len(items)):
		item = (str(items[i]).split("('")[1].split("',)")[0])
		if item in players[0]:
			players[0].remove(item)
		else:
			sql.execute(deleted.format(table=user_clan, nickname = str("'" + item + "'")))
			db.commit()
			file.write('Игрок '+ item + ' покинул клан ' + user_clan+ '\n')
			print('Игрок '+ item + ' покинул клан ' + user_clan)
	try:
		for i in range(len(players[0])):
			sql.execute(q.format(table=user_clan), [players[0][i]])
			db.commit()
			file.write(players[0][i] + ' вступил в клан ' + user_clan + '\n')
			print(players[0][i] + ' вступил в клан ' + user_clan)
	except:
		t='null'
	file.close()
			


if __name__ == '__main__':
	main()