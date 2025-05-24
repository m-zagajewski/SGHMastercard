# 🥉 SGH x Mastercard Hackathon 2025 – 3. miejsce

## 🧠 OOH Delivery Scoring Engine (Backend)

Backendowy silnik scoringowy stworzony podczas **SGH x Mastercard Hackathon 2025**, odpowiedzialny za analizę potencjału lokalizacji dla rozwoju usług OOH delivery. Projekt zdobył **III miejsce** w konkursie.

## 📌 Opis projektu

Aplikacja oblicza wskaźnik potencjału lokalizacji dla rozwoju usług OOH delivery (np. paczkomatów), bazując na danych demograficznych, dostępności infrastruktury, gęstości zabudowy oraz bliskości istniejących punktów odbioru. Wynik scoringu przekazywany jest do aplikacji frontendowej w React.

## ⚙️ Stack technologiczny

- Python 3.10+
- FastAPI (API)
- Pandas, GeoPandas
- scikit-learn (KDTree)
- Shapely
- Open source dane: OSM, GUS, dane dostawców paczkomatów (InPost itp.)

## 🧮 Metodologia scoringu

Główne komponenty użyte do obliczeń:
- **Supply Score:** ilość paczkomatów na mieszkańca i na km²
- **Demand Score:** gęstość, dostępność, dostępność 24/7, liczba firm i parkingów
- **Końcowy score:** relacja zapotrzebowania do podaży (`demand_score / supply_score`)

## 👥 Autorzy

- Jan Ancuta
- Maciej Ciesielski
- Adam Sulik
- Michał Zagajewski
