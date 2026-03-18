import psycopg2
from psycopg2 import sql, Error
import config
import math

class MenadzerBazyDanych:
    def __init__(self):
        self.polaczenie = None

    def polacz(self):
        if self.polaczenie is None or self.polaczenie.closed:
            try:
                self.polaczenie = psycopg2.connect(
                    dbname=config.dbname,
                    user=config.user,
                    password=config.password,
                    host=config.host,
                    port=config.port
                )
                return True
            except Error as e:
                print(f"Błąd połączenia: {e}")
                return False
        return True

    def _wykonaj(self, zapytanie, parametry=None, pobierz=False):
        if not self.polacz(): return ([], []) if pobierz else False
        try:
            with self.polaczenie.cursor() as kursor:
                kursor.execute(zapytanie, parametry)
                if pobierz:
                    naglowki = [opis[0] for opis in kursor.description] if kursor.description else []
                    return naglowki, kursor.fetchall()
                self.polaczenie.commit()
                return True
        except Error as e:
            print(f"Błąd bazy danych: {e}")
            if self.polaczenie: self.polaczenie.rollback()
            return ([], []) if pobierz else False

    def pobierz_tabele(self):
        zapytanie = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type IN ('BASE TABLE', 'VIEW');"
        _, wiersze = self._wykonaj(zapytanie, pobierz=True)
        return [wiersz[0] for wiersz in wiersze]

    def pobierz_kolumny(self, nazwa_tabeli):
        zapytanie = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = {}").format(sql.Literal(nazwa_tabeli))
        _, wiersze = self._wykonaj(zapytanie, pobierz=True)
        return [wiersz[0] for wiersz in wiersze]

    def pobierz_dane_tabeli(self, nazwa_tabeli, kolumny=None, sortuj_po=None, rosnaco=True, limit=50, przesuniecie=0, kolumna_filtra=None, wartosc_filtra=None):
        pola = sql.SQL(", ").join(map(sql.Identifier, kolumny)) if kolumny else sql.SQL("*")
        zapytanie = sql.SQL("SELECT {pola} FROM {tabela}").format(pola=pola, tabela=sql.Identifier(nazwa_tabeli))
        
        parametry = []
        if kolumna_filtra and wartosc_filtra:
            zapytanie += sql.SQL(" WHERE CAST({} AS TEXT) = %s").format(sql.Identifier(kolumna_filtra))
            parametry.append(wartosc_filtra)

        if sortuj_po:
            kierunek = sql.SQL("ASC") if rosnaco else sql.SQL("DESC")
            zapytanie += sql.SQL(" ORDER BY {} {}").format(sql.Identifier(sortuj_po), kierunek)

        zapytanie += sql.SQL(" LIMIT %s OFFSET %s")
        parametry.extend([limit, przesuniecie])
        return self._wykonaj(zapytanie, parametry, pobierz=True)

    def pobierz_sume_stron(self, nazwa_tabeli, rozmiar_strony, kolumna_filtra=None, wartosc_filtra=None):
        zapytanie = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(nazwa_tabeli))
        parametry = []
        if kolumna_filtra and wartosc_filtra:
            zapytanie += sql.SQL(" WHERE CAST({} AS TEXT) = %s").format(sql.Identifier(kolumna_filtra))
            parametry.append(wartosc_filtra)
        
        _, wiersze = self._wykonaj(zapytanie, parametry, pobierz=True)
        suma_wierszy = wiersze[0][0] if wiersze else 0
        return max(1, math.ceil(suma_wierszy / rozmiar_strony))

    def wykonaj_wstawianie(self, nazwa_tabeli, slownik_danych):
        kolumny = slownik_danych.keys()
        wartosci = list(slownik_danych.values())
        zapytanie = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(nazwa_tabeli),
            sql.SQL(', ').join(map(sql.Identifier, kolumny)),
            sql.SQL(', ').join([sql.Placeholder()] * len(wartosci))
        )
        return self._wykonaj(zapytanie, wartosci)

    def wykonaj_usuwanie(self, nazwa_tabeli, kolumna_warunku, wartosc_warunku):
        zapytanie = sql.SQL("DELETE FROM {} WHERE CAST({} AS TEXT) = %s").format(
            sql.Identifier(nazwa_tabeli), sql.Identifier(kolumna_warunku)
        )
        return self._wykonaj(zapytanie, (wartosc_warunku,))

    def wykonaj_aktualizacje(self, nazwa_tabeli, slownik_danych, kolumna_warunku, wartosc_warunku):
        dane_aktualizacji = {k: v for k, v in slownik_danych.items() if v is not None and str(v).strip() != ""}
        if not dane_aktualizacji: return False
        
        kolumny = list(dane_aktualizacji.keys())
        wartosci = list(dane_aktualizacji.values()) + [wartosc_warunku]
        klauzula_set = sql.SQL(', ').join([sql.SQL("{} = %s").format(sql.Identifier(k)) for k in kolumny])
        zapytanie = sql.SQL("UPDATE {} SET {} WHERE CAST({} AS TEXT) = %s").format(
            sql.Identifier(nazwa_tabeli), klauzula_set, sql.Identifier(kolumna_warunku)
        )
        return self._wykonaj(zapytanie, wartosci)