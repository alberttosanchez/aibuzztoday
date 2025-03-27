from datetime import datetime

# Configuración
OPENAI_API_KEY = ""

USUARIO = ""
PASSWORD = ""

WP_URL = "https:/domain.local"


API_WP_TOKEN_URL = f"{WP_URL}/wp-json/jwt-auth/v1/token"

API_WP_POSTS_URL = f"{WP_URL}/wp-json/wp/v2/posts"
API_WP_MEDIA_URL = f"{WP_URL}/wp-json/wp/v2/media"
API_WP_CATEGORIES_URL = f"{WP_URL}/wp-json/wp/v2/categories"
API_WP_TAGS_URL = f"{WP_URL}/wp-json/wp/v2/tags"

today = datetime.today().strftime('%Y-%m-%d')

#X-Api-Key from newsdatahub
X_API_KEY = "___"
API_NEWSDATAHUB_URL = f"https://api.newsdatahub.com/v1/news?start_date={today}&language=en"

#Apikey from newsapi
NEW_SAPI_KEY = "____"
API_NEWS_API_URL = f"https://newsapi.org/v2/top-headlines?pageSize=100&country=us&apiKey={NEW_SAPI_KEY}"

# Hugging Face -> https://huggingface.co/
HUGGING_TOKEN = "___" 

# This token only have read permissions
IA_MODEL_NAME = "strangerzonehf/Flux-Midjourney-Mix2-LoRA"

# https://huggingface.co/strangerzonehf/Flux-Midjourney-Mix2-LoRA
HUGGING_API_URL = f"https://router.huggingface.co/hf-inference/models/{IA_MODEL_NAME}"
