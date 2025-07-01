import pandas as pd
import numpy as np
import requests
import webbrowser
from bs4 import BeautifulSoup


product = input("What product are you looking for? ").replace(' ', '+')
URL = "https://www.amazon.ca/s?k=" + product
HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0', 'Accept-Language': 'en-US, en; q=0.5'})
    
webpage = requests.get(URL, headers = HEADERS)
soup = BeautifulSoup(webpage.content, "html.parser")

products = soup.find_all('div', attrs={'class' : 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'})
product_list = []

for product in products:
    product_list.append(product)

print(product_list[0].get_text())