# -*- coding: utf-8 -*-
"""
This application is used to track the inventory of food items in storage. Its features include:
    - creating a database of available items
    - display items that are expired, and items that are good in separate lists
    - sort items by name, expiration date, location
    

@author: Wolfgang Breu
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import filedialog
#import ToolTip as tt
import datetime
import sqlite3 
#import mysql.connector
#from mysql.connector import errorcode
#import MySQL_config as guiConf
from MySQL_Class import MySQL
from VerticalScrolledFrame import VerticalScrolledFrame
#from ScrollWindow import ScrolledWindow
from threading import Thread

# Connect to MySQL database
mysql = MySQL()
mysql.createTable()

orte = ('Kühlschrank', 'Regal Keller', 'Kühlschrank Keller', 'Schrank Wohnzimmer', 'Schrank Küche')    
#today = datetime.datetime.today()
#print("today: {}".format(today.ctime()))
scrollheight = 600 # Heiht of scollable Frame

# Create GUI instance
win = tk.Tk()
win.title("Essensdatenbank")
tabControl = ttk.Notebook(win)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Alle Produkte")
tabControl.add(tab2, text="Gute Produkte")
tabControl.add(tab3, text="Abgelaufene Produkte")
tabControl.pack(expand=1, fill="both")

# Exit GUI cleanly
def _quit():
    win.quit()
    win.destroy()
    exit()
    
# Display a Message Box
def _msgBox():
#    msg.showinfo('Python Message Info Box', 'A Python GUI created using tkinter:'
#                 '\nThe year is 2019.')
#    msg.showwarning('Python Message Warning Box', 'A Python GUI created using tkinter:'
#                 '\nWarning: There might be a bug in this code.')
#    msg.showerror('Python Message Error Box', 'A Python GUI created using tkinter:'
#                 '\nError: Houston ~ we DO have a serious PROBLEM!')
    answer = msg.askyesnocancel('Python Message Multi Choice Box', 
                                'Are you sure you really wish to do this?')
    print(answer)
    
    
def add_entry():
    """Add an entry to the database."""
    name_var = tk.StringVar()
    datum_var = tk.StringVar()
    ort_var = tk.StringVar()
    new_win = tk.Toplevel(win)
    new_win.title("Neuer Eintrag")
    ttk.Label(new_win, text="Produktname: ").grid(row=0, column=0)
    ttk.Entry(new_win, textvariable=name_var).grid(row=0, column=1)
    ttk.Label(new_win, text="Ablaufdatum: ").grid(row=1, column=0)
    ttk.Entry(new_win, textvariable=datum_var).grid(row=1, column=1)
    ttk.Label(new_win, text="Ort: ").grid(row=2, column=0)
#    ttk.Entry(new_win, textvariable=ort_var).grid(row=2, column=1)
    ort_var = ttk.Spinbox(new_win, values=orte)
    ort_var.grid(row=2, column=1)
    today = datetime.datetime.today().date()
    
    def _create_entry(name, datum, ort, hinzugefügt):
        """"""
        ID = mysql.insertProdukt(name, datum, ort, hinzugefügt)       
        DataEntry(alle_produkte, ID, name, datum, ort, hinzugefügt)   
        if datetime.date.fromisoformat(datum.replace('.','-')) > today:
            new_list = gute_produkte
        else:
            new_list = schlechte_produkte
        DataEntry(new_list, ID, name, datum, ort, hinzugefügt)
        new_win.destroy()
        win.focus()
        
    ttk.Button(new_win, text="Erstellen", command=lambda: _create_entry(name_var.get(), datum_var.get(), ort_var.get(), today)).grid(columnspan=2)
 
    
def read_textfile():
    """Add product entries from a text file."""
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Import", filetypes=(("Textdateien", "*.txt"), ("alle Dateien","*.*")))
    today = datetime.datetime.today().date()
    import_thread = Thread(target=mysql.importTextFile, args=(filename, today))
    import_thread.start()
    import_thread.join()
    refresh_lists()
    

class DataEntry(object):
    """Display a data entry widget with Name, Ablaufdatum and buttons."""
    
    __counter = 0 # Anzahl der Instanzen
    
    def __init__(self, parent, ID, label, expdate, place, add_date):
        type(self).__counter += 1 # Erhöhe Anzahl der Instanzen
        self.add_date = add_date
        self.id = ID
        self.label = label
        self.expdate = expdate
        self.parent = parent
        self.place = place
        # define widgets
        self.name_label = ttk.Label(master=self.parent, text=self.label)
        self.expdate_label = ttk.Label(master=self.parent, text=self.expdate)
        self.options_button = ttk.Button(master=self.parent, text="Optionen", command=self.show_options)
        self.delete_button = ttk.Button(master=self.parent, text="X", command=self.delete)
        # grid all the widgets
        col=0
        for widget in [self.name_label, self.expdate_label, self.options_button, self.delete_button]:
            widget.grid(row=type(self).__counter, column=col, padx=4, sticky='W')
            col += 1
        
        
    def show_options(self):
        """Let the user change properties of this data entry."""
        msg.showinfo('Python Message Info Box', 'Hinzugefügt: {}'
                     '\nID: {}'
                     '\nOrt: {}'.format(self.add_date, self.id, self.place))
        
        
    def delete(self):
        """Remove this data entry."""
        mysql.deleteProdukt(self.id)
        type(self).__counter -= 1 # Verringere Anzahl der Instanzen
        for widget in [self.name_label, self.expdate_label, self.options_button, self.delete_button]:
            widget.destroy()
        
        
def refresh_lists():
    global alle_produkte, gute_produkte, schlechte_produkte, sortierung
    global scroll_all, scroll_bad, scroll_good
    
    try:
        for widget in alle_produkte, gute_produkte, schlechte_produkte:
            widget.destroy()
        for widget in scroll_all, scroll_good, scroll_bad:
            widget.destroy()
    except:
        pass
    
    scroll_all = VerticalScrolledFrame(tab1, height=scrollheight)
    scroll_all.pack(fill="both", expand=True)
    alle_produkte = ttk.LabelFrame(scroll_all.interior, text="Alle Vorhandenen Produkte")
    alle_produkte.grid(row=0, column=0)
    all_products = mysql.showProdukte(sortierung.get())
    for product in all_products:
        DataEntry(alle_produkte, *product)
    
    scroll_good =VerticalScrolledFrame(tab2, height=scrollheight)
    scroll_good.pack(fill="both", expand=True)
    gute_produkte = ttk.LabelFrame(scroll_good.interior, text="Gute Produkte")
    gute_produkte.grid(row=0, column=0)
    good_products = mysql.goodProdukte(sortierung.get())
    for product in good_products:
        DataEntry(gute_produkte, *product)
        
    scroll_bad = VerticalScrolledFrame(tab3, height=scrollheight)
    scroll_bad.pack(fill="both", expand=True)
    schlechte_produkte = ttk.LabelFrame(scroll_bad.interior, text="Abgelaufene Produkte")
    schlechte_produkte.grid(row=0, column=0)
    bad_products = mysql.badProdukte(sortierung.get())
    for product in bad_products:
        DataEntry(schlechte_produkte, *product)
            
        
def refresh_lists_thread():
    run_thread = Thread(target=refresh_lists)
    run_thread.setDaemon(True)
    run_thread.start()
    
        
def refresh_callback(*args):
    refresh_lists_thread()
    
        
def _sort_expire():
    global sortierung
    sortierung.set("Produkt_Ablaufdatum")
    refresh_lists()


def _sort_place():
    global sortierung
    sortierung.set("Produkt_Ort")
    refresh_lists()


def _sort_name():
    global sortierung
    sortierung.set("Produkt_Name")    


def _sort_added():
    global sortierung
    sortierung.set("Produkt_Hinzugefügt")   
    

# Create a Menu bar
menu_bar = Menu(win)
win.config(menu=menu_bar)

# Create menu and add menu bar
file_menu = Menu(menu_bar, tearoff=0)                      # create File menu
file_menu.add_command(label="New", command=add_entry)      # add File menu item
file_menu.add_command(label="Import von Datei", command=read_textfile)
file_menu.add_command(label="Aktualisieren", command=refresh_callback)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=_quit)
menu_bar.add_cascade(label="File", menu=file_menu)   # add File menu to menu bar and give it a Label

options_menu = Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Sortieren nach")
options_menu.add_command(label="Ablaufdatum", command=_sort_expire)
options_menu.add_command(label="Hinzufügedatum", command=_sort_added)
options_menu.add_command(label="Lagerort", command=_sort_place)
options_menu.add_command(label="Name", command=_sort_name)
menu_bar.add_cascade(label="Optionen", menu=options_menu)

help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=_msgBox)

# Erstelle Liste der Produkte
#ttk.Label(tab1, text="Alle Vorhandenen Produkte").grid(row=0, column=0)
#ttk.Button(tab1, text="+", command=add_entry).grid(row=0, column=1)
sortierung = tk.StringVar()
sortierung.set("Produkt_Hinzugefügt") # default value
sortierung.trace("w", callback=refresh_callback)

refresh_lists()


win.mainloop()