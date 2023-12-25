from bs4 import BeautifulSoup
import requests
import rpa as r
import json


# Initialisons
r.init(visual_automation=True)

# fonction de scraping prenant un objet de type beautiful soup
def article_into_json(output_file="donnees.json", soup=None, with_author=False):
    try:
        entites = []
        
        # Boucler à travers chaque balise <article>
        for article_tag in soup.find_all('article', class_='content-item'):
            # Dictionnaire pour stocker les données de chaque entité
            article_data = {
                "titre": article_tag.find('h3', class_='content-title').text.strip() if article_tag.find('h3', class_='content-title') else '',
                "img": article_tag.find('img')['src'] if article_tag.find('img')  else '',
                "desc": article_tag.find('p', class_='content-description').text.strip() if article_tag.find('p', class_='content-description') else '',
                "date": article_tag.find('time', class_='content-pubdate')['pubdate'] if article_tag.find('time', class_='content-pubdate') else '',
                "xpath_tonext" : f"//h3/a[@href='{article_tag.find('h3', class_='content-title').find('a')['href']}']"
            }
            

            # Ajouter les balises de mots-clés à la liste des mots-clés
            keywords = [a.text for a in article_tag.find_all('a', href='/bibliotheque/?tag=') if article_tag.find_all('a', href='/bibliotheque/?tag=')]
            article_data["mots_cles"] = keywords
            if with_author and len(keywords):
                prev_url = r.url()
                r.click(article_data["xpath_tonext"])
                page = requests.get(r.url())
                soup = BeautifulSoup(page.content, "html.parser")
                article_data['authors'] = [author.text.strip() for author in soup.find('div', class_='members').find_all('li')]
                r.wait(2.5)
                # r.url change after click, so to go to prev page, we do:
                r.url(prev_url)


            # Ajouter les données de l'entité à la liste des entités
            entites.append(article_data)

        # Écrire les données dans un fichier JSON
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(entites, json_file, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du fichier JSON : {str(e)}")

def rpa_search(search_query):
    base_url = "https://zestedesavoir.com/"
    
    try:
        # on va à la page
        r.url(base_url)
        
        # les infos au niveau de la bar
        r.type('//input[@id="search-home"]', search_query)
        r.click("//*[@id='search-form']/button")
        
        # 2.5
        r.wait(2.5)
        
        # prendre l'url générer aprés la recherche
        current_url = r.url()
        
        # obtenir le dom pour le passer à beautifulsoup pour le scraping
        page = requests.get(current_url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            article_into_json("articles.json", soup=soup, with_author=True)# fonction de scraping des données obtenues aprés la recherche
        else:
            print("Une erreur s'est produite lors de la récupération de la page.")
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")
        
    # finally:
    #     # Close TagUI
    #     r.close() 

# Example usage
search_query = 'django'
rpa_search("django")
