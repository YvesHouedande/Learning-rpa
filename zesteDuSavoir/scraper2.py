import rpa as r
from utils import *

# Initialisons
r.init(visual_automation=True)



    
def rpa_search(r:r, search_query, action=False):
    base_url = "https://zestedesavoir.com/" 
    connexion(r=r)
    # on va à la page
    r.url(base_url)
    # type and submit to the searh bar
    r.type('//input[@id="search-home"]', search_query)
    r.click("//*[@id='search-form']/button")
    # wait fro 1.5s
    r.wait(1.5)
    
    # prendre l'url générer aprés la recherche
    current_url = r.url()
    scrape_article_info(to_scrape(current_url), "articles2.json", action=action, rpa_object=r)
    r.close() 

# Testing
rpa_search(r=r, search_query="Java") 

