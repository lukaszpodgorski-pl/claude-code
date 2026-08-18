# Oś czasu Claude Code

Interaktywna, przewijana w poziomie mapa całej historii wydań Claude Code —
od `0.2.21` (3 marca 2025) do `2.1.234` (17 sierpnia 2026). **366 wydań, 4489 zmian,
43 kamienie milowe.**

Otwórz `timeline.html` w przeglądarce. Plik jest samodzielny — nie wymaga serwera
ani internetu (bez sieci fonty IBM Plex podmienią się na systemowe).

## Skąd dane

| Co | Źródło |
|---|---|
| treść changelogu | `%USERPROFILE%\.claude\cache\changelog.md` (lokalny cache Claude Code) |
| daty wydań | rejestr npm — `https://registry.npmjs.org/@anthropic-ai/claude-code` |

Changelog nie zawiera dat, dlatego doklejane są daty publikacji paczek z npm.
358 z 366 wersji ma datę dokładną; 8 (m.in. `0.2.21`, `1.0.97`, `2.1.43`) nigdy nie
trafiło do rejestru — ich daty są interpolowane z sąsiednich wydań i oznaczone
w panelu jako „data szacowana".

## Jak czytać

- **Pas kamieni milowych** (góra) — karty z ikoną flagi. Kolor lewej krawędzi = kategoria.
  Najedź, żeby rozwinąć pełny opis; kliknij, żeby otworzyć panel wydania.
- **Słupki** (środek) — jedno wydanie = jeden słupek. Wysokość to liczba zmian,
  segmenty to kategorie. Jasność segmentu koduje rodzaj zmiany:
  pełna = nowość, przygaszona = ulepszenie, ciemna = poprawka.
- **Pasy kategorii** (dół) — gęstość zmian w danej kategorii w czasie.
- **Tło** — cztery ery: `0.2.x` research preview, `1.0.x` GA, `2.0.x`, `2.1.x`.

Skala wysokości słupków odnosi się do 92. percentyla liczby zmian, nie do maksimum —
inaczej `2.1.0` (90 wpisów) spłaszczyłoby wszystkie pozostałe wydania.

## Sterowanie

| Akcja | Jak |
|---|---|
| przewijanie w bok | kółko myszy, przeciąganie tła, `←` `→`, `PageUp` / `PageDown` |
| początek / koniec | `Home` / `End` |
| następny / poprzedni kamień milowy | `N` / `M` albo przyciski w nagłówku |
| szukanie w treści zmian | `/` albo pole w nagłówku; `Enter` skacze do kolejnego trafienia |
| filtr kategorii | kliknięcie w chip legendy (ponowne kliknięcie zdejmuje filtr) |
| szczegóły wydania | kliknięcie w słupek; `Esc` zamyka panel |
| skok w czasie | kliknięcie lub przeciągnięcie po minimapie na dole |

## Przebudowa

```powershell
python build.py
```

Generuje `timeline.html` (samodzielny dokument) i `artifact.html` (sama treść strony,
bez `<html>`/`<head>`/`<body>` — do publikacji jako Artifact).

Po nowych wydaniach Claude Code odśwież najpierw daty z npm:

```powershell
$r = Invoke-RestMethod "https://registry.npmjs.org/@anthropic-ai/claude-code"
$map = @{}
foreach ($p in $r.time.PSObject.Properties) {
  if ($p.Name -notin @('created','modified')) { $map[$p.Name] = ([datetime]$p.Value).ToString('yyyy-MM-dd') }
}
$map | ConvertTo-Json -Depth 3 | Set-Content data\npm_times.json -Encoding UTF8
python build.py
```

## Pliki

| Plik | Rola |
|---|---|
| `build.py` | klasyfikacja zmian na kategorie i rodzaje, sklejenie danych z szablonem |
| `parse_changelog.py` | parser `changelog.md` + dołączenie dat z npm |
| `milestones.py` | kuratorowana lista 43 kamieni milowych i 4 er |
| `template.html` | szablon strony (CSS + JS), znacznik `/*__DATA__*/` na dane |
| `data/npm_times.json` | mapa wersja → data publikacji |
| `data/releases.json` | sparsowany changelog z datami (produkt uboczny parsera) |
| `timeline.html` | **gotowa strona do otwarcia** |
| `artifact.html` | ta sama strona w formie treści do publikacji |

## Kategorie

Każda zmiana trafia do jednej z 12 kategorii przez uporządkowaną listę reguł
(pierwsza pasująca wygrywa) w `build.py`. Kolejność reguł ma znaczenie: wzorce ogólne
(`API`, `network`, `retry`) stoją **za** dziedzinowymi, żeby nie podkradać wpisów
o MCP, modelach czy uprawnieniach. Do kategorii „Pozostałe" wpada ok. 5% zmian.

Kamienie milowe nie są wykrywane automatycznie — to ręcznie wybrana lista
zakotwiczona w konkretnych wersjach, zweryfikowana przez wyszukanie pierwszego
wystąpienia danej funkcji w changelogu.
