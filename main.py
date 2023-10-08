#!/usr/bin/python3
import sys, subprocess, telebot, time, os.path, platform, os, logging, uuid, urllib.request, json, random
import scrapy.scrapyrealestate as db_module
from os import path
from art import *
from unidecode import unidecode

__author__ = "mferark"
__license__ = "GPL"
__version__ = "2.0.5"

def init_logs():
    global logger
    try:
        log_level = data['log_level'].upper()
    except:
        log_level = 'INFO'

    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level == 'INFO':
        log_level = logging.INFO
    elif log_level == 'WARNING':
        log_level = logging.WARNING
    elif log_level == 'ERROR':
        log_level = logging.ERROR
    elif log_level == 'CRITICAL':
        log_level = logging.CRITICAL

    #create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    #crear un controlador de consola y establecer el nivel para depurar
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    #crear formateador
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',"%Y-%m-%d %H:%M:%S")
    
    #agregar formateador al canal
    ch.setFormatter(formatter)

    #agregar canal al registrador
    logger.addHandler(ch)

    return logger


def del_json(dir):
    #Si existen fecha eliminamos los json que pueda haber
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        os.remove(os.path.join(dir, f))


def del_json_flats(dir):
    #Si existen fecha eliminamos los json que pueda haber
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        if f != 'config.json':
            os.remove(os.path.join(dir, f))

def mix_list(original_list):
    list = original_list[:]
    longitud_list = len(list)
    for i in range(longitud_list):
        index_random = random.randint(0, longitud_list - 1)
        temporal = list[i]
        list[i] = list[index_random]
        list[index_random] = temporal
    return list

def get_config():
    #os.chdir('../scrapyrealestate/scrapyrealestate')
    #Si no existe el archivo de configuración tomamos los datos de la web
    if not os.path.isfile('./data/config.json'):
        #Miremos si existe el directorio data y logs, sino lo creamos.
       if not os.path.exists('data'):
           os.makedirs('data')
       pid = init_app_flask()  #iniciar flask a localhost:8080
       get_config_flask(pid)  #tomamos los datos de la configuración
    else:
        with open('./data/config.json') as json_file:
            global data
            data = json.load(json_file)

def check_config(db_client, db_name):
    #creamos el objeto para enviar tg
    tb = telebot.TeleBot('6593481238:AAGyfrw7OsEl_7lwq_cj8iIDH9EIgFi0j54')

    #Si no existe el archivo scrapy.cfg, salimos
    if not path.exists("scrapy.cfg"):
        logger.error("NOT FILE FOUND scrapy.cfg")
        sys.exit()

    #comprobar URL
    urls = get_urls(data)
    urls_ok = ''
    urls_text = ''
    db_urls = ''
    urls_ok_count = 0

    #Crear una URL del portal
    for portal in urls:
        for url in urls[portal]:
            # Miremos si hay más de una url por portal
            # Si tenemos mas de x urls, salimos
            # if len(urls[portal]) > 1:
            #     logger.error(f"MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}")
            #     info_message = tb.send_message(data['telegram_chatuserID'], f"<code>Loading ...</code>\n"
            #                                                                 f"\n"
            #                                                                 f"<code>Scrapy \n</code>"
            #                                                                 f"\n"
            #                                                                 f"<code>MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}</code>\n",
            #                                    parse_mode='HTML')
            #     sys.exit()
            # Si te mes de 3 parts es que es url llarga i la guardem a la llista de ok
            # url = url[0] if isinstance(url, list) else url
            # print(url)
            if len(url.split('/')) > 2:
                portal_url = url.split('/')[2]
                portal_name = portal_url.split('.')[1]
                urls_ok_count += 1
                urls_ok += f' <a href="{url}">{portal_name}</a>    '
                db_urls += f'{url};'
                try:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[-4]}\n"
                except:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[-3]}\n"

    # Si tenim mes de x urls, sortim
    # if urls_ok_count > 4:
    #     logger.error(f"MAXIM URLS (4) YOU HAVE ({urls_ok_count})")
    #     info_message = tb.send_message(data['telegram_chatuserID'], f"<code>Loading...</code>\n"
    #                                                                 f"\n"
    #                                                                 f"<code>Scrapy \n</code>"
    #                                                                 f"\n"
    #                                                                 f"<code>MAXIM URLS (4) YOU HAVE ({urls_ok_count})</code>\n",
    #                                    parse_mode='HTML')
    #     sys.exit()

    if not data['telegram_chatuserID'] is None:
        try:
            if data['start_msg'] == 'True':
                info_message = tb.send_message(data['telegram_chatuserID'], f"<code>Loading...</code>\n"
                                                                            f"\n"
                                                                            f"<code>ScrapyBot \n</code>"
                                                                            f"\n"
                                                                            f"<code>REFRESH   <b>{data['time_update']}</b>s</code>\n"
                                                                            f"<code>MIN PRICE <b>{data['min_price']}€</b></code>\n"
                                                                            f"<code>MAX PRICE <b>{data['max_price']}€</b> (0 = NO LIMIT)</code>\n"
                                                                            f"<code>URLS      <b>{urls_ok_count}</b>  →   </code>{urls_ok}\n",
                                               parse_mode='HTML'
                                               )
            else:
                info_message = tb.send_message(data['telegram_chatuserID'],
                                               f"LOADING... ScrapyBot \n")
        # Si no se ha enviado el mensaje de telegramo correctamente, salimos
        except telebot.apihelper.ApiTelegramException:
            logger.error('TELEGRAM CHAT ID IS NOT CORRECT OR BOT @scrapyrealestatebot NOT ADDED CORRECTLY TO CHANNEL')
            sys.exit()

        # data
        data_host = {
            'id': str(uuid.uuid4())[:8],
            'chat_id': info_message.chat.id,
            'group_name': info_message.chat.title,
            'refresh': data['time_update'],
            'min_price': data['min_price'],
            'max_price': data['max_price'],
            'urls': db_urls,
            'host_name': platform.node(),
            'connections': 0,
            'so': platform.platform()
        }

        #Si ha funcionado enviamos datos
        logger.info(f"TELEGRAM {info_message.chat.title} CHANNEL VERIFIED")

        #enviamos datos
        #comprobamos si ya existe una conexión igual
        query_dbcon = db_module.query_host_mongodb(db_client, db_name, 'sr_connections', data_host, logger)
        if not len(query_dbcon) > 0:
            # creem el registre a mongodb
            db_module.insert_host_mongodb(db_client, db_name, 'sr_connections', data_host, logger)
        #Si ya existe actualizar el valor de conexiones
        else:
            db_module.update_host_mongodb(db_client, db_name, 'sr_connections', query_dbcon[0], logger)

    else:
        logger.error('TELEGRAM CHAT ID IS EMPTY')
        sys.exit()

    return info_message


def checks():
    # Mirem el time update
    if int(data['time_update']) < 300:
        logger.error("TIME UPDATE < 300")
        sys.exit()
    time.sleep(0.05)
    db_client = db_module.check_bbdd_mongodb(config_db_mongodb, logger)  #comprobamos la conexión con la bbdd
    info_message = check_config(db_client, config_db_mongodb['db_name'])  #Comprobamos parámetros configuración
    return db_client, info_message


def check_url(url):
    try:
        url_code = urllib.request.urlopen(url).getcode()
    except:
        url_code = 404

    return url_code


def init_app_flask():
    #comprobamos si el servidor está encendido.
    #si no encontramos ninguna página en localhost:8080 ejecutamos el servidor
    localhost_code = check_url("http://localhost:8080")
    if localhost_code != 200:
        try:
            # os.system('python ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python ./scrapyrealestate/flask_server.py &', shell=True)
        except:
            # os.system('python3 ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python3 ./scrapyrealestate/flask_server.py &', shell=True)
        # proces_server.wait()
        pid = proces_server.pid
        real_pid = pid + 1  # +1 perque el pid real sempre es un numero mes
        # proces_server.terminate()
    else:
        real_pid = os.popen('pgrep python ./scrapyrealestate/flask_server.py').read()

    return real_pid


def get_config_flask(pid):
    while True:
        try:
            #si encontramos info en localhost:8080/data guardamos los datos y salimos del bucle
            with open('./data/config.json') as json_file:
                global data
                data = json.load(json_file)
                os.system(f'kill {pid}')  #matem el proces del servidor web
                break
        except:
            pass
        time.sleep(1)


def get_urls(data):
    urls = {}

    # sino hi ha urls, sortim
    if data.get('url_idealista', '') == '' and data.get('url_pisoscom', '') == '' and data.get('url_fotocasa', '') == '' and data.get(
        'url_habitaclia', '') == '':
        logger.warning("NO URLS ENTERED (MINIUM 1 URL)")
        sys.exit()

    start_urls_idealista = data.get('url_idealista', [])
    start_urls_idealista = [url + '?ordenado-por=fecha-publicacion-desc' for url in start_urls_idealista]

    start_urls_pisoscom = data.get('url_pisoscom', [])
    start_urls_pisoscom = [url + 'fecharecientedesde-desc/' for url in start_urls_pisoscom]

    start_urls_fotocasa = data.get('url_fotocasa', [])

    start_urls_habitaclia = data.get('url_habitaclia', [])
    start_urls_habitaclia = [url + '?ordenar=mas_recientes' for url in start_urls_habitaclia]

    urls['start_urls_idealista'] = start_urls_idealista
    urls['start_urls_pisoscom'] = start_urls_pisoscom
    urls['start_urls_fotocasa'] = start_urls_fotocasa
    urls['start_urls_habitaclia'] = start_urls_habitaclia

    return urls


def check_new_flats(json_file_name, scrapy_rs_name, min_price, max_price, tg_chatID, db_client, db_name, telegram_msg, logger):
    '''
    Funció que llegeix un json dels habitatges amb les seves propietats.
    Compara si n'hi ha cap que no estigui a la bbdd i notifica amb missatge.
    :param json:
    :return:
    '''
    # creem l'objecte per enviar tg
    tb = telebot.TeleBot('6593481238:AAGyfrw7OsEl_7lwq_cj8iIDH9EIgFi0j54')

    new_urls = []

    # Obrir json
    # with open('flats_idealista.json') as json_file:
    json_file = open(json_file_name)

    #Encapsulamos por si da error
    try:
        data_json = json.load(json_file)
    except:
        data_json = ""

    # Check if JSON is empty
    if len(data_json) == 0:
        logger.warning(f'NO DATA IN JSON {scrapy_rs_name.upper()}')
    json_file.close()

    # open file and read the content in a list
    try:
        with open("./data/ids.json", "r") as outfile:
            ids_file = json.load(outfile)
            new_ids_file = []
        outfile.close()
    except FileNotFoundError:
        ids_file = []
        new_ids_file = []
        pass

    #Iteramos cada piso del diccionar y tratamos los datos
    for flat in data_json:
        flat_id = int(flat['id'])  #Convertimos a int
        title = flat["title"].replace("\'", "")
        try:
            town = flat['town']
        except:
            town = ''
        try:
            neighbour = flat['neighbour']
        except:
            neighbour = ''
        try:
            street = flat['street']
        except:
            street = ''
        try:
            number = flat['number']
        except:
            number = ''
        try:
            type = flat['type']
        except:
            type = ''
        #Cogemos sólo los digits de price, rooms y m2
        try:
            price_str = flat['price']
        except:
            prince_str = 0

        try:
            price = int(''.join(char for char in flat['price'] if char.isdigit()))
        except:
            price = 0

        if price == 0:
            price = price_str

        try:
            rooms = int(''.join(char for char in flat['rooms'] if char.isdigit()))
        except:
            try: rooms = flat['rooms']
            except: rooms = 0
        try:
            m2 = int(''.join(char for char in flat['m2'] if char.isdigit())[:-1])
            m2_tg = f'{m2}m²'
        except:
            try:
                m2 = flat['m2']
                m2_tg = f'{m2}m²'
            except:
                m2 = 0
                m2_tg = ''
        try:
            floor = flat['floor']
        except:
            floor = ''

        href = flat['href']
        site = flat['site']


        #Si la id del flat no está en los ids del archivo:
        if not flat_id in ids_file:
            #Añadimos el id nuevo a la lista
            new_ids_file.append(flat_id)
            # data
            data_flat = {
                'id': flat_id,
                'price': price,
                'm2': m2,
                'rooms': rooms,
                'floor': floor,
                'town': town,
                'neighbour': neighbour,
                'street': street,
                'number': number,
                'title': title,
                'href': href,
                'type': type,
                'site': site,
                'online': False
            }
            #Guarden la vivienda a la bbdd de mongo # db.sr flats.createIndex({id: 1},{unique: true})
            if not town == '':
                town_nf = unidecode(town.replace(' ', '_').lower())
                #Comparamos si hay viviendas iguales a mongodb:
                #Viviendas iguales significa que población, precio, m2, num. habitaciones son iguales.
                #También deben ser de otro site, es decir, si estamos comparando un piso que está a idealista, buscaremos en pisoscom, habitaclia y fotocasa
                match_flat_list = db_module.query_flat_mongodb(db_client, db_name, town_nf, data_flat, logger)
                if len(match_flat_list) > 0:
                    '''logger.debug(f"FLAT MATCH - NOT INSERTING: \n"
                                 f"{data_flat} \n"
                                 f"{match_flat_list}")'''
                    pass
                else:
                    if not site == 'fotocasa':
                        db_module.insert_flat_mongodb(db_client, db_name, town_nf, data_flat, logger)
            if price == 'Aconsultar':
                continue
            elif price == 'A consultar':
                continue

            #Si el precio es <= max_price
            if int(max_price) >= int(price) >= int(min_price) or int(max_price) == 0 and int(price) >= int(min_price):
                #Enviar mensaje a telegramo si se True
                if telegram_msg:
                    new_urls.append(href)
                    try: mitja_price_m2 = '%.2f' % (price / float(m2)) #Formateamos tg del precio, m2, media y href
                    except:
                        mitja_price_m2 = ''
                    tb.send_message(tg_chatID, f"<b>{price_str}</b> [{m2_tg}] → {mitja_price_m2}€/m²\n{href}", parse_mode='HTML')
                    logger.debug(f'{href} SENT TO TELEGRAM GROUP')
                    time.sleep(3.05)
                time.sleep(0.10)

    #abrir archivo en modo escritura
    with open("./data/ids.json", "w") as outfile:
        json.dump(ids_file+new_ids_file, outfile)
    outfile.close()
    if len(new_urls) > 0:
        logger.info(
            f"SPIDER FINISHED - [NEW: {len(new_urls)}] [TOTAL: {len(data_json)}]: {new_urls}")
    else:
        logger.debug(
            f"SPIDER FINISHED - [NEW: {len(new_urls)}] [TOTAL: {len(data_json)}]: {new_urls}")


def scrap_realestate(db_client, telegram_msg):
    start_time = time.time()

    #Si el nombre del proyecto tiene alguna "-" las cambiamos ya que da problemas con el sqlite
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    scrapy_log = data['log_level_scrapy'].upper()
    proxy_idealista = data['proxy_idealista']

    urls = []
    # urls.append(data['url_idealista'])
    # urls.append(data['url_pisoscom'])
    # urls.append(data['url_fotocasa'])
    # urls.append(data['url_habitaclia'])
    for key in data:
        if "url" in key and isinstance(data[key], list):
            urls += data[key]
        elif "url" in key:
            urls.append(data[key])

    #Mezclamos las urles para no repetir la misma spider
    urls_mixed = mix_list(urls)

    # iterem les urls que hi ha i fem scrape
    for url in urls_mixed:
        #Miramos qué portal es ['idealista', 'pisoscomo', 'fotocasa', 'habitaclia', 'yaencontre', 'enalquiler' ]
        #try:
        if url == '':
            continue

        portal_url = url.split('/')[2]
        portal_name = portal_url.split('.')[1]
        try:
            portal_name_url = portal_url.split('.')[1] + '.' + portal_url.split('.')[2]
        except:
            portal_name = portal_url
            portal_name_url = ''

        #Validemos que las spiders están ahí
        command = "scrapy list"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            logger.error("SPIDERS NOT DETECTED")
            sys.exit()

        #Hagamos crawl con la spider dependen del portal con la url
        logger.debug(f"SCRAPING PORTAL {portal_name_url} FROM {scrapy_rs_name}...")
        if portal_name_url == 'idealista.com':
            url_last_flats = url + '?ordenado-por=fecha-publicacion-desc'
            #Miramos si está o no activado el proxy y hacemos crawl gritando la spider por terminal
            if proxy_idealista == 'on':
                logger.debug('IDEALISTA PROXY ACTIVATED')
                os.system(
                    f"scrapy crawl -L {scrapy_log} idealista_proxy -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
            else:
                os.system(
                    f"scrapy crawl -L {scrapy_log} idealista -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'pisos.com':
            url_last_flats = url + '/fecharecientedesde-desc/'
            os.system(
                f"scrapy crawl -L {scrapy_log} pisoscom -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'fotocasa.es':
            os.system(f"scrapy crawl -L {scrapy_log} fotocasa -o ./data/{scrapy_rs_name}.json -a start_urls={url}")
        elif portal_name_url == 'habitaclia.com':
            #Hacemos crawl llamando la spider por terminal
            url_last_flats = url + '?ordenar=mas_recientes'
            os.system(
                f"scrapy crawl -L {scrapy_log} habitaclia -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")

        logger.debug(f"CRAWLED {portal_name.upper()}")

    #Arreglar JSON -Se deben unir las diferentes partes -o quitar las partes que los unen (][)
    logger.debug(f"EDITING ./data/{scrapy_rs_name}.json...")
    with open(f'./data/{scrapy_rs_name}.json', 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('\n][', ',')
    # Write the file out again
    with open(f'./data/{scrapy_rs_name}.json', 'w') as file:
        file.write(filedata)
        
    #Llamamos la función que comprueba los pisos nuevos que hay y los envía por telegramo y guarda en la bbdd
    check_new_flats(f"./data/{scrapy_rs_name}.json",
                                scrapy_rs_name,
                                data['min_price'],
                                data['max_price'],
                                data['telegram_chatuserID'],
                                db_client,
                                'sr_flats',
                                telegram_msg,
                                logger)


def init():
    global config_db_mongodb
    config_db_mongodb = {
        'db_user': "alain08367",
        'db_password': "A.mongodb.00",
        'db_host': "cluster0.mg16mjy.mongodb.net",
        'db_name': "Cluster0",
    }
    print('LOADING...')
    time.sleep(1)
    print(f'ScrapyBot')
    tprint("ScrapyBot")
    print(f'ScrapyBot')

    time.sleep(0.05)
    get_config()  #Cogemos la configuración
    time.sleep(0.05)
    logger = init_logs()  #iniciamos los logs
    time.sleep(0.05)
    db_client, info_message = checks()  #Comprobaciones
    time.sleep(0.05)
    count = 0
    telegram_msg = False
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    send_first = data['send_first']

    while True:
        try:
            os.remove(f"./data/{scrapy_rs_name}.json")  #Eliminamos el archivo json
        except:
            pass

        #Si senf_first está activado o hemos pasado al segundo ciclo, cambiamos telegram_msg a true para enviar los mensajes
        if send_first == 'True' or count > 0:
            telegram_msg = True
            logger.debug('TELEGRAM MSG ENABLED')

        #try:
        #Llamamos la función de scraping
        scrap_realestate(db_client, telegram_msg)
        # except:
        #    pass

        count += 1  #Sumamos 1 ciclo
        logger.info(f"SLEEPING {data['time_update']} SECONDS")
        time.sleep(int(data['time_update']))


if __name__ == "__main__":
    init()


