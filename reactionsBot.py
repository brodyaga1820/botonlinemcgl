import config 
import time
import discord
from discord.ext import commands
import getOnline
from bs4 import BeautifulSoup
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sqlite3
import os

driver = getOnline.opt()
getOnline.autorize(driver)
db = sqlite3.connect('server.db')
sql = db.cursor()
clans = ['Alliance', 'AllianceA', 'AlphaCentauri', 'HauntedFamily', 'Hell', 'MonteCarlo', 'NightRobbers', 'OrdenChaos', 'ProjectTRoN', 'Revenant', 'Storm', 'TRIADA', 'TRoN', 'TheFreezed', 'TheRegents', 'ZERG']
class MyClient(discord.Client):
	async def on_raw_reaction_add(self, payload):
		if payload.message_id == config.PostID:
			channel = self.get_channel(payload.channel_id) # получаем объект канала
			message = await channel.fetch_message(payload.message_id) # получаем объект сообщения
			emoji = payload.emoji.name # эмоджик который выбрал юзер
			if emoji == 'all':
				mess = ['```']
				mymessage = []
				j=0
				playersToPrint = getOnline.getOnlineAllClan(getOnline.getAllOnline(), clans, sql)
				for i in playersToPrint:
					if len(mess[j])+len(str(i))>1950:
						mess.append('```')
						j+=1
					else:
						mess[j]+=(str(i) + '\n')
				for k in range(len(mess)):
					try:
						mymessage.append(await channel.send(str(mess[k]+str('```'))))
					except:
						t = 'null'
				time.sleep(120)
				for k in range(len(mymessage)):
					await mymessage[k].delete()
						
			else:
				playersToPrint = getOnline.getOnlineClan(getOnline.getAllOnline(), getOnline.nicksFromTable(sql, emoji), emoji)
				mess = '** ['+emoji+'] Общее количество игроков: ' + str(len(playersToPrint)) +'\n' + '**' 
				for i in playersToPrint:
					mess += (str(i) + '\n')
				mymessage = await channel.send(mess)
				time.sleep(60)
				await mymessage.delete()
bot = MyClient()
token = os.environ.get('BOT_TOKEN')
bot.run(str(token))


           
