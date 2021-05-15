from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
import requests
from tkinter import messagebox
import socket
import pickle
import sys
sys.setrecursionlimit(10000) #dla prawidlowego zapisania slownika do pliku pickle

class Current(tk.Frame):

    def __init__(self, root):
        """
        Iniicjuje poczatkowe wartsoci: wysokosć szerokośc, czcionke
        Przekształcam dane
        """

        self.height = 600
        self.width = 400
        self.title = root.title('Currency Converter')
        self.canvas = tk.Canvas(root, height=self.height, width=self.width)
        self.canvas.pack()

        self.font = ('courier', 12)

        self.tab = []  # lista przechowująca dane(nazwa waluty, symbol, kurs, zmiana(zł)
        for i in range(len(self.Strona()['Nazwa waluty'])-1):
            self.tab.append(self.Strona()['Symbol'][i] + ' - ' + self.Strona()['Nazwa waluty'][i])

        self.Strona()['newcol'] = self.tab #tworze nowa kolumne przechowujaca dane postaci: symbol - nazwa waluty, np 1 PLN - Złoty

        d = ['1 PLN -  złoty'] + self.tab  # uzpełniam tablice o brakujące dane dla polskiej waluty
        self.data = d

        self.interface(root)


    def interface(self,root):
        """
        Funkcja tworząca interfejs
        """

        self.up = tk.Frame(root, bg="#68C6F9")
        self.up.place(relx=0, rely=0, relwidth=1, relheight=0.5)

        text = tk.Label(self.up, bg="#68C6F9", fg="#ffffff", font=('consolas', 22),
                        justify='center', text="Currency")
        text.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.20, anchor="n")

        self.entry = tk.Entry(self.up, bg="#68C6F9", bd=0, font=('consolas', 20), fg="#ffffff")
        self.entry.place(relx=0.25, rely=0.45, relwidth=0.4, relheight=0.2, anchor='n')

        line1 = tk.Frame(self.up)
        line1.place(relx=0.25, rely=0.63, relheight=0.01, relwidth=0.4, anchor="n")


        self.down = tk.Frame(root, background="#ffffff")
        self.down.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

        changebutton = tk.Button(root, bg="#ffffff", bd=1, fg="#68C6F9", text=u"\u2b81", relief="ridge",
                                          font=('consolas', 20), command=lambda: self.change())
        changebutton.place(relx=0.775, relwidth=0.15, rely=0.45, relheight=0.1, anchor='n')

        button = tk.Button(root, text="Convert", font=('consolas', 20), bg="#ffffff", bd=1, fg="#68C6F9",
                                    relief="ridge", command=self.pln_other)
        button.place(relx=0.35, relwidth=0.4, rely=0.45, relheight=0.1, anchor='n')

        line2 = tk.Frame(self.down, bg="#68C6F9")
        line2.place(relx=0.25, rely=0.63, relheight=0.01, relwidth=0.4, anchor="n")

        button_end = tk.Button(self.down, text="EXIT", bd=0, fg="#68C6F9", bg="#ffffff",
                               font=('consolas', 15), command=lambda: self.end(root))
        button_end.place(relx=0.5, rely=0.8, relwidth=0.2, relheight=0.1, anchor='n')


        self.currency = ttk.Combobox(root, font=('consolas', 11),textvariable=tk.StringVar())
        self.currency['values'] = self.data
        self.currency.current(0) #domyślnie ustawiam polską walutę jako pierwszą
        self.currency.place(relx=0.75, rely=0.22, relheight=0.1, relwidth=0.45, anchor="n")

        self.currency_1 = ttk.Combobox(root, font=('consolas', 11), textvariable=tk.StringVar())
        self.currency_1['values'] = self.data
        self.currency_1.current(2) #domyślnie dolar amerykanski jako pierwszy
        self.currency_1.place(relx=0.75, rely=0.72, relheight=0.1, relwidth=0.45, anchor="n")


    def change(self):
        """
        Funkcja zamienia wartości rozwijanych przycisków - self.currency i self.currency_1
        a także zamienia je miejscami
        """
        self.currency_1.place(rely=0.22)
        self.currency.place(rely=0.72)
        self.currency, self.currency_1 = self.currency_1, self.currency


    def is_connected(self):
        """
        Funkcja sparawdza połaczenie z internetem
        :return: True gdy mamy połączenie lub False w przeciwnym wypadku
        """
        try:
            socket.create_connection(("www.nbp.pl", 80))
            return True
        except OSError:
            pass
        return False

    def Strona(self):
        """
        Funkcja pobierająca dane ze strony i przekształające je na słownik.
        Zapisuję dane do formatu .pkl
        W sytuacji braku połączenia sieciowego korzysta z ostatnich zapisanych danych.

        :return: Slownik z danymi, przchowujacy: nazwe waluty, symbol, kurs
        """
        if self.is_connected() == True:
            index_url = "https://www.nbp.pl/home.aspx?f=/kursy/kursya.html"
            r = requests.get(index_url)

            soup = BeautifulSoup(r.content, 'html.parser')
            h2 = soup.find_all('tr') #pobieram elemnty zawerajce tr

            dane = []
            for i in h2[43:-16]: #interesujace nas dane zawieraja sie w tym przedziale
                currents = [link.string for link in i.find_all('td')]
                dane.extend(currents)
            repair = [('Nazwa waluty', []), ('Symbol', []), ('Kurs', ["1"])] # zamieszczam kurs dla polskiej waluty

            for i, el in enumerate(dane): # rozdzielam nazwy walut, symbole i kursy do osobnych list
                if i % 3 == 0:
                    repair[0][1].append(el)
                elif (i + 2) % 3 == 0:
                    repair[1][1].append(el)
                elif (i + 1) % 3 == 0:
                    repair[2][1].append(el)

            Dict = {title: column for (title, column) in repair} #tworze slownik z danymi

            with open('saved_currents.pkl', 'wb') as output: #zapisuje do pliku pickle
                pickle.dump(Dict, output)
            output.close()

            return Dict
        else: # w przyapdku braku internetu pobieram zapisane wczesniej dane
            pkl_file = open('saved_currents.pkl', 'rb')
            Dict2 = pickle.load(pkl_file)
            pkl_file.close()

            return Dict2

    def pln_other(self):
        """
        Funkcja przeliczająca kursy walut
        Sprawda czy podana wartość jest liczbą
        Obsługuje sytuacje gdy podamy dwie takie same waluty

        Wynik liczymy wedlug wzoru (zakladamy ze kurs PLN = 1):

            wpisana wartość * (kurs pierwszej waluty / kurs drugiej waluty)


        :return: wypisuje wynik w Label o nazwie output
        """

        if self.entry.get().replace('.','',1).isdigit() == False:
            self.output = tk.Label(self.down, fg="#68C6F9", bd=0, font=('consolas 16 bold'), bg="#ffffff", anchor="s")
            self.output.place(relx=0.25, rely=0.35, relwidth=0.4, relheight=0.25, anchor='n')

            self.output["text"] = "Enter\nnumber."


        elif self.currency_1.get() == self.currency.get():
            self.output = tk.Label(self.down, fg="#68C6F9", bd=0, font=('consolas', 16), bg="#ffffff", anchor="s")
            self.output.place(relx=0.25, rely=0.35, relwidth=0.4, relheight=0.25, anchor='n')


            self.output["text"] = "Enter two\ndifferent\ncurrencies."

        else:
            self.output = tk.Label(self.down, fg="#68C6F9", bd=0, font=('consolas', 20), bg="#ffffff",anchor="s")
            self.output.place(relx=0.25, rely=0.35, relwidth=0.4, relheight=0.25, anchor='n')


            txt = self.Strona()["Kurs"][self.data.index(self.currency.get())]
            x = txt.replace(",", ".") #w naszych danych kurs jest zapisany w postaci np "4,56" , musimy zmienic do postaci "4.56"
            txt1 = self.Strona()["Kurs"][self.data.index(self.currency_1.get())]
            x1 = txt1.replace(",", ".")
            wynik = float(self.entry.get()) * (float(x) / float(x1))


            #stosuję dodatkowe obliczenia dla poniższych walut aby uzyskać przeliczenie "jeden do jednego"
            kurs_100 = ["100 HUF - forint (Węgry)","100 JPY - jen (Japonia)","100 ISK - korona islandzka",
                        "100 CLP - peso chilijskie","100 INR - rupia indyjska","100 KRW - won południowokoreański"]
            kurs_1000 = "10000 IDR - rupia indonezyjska"

            if self.currency.get() in kurs_100:
                self.output["text"] = round(wynik * 0.01, 2)
            elif self.currency_1.get() in kurs_100:
                self.output["text"] = round(wynik * 100, 2)

            elif self.currency.get() == kurs_1000:
                self.output["text"] = round(wynik * 0.0001, 2)
            elif self.currency_1.get() == kurs_1000:
                self.output["text"] = round(wynik * 10000, 2)

            else:
                self.output["text"] = round(wynik, 2)


    def end(self,root):
        """
        Funkcja wyłączająca program
        """
        result = messagebox.askquestion("Exit", "Are you sure you want to terminate the program?",
                                        icon='warning')
        if result == 'yes':
            root.quit()
            root.destroy()
            sys.exit()
        else:
            pass
