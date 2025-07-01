import pandas as pd
import numpy as np
import requests
import webbrowser
from bs4 import BeautifulSoup
#Product detail extraction
def get_title(product):
    try:
        title = product.find('h2', attrs = {'class' : 'a-size-base-plus a-spacing-none a-color-base a-text-normal'}).text.strip()
    except AttributeError:
        return np.nan

    return title

def get_price(product):
    try:
        price = product.find('span', attrs = {'class' : 'a-price'}).find('span', attrs = {'class' : 'a-offscreen'}).text.strip()
        price = price.replace('$', '')
        price = price.replace(',', '')
        price = float(price)
    except AttributeError:
        return np.nan

    return price

def get_rating(product):
    try:
        score = product.find('span', attrs = {'class' : 'a-icon-alt'}).text.strip()
    except AttributeError:
        return "N/A"

    return score

def get_reviews(product):
    try:
        reviews = product.find('span', attrs = {'class' : 'a-size-base s-underline-text'}).text.strip().replace(',', '')
    except AttributeError:
        return "N/A"
    
    return reviews

def get_link(product):
    try:
        link = "https://amazon.ca" + product.find('a', attrs = {'class' : 'a-link-normal s-line-clamp-4 s-link-style a-text-normal'}).get('href')
    except AttributeError:
        return ""
    
    return link


product = input("What product are you looking for? ").replace(' ', '+')
URL = "https://www.amazon.ca/s?k=" + product
HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0', 'Accept-Language': 'en-US, en; q=0.5'})
    
webpage = requests.get(URL, headers = HEADERS)
soup = BeautifulSoup(webpage.content, "html.parser")

products = soup.find_all('div', attrs={'class' : 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'})
product_list = []

for product in products:
    product_list.append(product)

for product in products:
        product_list.append(product)

product_dict = {"title" : [], "price" : [], "rating" : [], "reviews": [], "link" : []}

for product in product_list:
    product_dict['title'].append(get_title(product))
    product_dict['price'].append(get_price(product))
    product_dict['rating'].append(get_rating(product))
    product_dict['reviews'].append(get_reviews(product))
    product_dict['link'].append(get_link(product))

df = pd.DataFrame.from_dict(product_dict)
df = df.dropna(subset=['title'])
df = df.dropna(subset=['price'])
df.to_csv('test.csv', header=True, index=False)