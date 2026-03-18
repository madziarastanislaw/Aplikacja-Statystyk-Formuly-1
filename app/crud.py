import customtkinter as ctk
from tkinter import messagebox

class OknoCRUD(ctk.CTkToplevel):
    def __init__(self, rodzic, menadzer_bazy):
        super().__init__(rodzic)
        self.baza = menadzer_bazy
        self.title("Panel Sterowania Danymi F1")
        self.geometry("500x700")
        self.attributes("-topmost", True)
        self.pola_wprowadzania = {}
        self._konfiguruj_interfejs()
        self.generuj_pola(self.wybor_tabeli.get())

    def _konfiguruj_interfejs(self):
        ctk.CTkLabel(self, text="Wybierz tabelę:", font=("Arial", 12, "bold")).pack(pady=5)
        self.wybor_tabeli = ctk.CTkOptionMenu(self, values=self.baza.pobierz_tabele(), command=self.generuj_pola)
        self.wybor_tabeli.pack(pady=5)

        self.ramka_pol = ctk.CTkScrollableFrame(self, width=450, height=350)
        self.ramka_pol.pack(pady=10, padx=10, fill="both", expand=True)

        self.ramka_warunku = ctk.CTkFrame(self)
        self.ramka_warunku.pack(pady=10, padx=10, fill="x")
        
        self.wybor_kolumny_warunku = ctk.CTkOptionMenu(self.ramka_warunku)
        self.wybor_kolumny_warunku.grid(row=0, column=1, padx=5, pady=5)
        self.wpis_wartosci_warunku = ctk.CTkEntry(self.ramka_warunku, placeholder_text="Wartość WHERE")
        self.wpis_wartosci_warunku.grid(row=2, column=1, padx=10, pady=10)

        ramka_przyciskow = ctk.CTkFrame(self)
        ramka_przyciskow.pack(pady=10)
        ctk.CTkButton(ramka_przyciskow, text="Wstaw (Insert)", fg_color="green", command=self.akcja_wstawiania).grid(row=0, column=0, padx=5)
        ctk.CTkButton(ramka_przyciskow, text="Aktualizuj (Update)", command=self.akcja_aktualizacji).grid(row=0, column=1, padx=5)
        ctk.CTkButton(ramka_przyciskow, text="Usuń (Delete)", fg_color="#922b21", command=self.akcja_usuwania).grid(row=0, column=2, padx=5)

        self.etykieta_statusu = ctk.CTkLabel(self, text="")
        self.etykieta_statusu.pack(pady=5)

    def generuj_pola(self, nazwa_tabeli):
        for widget in self.ramka_pol.winfo_children(): widget.destroy()
        self.pola_wprowadzania = {}
        kolumny = self.baza.pobierz_kolumny(nazwa_tabeli)
        for kol in kolumny:
            wiersz = ctk.CTkFrame(self.ramka_pol, fg_color="transparent")
            wiersz.pack(fill="x", pady=2)
            ctk.CTkLabel(wiersz, text=kol, width=120, anchor="w").pack(side="left")
            wpis = ctk.CTkEntry(wiersz)
            wpis.pack(side="right", fill="x", expand=True, padx=5)
            self.pola_wprowadzania[kol] = wpis
        
        self.wybor_kolumny_warunku.configure(values=kolumny)
        if kolumny: self.wybor_kolumny_warunku.set(kolumny[0])

    def pokaz_status(self, wiadomosc, kolor="white"):
        self.etykieta_statusu.configure(text=wiadomosc, text_color=kolor)

    def akcja_wstawiania(self):
        dane = {kol: (e.get() if e.get() else None) for kol, e in self.pola_wprowadzania.items()}
        if self.baza.wykonaj_wstawianie(self.wybor_tabeli.get(), dane):
            self.pokaz_status("Dodano rekord", "green")
        else:
            self.pokaz_status("Błąd INSERT", "red")

    def akcja_usuwania(self):
        wartosc = self.wpis_wartosci_warunku.get()
        if not wartosc: return self.pokaz_status("Wpisz wartość WHERE!", "red")
        
        if messagebox.askyesno("Potwierdzenie", "Usunąć rekord?"):
            if self.baza.wykonaj_usuwanie(self.wybor_tabeli.get(), self.wybor_kolumny_warunku.get(), wartosc):
                self.pokaz_status("Usunięto", "green")

    def akcja_aktualizacji(self):
        wartosc = self.wpis_wartosci_warunku.get()
        if not wartosc: return self.pokaz_status("Wpisz wartość WHERE!", "red")
        
        dane = {kol: e.get() for kol, e in self.pola_wprowadzania.items()}
        if self.baza.wykonaj_aktualizacje(self.wybor_tabeli.get(), dane, self.wybor_kolumny_warunku.get(), wartosc):
            self.pokaz_status("Zaktualizowano", "green")