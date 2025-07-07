import ttkbootstrap as tb
import webbrowser
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter import messagebox
from scraper import search_items, sort_price, combine_search



class App:
    def __init__(self, base):
        #Window Setup
        self.base = base
        self.base.geometry('1920x1080')
        self.base.state('zoomed')
        self.base.title('Product Scraper')

        #Universal Variables
        self.logo = PhotoImage(file='logo.png').subsample(4, 4)
        self.sideicon = PhotoImage(file="drawing.png").subsample(10,10)
        self.selected = "X"
        self.links = []

        #Widget Styles
        style = tb.Style()
        style.configure('Custom.TLabel', background="#303030", font=("Arial", 20))
        style.configure('Custom.TCheckbutton', background="#303030", font=("Arial", 20))
        style.configure('Normal.TButton', font=("Arial", 30))
        style.configure('Toggled.TButton', font=("Arial", 30), background="#303030")
        
        

        #Widget Declaration
        self.label = Label(self.base, text='Parts Finder', font=('Arial', 40), relief='raised', bd='5', compound='top', image=self.logo)
        self.search_frame = Frame(self.base)
        self.sidebar = tb.Frame(self.base, style="Custom.TLabel", width=300)
        self.bars = tb.Label(self.base, image=self.sideicon, cursor='hand2')
        self.entry = Entry(self.search_frame, bg='white', fg='black', font=('Arial', 30))
        self.search_button = tb.Button(self.search_frame, text="Search", cursor='hand2', style='Normal.TButton', takefocus=0, 
                             command=lambda: search(self.entry.get(), self.product_list, self.websites, self.web_list, self.links))
        self.product_list = Listbox(self.base, font=('Arial', 15), background='white', height=17, width=75)
        self.open_button = tb.Button(self.base, text='▶', cursor='hand2', style='Normal.TButton', takefocus=0, 
                                     command=lambda: open_links(self.links, self.product_list.curselection()))
        self.switch_button = tb.Button(self.base, text='Multi', cursor='hand2', style='Normal.TButton', takefocus=0, 
                                       command=lambda: toggle_muliple(self.switch_button, self.product_list))
        self.loading = tb.Progressbar(self.base, orient=VERTICAL, length=450)

        file = open('websites.txt', 'r')
        self.websites = file.readlines()
        file.close()

        self.web_list = []

        for i in range(len(self.websites)):
            website = self.websites[i].split(';')[0]
            self.web_list.append(BooleanVar())
            self.web_list[i].set(True) 
            new_check = tb.Checkbutton(self.sidebar, variable=self.web_list[i], onvalue=True, offvalue=False,
                                       text=website, style="Custom.TCheckbutton")
            new_check.pack(anchor='w', padx=15, pady=10)
            if i == 0:
                new_check.pack_configure(pady=(150, 10))


        def show_options(list, df, links):
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
                links.append(df.iloc[i]['link'])

        def search(user_input, listbox, websites, web_check, links):

            if(user_input == ""):
                return
            self.loading['value'] = 0
            self.base.update()
            results = []
            for i in range(len(websites)):
                if web_check[i].get() == True:
                    result = search_items(user_input, websites[i].split(';'))
                    results.append(result)
                    self.loading['value'] += 20
                    self.base.update()
            
            if len(results) == 0:
                messagebox.showwarning(title='Select Website', message='Please select at least one website!')
                return
            combined_df = combine_search(results)
            self.loading['value'] += 20
            self.base.update()
            #combined_df.sort_values(by='price', inplace=True)
            sort_price(combined_df, 0, len(combined_df) - 1) #For Practice
            self.loading['value'] += 20
            self.base.update()
            show_options(listbox, combined_df, links)

        def open_links(listbox, indexes):
            for i in indexes:
                webbrowser.open(listbox[i])

        def toggle_sidebar(event, sidebar):
            if sidebar.winfo_manager() != 'place':
                event.widget.configure(style="Custom.TLabel")
                sidebar.place(x=0, y=0, relheight=1)
            else:
                event.widget.configure(style="")
                sidebar.place_forget()

        def on_enter(button):
            button.invoke()

        def on_click(event):
            lists = event.widget
            if lists.cget('selectmode') == MULTIPLE or lists.size() == 0:
                return
            curr = lists.get(lists.curselection()) 
            if curr != self.selected:
                self.selected = curr
            else:
                open_links(self.links, lists.curselection())

        def on_hover(event):
            listbox = event.widget
            item = listbox.nearest(event.y)
            if listbox.get(item) == self.selected:
                listbox.config(cursor="hand2")
            else:
                listbox.config(cursor="arrow")
                
        def toggle_muliple(button, listbox):
            if listbox.cget('selectmode') != MULTIPLE:
                listbox.config(selectmode='multiple')
                button.config(style='Toggled.TButton')
            else:
                listbox.config(selectmode='browse')
                button.config(style='Normal.TButton')

        self.base.bind("<Return>", lambda event: on_enter(self.search_button))
        self.bars.bind("<Button-1>", lambda event: toggle_sidebar(event, self.sidebar))
        self.product_list.bind("<<ListboxSelect>>", on_click)
        self.product_list.bind("<Motion>", on_hover)

        self.sidebar.pack_forget()
        self.bars.place(x=10, y=10)
        self.label.pack()
        self.search_frame.pack()
        self.entry.pack(side=LEFT, padx=40)
        self.search_button.pack(side=RIGHT, padx=40)
        self.open_button.place(relx=0.75, rely=0.7)
        self.switch_button.place(relx=0.75, rely=0.6)
        self.product_list.place(relx=0.5, rely=0.7, anchor="center")
        self.loading.place(relx=0.2, rely=0.5)