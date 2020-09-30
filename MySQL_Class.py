# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 03:19:01 2019

This class was originally meant to interact with a MySQL server, but has been
adapted to Sqlite instead. Some methods don't work, but are not used in the 
application anyways. 

@author: Wolfgang Breu
"""
import os
#import mysql.connector
import sqlite3
#from mysql.connector import errorcode
import MySQL_config as guiConf

class MySQL():
    # class variable
    GUIDB  = 'Essensdatenbank'   
     
    #------------------------------------------------------
    def connect(self):
        # connect by unpacking dictionary credentials
        # conn = mysql.connector.connect(**guiConf.config)
        database = os.path.join(os.getcwd(), 'Essensdatenbank.db')
        conn = sqlite3.connect(database)
    
        # create cursor 
        cursor = conn.cursor()    
        
            
        return conn, cursor
    
    #------------------------------------------------------    
    def close(self, cursor, conn):        
        # close cursor
        cursor.close()
                
        # close connection to MySQL
        conn.close()    

    #------------------------------------------------------        
    def showDBs(self):
        # connect to MySQL
        conn, cursor = self.connect()        
        
        # print results
        cursor.execute("SHOW DATABASES")
        # print(cursor)
        print(cursor.fetchall())

        # close cursor and connection
        self.close(cursor, conn)
                   
    #------------------------------------------------------
    def createGuiDB(self):
        # connect to MySQL
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(MySQL.GUIDB))
        except mysql.connector.Error as err:
            print("Failed to create DB: {}".format(err))        

        # close cursor and connection
        self.close(cursor, conn) 

    #------------------------------------------------------
    def dropGuiDB(self):
        # connect to MySQL
        conn, cursor = self.connect()
        try:
            cursor.execute(
                "DROP DATABASE {}".format(MySQL.GUIDB))
        except mysql.connector.Error as err:
            print("Failed to drop DB: {}".format(err))        

        # close cursor and connection
        self.close(cursor, conn) 
             
    #------------------------------------------------------        
    def useGuiDB(self, cursor):
        '''Expects open connection.'''
        # select DB
        cursor.execute("USE Essensdatenbank")
        
     #------------------------------------------------------
    def showTables(self):
        # connect to MySQL
        conn, cursor = self.connect()
    
        # show Tables from guidb DB
        cursor.execute("SHOW TABLES FROM Essensdatenbank") 
        print(cursor.fetchall())
        
        # close cursor and connection
        self.close(cursor, conn)        
        
    #------------------------------------------------------        
    def insertProdukt(self, name, ablaufdatum, ort, hinzugefügt):
        # connect to MySQL
        conn, cursor = self.connect()
        
        # self.useGuiDB(cursor)
        
        # insert data
        cursor.execute("INSERT INTO Produkte (Produkt_Name, Produkt_Ablaufdatum, Produkt_Ort, Produkt_Hinzugefügt) VALUES ('{}','{}','{}','{}')".format(name, ablaufdatum, ort, hinzugefügt))
        # last inserted auto increment value   
        keyID = cursor.lastrowid 
        
        # commit transaction
        conn.commit ()

        # close cursor and connection
        self.close(cursor, conn)
        
        return keyID
    
    #------------------------------------------------------        
    def showProdukte(self, sortierung):
        # connect to MySQL
        conn, cursor = self.connect()    
        
        # self.useGuiDB(cursor)    
        
        # print results
        cursor.execute("SELECT * FROM Produkte ORDER BY (%s)" % sortierung)
        alleProdukte = cursor.fetchall()
#        print(alleProdukte)

        # close cursor and connection
        self.close(cursor, conn)   
        
        return alleProdukte
    
    #------------------------------------------------------        
    def goodProdukte(self, sortierung):
        # connect to MySQL
        conn, cursor = self.connect()    
        
        # self.useGuiDB(cursor)    
        
        # print results
        cursor.execute("SELECT * FROM Produkte WHERE Produkt_Ablaufdatum > date('now') ORDER BY (%s)" % sortierung)
        guteProdukte = cursor.fetchall()
#        print(guteProdukte)

        # close cursor and connection
        self.close(cursor, conn)   
        
        return guteProdukte
    
    #------------------------------------------------------        
    def badProdukte(self, sortierung):
        # connect to MySQL
        conn, cursor = self.connect()    
        
        # self.useGuiDB(cursor)    
        
        # print results
        cursor.execute("SELECT * FROM Produkte WHERE Produkt_Ablaufdatum < date('now') ORDER BY (%s)" % sortierung)
        schlechteProdukte = cursor.fetchall()
#        print(schlechteProdukte)

        # close cursor and connection
        self.close(cursor, conn)   
        
        return schlechteProdukte
    
    #------------------------------------------------------        
    def deleteProdukt(self, ID):
        # connect to MySQL
        conn, cursor = self.connect()   
        
        # self.useGuiDB(cursor)      
        
        try: 
            # execute command
            cursor.execute("DELETE FROM Produkte WHERE Produkt_ID = (%s)", (ID,))
            
            # commit transaction
            conn.commit ()
        except:
            pass
               
        # close cursor and connection
        self.close(cursor, conn)  
        
    #-------------------------------------------------------
    def createTable(self):
        # connect to MySQL
        conn, cursor = self.connect()   
        
        # check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        if "Produkte" not in tables:
        
            # self.useGuiDB(cursor)
            try:
                # cursor.execute("CREATE TABLE Produkte (Produkt_ID INT NOT NULL 1 AUTO_INCREMENT PRIMARY KEY,"\
                                                       # "Produkt_Name VARCHAR(128) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,"\
                                                       # "Produkt_Ablaufdatum DATE NOT NULL,"\
                                                       # "Produkt_Ort VARCHAR(25) NOT NULL,"\
                                                       # "Produkt_Hinzugefügt DATE NOT NULL) ENGINE=InnoDB")
                cursor.execute("CREATE TABLE Produkte (Produkt_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"\
                                                       "Produkt_Name CHARACTER NOT NULL,"\
                                                       "Produkt_Ablaufdatum DATE NOT NULL,"\
                                                       "Produkt_Ort VARCHAR(25) NOT NULL,"\
                                                       "Produkt_Hinzugefügt DATE NOT NULL);")
                conn.commit()
            except:
                pass
                
        conn.close()
        
    #-------------------------------------------------------
    def dropTable(self):
        # connect to MySQL
        conn, cursor = self.connect()   
        
        # self.useGuiDB(cursor)
        try:
            cursor.execute("DROP TABLE Produkte")
            conn.commit ()
        except:
            pass
        
    #-------------------------------------------------------
    def importTextFile(self, filename, hinzugefügt):
        # read in text file with products listed
        
        with open(filename, 'r') as f:
            file = [[item.strip() for item in line.split(',')] for line in f.readlines()]
            
        # fileformat: Name, Ablaufdatum, Ort
        for line in file:
            try:
                name, date, place = line[:3]
#                name = name.encode('utf-8')
            except ValueError:
                print(line)
            self.insertProdukt(name, date, place, hinzugefügt)
            
        