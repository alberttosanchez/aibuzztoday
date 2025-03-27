import requests
from bs4 import BeautifulSoup

class BSoup:    
   
    # 1️⃣ Obtener la página
    def get_page(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120) # 2 minutos
            response.raise_for_status()  # Lanza una excepción si hay un error HTTP
            soup = BeautifulSoup(response.text, "html.parser")        
            return soup
        except requests.Timeout:
            print("⏳ La solicitud ha tardado demasiado y ha sido cancelada.")
            return None
        except:
            return None

    def get_tag_name_from_url(self, url):
        
        tag_name = "article"

        if "elcomercio" in url:
            tag_name = "article"
        elif "gestion" in url:
            tag_name = "article"
        elif "depor" in url:
            tag_name = "article"
        elif "peru21" in url:
            tag_name = "article"
        elif "rpp" in url:
            tag_name = "article"
        elif "americatv" in url:
            tag_name = "article"
        elif "exitosape" in url:
            tag_name = "article"
        elif "larepublica" in url:
            tag_name = "article"
        elif "trome" in url:
            tag_name = "article"
        elif "diariocorreo" in url:
            tag_name = "article"
        elif "expreso" in url:
            tag_name = "article"
        elif "peru.com" in url:
            tag_name = "article"
        elif "libero" in url:
            tag_name = "article"
        elif "ojo" in url:
            tag_name = "article"
        elif "trome" in url:
            tag_name = "article"
        elif "thehill.com" in url:
            tag_name = "article"
        elif "foxnews.com" in url:
            tag_name = "article"
        
        return tag_name

    # 2️⃣ Encontrar el contenido del artículo
    def get_article_from_tagname(self, soup, url, tag_name = "article"):

        tag_name = self.get_tag_name_from_url(url)

        article = soup.find(tag_name)
        
        # 2️⃣ Buscar la etiqueta <article>        
        if article is None:
            article = soup.find("div", class_={tag_name})        
        
        return article
    
    def get_article_text(self, article):
        # 3️⃣ Extraer el texto del artículo
        article_text = article.get_text()
        return article_text


