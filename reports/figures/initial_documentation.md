# Projekt IUM - zadanie 2, zestaw danych 2
## Autorzy
- Bartosz Świrta *300390*
- Radosław Radziukiewicz 

## Słownik dziedziny problemu
- Użytkownik/Klient - osoba odwiedzająca stronę sklepu internetowego eSzoppping.
- Prowadzący - prowadzący projekt z przedmiotu IUM.

## Definicje problemu, zadania modelowania, założenia

### Definicja problemu
>Są osoby, które wchodzą na naszą stronę i nie mogą się zdecydować, którym produktom przyjrzeć się nieco lepiej. Może dało by się im coś polecić?

Z tak postawionego problemu wynika, że celem jest wytworzenie systemu rekomendujacego, który będzie rekomendował *"interesujące dla użytkownika"* produkty. Szczególnie należy podkreślić, że w problemie nie ma mowy bezpośrednio o podniesieniu liczby odsłon.

### Zadanie biznesowe
Analizując otrzymany problem można zdefiniować następujace zadanie biznesowe:
> Sugerowanie/rekomendowanie *"interesujących dla danego klienta"* produktów. 

### Biznesowe kryterium sukcesu
System powinien pozwolić na zwiększenie ilości przeglądanych przez użytkowników produktów o 10%.
Czyli o około 41 wyświetleń produktów dziennie więcej.

### Zadanie modelowania
W ramach projektu wykonane zostanie jedno zadanie modelowania. Mianowicie wytowrzenie modelu rekomendacyjnego, który dla danego użytkownika, na podstawie jego historii interkacji w sklepie (oglądane/kupione produkty), wygeneruje listę polecanych produktów. 

### Analityczne kryterium sukcesu
Osiągnięcie odpowiedniego odsetka trafnych rekomendacji: *alfa*.

Przjmujemy: liczba trafnych rekomendacji/liczba wszystkich rekomendacji >= *alfa*  
,gdzie *alfa* to parametr oszacowany na podstawie dostarczonych danych i wynoszący 41/dzienna liczba wyświetleń produktów

### Przyjęte założenia

- Model zostanie zbudowany wyłącznie w oparciu o dostarczone przez prowadzącego dane, w szczególności nie mamy możliwości zebrania danych na własną rękę.
- Docelowe rozwiązanie ma umożliwiać ciągłe rekomendowanie (system działajacy ciągle).

## Analiza danych z perspektywy realizowanego zadania
Od prowadzącego otrzymaliśmy cztery zbiory danych zawierające informacje o:
- użytkownikach zarejestrowanych w sklepie internetowym (users).
- produktach oferowanych prze sklep internetowy (products).
- sesjach użytkowników (sessions).
- przeprowadzonych dostawach (deliveries).

### Wstępna analiza
Dane zostały wstępnie przeanalizowane w poszukiwaniu błędów w danych i brakujących wartości.
#### Dane użytkowników (users)
Analiza wykazała, że dane odnośnie ulic zostały źle wpisane. Przed nazwą ulicy znajdują się zbędne słowa takie jak: *ul.*, *ulica*, *plac*, *aleja*. Ze wzgledu na to, że zadanie dotyczy systemu rekomendacji, dokładne adresy użytkowników nie będą nam potrzebne.  
Poza wyżej wymienionymi problemami, analiza nic nie wykazała, stąd z perspektwy realizowanego zadania uznajemy te dane za poprawne.

#### Dane sesji (sessions)
W danych sesji wykryto około 8% brakujących danych w kolumnie *purchase_id*, jednakże należy zauważyć że odnoszą się one jedynie do zdażeń oznaczonych jako *VIEW_PRODUCT* co oznacza, że dany produkt nie został kupiony a tylko obejrzany, co jest poprawną reprezentacją danych. Nie stwierdzono innych brakujących danych.

#### Dane produktów (products)
Analiza nie wykazała brakujących wartości. Znaleźlśmy 3 produkty w kategorii *"Gry i konsole;Gry komputerowe"* o potencjalnie błędnej cenie wynoszącej 1. Nie znaleziono innych problemów.

#### Dane dostaw (deliveries)
Dane te nie zostaną wykorzystane w procesie modelowania, stąd pominęliśmy analizę tego zbioru.

