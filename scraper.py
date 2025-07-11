import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

#Extracts various product details
def get_title(product, attribute):
    try:
        title = product.find(attrs = {'class' : attribute}).text.strip()
    except AttributeError:
        return np.nan
    
    return title

def get_price(product, attribute):
    try:
        if len(attribute.split(',')) != 1:
            price = product.find('span', attrs = {'class' : attribute.split(',')[0]}).find('span', attrs = {'class' : attribute.split(',')[1]}).text.strip()
        else:
            price = product.find(attrs = {'class' : attribute}).text.strip()

    except AttributeError:
        return np.nan
    
    price = price.replace(',', '')
    price = re.findall(r"\d+\.?\d*", price)
    price = float(price[0])
    return price

def get_rating(product, attribute):
    try:
        if len(attribute.split(',')) != 1:
            score = product.find(attrs = {'class' : attribute.split(',')[0]}).get(attribute.split(',')[1])
        else:
            score = product.find('span', attrs = {'class' : attribute}).text.strip()
    except AttributeError:
        return 0
    
    num = re.findall(r"\d+\.?\d*", score)
    score = float(int(float(num[0]) * 100)/100)
    return score

def get_reviews(product, attribute):
    try:
        reviews = product.find('span', attrs = {'class' : attribute}).text.strip()
    except AttributeError:
        return 0
    reviews = reviews.replace(',', '').replace('(', '').replace(')', '')
    reviews = int(reviews)
    return reviews

def get_link(product, attribute):
    try:
        link = attribute.split(',')[0] + product.find('a', attrs = {'class' : attribute.split(',')[1].strip()}).get('href')   
    except AttributeError:
        return ""
    
    return link


#Sorting products based on provided column with mergesort
def sort_data(data, l, r, selected, check):
    if(l >= r):
        return
    
    mid = (l + r)//2
    sort_data(data, l, mid, selected, check)
    sort_data(data, mid + 1, r, selected, check)
    merge(data, l, mid, r, selected, check)

def merge(data, l, mid, r, selected, check):
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
        if (left_list.iloc[i][selected] * check) <= (right_list.iloc[j][selected] * check):
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


#Searches and scrapes product data from given website
def search_items(product, website_info):
    URL = website_info[1].split(',')[0] + product + website_info[1].split(',')[1]
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


#Combines data from multiple website searches
def combine_search(df_list):
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

def copy_data(df):
    return df.copy(deep=True)