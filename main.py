import pandas as pd
import numpy as np
import requests
import webbrowser
from bs4 import BeautifulSoup
from tkinter import *

#Product detail extraction
def get_title(product):
    try:
        title = product.find('h2', attrs = {'class' : 'h3 product-title mb-1'}).text.strip()
        #title = product.find('h2', attrs = {'class' : 'a-size-base-plus a-spacing-none a-color-base a-text-normal'}).text.strip()
    except AttributeError:
        return np.nan

    return title

def get_price(product):
    try:
       # price = product.find('span', attrs = {'class' : 'a-price'}).find('span', attrs = {'class' : 'a-offscreen'}).text.strip()
        price = product.find('span', attrs = {'class' : 'price no-sale-price'}).text.strip()
        
        price = price.replace('$', '')
        price = price.replace(',', '')
        price = float(price)
    except AttributeError:
        return np.nan

    return price

def get_rating(product):
    try:
        score = product.find(attrs={'class': 'col-md-12 align-self-center review-icon'}).get('data-score')
        
    except AttributeError:
        return "N/A"

    return score

def get_reviews(product):
    try:
        reviews = product.find('span', attrs = {'class' : 'star-number'}).text.strip().replace(',', '').replace('(', '').replace(')', '')
        #reviews = product.find('span', attrs = {'class' : 'a-size-base s-underline-text'}).text.strip().replace(',', '')
    except AttributeError:
        return "N/A"
    
    return reviews

def get_link(product):
    try:
        link = product.find('a').get('href')
       # link = "https://amazon.ca" + product.find('a', attrs = {'class' : 'a-link-normal s-line-clamp-4 s-link-style a-text-normal'}).get('href')
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



def search_items(product):
    URL = "https://www.canadacomputers.com/en/search?s=" + product
    HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0', 'Accept-Language': 'en-US, en; q=0.5'})
        
    webpage = requests.get(URL, headers = HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")

    products = soup.find_all('div', attrs={'class' : 'product-description'})
    product_list = []

    for product in products:
        product_list.append(product)

    for product in products:
            product_list.append(product)

    product_dict = {"title" : [], "price" : [], "rating" : [], "reviews" : [], "link" : []}

    for product in product_list:
        product_dict['title'].append(get_title(product))
        product_dict['price'].append(get_price(product))
        product_dict['rating'].append(get_rating(product))
        product_dict['reviews'].append(get_reviews(product))
        product_dict['link'].append(get_link(product))

    df = pd.DataFrame.from_dict(product_dict)
    df = df.dropna(subset=['title'])
    df = df.dropna(subset=['price'])
    #df.sort_values(by='price', inplace=True)
    sort_price(df, 0, len(df) - 1) #For Practice
    df.to_csv('test.csv', header=True, index=False)

def open_file(fileName):
    df = pd.read_csv(fileName)
    return df

def show_options(list, df):
    list.delete(0, END)
    max = len((str(df.iloc[len(df) - 1]['price'])).split('.')[0])
    for i in range(len(df)):
        price = str(df.iloc[i]['price'])
        bef = price.split('.')[0]
        aft = price.split('.')[1]
        bef_len = len(bef)
        while bef_len < max:
            bef = '  ' + bef
            bef_len += 1
        while len(aft) < 2:
            aft = aft + '0'
        list.insert(list.size(), '    $' + bef + '.' + aft + '    ' + '|' + '    ' + df.iloc[i]['title'])


def search(input, list):
    if(input == ""):
        return
    search_items(input)
    df = open_file('test.csv')
    show_options(list, df)

if __name__ == "__main__":
    app = Tk()
    app.geometry('1920x1080')
    app.state('zoomed')
    app.title('Product Search')
        
    icon = PhotoImage(file='logo.png')
    test_img = PhotoImage(file="test.png").subsample(4, 4)

    app.iconphoto(True, icon)
    app.config(background='black')

    label = Label(app, text='Deal Finder', font=('Arial', 40), fg='blue', bg='yellow', relief='raised', bd='5', compound='top', image=test_img)
    search_frame = Frame(app)
    title_list = Listbox(app, font=('Arial', 15), background='white', height=15, width=100)
    entry = Entry(search_frame, bg='white', fg='black', font=('Arial', 40))
    button = Button(search_frame, text="Search", font=('Arial', 40), command=lambda: search(entry.get(), title_list))

    def on_enter(button2):
        button2.config(relief="sunken")
        button2.after(100, lambda: button2.config(relief="raised"))
        button2.invoke()

    app.bind("<Return>", lambda event: on_enter(button))
    label.pack()
    search_frame.pack()
    entry.pack(side=LEFT, padx=40)
    button.pack(side=RIGHT, padx=40)
    title_list.pack(pady=25)

    app.mainloop()
    