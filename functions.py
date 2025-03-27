from admin.settings import *
import html
import requests
import json
import time
import datetime
import os
import io
import re
from PIL import Image
from classes.BSoup import BSoup
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# obtiene el tema en tendencia con OpenIA
def get_trend_topic(news_title,before_topics):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
        { 
            "role": "system", 
            "content": (
                "Tu tarea es seleccionar un tema que no esté repetido y devolverlo en inglés. "
                "No incluyas el año en los temas. "
                "Devuelve únicamente el texto del tema sin comentarios adicionales, "
                "para que pueda ser utilizado en un algoritmo."
            )
        },
        {
            "role": "user",
            "content": (
                f"Compara estos títulos: {before_topics} con estos otros: {news_title}. "
                "Selecciona un título de la segunda lista que no se repita en la primera. "
                "Si todos están repetidos, responde exactamente con: 'No hay noticias disponibles'."
            )
        }]
    )
    # ver https://platform.openai.com/docs/api-reference/chat/create
    return completion.choices[0].message.content


# obtiene los titulos de los post desde hace 30 días de newstoday
def get_post_titles(headers):

    # Fecha de hace 30 días en formato ISO 8601    
    last30days = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)).isoformat()    

    params = {
        "after": last30days,  # Fecha de hace 30 días
        "per_page": 100,  # Número de posts por página (máximo 100)
        "orderby": "date",
        "order": "desc",
        "_fields" : "title",
    }

    r = requests.get(API_WP_POSTS_URL, headers=headers, params=params)
    posts = r.json()
    
    before_topics = ""
    c = 1
    for post in posts:
        #print(f"old->{c}:  {html.unescape(post['title']['rendered'])}")
        c = c+1
        before_topics = before_topics + html.unescape(post['title']['rendered']) + "||"

    
    return before_topics

# obtiene el articulo (deprecated)
def get_trend_article_from_title_and_text(title, text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
        { 
            "role": "system",                 
            "content": (
                "Escribe un artículo con el estilo de Xataka: **analítico pero accesible**, combinando **datos técnicos** con divulgación. "
                "Debe incluir un **título atractivo** y **subtítulos llamativos** en el desarrollo. "
                "Resalta conceptos clave en **negritas**, utiliza **párrafos cortos** y aporta **ejemplos actuales**. "
                "Evita un tono excesivamente académico o informal. "
                "No incluyas subtítulos de 'Introducción' ni 'Conclusión', pero desarrolla sus párrafos. "
                "Los subtítulos deben estar en formato **<h5>** compatible con WordPress y sin numeración. "
                "Las categorías no deben contener vocales acentuadas. "
                "Añade **citas de fuentes** al final con sus **hipervínculos** en formato compatible con WordPress. "                
                "Incrusta **enlaces imagenes relacionadas en codigo html** (hotlinking) entre parrafos compatibles con wordpress. "
                "Las imagenes tomalas de repositorios gratuitos, asegurate que esten accesibles. "
                "Devuelve el artículo en un JSON válido con los siguientes atributos: "
                "- **title**: título del artículo en ingles"
                "- **title_es**: título del artículo en español"
                "- **content**: contenido del artículo en ingles con formato WordPress "
                "- **content_es**: contenido del artículo en español con formato WordPress "
                "- **excerpt**: resumen del artículo en ingles "
                "- **excerpt_es**: resumen del artículo en español "
                "- **categories**: lista de categorías en ingles (sin vocales acentuadas) "
                "- **categories_es**: lista de categorías en español (sin vocales acentuadas) "
                "- **tags**: lista de etiquetas en ingles relevantes del articulo (sin vocales acentuadas) "
                "- **tags_es**: lista de etiquetas en español relevantes del articulo (sin vocales acentuadas) "
                "- **status**: siempre 'publish' "
                "Devuelve exclusivamente el JSON sin comentarios adicionales, ya que se usará en un algoritmo. "
                "Todo el articulo debe ser escrito para una entrada de wordpress tomando en cuenta el codigo html"
            )
        },
        {
            "role": "user",
            "content": (
                f"Escribe un articulo en ingles con el titulo {title} y utiliza el siguiente texto para el contenido {text}"
                "Parafrasea el texto mejorando el estilo."
            )
        }
    ]
    )
    # ver https://platform.openai.com/docs/api-reference/chat/create
    return completion.choices[0].message.content


# obtiene el articulo de un tema en tendencia con IA
def get_trend_article(trend_topic):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
        { 
            "role": "system",                 
            "content": (
                "Escribe un artículo con el estilo de Xataka: **analítico pero accesible**, combinando **datos técnicos** con divulgación. "
                "Debe incluir un **título atractivo** y **subtítulos llamativos** en el desarrollo. "
                "Resalta conceptos clave en **negritas**, utiliza **párrafos cortos** y aporta **ejemplos actuales**. "
                "Evita un tono excesivamente académico o informal. "
                "No incluyas subtítulos de 'Introducción' ni 'Conclusión', pero desarrolla sus párrafos. "
                "Los subtítulos deben estar en formato **<h5>** compatible con WordPress y sin numeración. "
                "Las categorías no deben contener vocales acentuadas. "
                "Añade **citas de fuentes** al final con sus **hipervínculos** en formato compatible con WordPress. "                
                "Incrusta **enlaces imagenes relacionadas en codigo html** (hotlinking) entre parrafos compatibles con wordpress. "
                "Las imagenes tomalas de repositorios gratuitos, asegurate que esten accesibles. "
                "Devuelve el artículo en un JSON válido con los siguientes atributos: "
                "- **title**: título del artículo "
                "- **content**: contenido del artículo con formato WordPress "
                "- **excerpt**: resumen del artículo "
                "- **categories**: lista de categorías (sin vocales acentuadas) "
                "- **status**: siempre 'publish' "
                "Devuelve exclusivamente el JSON sin comentarios adicionales, ya que se usará en un algoritmo."
            )
        },
        {
            "role": "user",
            "content": (
                f"Realiza una búsqueda en internet en páginas de noticias y escribe un artículo en inglés, parafraseado, sobre el tema: {trend_topic}."
            )
        }
    ])

    # ver https://platform.openai.com/docs/api-reference/chat/create
    return completion.choices[0].message.content


# obtiene los ids de las etiquetas
def get_tags_ids(post_tags,headers):
    tags_ids = []
    
    # Si es una cadena conviertela en lista
    if isinstance(post_tags, str):
        post_tags = post_tags.split(",")

    for tag in post_tags:
        r = requests.get(API_WP_TAGS_URL, headers=headers)
        tags = r.json()
        
        counter = 0
        for tgs in tags:
            
            if tgs['name'].lower() == tag.lower():
                tags_ids.append(tgs['id'])
                counter = counter+1

        if counter == 0:
            response = requests.post(API_WP_TAGS_URL, headers=headers, json={"name": tag})
            
            #print(f"response.json: {response.json()}")

            if response.status_code == 201:
                tags_ids.append(response.json()['id'])
            if response.status_code == 400 and response.json()['data']['term_id']:
                tags_ids.append(response.json()['data']['term_id'])

    if len(tags_ids) == 0:
        tags_ids.append('1')

    return tags_ids

# obtiene los ids de las categorias
def get_categories_ids(post_categories,headers):
    categories_ids = []
    
    # Si es una cadena conviertela en lista
    if isinstance(post_categories, str):
        post_categories = post_categories.split(",")

    for category in post_categories:
        r = requests.get(API_WP_CATEGORIES_URL, headers=headers)
        categories = r.json()
        
        counter = 0
        for cat in categories:
            
            if cat['name'].lower() == category.lower():
                categories_ids.append(cat['id'])
                counter = counter+1

        if counter == 0:
            response = requests.post(API_WP_CATEGORIES_URL, headers=headers, json={"name": category})
            
            #print(f"response.json: {response.json()}")

            if response.status_code == 201:
                categories_ids.append(response.json()['id'])
            if response.status_code == 400 and response.json()['data']['term_id']:
                categories_ids.append(response.json()['data']['term_id'])

    if len(categories_ids) == 0:
        categories_ids.append('1')

    return categories_ids


# obtiene los titulos de los articulos
def get_today_news_title_from_newsapidatahub():
        
    headers = {
        "Accept" : "application/json",
        "X-Api-Key": X_API_KEY
    }
    response = requests.get(API_NEWSDATAHUB_URL, headers=headers)

    news_titles = []

    if response.status_code == 200:

        json_object =  json.loads(response.text)

        data = json_object['data']

        #print(data)
        

        for news in data:
            print(f"--------->>news_api_titles:  "+ news['title'])
            print(f"--------->>__article_links:  "+ news['article_link'])
            
            news_titles.append(news['title'])
        
        # convertirmos la lista en una cadena
        news_titles = "|| ".join(news_titles)

    return news_titles


# obtiene los titulos de los articulos
def get_news_title_and_url_from_apinews():
    
    params = {
        "country": "us",
        "apiKey": NEW_SAPI_KEY
    }

    headers = {
        "Accept" : "application/json",        
    }

    response = requests.get(API_NEWS_API_URL, headers=headers, params=params)

    news_object = []

    if response.status_code == 200:

        json_object =  json.loads(response.text)

        data = json_object['articles']

        #print(data)
        

        for news in data:
            #print(f"--------->>news_api_titles: "+'{"title":"'+news['title']+'","url":"'+news['url']+'"}')            
            
            news_object.append('{"title":"'+news['title']+'","url":"'+news['url']+'"}')
        
        # convertirmos la lista en una cadena
        #news_object = ", ".join(news_object)

    return news_object


def is_a_valid_news_page(page_content):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
        { 
            "role": "system", 
            "content": (
                "Tu tarea analizar el texto y determinar si se puede obtener de el un articulo de noticias válido. "
                "Devuelve 'True' si es un articulo de noticias válida y 'False' si no lo es. "
                "No incluyas comentarios adicionales, ya que se usará en un algoritmo."          
            )
        },
        {
            "role": "user",
            "content": (
                f"{page_content}"                
            )
        }]
    )
    # ver https://platform.openai.com/docs/api-reference/chat/create
    return completion.choices[0].message.content


def save_url_in_the_black_list(url_string):
    # Nombre del archivo
    black_list_file_name = "temp/urlblacklist.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(black_list_file_name):
        # Crear el archivo si no existe
        with open(black_list_file_name, "w", encoding="utf-8") as f:
            f.write("")
    
    # Abrir el archivo en modo 'a' (append) para agregar texto sin borrar el contenido
    with open(black_list_file_name, "a", encoding="utf-8") as f:
        f.write(f"{url_string}\n")

    return True

# verifica si la url esta en la lista negra
def is_url_in_the_black_list(url_string):
    # Nombre del archivo
    black_list_file_name = "temp/urlblacklist.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(black_list_file_name):
        # Crear el archivo si no existe
        with open(black_list_file_name, "w", encoding="utf-8") as f:
            f.write("")
    
    # Abrir el archivo en modo 'r' (read) para leer el contenido
    with open(black_list_file_name, "r", encoding="utf-8") as f:
        # Leer todas las líneas del archivo
        lines = f.readlines()
        
        # Verificar si la URL está en la lista negra
        for line in lines:
            if url_string in line:
                return True

    return False


def get_page_content(url):
    # instanciamos a BeautifulSoup
    BS = BSoup()
    
    # obtenemos la pagina cruda
    soup = BS.get_page(url)
    
    if soup == None:        
        page_content = ""
    else:
        # obtenemos el texto de la sopa de lo contrario devolvemos false
        page_content = soup.get_text()
    
    return page_content


# Verfica que la url se pueda scrapear
def is_valid_url(url):

    page_content = get_page_content(url)
    
    if page_content == "":
        concat_url = f"[error]{url}"
        result = save_url_in_the_black_list(concat_url)
        return False
    else:

        result = is_a_valid_news_page(page_content)

        print(f"result is_a_valid_news_page: {result}")

        if result == False:

            # guarda la url no valida en la lista negra 
            # Es el contenido de una entrada de wordpress
            result = save_url_in_the_black_list(url)

            if result == True:
                return False
            
        else:
            return True
        

# obtiene un titulo unico no usado antes
def get_unique_title(obj_news_title_and_url,before_topics):
    
    unique_news_title_and_url = "No hay noticias disponibles"
    counter = 0
    for title_and_news in obj_news_title_and_url:
        #print(f"counter: {counter}")
        counter = counter + 1
        
        # Reemplazar comillas dentro de valores JSON correctamente
        # Reemplazar comillas dobles que no están al lado de {, }, :, o ","
        title_and_news = re.sub(r'(?<![{}:,])"(?![{}:,])', r'\\"', title_and_news)

        #print(f"title_and_news: {title_and_news}")

        parse_title_and_news = json.loads(title_and_news)
        
        if not is_url_in_the_black_list(parse_title_and_news['url']):
            
            found = False        
            for old_topic in before_topics.split("||"):
                
                # si el titulo ya fue usado en el worpress, no lo usamos
                if old_topic.lower() == parse_title_and_news['title'].lower():
                    found = True
                    print("found")
                    break        

            if found == False:
                
                if is_valid_url(parse_title_and_news['url']):
                
                    print(f"new_topic: {parse_title_and_news['title'].lower()}")                
                    unique_news_title_and_url = parse_title_and_news                
                    return unique_news_title_and_url                
                
    return unique_news_title_and_url

# obtiene un titulo unico no usado antes desde un archivo
def remove_line_from_file(line_to_remove = ""):
    
    #line_to_remove = json.loads(line_to_remove)

    # Nombre del archivo
    news_file_name = "temp/news.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(news_file_name):
        # Crear el archivo si no existe
        with open(news_file_name, "w", encoding="utf-8") as f:
            f.write("")

    # Abrir el archivo en modo 'r' (read) para leer el contenido
    with open(news_file_name, "r", encoding="utf-8") as f:
        # Leer todas las líneas del archivo
        file_lines = f.readlines()

    # Abrir el archivo en modo 'w' (write) para escribir el contenido
    with open(news_file_name, "w", encoding="utf-8") as f:    
        # Escribir todas las líneas menos la que se quiere eliminar
        for line in file_lines:
                        
            #print(line)
            if line != "":
                # Reemplazar comillas dentro de valores JSON correctamente
                # Reemplazar comillas dobles que no están al lado de {, }, :, o ","
                # parse_line = re.sub(r'(?<![{}:,])"(?![{}:,])', r'\\"', line)

                try:
                    obj_line = json.loads(line)            
                except json.JSONDecodeError as e:
                    # Reemplazar comillas dentro de valores JSON correctamente
                    # Reemplazar comillas dobles que no están al lado de {, }, :, o ","                                        
                    parse_line = re.sub(r'(?<![:{,])"(?![:,}])|(?<=,)"(?=\s)', r'\\"', line)

                    obj_line = json.loads(parse_line)

                    print(obj_line)

                               
                if obj_line['url'] != line_to_remove['url']:
                    #f.write(f"{json.dumps(html.unescape(line))}\n")                
                    f.write(json.dumps(obj_line, ensure_ascii=False) + "\n")
    return True


# Verifica si hay link de noticias pendientes
def are_news_on_list():

    # Nombre del archivo
    news_file_name = "temp/news.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(news_file_name):
        # Crear el archivo si no existe
        with open(news_file_name, "w", encoding="utf-8") as f:
            f.write("")

    # Abrir el archivo en modo 'r' (read) para leer el contenido
    with open(news_file_name, "r", encoding="utf-8") as f:
        # Leer todas las líneas del archivo
        file_lines = f.readlines()

    #print(len(file_lines))

    if len(file_lines) < 1:
        return False
    
    return True

# obtiene un titulo unico no usado antes desde un archivo
def get_unique_title_from_file(before_topics):

    unique_news_title_and_url = "No hay noticias disponibles"

    # Nombre del archivo
    news_file_name = "temp/news.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(news_file_name):
        # Crear el archivo si no existe
        with open(news_file_name, "w", encoding="utf-8") as f:
            f.write("")

    # Abrir el archivo en modo 'r' (read) para leer el contenido
    with open(news_file_name, "r", encoding="utf-8") as f:
        # Leer todas las líneas del archivo
        file_lines = f.readlines()

    
    #print(f"file_lines: {file_lines}")
    
    counter = 0
    for title_and_news in file_lines:
        #print(f"counter: {counter}")
        counter = counter + 1
        
        #parse_title_and_news = json.loads(title_and_news)
        
        try:
            obj_title_and_news = json.loads(title_and_news)            
        except json.JSONDecodeError as e:

            # Reemplazar comillas dentro de valores JSON correctamente
            # Reemplazar comillas dobles que no están al lado de {, }, :, o ","
            parse_title_and_news = re.sub(r'(?<![{}:,])"(?![{}:,])', r'\\"', title_and_news)
            obj_title_and_news = json.loads(parse_title_and_news)

            print(obj_title_and_news)

        if not is_url_in_the_black_list(obj_title_and_news['url']):
            
            found = False        
            for old_topic in before_topics.split("||"):
                
                # si el titulo ya fue usado en el worpress, no lo usamos
                if old_topic.lower() == obj_title_and_news['title'].lower():
                    found = True
                    print("found")
                    remove_line_from_file(obj_title_and_news)
                    break        

            if found == False:
                
                if is_valid_url(obj_title_and_news['url']):
                
                    print(f"new_topic: {obj_title_and_news['title'].lower()}")                
                    unique_news_title_and_url = obj_title_and_news                
                    return unique_news_title_and_url
                else:
                    remove_line_from_file(obj_title_and_news)
        else:
            remove_line_from_file(obj_title_and_news) 

    return unique_news_title_and_url


# obtiene el contenido de un articulo con IA
def create_article_from_page_content(title,page_content,url = ""):
    categories = '''
        Sports, 
        Android, 
        Apple, 
        SmarthPhones,
        Politics,
        Health,
        Entertainment,
        Society,
        Technology,
        Music,
        Science,
        Art,
        Film,
        Cryptocurrencies,
        AI,
        Economy,
        History,
        Astronomy,
        Archaeology,
        Wild World,
        Animals,
        Architecture,
        Change Climate,
        Cybersecurity,
        Travel,
        Climate,
        Telecommunications,
        Communities,
        Conflicts,
        Creativity,
        Democracy,
        Diets,
        Designs,
        Education,
        Electronics,
        Companies,
        Energy,
        Diseases,
        Epidemics,
        Pandemics,
        Countries,
        Evolution,
        Exoplanets,
        Events,
        Finance,
        Geopolitics,
        Government,
        War,
        Immigration,
        IT,
        Information,
        Innovation,
        International,
        Games,
        Videogames,
        Jobs,
        Law,
        Legal,
        Legislation,
        Marketing,
        Pets,
        Medication,
        Vaccines,
        Militia,
        Nutrition,
        Awards,
        Planets,
        Programming,
        Neuroscience,
        Machine Learning,
        NASA,
        Podcast,
        Lottery,
        Social Networks,
        Caribbean,
        Vacation,
        Trends,
        Teleworking,
        Transportation,
        Tourism,
        Religion,
        Terrorism,
        Human Rights,
        Eurozone,
        Women,
        Men,
        Children,
        Teenagers,
        Family,
        Universe,
        Cosmos,
        Performance,
        Singers,
        Psychology,
        Space exploration,
        Fantasy,
        Fun,        
        Rockets,
        Spacecraft,
        Launches,
        Shuttle,
        Vatican'''
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
        { 
            "role": "system",                 
            "content": (
                f"Escribe un artículo en ingles con el siguiente titulo **{title}**, utilizando el siguiente texto proporcionado. "
                "El articulo debe tener entre 1500 y 3000 palabras"
                "utiliza el estilo de Xataka: **analítico pero accesible**, combinando **datos técnicos** con divulgación. "
                "Debe incluir un **título atractivo** y **subtítulos llamativos** en el desarrollo. "
                "Resalta conceptos clave en **negritas**, utiliza **párrafos cortos** y aporta **ejemplos actuales**. "
                "Evita un tono excesivamente académico o informal. "
                "No incluyas subtítulos de 'Introducción' ni 'Conclusión', pero desarrolla sus párrafos. "
                "Los subtítulos deben estar en formato **<h5>** compatible con WordPress y sin numeración. "
                "Las categorías no deben contener vocales acentuadas. "
                f"Añade **este enlace {url} como fuente prinicpal consultada al final** en formato compatible con WordPress. "                
                #"Añade al final **un mensaje en letra pequeña y de forma discreta** que indique lo siguiente: '<small><i>Disclaimer: The images used in this article have been generated by AI and do not represent real-world people, objects, places or situations.</i></small>' "
                #"Incrusta **enlaces imagenes relacionadas en codigo html** (hotlinking) entre parrafos compatibles con wordpress. "
                #"Las imagenes tomalas de repositorios gratuitos, asegurate que esten accesibles. "
                #"Incluye el codigo html de las imagenes en el articulo para mostrarlas en la entrada de wordpress. "
                "Devuelve el artículo en un JSON válido con los siguientes atributos: "
                "- **title**: título del artículo "
                "- **title_es**: título del artículo en español"
                "- **content**: contenido del artículo con formato WordPress "
                "- **content_es**: contenido del artículo en español con formato WordPress "
                "- **excerpt**: resumen del artículo "
                "- **excerpt_es**: resumen del artículo en español "
                "- **media_prompt**: escribe un prompt para crear una imagen destacada referente al contenido del articulo "
                f"- **categories**: utiliza una categorías de estas en ingles: **{categories}**, que coincida con el articulo "
                f"- **categories_es**: utiliza una categorías de estas en español: **{categories}**, que coincida con el articulo "
                "- **tags**: lista de etiquetas en ingles relevantes del articulo (sin vocales acentuadas) "
                "- **tags_es**: lista de etiquetas en español relevantes del articulo (sin vocales acentuadas) "
                "- **status**: siempre 'publish' "
                "Devuelve exclusivamente el JSON sin comentarios adicionales, ya que se usará en un algoritmo."
            )
        },
        {
            "role": "user",
            "content": (
                f"{page_content}."
            )
        }
    ]
    )
    # ver https://platform.openai.com/docs/api-reference/chat/create
    return completion.choices[0].message.content


# obtiene el contenido de un articulo
def get_article_from_title_and_url(unique_news_title_and_url):
        
    # obtenemos el texto de la sopa de lo contrario devolvemos false
    page_content = get_page_content(unique_news_title_and_url['url'])
    
    # obtenemos el texto de la sopa de lo contrario devolvemos false
    article_text = create_article_from_page_content(unique_news_title_and_url['title'],page_content,unique_news_title_and_url['url'])
    
    #print(f"[][][]>>>create_article_from_page_content: {article_text}")

    return article_text


def save_news_title_and_url_on_file(obj_with_news):
    
    # Nombre del archivo
    news_file_name = "temp/news.txt"
    
    # Verificar si el archivo existe
    if not os.path.exists(news_file_name):
        # Crear el archivo si no existe
        with open(news_file_name, "w", encoding="utf-8") as f:
            f.write("")
    
    for json_new in obj_with_news:
        # Reemplazar comillas dentro de valores JSON correctamente
        # Reemplazar comillas dobles que no están al lado de {, }, :, o ","
        #json_new = re.sub(r'(?<![{}:,])"(?![{}:,])', r'\\"', json_new)
        # Convertir el JSON en un objeto de Python
        #json_new = json.loads(json_new)

        # Abrir el archivo en modo 'a' (append) para agregar texto sin borrar el contenido
        with open(news_file_name, "a", encoding="utf-8") as f:
            f.write(f"{json_new}\n")

    return True


# Subir imagen a WordPress
def upload_image_to_wp(image_path = "temp", token = ""):

    # Encabezados con autenticación Bearer
    headers = {
        "Authorization": f"Bearer {token}"        
    }

    with open(image_path, "rb") as img:
        image_data = img.read()
   
    image_filename = image_path.split("/")[-1]

    print(f"image_filename: {image_filename}")
    
    #print(f"media_endpoint: {API_WP_MEDIA_URL}")

    files = {"file": (image_filename, image_data, "image/jpeg")}
    
    response = requests.post(API_WP_MEDIA_URL, headers=headers, files=files)
    
    print(f"response: {response}")

    print(f"response.status_code: {response.status_code}")
    #print(f"response.json: {response.json()}")
    #print(f"response.content: {response.content}")

    if response.status_code == 201:
        media_id = response.json().get("id")
        print(f"Imagen subida con éxito. ID: {media_id}")
        return media_id
    else:
        print(f"Error al subir la imagen: {response.text}")
        return None


def delete_temp_image(image_path):

    if image_path == None:
        return False
    
    # Eliminar archivo
    if os.path.exists(image_path):
        os.remove(image_path)
        return True
    else:
        return False


# Función para descargar la imagen
def download_image(image_url, file_name="temp/image.png"):

    try:
        response = requests.get(image_url)

        if response.status_code == 200:
            with open(file_name, "wb") as file:
                file.write(response.content)
            print(f"Imagen descargada: {file_name}")
            return file_name
        else:
            print("Error al descargar la imagen.")
            return None
    except Exception as e:
        print(f"Error al descargar la imagen: {e}")
        return None   

#image_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-iPCwpfdVDi1DhWqbecLBWxfr/user-UYvsGGFFtLuvYxBRH9SMigDL/img-R00z7niyEL9WpkPzYNcypw9q.png?st=2025-03-10T13%3A50%3A21Z&se=2025-03-10T15%3A50%3A21Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-03-09T22%3A26%3A22Z&ske=2025-03-10T22%3A26%3A22Z&sks=b&skv=2024-08-04&sig=JqGE2/dbNc1UALqxduHgGUuNr8Wsw8/azJxS8Fbu/74%3D"
#download_image(image_url)

# crea una imagen con OpenIA
def create_image_with_openia_prompt(prompt):
    
    print(f"openIa_image_prompt: {prompt}")

    try:

        completion = client.images.generate(
            model="dall-e-3",
            prompt=f"{prompt}",
            n=1,
            size="1024x1024"        
        )

        #print(completion.data)
        #print(f"completion.data.url: {completion.data["url"]}")
        print(f"completion.data[0].url: {completion.data[0].url}")
        
        url = completion.data[0].url
        # ex. 20240228153045  # (28 de febrero de 2024, 15:30:45 UTC)        
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        file_name = f"temp/image_{now}.png"
        
        image_path = download_image(url,file_name)

        # si el archivo existe
        if image_path:
            # image.show()
            return  image_path
        
    except OpenAI.BadRequestError as e:
        #if "content_policy_violation" in str(e):
        return None
    
    return None


#prompt = "Imagen del universo mientras era creado por dios"
#create_image_with_openia_prompt(prompt)