import scrapy, os, logging, time
from scrapyrealestate.proxies import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
#from items import ScrapyrealestateItem # ERROR (es confundeix amb items al 192.168.1.100)
from scrapyrealestate.items import ScrapyrealestateItem

class IdealistaSpider(CrawlSpider):
    name = "idealista"
    allowed_domains = ["idealista.com"]
    total_time = 0
    #start_urls = data['idealista_data']['urls']

    def start_requests(self):
        #start_urls = [url + '?ordenado-por=fecha-publicacion-desc' for url in self.start_urls]
        yield scrapy.Request(f'{self.start_urls}')

    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es-ES,es;q=0.9,ca;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

    }
    }

    # Si esta activat el mode rapid, NO agafem la seguent URL
    '''if not data['speed_mode']:
        rules = (
            # Filter all the flats paginated by the website following the pattern indicated
            Rule(LinkExtractor(restrict_xpaths=("//a[@class='icon-arrow-right-after']")),
                 callback='parse',  # cridem la funcio parse de nou
                 follow=True),  # Seguim l'enllaç
        )'''

    def parse(self, response):
        start_time = time.time()
        ids = []
        same_id = False

        # Import items
        items = ScrapyrealestateItem()

        #Necesario para crear el enlace completo hacia el sitio web.
        default_url = 'https://idealista.com'
        #Pasamos la respuesta a texto con BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        #Cogemos los div de todas las viviendas de la página
        flats = soup.find_all("div", {"class": "item-info-container"})

        #Obtenemos si se de alquiler o compra a partir de la url
        if self.start_urls.split('/')[3].split('-')[0] == 'alquiler':
            type = 'rent'
        elif self.start_urls.split('/')[3].split('-')[0] == 'venta':
            type = 'buy'

        #Iteramos por cada número de vivienda de la página y tomamos los datos
        for nflat in range(len(flats)):
            #Cogemos href, título, precio, detalles
            href = flats[nflat].find(class_="item-link")['href']
            title = flats[nflat].find(class_="item-link").text.strip()
            #print(title)
            #Intentamos tomar ciudad, barrio y calle
            #En idealista puede haber 4 tipos de título, de ob obtendremos estos datos
            # Verificar si se encuentra la clase "logo-branding" dentro de <div class="item-info-container">
            if flats[nflat].find(class_="item-info-container").find(class_="logo-branding"):
            # La clase "logo-branding" está presente, continuar con la próxima vivienda
                continue
            
            neighbour = ''
            street = ''
            number = ''
            town = ''
            #Piso en Pasaje del Olivo, 12, La Maurina, Terrassa (4)
            if len(title.split(',')) == 4:
                town = title.split(',')[-1]
                number = title.split(',')[1]
                neighbour = title.split(',')[2]
                street = title.split(',')[0].split(' en ')[-1]
            #Piso en Pasaje del Olivo, La Maurina, Terrassa (3)
            elif len(title.split(',')) == 3:
                town = title.split(',')[-1]
                neighbour = title.split(',')[1]
                street = title.split(',')[0].split(' en ')[-1]
            #Ático en Centre, Terrassa (2)
            elif len(title.split(',')) == 2:
                town = title.split(',')[-1]
                neighbour = title.split(',')[0].split(' en ')[-1]  
            else:
                street = ''
                neighbour = ''
                if len(town) > 12:
                    town = town.split(' en ')[-1]
                if town[:1] == ' ':
                    town = town[1:]
            try:
                if town[0] == ' ':
                    town = town[1:]
            except:
                pass

            try:
                if ' / ' in town:
                    town = town.split(' / ')[1]
                elif '-' in town:
                    town = town.split('-')[0]
            except:
                pass

            try:
                if neighbour[0] == ' ':
                    neighbour = neighbour[1:]
            except:
                pass
            try:
                if number[0] == ' ':
                    number = number[1:]
            except:
                pass

            #buscamos posibles nombres de calles
            if len(street) > 0:
                if 'calle' in street.lower():
                    street = street
                elif 'c.' in street.lower():
                    street = street
                elif 'avenida' in street.lower():
                    street = street
                elif 'av.' in street.lower():
                    street = street
                elif 'plaza' in street.lower():
                    street = street
                elif 'via' in street.lower():
                    street = street
                elif 'gran via' in street.lower():
                    street = street
                elif 'camino' in street.lower():
                    street = street
                elif 'paseo' in street.lower():
                    street = street
                elif 'passaje' in street.lower():
                    street = street
                elif 'carretera' in street.lower():
                    street = street
                elif 'ctra.' in street.lower():
                    street = street
                else:
                    street = street

            #print(f"MUNICIPI: {town}, STREET: {street}, BARRI: {neighbour}, NUMBER: {number}")
            price = flats[nflat].find("span", {"class": "item-price h2-simulated"}).text.strip()

            details = flats[nflat].find_all("span", {"class": "item-detail"})
            # Agafem id
            try:
                id = href.split('/')[2]
                # Si la id ja era a la llista, sortim
                for id_ in ids:
                    if id_ == id:
                        same_id = True
                        break
            except:
                id = ''

            #Iteramos los elementos de detailes para identificar cada uno (hab, m², planta, hora)
            for d in details[0:3]:
                # print(d.text.strip()[1:])
                if d.text.strip()[-4:] == 'hab.':
                    rooms = d.text.strip()
                    continue
                elif d.text.strip()[-2:] == 'm²':
                    m2 = d.text.strip()
                    continue
                elif 'Planta' in d.text.strip() or 'Bajo' in d.text.strip() or 'Sótano' in d.text.strip() or 'Entreplanta' in d.text.strip():
                    floor = d.text.strip()
                    continue
                #Si alguna de las variables no existen, las creamos vacías
                #Hay pisos sin fecha o planta. Para evitar problemas asignamos variable vacía.
                else:
                    if not 'rooms' in locals(): rooms = '-'
                    if not 'm2' in locals(): m2 = '-'
                    if not 'floor' in locals(): floor = '-'

            #Si está activado, pasamos al siguiente ya que repite ids
            if same_id:
                continue
            else:
                # Add items
                items['id'] = id
                items['price'] = price
                items['m2'] = m2
                items['rooms'] = rooms
                try:
                    items['floor'] = floor  #sino peta lugares sin pisos (pe. cerdanya francesa)
                except:
                    items['floor'] = ''
                items['town'] = town
                items['neighbour'] = neighbour
                items['street'] = street
                items['number'] = number
                items['type'] = type
                items['title'] = title
                items['href'] = default_url + href
                items['site'] = 'idealista'
                ids.append(id)

                yield items

        #Mostramos log de total de páginas y tiempo
        end_time = time.time()
        self.total_time += end_time  #Sumamos el tiempo total
        #Notifiquemos paginas total al log
        #logger.info(f'PAGES SCRAPED TIME ({str(end_time -start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # Overriding parse_start_url to get the first page
    parse_start_url = parse
