import customtkinter as ctk
import MenadzerBazyDanych
import crud

class AplikacjaF1(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.baza = MenadzerBazyDanych.MenadzerBazyDanych()
        self.aktualna_strona = 0
        self.rozmiar_strony = 50
        
        self.title("F1 Eksplorator Danych")
        self.geometry("1100x700")
        self._konfiguruj_interfejs()
        self.aktualizuj_liste_kolumn(self.wybor_tabeli.get())

    def _konfiguruj_interfejs(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel boczny (Sidebar)
        self.panel_boczny = ctk.CTkFrame(self, width=250)
        self.panel_boczny.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkButton(self.panel_boczny, text="Zarządzaj Danymi", command=self.otworz_crud).pack(pady=10)
        
        self.wybor_tabeli = ctk.CTkOptionMenu(self.panel_boczny, values=self.baza.pobierz_tabele(), command=self.aktualizuj_liste_kolumn)
        self.wybor_tabeli.pack(pady=10)

        self.ramka_kolumn = ctk.CTkScrollableFrame(self.panel_boczny, width=200, height=250)
        self.ramka_kolumn.pack(pady=10, fill="both", expand=True)
        self.pola_wyboru_kolumn = {}

        # Nawigacja
        self.ramka_nawigacji = ctk.CTkFrame(self.panel_boczny, fg_color="transparent")
        self.ramka_nawigacji.pack(pady=20)
        self.przycisk_poprzednia = ctk.CTkButton(self.ramka_nawigacji, text="<", width=40, command=lambda: self.zmien_strone(-1))
        self.przycisk_poprzednia.grid(row=0, column=0, padx=5)
        self.etykieta_strony = ctk.CTkLabel(self.ramka_nawigacji, text="Strona: 1 / 1")
        self.etykieta_strony.grid(row=0, column=1, padx=10)
        self.przycisk_nastepna = ctk.CTkButton(self.ramka_nawigacji, text=">", width=40, command=lambda: self.zmien_strone(1))
        self.przycisk_nastepna.grid(row=0, column=2, padx=5)

        # Panel Wyników
        self.ramka_wynikow = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.ramka_wynikow.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Sekcja Sortowania i Filtrowania
        self.ramka_filtrowania = ctk.CTkFrame(self)
        self.ramka_filtrowania.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.ramka_filtrowania, text="Sortuj po:").grid(row=0, column=0, padx=5)
        self.wybor_sortowania = ctk.CTkOptionMenu(self.ramka_filtrowania, values=["---"])
        self.wybor_sortowania.grid(row=0, column=1, padx=5, pady=5)
        self.wybor_kierunku = ctk.CTkOptionMenu(self.ramka_filtrowania, values=["Rosnąco (ASC)", "Malejąco (DESC)"])
        self.wybor_kierunku.grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkLabel(self.ramka_filtrowania, text="Filtruj kolumnę:").grid(row=1, column=0, padx=5)
        self.wybor_kolumny_filtra = ctk.CTkOptionMenu(self.ramka_filtrowania, values=["---"])
        self.wybor_kolumny_filtra.grid(row=1, column=1, padx=5, pady=5)
        self.wpis_wartosci_filtra = ctk.CTkEntry(self.ramka_filtrowania, placeholder_text="Wartość (dokładna)...")
        self.wpis_wartosci_filtra.grid(row=1, column=2, padx=5, pady=5)
        
        ctk.CTkButton(self.ramka_filtrowania, text="Zastosuj filtry", command=self.zastosuj_filtry).grid(row=1, column=3, padx=5)

    def aktualizuj_liste_kolumn(self, nazwa_tabeli):
        for dziecko in self.ramka_kolumn.winfo_children(): dziecko.destroy()
        self.pola_wyboru_kolumn = {}
        kolumny = self.baza.pobierz_kolumny(nazwa_tabeli)
        
        for kol in kolumny:
            zmienna = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(self.ramka_kolumn, text=kol, variable=zmienna).pack(anchor="w", pady=2, padx=10)
            self.pola_wyboru_kolumn[kol] = zmienna
        
        opcje = ["---"] + kolumny
        self.wybor_sortowania.configure(values=opcje)
        self.wybor_sortowania.set("---")
        self.wybor_kolumny_filtra.configure(values=opcje)
        self.wybor_kolumny_filtra.set("---")
        self.wpis_wartosci_filtra.delete(0, 'end')
        self.zastosuj_filtry()

    def zmien_strone(self, delta):
        self.aktualna_strona += delta
        self.wyswietl_wyniki()

    def zastosuj_filtry(self):
        self.aktualna_strona = 0
        self.wyswietl_wyniki()

    def wyswietl_wyniki(self):
        tabela = self.wybor_tabeli.get()
        wybrane_kolumny = [kol for kol, var in self.pola_wyboru_kolumn.items() if var.get()]
        if not wybrane_kolumny: return

        k_filtra = self.wybor_kolumny_filtra.get()
        w_filtra = self.wpis_wartosci_filtra.get()
        finalna_k_filtra = None if k_filtra == "---" else k_filtra
        
        kol_sortowania = self.wybor_sortowania.get()
        finalne_sortowanie = None if kol_sortowania == "---" else kol_sortowania

        suma_stron = self.baza.pobierz_sume_stron(tabela, self.rozmiar_strony, finalna_k_filtra, w_filtra)
        self.etykieta_strony.configure(text=f"Strona: {self.aktualna_strona + 1} / {suma_stron}")
        
        self.przycisk_poprzednia.configure(state="normal" if self.aktualna_strona > 0 else "disabled")
        self.przycisk_nastepna.configure(state="normal" if self.aktualna_strona < suma_stron - 1 else "disabled")

        naglowki, wiersze = self.baza.pobierz_dane_tabeli(
            tabela, wybrane_kolumny, finalne_sortowanie, 
            "Rosnąco" in self.wybor_kierunku.get(),
            self.rozmiar_strony, self.aktualna_strona * self.rozmiar_strony,
            finalna_k_filtra, w_filtra
        )

        for w in self.ramka_wynikow.winfo_children(): w.destroy()
        for i, h in enumerate(naglowki):
            ctk.CTkLabel(self.ramka_wynikow, text=h.upper(), font=("Arial", 11, "bold"), fg_color="gray30").grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

        for r_idx, wiersz in enumerate(wiersze, 1):
            for c_idx, wartosc in enumerate(wiersz):
                ctk.CTkLabel(self.ramka_wynikow, text=str(wartosc) if wartosc is not None else "", font=("Arial", 10)).grid(row=r_idx, column=c_idx, padx=5, pady=1, sticky="w")

    def otworz_crud(self):
        crud.OknoCRUD(self, self.baza)

if __name__ == "__main__":
    AplikacjaF1().mainloop()