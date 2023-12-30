from bs4 import BeautifulSoup
import requests
import json



def connexion(r:None, name:str="", password:str=""):
    base_url = "https://zestedesavoir.com/membres/connexion/?next=/"
    if not (name and password ):
        name="Blockchain"
        password = '15037282d'
    try:
        r.url(base_url)
        r.type("//*[@id='id_username']", name)
        r.type("//*[@id='id_password']", password)
        r.click("//*[@id='content']/section/div[1]/form/div[4]/button")
    except Exception as e:
        print(f"An error occured{e}")

def to_scrape(url:str="")->BeautifulSoup:
    """ return a soup to parse
    """
    if not url:
        return "Not url was given"
    response = requests.get(url)
    print(dir(response))
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def _scrape_article_author(element:BeautifulSoup=to_scrape())->list:
    """
        author are not in the same page_url with scraping_article_info func,
        so we need to it's own soup to retrieve article info.
    """
    return [author.text.strip() for author in element.find('div', class_='members').find_all('li')]

def scrape_article_info( element:BeautifulSoup, output_file:str="articles.json", action=False, rpa_object=None)->list:
    """"
    Scraping Data from The search result: element
    action: 
    """
    articles = []
    try:
        for article_tag in element.find_all('article', class_='content-item'):
            article_data = {
                "href":f"https://zestedesavoir.com{article_tag.find('h3', class_='content-title').find('a')['href']}", 
                "titre": article_tag.find('h3', class_='content-title').text.strip() if article_tag.find('h3', class_='content-title') else '',
                "img": article_tag.find('img')['src'] if article_tag.find('img')  else '',
                "desc": article_tag.find('p', class_='content-description').text.strip() if article_tag.find('p', class_='content-description') else '',
                "date": article_tag.find('time', class_='content-pubdate')['pubdate'] if article_tag.find('time', class_='content-pubdate') else '',
                "xpath_tonext" : f"//h3/a[@href='{article_tag.find('h3', class_='content-title').find('a')['href']}']"
            }
            # Add Tag to our dictionnary
            keywords = [a.text for a in article_tag.find_all('a', href='/bibliotheque/?tag=') if article_tag.find_all('a', href='/bibliotheque/?tag=')]
            article_data["mots_cles"] = keywords

            # only article with tag have authors
            if  len(keywords):
                # don't need to click to get the article page url
                prev_url = rpa_object.url()
                rpa_object.click(article_data["xpath_tonext"]) if (rpa_object is not None and action is True) else None
                article_data["authors"]=_scrape_article_author(to_scrape(article_data['href']))
                rpa_object.wait(1.5) if (rpa_object is not None and action is True) else None
                # return to the prev_page after 1.5 s
                rpa_object.url(prev_url)
            # add article data to articles
            articles.append(article_data)

        # write data into the json
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(articles, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du fichier JSON : {str(e)}")
    return articles
        



