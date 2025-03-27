import requests
import time
from datetime import datetime
import io
import os
from PIL import Image


class HuggingFace:
    
    def __init__(self,api_url,token_bearer):
        self.hugging_api_url = api_url
        self.hugging_token = token_bearer
        self.prompt = ""

    def query_hugging_face(self):

        # este input recibe el prompt para crear una imagen a partir de texto
        payload = {
            "inputs": self.prompt
        }
        
        print(f"payloads: {payload}")

        counter = 0  # Usamos un contador para solo repetir una vez en caso de code 504
        while (counter <= 1):
            headers = {"Authorization": f"Bearer {self.hugging_token}"}
            response = requests.post(self.hugging_api_url, headers=headers, json=payload)
            print(response.status_code)            

            if response.status_code == 200:        
                counter = 2
                time.sleep(1)
                return response.content
                
            if response.status_code == 504:
                if counter < 1:
                    print(f"response.status_code: {response.status_code}, reintentando una vez mas...")
                counter = counter + 1
            else:
                return None
        #exit()

        
    # devuelve el directorio donde se guarda la imagen
    def save_image(self,image):
        
        # ex. 20240228153045  # (28 de febrero de 2024, 15:30:45 UTC)        
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        dir_path = "temp"
        path = f"temp/imagen_{now}.jpeg"

        if not os.path.exists(dir_path): 
            os.makedirs(dir_path, exist_ok=True) # Crea la carpeta si no existe

        # Guardar la imagen en un directorio específico
        
        result = image.save(path, format="JPEG")
        
        print(f"image saved: {result}")

        return path
        

    # crea una imagen con IA
    def create_image_with_ia_prompt(self, prompt):
        
        self.prompt = prompt

        # hugging_face
        image_bytes = self.query_hugging_face()
    
        if image_bytes == None:
            return None

        # You can access the image with PIL.Image for example
        image = Image.open(io.BytesIO(image_bytes))

        if image:
           # image.show()
            image_path = self.save_image(image)

        return image_path