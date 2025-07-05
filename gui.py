import ttkbootstrap as tb
import webbrowser
from tkinter import *
from scraper import search_items, sort_price, combine_search


class App:
    def __init__(self, base):
        self.base = base
        self.base.geometry('1920x1080')
        self.base.state('zoomed')
        self.base.title('Product Search')
            
        self.icon = PhotoImage(file='logo.png')
        self.test_img = PhotoImage(file="test.png").subsample(4, 4)

        self.base.iconphoto(True, self.icon)
        self.sideicon = PhotoImage(file="drawing.png").subsample(10,10)
        self.selected = "X"

        style = tb.Style()
        style.configure('Custom.TLabel', background="#303030", font=("Arial", 20))
        style.configure('Custom.TCheckbutton', background="#303030", font=("Arial", 20))
        
        self.label = Label(base, text='Parts Finder', font=('Arial', 40), relief='raised', bd='5', compound='top', image=self.test_img)
        self.search_frame = Frame(base)
        self.sidebar = tb.Frame(base, style="Custom.TLabel", width=300)
        self.bars = tb.Label(self.base, image=self.sideicon, cursor='hand2')
        self.title_list = Listbox(base, font=('Arial', 15), background='white', height=15, width=75)
        self.entry = Entry(self.search_frame, bg='white', fg='black', font=('Arial', 30))
        self.button = Button(self.search_frame, text="Search", cursor='hand2', font=('Arial', 30), 
                             command=lambda: search(self.entry.get(), self.title_list, self.websites, self.web_list))

        file = open('websites.txt', 'r')
        self.websites = file.readlines()
        file.close()

        self.web_list = []

        for i in range(len(self.websites)):
            website = self.websites[i].split(';')[0]
            self.web_list.append(BooleanVar())
            self.web_list[i].set(True)
            new_check = tb.Checkbutton(self.sidebar, variable=self.web_list[i], onvalue=True, offvalue=False, text=website, style="Custom.TCheckbutton")
            new_check.pack(anchor='w', padx=15, pady=10)
            if i == 0:
                new_check.pack_configure(pady=(150, 10))


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

        def search(user_input, listbox, websites, web_check):
            if(user_input == ""):
                return
            results = []
            for i in range(len(websites)):
                if web_check[i].get() == True:
                    result = search_items(user_input, websites[i].split(';'))
                    results.append(result)
                    
            combined_df = combine_search(results)
            #combined_df.sort_values(by='price', inplace=True)
            sort_price(combined_df, 0, len(combined_df) - 1) #For Practice
            show_options(listbox, combined_df)

        def on_enter(button2):
            button2.config(relief="sunken")
            button2.after(100, lambda: button2.config(relief="raised"))
            button2.invoke()

        def toggle_sidebar(event, sidebar):
            if sidebar.winfo_manager() != 'place':
                event.widget.configure(style="Custom.TLabel")
                sidebar.place(x=0, y=0, relheight=1)
            else:
                event.widget.configure(style="")
                sidebar.place_forget()

        def on_click(event):
            lists = event.widget
            curr = lists.get(lists.curselection()) 
            if(curr != self.selected):
                self.selected = curr
                print(self.selected)

        self.base.bind("<Return>", lambda event: on_enter(self.button))
        self.title_list.bind("<<ListboxSelect>>", on_click)
        self.bars.bind("<Button-1>", lambda event: toggle_sidebar(event, self.sidebar))

        self.sidebar.pack_forget()
        self.bars.place(x=10, y=10)
        self.label.pack()
        self.search_frame.pack()
        self.entry.pack(side=LEFT, padx=40)
        self.button.pack(side=RIGHT, padx=40)
        self.title_list.pack(pady=25)