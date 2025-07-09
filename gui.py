import os
import sys
import webbrowser
import ttkbootstrap as tb
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter import messagebox
from scraper import search_items, sort_data, combine_search, copy_data


class App:
    def __init__(self, base):
        #For file access when turning into exe file
        path = getattr(sys, '_MEIPASS', os.path.abspath("."))

        #Window Setup
        self.base = base
        self.base.geometry('1920x1080')
        self.base.minsize(640, 360)
        self.base.state('zoomed')
        self.base.title('Product Scraper')
        self.base.iconbitmap(os.path.join(path, 'logo.ico'))

        #Universal Variables
        self.logo = PhotoImage(file=os.path.join(path, 'images', 'logo.png')).subsample(4, 4)
        self.sideicon = PhotoImage(file=os.path.join(path, 'images', 'drawing.png')).subsample(10, 10)
        self.arrow = PhotoImage(file=os.path.join(path, 'images', 'arrow.png')).subsample(5, 5)
        file = open(os.path.join(path, 'websites.txt'), 'r')
        self.websites = file.readlines()
        file.close()
        self.links = []
        self.product_select = "X"
        self.data = []
        self.web_list = []
        self.sort_options = ["Relevance", "Relevance", "Price", "Rating", "Reviews"]
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
                             command=lambda: search(self.entry.get(), self.product_list, self.websites, self.loading, self.search_button))
        self.open_button = tb.Button(self.base, image=self.arrow, cursor='hand2', style='Normal.TButton', takefocus=0, 
                                     command=lambda: open_links(self.product_list.curselection()))
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

        def show_options(list, df):
            list.delete(0, END)
            self.links.clear()
            col = ""
            max = 0
            if self.sort_select.get() != self.sort_options[0]:
                max = str(df.iloc[len(df) - 1][self.sort_select.get().lower()])
                if '.' in max:
                    max = str(df.iloc[len(df) - 1][self.sort_select.get().lower()])
                    max = max.split('.')[0]
                else:
                    max = str(df.iloc[0][self.sort_select.get().lower()])
                max = len(max)
                col = self.sort_select.get().lower()
            else:
                for i in range(len(df)):
                    list.insert(list.size(), '    ' + df.iloc[i]['title'])
                    self.links.append(df.iloc[i]['link'])
                return
            for i in range(len(df)):
                if self.sort_select.get() == self.sort_options[3]:
                    symbol = '✰'
                elif self.sort_select.get() == self.sort_options[4]:
                    symbol = '#'
                else:
                    symbol = '$'
            
                combine = ''
                select = str(df.iloc[i][col])
                if '.' in select:
                    bef = select.split('.')[0]
                    aft = select.split('.')[1]      
                    bef_len = len(bef)
                    while bef_len < max:
                        bef = '  ' + bef
                        bef_len += 1
                    while len(aft) < 2:
                        aft = aft + '0'
                    combine = bef + '.' + aft
                else:
                    sel_len = len(select)
                    while sel_len < max:
                        select = '  ' + select
                        sel_len += 1
                    combine = select
                list.insert(list.size(), '    ' + symbol + combine + '    ' + '|' + '    ' + df.iloc[i]['title'])
                self.links.append(df.iloc[i]['link'])
        
        def check_sort():
            if self.sort_select.get() == self.sort_options[0]:
                return 0
            elif self.sort_select.get() == self.sort_options[2]:
                return 1
            else:
                return -1
            
        def search(user_input, listbox, websites, loading, button):
            if(user_input == ""):
                return
            toggle_button(button)
            button.config(state=DISABLED)
            loading['value'] = 0
            self.base.update()
            results = []
            for i in range(len(websites)):
                if self.web_list[i].get() == True:
                    result = search_items(user_input, websites[i].split(';'))
                    results.append(result)
                    loading['value'] += 60/len(websites)
                    self.base.update()
            if loading['value'] != 60:
                loading['value'] += 60 - loading['value']
            if len(results) == 0:
                messagebox.showwarning(title='Select Website', message='Please select at least one website!')
                return
            self.data.clear()
            combined_df = combine_search(results)
            copy_df = copy_data(combined_df)
            loading['value'] += 20
            self.base.update()
            self.data.append(combined_df)
            copy_df = copy_data(combined_df)
            #combined_df.sort_values(by=sort_select.get(), inplace=True)
            check = check_sort()
            if check != 0:
                sort_data(copy_df, 0, len(copy_df) - 1, self.sort_select.get().lower(), check) #For Practice
            loading['value'] += 20
            self.base.update()
            show_options(listbox, copy_df)
            button.config(state=NORMAL)
            toggle_button(button)

        def open_links(indexes):
            for i in indexes:
                webbrowser.open(self.links[i])

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
                open_links(lists.curselection())

        def on_hover(event):
            listbox = event.widget
            item = listbox.nearest(event.y)
            if listbox.get(item) == self.product_select:
                listbox.config(cursor="hand2")
            else:
                listbox.config(cursor="arrow")
        
        def on_change(lists):
            if lists.size() == 0:
                return
            check = check_sort()
            copy_df = copy_data(self.data[0])
            if check != 0:
                sort_data(copy_df, 0, len(copy_df) - 1, self.sort_select.get().lower(), check)
                show_options(lists, copy_df)
            else:
                show_options(lists, copy_df)
            
        
        def toggle_muliple(button, listbox):
            if listbox.cget('selectmode') != MULTIPLE:
                listbox.config(selectmode='multiple')
            else:
                listbox.selection_clear(0, END)
                listbox.config(selectmode='browse')
            toggle_button(button)


        #Binds for toggling functions above
        self.base.bind("<Return>", lambda event: on_enter(self.search_button))
        self.bars.bind("<Button-1>", lambda event: toggle_sidebar(event, self.side_frame))
        self.product_list.bind("<<ListboxSelect>>", on_click)
        self.product_list.bind("<Motion>", on_hover)
        self.sort_select.trace_add('write', lambda *args: on_change(self.product_list))


        #Packs and places widgets
        self.label.pack(pady=[0, 20])
        self.search_frame.pack()
        self.entry.pack(side=LEFT, padx=40)
        self.search_button.pack(side=RIGHT, padx=40)
        self.side_frame.pack_forget()
        self.bars.place(relx=0.005, rely=0.005)
        self.loading.place(relx=0.2, rely=0.449)
        self.product_list.place(relx=0.5, rely=0.7, anchor="center")
        self.open_button.place(relx=0.825, rely=0.7, anchor="center", width=170)
        self.sort_by.place(relx=0.825, rely=0.59, anchor="center", width=170, height=75)
        self.switch_button.place(relx=0.825, rely=0.81, anchor="center", width=170, height=75)