# -*- coding: utf-8 -*-

import requests
import time
import math

from bs4 import BeautifulSoup

class CityNotFoundError(Exception):
    def __init__(self):
        super().__init__("Nije pronađen traženi grad.")

class SiteUnavailable(Exception):
    def __init__(self, e):
        super().__init__(e)

class monitoringzraka(object):
    url = 'http://monitoringzrakatk.info/'
    url_news = 'http://monitoringzrakatk.info/news.html'

    gradovi = []

    def __init_(self):
        self.grad = None
        self.so2 = 0
        self.no2 = 0
        self.co = 0
        self.o3 = 0
        self.pm25 = 0
        self.h = 0
        self.p = 0
        self.t = 0
        self.ws = 0
        self.wd = 0
        self.vrijeme = None
        self.datum = None
        self.__update = None
    
    def prikupi_gradove(self):
        ''' Prikupi sve moguće gradove sa stranice '''
        try:
            page = requests.get(self.url)

        except requests.RequestException as e:
            return e

        soup = BeautifulSoup(page.content, 'lxml')
        values = soup.find_all('ul', class_ = "nav nav-pills nav-justified")

        for a in values[0].find_all('a', href = True):
            self.gradovi.append(a['href'][:-5])

        return self.gradovi
        
    def prikupi_podatke(self, grad):
        if grad in gradovi:
            self.grad = grad
        else:
            raise CityNotFoundError
            return 

        try:
            page = requests.get('{0}{1}.html'.format(self.url, self.grad))
        except requests.RequestException as e:
            raise SiteUnavailable(e)

        soup = BeautifulSoup(page.content, 'lxml')
        self.__update = time.localtime(time.time())
        self.vrijeme = time.strftime('%H:%M', time.strptime(soup.find_all('strong')[0].get_text(), '%d.%m.%Y %H:%M'))
        self.datum = time.strftime('%Y-%m-%d', time.strptime(soup.find_all('strong')[0].get_text(), '%d.%m.%Y %H:%M'))

        values = soup.find_all('div', class_ = 'col-xs-5 data-values_value ie-old-hidden')
        try:
            self.so2 = float(values[0].find('span').get_text())
        except:
            self.so2 = 0

        try:
            self.no2 = float(values[1].find('span').get_text())
        except:
            self.no2 = 0

        try:
            self.co = float(values[2].find('span').get_text())
        except:
            self.co = 0

        try:
            self.o3 = float(values[3].find('span').get_text())
        except:
            self.o3 = 0

        try:
            self.pm25 = float(values[4].find('span').get_text())
        except:
            self.pm25 = 0

        try:
            self.h = float(values[5].find('span').get_text())
        except:
            self.h = 0

        try:
            self.p = float(values[6].find('span').get_text())
        except:
            self.p = 0

        try:
            self.t = float(values[7].find('span').get_text())
        except:
            self.t = 0

        try:
            self.ws = float(values[8].find('span').get_text())
        except:
            self.ws = 0

        try:
            self.wd = float(values[9].find('span').get_text())
        except:
            self.wd = 0        