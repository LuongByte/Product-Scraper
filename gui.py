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
        self.base.minsize(640, 360)
        self.base.state('zoomed')
        self.base.title('Product Scraper')

        #Universal Variables
        self.logo = PhotoImage(file='images/logo.png').subsample(4, 4)
        self.sideicon = PhotoImage(file="images/drawing.png").subsample(10,10)
        self.arrow = PhotoImage(file='images/arrow.png').subsample(5, 5)
        file = open('websites.txt', 'r')
        self.websites = file.readlines()
        file.close()
        self.links = []
        self.product_select = "X"
        self.data = []
        self.web_list = []
        self.sort_options = ["Relevance", "Relevance", "Price", "Score", "Reviews"]
        self.sort_select = StringVar()
        self.sort_select.set(self.sort_options[0])
        #Widget Styles
        style = tb.Style()
        style.configure('Custom.TLabel', background="#303030", font=("Arial", 20))
        style.configure('Custom.TCheckbutton', background="#303030", font=("Arial", 20))
        style.configure('Normal.TButton', font=("Arial", 30))
        style.configure('Toggled.TButton', font=("Arial", 30), background= "#303030")
        style.map('Toggled.TButton', foreground=[('disabled', 'white')], background=[('disabled', '#303030')])
        style.configure('Custom.TMenubutton', font=("Arial", 15))
        

        #Widget Declaration
        self.label = Label(self.base, text='PARTS FINDER', font=('Lexend ', 40, 'bold'), compound='top', image=self.logo)
        self.loading = Progressbar(self.base, orient=VERTICAL, length=500)
        self.search_frame = Frame(self.base)
        self.side_frame = tb.Frame(self.base, style="Custom.TLabel")
        self.product_list = Listbox(self.base, font=('Arial', 15), background='white', height=17, width=75)
        self.entry = Entry(self.search_frame, font=('Arial', 30))
        self.bars = tb.Label(self.base, image=self.sideicon, cursor='hand2')
        self.search_button = tb.Button(self.search_frame, text="Search", cursor='hand2', style='Normal.TButton', takefocus=0, 
                             command=lambda: search(self.entry.get(), self.product_list, self.websites, self.web_list, self.links, self.search_button))
        self.open_button = tb.Button(self.base, image=self.arrow, cursor='hand2', style='Normal.TButton', takefocus=0, 
                                     command=lambda: open_links(self.links, self.product_list.curselection()))
        self.switch_button = tb.Button(self.base, text='Multi', cursor='hand2', style='Normal.TButton', takefocus=0, 
                                       command=lambda: toggle_muliple(self.switch_button, self.product_list))
        self.sort_by = tb.OptionMenu(self.base, self.sort_select, *self.sort_options, style='Custom.TMenubutton')
        self.sort_by['menu'].config(font=('Arial', 15))

        for i in range(len(self.websites)):
            website = self.websites[i].split(';')[0]
            self.web_list.append(BooleanVar())
            self.web_list[i].set(True) 
            new_check = tb.Checkbutton(self.side_frame, variable=self.web_list[i], onvalue=True, offvalue=False,
                                       text=website, cursor='hand2', style="Custom.TCheckbutton")
            new_check.pack(anchor='w', padx=15, pady=10)
            if i == 0:
                new_check.pack_configure(pady=(115, 10))

        #Display Functions
        def toggle_button(button):
            if button.cget('style') == 'Normal.TButton':
                button.config(style='Toggled.TButton')
            else:
                button.config(style='Normal.TButton')
            button.update()

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

        def search(user_input, listbox, websites, web_check, links, button):
            if(user_input == ""):
                return
            toggle_button(button)
            button.config(state=DISABLED)
            self.loading['value'] = 0
            self.base.update()
            results = []
            for i in range(len(websites)):
                if web_check[i].get() == True:
                    result = search_items(user_input, websites[i].split(';'))
                    results.append(result)
                    self.loading['value'] += 60/len(websites)
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
            button.config(state=NORMAL)
            toggle_button(button)


        def open_links(listbox, indexes):
            for i in indexes:
                webbrowser.open(listbox[i])

        def toggle_sidebar(event, sidebar):
            if sidebar.winfo_manager() != 'place':
                event.widget.config(style="Custom.TLabel")
                sidebar.place(x=0, y=0, relheight=1)
            else:
                event.widget.config(style='')
                sidebar.place_forget()

        def on_enter(button):
            button.invoke()
           

        def on_click(event):
            lists = event.widget
            if lists.cget('selectmode') == MULTIPLE or lists.size() == 0:
                return
            curr = lists.get(lists.curselection()) 
            if curr != self.product_select:
                self.product_select = curr
            else:
                open_links(self.links, lists.curselection())

        def on_hover(event):
            listbox = event.widget
            item = listbox.nearest(event.y)
            if listbox.get(item) == self.product_select:
                listbox.config(cursor="hand2")
            else:
                listbox.config(cursor="arrow")
                
        def toggle_muliple(button, listbox):
            if listbox.cget('selectmode') != MULTIPLE:
                listbox.config(selectmode='multiple')
            else:
                listbox.selection_clear(0, END)
                listbox.config(selectmode='browse')
            toggle_button(button)

        self.base.bind("<Return>", lambda event: on_enter(self.search_button))
        self.bars.bind("<Button-1>", lambda event: toggle_sidebar(event, self.side_frame))
        self.product_list.bind("<<ListboxSelect>>", on_click)
        self.product_list.bind("<Motion>", on_hover)
        self.switch_button2 = tb.Button(self.base, text='Multi', cursor='hand2', style='Normal.TButton', takefocus=0, 
                                       command=lambda: toggle_muliple(self.switch_button, self.product_list))
        self.side_frame.pack_forget()
        self.bars.place(relx=0.005, rely=0.005)
        self.label.pack(pady=[0, 20])
        self.search_frame.pack()
        self.entry.pack(side=LEFT, padx=40)
        self.search_button.pack(side=RIGHT, padx=40)
        self.open_button.place(relx=0.82, rely=0.7, anchor="center", width=170)
        self.switch_button.place(relx=0.82, rely=0.81, anchor="center", width=170, height=75)
        self.sort_by.place(relx=0.82, rely=0.59, anchor="center", width=170, height=75)
        self.product_list.place(relx=0.5, rely=0.7, anchor="center")
        self.loading.place(relx=0.2, rely=0.449)