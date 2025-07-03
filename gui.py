import webbrowser
from tkinter import *
from scraper import search_items, open_file


class App:
    def __init__(self, base):
        self.base = base
        self.base.geometry('1920x1080')
        self.base.state('zoomed')
        self.base.title('Product Search')
            
        self.icon = PhotoImage(file='logo.png')
        self.test_img = PhotoImage(file="test.png").subsample(4, 4)

        self.base.iconphoto(True, self.icon)
        self.base.config(background='black')

        self.label = Label(self.base, text='Deal Finder', font=('Arial', 40), fg='blue', bg='yellow', relief='raised', bd='5', compound='top', image=self.test_img)
        self.search_frame = Frame(self.base)
        self.title_list = Listbox(self.base, font=('Arial', 15), background='white', height=15, width=100)
        self.entry = Entry(self.search_frame, bg='white', fg='black', font=('Arial', 40))
        self.button = Button(self.search_frame, text="Search", font=('Arial', 40), command=lambda: search(self.entry.get(), self.title_list))


    
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

        def on_enter(button2):
            button2.config(relief="sunken")
            button2.after(100, lambda: button2.config(relief="raised"))
            button2.invoke()

        self.base.bind("<Return>", lambda event: on_enter(self.button))
        self.label.pack()
        self.search_frame.pack()
        self.entry.pack(side=LEFT, padx=40)
        self.button.pack(side=RIGHT, padx=40)
        self.title_list.pack(pady=25)