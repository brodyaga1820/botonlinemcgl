from bs4 import BeautifulSoup
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sqlite3
import getOnline

def main():
	driver = getOnline.opt()
	db = sqlite3.connect('server.db')
	sql = db.cursor()
	getOnline.compare(getOnline.getClansArr(), getOnline.getClanInfo(getOnline.getClansArr()), 16, sql, db, driver)

if __name__ == '__main__':
	main()