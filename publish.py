import requests
import base64
import json
import schedule
import threading
import time
from classes.BSoup import BSoup
from classes.Hugging import HuggingFace
from admin.settings import *
from functions import *

def recursive_get_news_from_api():
    # Obteniendo las noticias de apinews
    obj_news_title_and_url = get_news_title_and_url_from_apinews()
    
    #Guardamos las noticias en un archivo
    save_news_title_and_url_on_file(obj_news_title_and_url)

    # Después de 2 horas (2 * 60 * 60 horas), vuelve a llamar a esta función
    # threading.Timer(5 * 60, recursive_get_news_from_api).start()
    

# Programar la ejecución de la función cada 2 horas
schedule.every(2).hours.do(recursive_get_news_from_api)

# Iniciando el hilo
recursive_get_news_from_api()

#def publish_news():

while True:

    # Ejecutar todas las tareas programadas
    schedule.run_pending()
    time.sleep(5)  # Evitar que el programa consuma demasiado CPU

    # Verifica si hay link de noticias pendientes
    result = are_news_on_list()

    if result == False:
        print("No hay noticias disponibles 0")
        continue
    else:
        print("Noticias disponibles")

    # Autenticación en WordPress
    # USUARIO = "newstoday"
    # PASSWORD = "Juventudrd+"
    payload = dict(username=USUARIO, password=PASSWORD)
    # print(payload)

    # obteniendo el token de autentificacion de newstoday
    r = requests.post(API_WP_TOKEN_URL, data=payload)

    if r.status_code != 200:
        print("Error en la autenticación")
        exit()
        
    jobject = r.json()

    token               = jobject['token']
    user_email          = jobject['user_email']
    user_nicename       = jobject['user_nicename']
    user_display_name   = jobject['user_display_name']

    # Encabezados con autenticación Bearer
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }    
    
    # Obteniendo los títulos de los posts de aibuzz.today
    before_topics = get_post_titles(headers)

    # Obteniendo un titulo y url no repetido
    #unique_news_title_and_url = get_unique_title(obj_news_title_and_url,before_topics)
    unique_news_title_and_url = get_unique_title_from_file(before_topics)

    # Obteniendo el tema en tendencia con la IA
    #trend_topic = get_trend_topic(news_title,before_topics)

    if unique_news_title_and_url == "No hay noticias disponibles":
        print("No hay noticias disponibles 1")
        continue

    print(f"---->>>>>>unique_news_title_and_url: {unique_news_title_and_url}")

    # Obteniendo el artículo en tendencia
    trend_article = get_article_from_title_and_url(unique_news_title_and_url)

    if trend_article[:3] == '```':
        trend_article = trend_article[8:-3]

    if trend_article[(len(trend_article)-3):] == '```':
        trend_article = trend_article[:-3]

    if trend_article[0:1] != "{":
        print(f"inicio: {trend_article[0:20]}")
        print(f"fin: {trend_article[(len(trend_article)-3):]}")
        #print("No hay noticias disponibles 2")
        continue  

    json_string = trend_article

    try:    
        #json_string = trend_article[8:-4]
        json_article = json.loads(json_string)    
    except json.JSONDecodeError as e:
        print(f"Error en JSON: {e}")
        print("No hay noticias disponibles 3")    
        continue  

    post_title        = json_article.get("title")
    post_title_es     = json_article.get("title_es")
    post_content      = json_article.get("content")
    post_content_es   = json_article.get("content_es")
    post_media_prompt = json_article.get("media_prompt")
    post_excerpt      = json_article.get("excerpt")
    post_excerpt_es   = json_article.get("excerpt_es")
    post_categories   = json_article.get("categories")
    post_categories_es= json_article.get("categories_es")
    post_tags         = json_article.get("tags")
    post_tags_es      = json_article.get("tags_es")
    post_status       = json_article.get("status")

    #print(f"post_title: {post_title}")
    print(f"post_categories: {post_categories}")
    print(f"post_tags: {post_tags}")

    #print(f"post_title_es: {post_title_es}")
    #print(f"post_content_es: {post_content_es}")
    #print(f"post_excerpt_es: {post_excerpt_es}")
    #print(f"post_categories_es: {post_categories_es}")
    #print(f"post_tags_es: {post_tags_es}")

    #Generamos la Imagen destacada con IA
    HF = HuggingFace(HUGGING_API_URL,HUGGING_TOKEN)
    
    # pasamos un prompt text-to-image para crear la imagen
    prompt = post_media_prompt

    image_path = HF.create_image_with_ia_prompt(prompt)
    #image_path = create_image_with_openia_prompt(prompt)

    print(f"image_path: {image_path}")

    media_id = None

    # si el archivo existe cargalo a wp y obten el media id
    if image_path != None:
        # verifica si existe la imagen    
        if os.path.exists(image_path):
            media_id = upload_image_to_wp(image_path,token)
            print(f"media_id: {media_id}")

    """ image_path = "temp/imagen_20250228184706.jpeg"
    media_id = upload_image_to_wp(image_path,token)
    print(f"media_id: {media_id}")

    exit() """

    # Obteniendo los ids de las categorias
    categories_ids = get_categories_ids(post_categories,headers)


    if not post_tags == None:
        # Obteniendo los ids de las categorias
        tags_ids = get_tags_ids(post_tags,headers)

    #print(f"categories_id: {categories_ids}")

    # Datos del post
    payload = {
        "title"     : post_title,
        "content"   : post_content,
        "excerpt"   : post_excerpt,     
        "tags"      : post_tags,
        "status"    : post_status,        
    }

    if isinstance(categories_ids, list):
        payload["categories"] = ",".join(map(str, categories_ids)) # Convertimos en string
    if isinstance(categories_ids, str) and len(categories_ids) < 1:
        payload["categories"] = "1"

    # agregamos la categoria "en" en los articulos en ingles
    payload["categories"] = f"{payload["categories"]}, 667" # 667 -> en

    if isinstance(tags_ids, list):
        payload["tags"] = ",".join(map(str, tags_ids)) # Convertimos en string
    if isinstance(tags_ids, str) and len(tags_ids) < 1:
        payload["tags"] = "637"

    #print(f"payload_categories: {payload["categories"]}")

    # agreamos un descargo de responsabilidad en todas las entradas al final
    payload["content"] = f'''{payload["content"]}<hr><small style="font-size:10px"><i>To learn about the disclaimer of liability for the content of this website, <a href="/disclaimer-of-liability-for-the-content-of-this-website/" rel="noopener noreferrer">click here</a></i></small>'''

    if media_id != None:        
        payload["featured_media"] = media_id

    #print(f"headers: {headers}")

    
    #exit()

    r = requests.post(API_WP_POSTS_URL, json=payload, headers=headers)

    print(f"status_code: {r.status_code}")

    if r.status_code == 201:
        save_url_in_the_black_list(unique_news_title_and_url['url'])
        delete_temp_image(image_path) 
        result = remove_line_from_file(unique_news_title_and_url)

        if result:
            print("Artículo publicado con éxito")

            # Procedemos a publicar el articulo en español

             # Obteniendo los ids de las categorias
            categories_ids_es = get_categories_ids(post_categories_es,headers)


            if not post_tags_es == None:
                # Obteniendo los ids de las categorias
                tags_ids_es = get_tags_ids(post_tags_es,headers)

            payload = {
                "title"     : post_title_es,
                "content"   : post_content_es,
                "excerpt"   : post_excerpt_es,     
                "tags"      : post_tags_es,
                "status"    : post_status,        
            }

            if isinstance(categories_ids_es, list):
                payload["categories"] = ",".join(map(str, categories_ids_es)) # Convertimos en string
            if isinstance(categories_ids_es, str) and len(categories_ids_es) < 1:
                payload["categories"] = "1"
            
            # agregamos la categoria "es" en los articulos en español
            payload["categories"] = f"{payload["categories"]}, 643" # 643 -> es

            if isinstance(tags_ids_es, list):
                payload["tags"] = ",".join(map(str, tags_ids_es)) # Convertimos en string
            if isinstance(tags_ids_es, str) and len(tags_ids_es) < 1:
                payload["tags"] = "637"

            # agreamos un descargo de responsabilidad en todas las entradas al final
            payload["content"] = f'''{payload["content"]}<hr><small style="font-size:10px"><i>To learn about the disclaimer of liability for the content of this website, <a href="/disclaimer-of-liability-for-the-content-of-this-website/" rel="noopener noreferrer">click here</a></i></small>'''

            if media_id != None:        
                payload["featured_media"] = media_id

            r = requests.post(API_WP_POSTS_URL, json=payload, headers=headers)

            print(f"status_code: {r.status_code}")

            if r.status_code == 201:                
                print("Artículo español publicado con éxito")