import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

#Product detail extraction
def get_title(product, attribute):
    try:
        title = product.find('h2', attrs = {'class' : attribute}).text.strip()
    except AttributeError:
        return np.nan
    
    return title

def get_price(product, attribute):
    try:
        if len(attribute.split(',')) != 1:
            price = product.find('span', attrs = {'class' : attribute.split(',')[0]}).find('span', attrs = {'class' : attribute.split(',')[1]}).text.strip()
        else:
            price = product.find('span', attrs = {'class' : attribute}).text.strip()

    except AttributeError:
        return np.nan
    
    price = price.replace('$', '')
    price = price.replace(',', '')
    price = float(price)
    return price

def get_rating(product, attribute):
    try:
        if len(attribute.split(',')) != 1:
            score = product.find(attrs = {'class' : attribute.split(',')[0]}).get(attribute.split(',')[1])
        else:
            score = product.find('span', attrs = {'class' : attribute}).text.strip()
        score = float(score.split()[0])
    except AttributeError:
        return "N/A"
    
    return score

def get_reviews(product, attribute):
    try:
        reviews = product.find('span', attrs = {'class' : attribute}).text.strip()
    except AttributeError:
        return "N/A"
    reviews = reviews.replace(',', '').replace('(', '').replace(')', '')
    return reviews

def get_link(product, attribute):
    try:
        link = attribute.split(',')[0] + product.find('a', attrs = {'class' : attribute.split(',')[1].strip()}).get('href')   
    except AttributeError:
        return ""
    
    return link

def sort_price(data, l, r):
    if(l >= r):
        return
    
    mid = (l + r)//2
    sort_price(data, l, mid)
    sort_price(data, mid + 1, r)
    merge(data, l, mid, r)

def merge(data, l, mid, r):
    n1 = mid - l + 1
    n2 = r - mid

    columns = data.columns
    left_list = pd.DataFrame(index=range(n1), columns=columns)
    right_list = pd.DataFrame(index=range(n2), columns=columns)

    for i in range(n1):
        left_list.iloc[i] = data.iloc[l + i]

    for j in range(n2):
        right_list.iloc[j] = data.iloc[mid + 1 + j]

    i = 0
    j = 0
    k = l
    while i < n1 and j < n2:
        if left_list.iloc[i]['price'] <= right_list.iloc[j]['price']:
            data.iloc[k] = left_list.iloc[i]
            i += 1
        else:
            data.iloc[k] = right_list.iloc[j]
            j += 1
        k += 1

    while i < n1:
        data.iloc[k] = left_list.iloc[i]
        i += 1
        k += 1
    while j < n2:
        data.iloc[k] = right_list.iloc[j]
        j += 1
        k += 1


def search_items(product, website_info):
    URL = website_info[1] + product
    HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0', 'Accept-Language': 'en-US, en; q=0.5'})
    
    webpage = requests.get(URL, headers = HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")

    products = soup.find_all('div', attrs={'class' : website_info[2]})

    product_list = []

    for product in products:
        product_list.append(product)

    product_dict = {"title" : [], "price" : [], "rating" : [], "reviews" : [], "link" : []}

    for product in product_list:
        product_dict['title'].append(get_title(product, website_info[3]))
        product_dict['price'].append(get_price(product, website_info[4]))
        product_dict['rating'].append(get_rating(product, website_info[5]))
        product_dict['reviews'].append(get_reviews(product, website_info[6]))
        product_dict['link'].append(get_link(product, website_info[7]))
    
    df = pd.DataFrame.from_dict(product_dict)
    df = df.dropna(subset=['title'])
    df = df.dropna(subset=['price'])
    return df

def open_file(fileName):
    df = pd.read_csv(fileName)
    return df

def combine_search(df_list):
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.to_csv('test.csv', header=True, index=False)
    return combined_df