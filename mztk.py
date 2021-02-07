import requests
import time
import math

from bs4 import BeautifulSoup

gradovi = ['lukavac', 'bkc', 'skver', 'bukinje', 'gradacac', 'doboj-istok', 'gracanica', 'srebrenik', 'celic', 'banovici', 'zivinice', 'kalesija', 'sapna', 'teocak', 'kladanj', 'mobilna']
mobilna_gradovi = ['gradacac', 'doboj-istok', 'gracanica', 'srebrenik', 'celic', 'banovici', 'kalesija', 'sapna', 'teocak', 'kladanj']
values = ['so2', 'no2', 'co', 'o3', 'pm25', 'h', 'p', 't', 'ws', 'wd']
units = ['µg/m³', 'µg/m³', 'mg/m³', 'µg/m³', 'µg/m³', '%', 'mBar', '°C', 'm/s', '°']

url = 'http://monitoringzrakatk.info/'
url_news = 'http://monitoringzrakatk.info/news.html'

class mztk:
    ''' 
    Prikupljanje podataka o kvaliteti zraka s stranice www.monitoringzrakatk.info za grad Lukavac 
    * Ukoliko traženi podatak nije dostupan u tom trenutku, njegova vrijednost će biti 0

    Funkcije:
        - __init__(grad)                        - Pri inicijalizaciji, potrebno je specificirati traženi grad s liste
        - posljednja_provjera()                 - Posljednji puta provjeren sadržaj stranice (uljepšani prikaz vremena "prije...")
        - posljednja_provjera_klasicno()        - Posljednji puta provjeren sadržaj stranice (u klasičnom formatu)
        - posljednja_provjera_mztk()            - Posljednji podaci na MZTK stranici ("prije...")
        - posljednja_provjera_mztk_klasicno()   - Posljednji podaci na MZTK stranici (u klasičnom formatu)
        - prikupi_vrijednosti()                 - Prikupi ponovno podatke s stranice
        - prikupi_vijesti()                     - Prikupi obavještenja s stranice (vraća u obliku liste rezultata klase News)
        - prikazi_gradove()                     - Vraća listu mogućih gradova

    Klase:
        - News                      - sadrži podatke o obavještenjima
            ° date                  - datum obavjesti
            ° content_raw           - izvorni sadržaj, bez formatiranja
            ° content_no_html       - sadržaj s uklonjenim html tagovima, i ubačenih prijeloma na određenim mjestima

    Varijable:
        so2                     - [µg/m³]   - SO2
        no2                     - [µg/m³]   - NO2
        co                      - [mg/m³]   - CO
        o3                      - [µg/m³]   - O3
        pm25                    - [µg/m³]   - Suspendovane čestice veličine PM2.5
        h                       - [%]       - Relativna vlažnost
        p                       - [mBar]    - Zračni pritisak
        t                       - [°C]      - Temperatura zraka
        ws                      - [m/s]     - Brzina vjetra
        wd                      - [°]       - Smjer vjetra
        update                  - [seconds since epoch]
        mztk_update             - [struct_time]
        mztk_vrijeme            - [string]
        mztk_datum              - [string]
        mztk_update_pretty      - [string]
    '''

    class News:
        def __init__(self, date, content):
            self.date = date
            self.content_raw = content
            self.content_no_html = self.__strip_html(content)

        @staticmethod
        def __strip_html(content):
            ''' Uklanja sve HTML tagove, i vrši prostije formatiranje '''
            # Može se ispraviti s regexom, ali zbog \n na nekim "logičnim" mjestima,
            # bi se svelo na isti sistem s više regex izraza... 
            # Ovako je makar preglednije

            replace_dict = [
                ['<ul class="minus">', ''],
                ['</ul>', ''],
                ['<li>', '\n'],
                ['</li>', ''],
                ['<p class="paragraph">', '\n'],
                ['<p class="paragraph"/>', ''],
                ['<div>', ''],
                ['</div>', ''],
                ['<p>', ''],
                ['</p>', '\n'],
                [',\n', ', '],
                [' a)', '\na)'],
                [' b)', '\nb)'],
                [' c)', '\nc)'],
                [' d)', '\nd)'],
                [' e)', '\ne)'],
                [' f)', '\nf)'],
                [' g)', '\ng)'],
                [' h)', '\nh)'],
                [' i)', '\ni)'],
                [' j)', '\nj)'],
                ['\t', ' '],
                ['\n\n\n', '\n'],
                ['\n\n', '\n']]

            for r in replace_dict:
                content = content.replace(r[0], r[1])

            return content

    def __init__(self, grad):
        ''' Osnovni podaci  '''
        if not grad.lower() in gradovi:
            raise Exception('Nije pronađen specificiran grad. :/')
            return

        if grad in mobilna_gradovi:
            self.__mobilna = True
        else:
            self.__mobilna = False

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
        self.grad = grad.lower()
    
        ''' epoch kada su prikupljeni podaci '''
        self.__update = None

        ''' struct_time prikupljenih podataka  '''
        self.update = None

        ''' Daljnje vrijednosti s MZTK '''
        self.__mztk_update = None
        self.mztk_vrijeme = None
        self.mztk_datum = None

        ''' Pri inicijalizaciji klase prikupi podatke '''
        self.prikupi_podatke()

    @staticmethod
    def prikazi_gradove():
        ''' Prikaži listu svih mogućih gradova '''
        return (g.capitalize() for g in gradovi)

    def posljednja_provjera(self):
        ''' Prikaži kada su zadnji puta prikupljeni podaci (uljepšano)'''
        return  self.__pretty(time.time() - self.__update)

    def posljednja_provjera_klasicno(self):
        ''' Prikaži kada su zadnji puta prikupljeni podaci u formatu "%d. %m. %Y %H:%M"'''
        return time.strftime("%d. %m. %Y %H:%M", time.localtime(self.__update))

    def posljednja_provjera_mztk(self):
        ''' Vrijeme i datum posljednjih podataka sa stranice (uljepšano) '''
        return self.__pretty(time.time() - time.mktime(self.mztk_update))

    def posljednja_provjera_mztk_klasicno(self):
        ''' Vrijeme i datum posljednjih podataka sa stranice (klasično) '''
        return time.strftime("%d. %m. %Y %H:%M", self.mztk_update)


    @staticmethod
    def __pretty(seconds, exact = False):
        ''' Uljepšaj vrijednosti datuma i vremena '''

        # 365.2425 dana u godini
        # tačnije 365.242375
        # (prijestupna godina - djeljivo s 4, nije djeljivo s 100)
        # (ali ne uključujući godine 2000 i 2400...)
        # ... ali je ovo višak podataka... 

        year = int(math.floor(seconds / 31556926))
        remainder = seconds % 31556926

        days = int(math.floor(remainder / 86400))
        remainder = seconds % 86400

        hours = int(math.floor(remainder / 3600))
        remainder = seconds % 3600

        minutes = int(math.floor(remainder / 60))
        seconds = int(math.floor(remainder % 60))

        if exact is True:
            if year == 0 and days == 0 and hours == 0:
                return "00:{0:02d}:{1:02d}".format(minutes, seconds)
            elif year == 0 and days == 0:
                return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
            elif year == 0:
                return "{0}d {1:02d}:{2:02d}:{3:02d}".format(days, hours, minutes, seconds)
            else:
                return "{0}y {1}d {2:02d}:{3:02d}:{4:02d}".format(
                    year, days, hours, minutes, seconds)
        else:
            if year == 0 and days == 0 and hours == 0 and minutes == 0 and seconds < 10:
                return "Prije par sekundi"
            elif year == 0 and days == 0 and hours == 0 and minutes == 0 and seconds < 30:
                return "Prije pola minute"
            elif year == 0 and days == 0 and hours == 0 and minutes < 1:
                return "Prije minut"
            elif year == 0 and days == 0 and hours == 0 and minutes < 5:
                return "Prije par minuta"
            elif year == 0 and days == 0 and hours == 0 and minutes < 10:
                return "Prije manje od deset minuta"
            elif year == 0 and days == 0 and hours == 0 and minutes < 30:
                return "Prije manje od pola sata"
            elif year == 0 and days == 0 and hours == 0 and minutes < 40:
                return "Prije pola sata"
            elif year == 0 and days == 0 and hours < 1:
                return "Prije sat"
            elif year == 0 and days == 0 and hours < 2:
                return "Prije dva sata"
            elif year == 0 and days == 0 and hours < 12:
                return "Prije pola dana"
            elif year == 0 and days == 0:
                return "u {0}:{1}".format(hours, minutes)
            elif year == 0:
                return "prije {0}d {1:02d}:{2:02d}".format(days, hours, minutes)
            else:
                return "prije {0}g {1}d {2:02d}:{3:02d}".format(year, days, hours, minutes)

    def prikupi_podatke(self):
        ''' Prikupljanje podataka s http://monitoringzraka.tk '''
        try:
            if not self.__mobilna:
                page = requests.get("{0}{1}.html".format(url, self.grad))
            else:
                page = requests.get("{0}mobilna-{1}.html".format(url, self.grad))

        except: 
            return 

        soup = BeautifulSoup(page.content, 'lxml')
        self.__update = time.time()
        self.update = time.localtime(time.time())
        self.mztk_update = time.strptime(soup.find_all('strong')[0].get_text(), '%d.%m.%Y %H:%M')
        self.mztk_vrijeme = time.strftime('%H:%M', self.mztk_update)
        self.mztk_datum = time.strftime('%Y-%m-%d', self.mztk_update)

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

    def prikupi_obavjestenja(self):
        ''' Prikupi zadnje vijesti s stranice '''
        try:
            page = requests.get(url_news)
        except: 
            return 

        soup = BeautifulSoup(page.content, 'lxml')
        news = soup.find_all('div', class_ = 'col-md-12 alert alert-warning')

        results = []

        for new in news:
            date = str(new.find('h3'))[4:-5]
            content = str(new)[62:]

            results.append(self.News(date, content))

        return results 

    def __str__(self):
        return "Trenutno stanje zraka: SO2: {0} [µg/m³], NO2: {1} [µg/m³], CO: {2} [mg/m³], O3: {3} [µg/m³], PM2.5: {4} [µg/m³], rel. vlažnost: {5} [%], pritisak: {6} [mBar], temperatura: {7} [°C], brzina vjetra: {8} [m/s], smjer vjetra: {9} [°]. Podaci prikupljeni {10} ({11} {12}).".format(
            self.so2,
            self.no2,
            self.co,
            self.o3,
            self.pm25,
            self.h,
            self.p,
            self.t,
            self.ws,
            self.wd,
            self.__pretty(time.time() - time.mktime(self.mztk_update)).lower(),
            self.mztk_datum,
            self.mztk_vrijeme)