# Claude Code - oś czasu wydań

Interaktywna, przewijana w poziomie mapa całej historii Claude Code: **366 wydań,
4489 zmian, 43 kamienie milowe**, od `0.2.21` (3 marca 2025) do dziś.

Strona: **https://lukaszpodgorski.pl/claude-code/timeline**

Dwa języki (polski i angielski), tryb jasny i ciemny, wyszukiwarka pełnotekstowa
po obu wersjach językowych naraz. Cały changelog jest przetłumaczony na polski.

## Skąd dane

| Co | Źródło |
|---|---|
| treść changelogu | publiczny changelog Claude Code na GitHubie |
| daty wydań | rejestr npm paczki `@anthropic-ai/claude-code` |
| tłumaczenie na polski | Claude Code w trybie headless, wsadami |

Changelog nie zawiera dat, dlatego doklejane są daty publikacji paczek z npm.
Osiem wersji (m.in. `0.2.21`, `1.0.97`, `2.1.43`) nigdy nie trafiło do rejestru -
ich daty są interpolowane z sąsiednich wydań i oznaczone w panelu jako „data szacowana".

## Jak czytać

- **Pas kamieni milowych** (góra) - karty z ikoną flagi. Kolor lewej krawędzi = kategoria.
  Najedź, żeby rozwinąć pełny opis; kliknij, żeby otworzyć panel wydania.
- **Słupki** (środek) - jedno wydanie = jeden słupek. Wysokość to liczba zmian,
  segmenty to kategorie. Jasność segmentu koduje rodzaj zmiany:
  pełna = nowość, przygaszona = ulepszenie, ciemna = poprawka.
- **Pasy kategorii** (dół) - gęstość zmian w danej kategorii w czasie.
- **Tło** - cztery ery: `0.2.x` research preview, `1.0.x` GA, `2.0.x`, `2.1.x`.

Skala wysokości słupków odnosi się do 92. percentyla liczby zmian, nie do maksimum -
inaczej `2.1.0` (90 wpisów) spłaszczyłoby wszystkie pozostałe wydania.

## Sterowanie

| Akcja | Jak |
|---|---|
| przewijanie w bok | kółko myszy, przeciąganie tła, `←` `→`, `PageUp` / `PageDown` |
| początek / koniec | `Home` / `End` |
| następny / poprzedni kamień milowy | `N` / `M` albo przyciski w nagłówku |
| szukanie | `/` albo pole w nagłówku; `↑` `↓` po wynikach, `Enter` otwiera |
| filtr kategorii | kliknięcie w chip legendy (ponowne zdejmuje filtr) |
| język, motyw | przyciski `PL`/`EN` i ikona motywu (auto → jasny → ciemny) |
| szczegóły wydania | kliknięcie w słupek; `Esc` zamyka panel |

Wybór języka i motywu zostaje w `localStorage`. Język można wymusić parametrem
`?lang=en` albo `?lang=pl`.

## Kategorie

Każda zmiana trafia do jednej z 12 kategorii przez uporządkowaną listę reguł,
gdzie pierwsza pasująca wygrywa. Kolejność reguł ma znaczenie: wzorce ogólne
(`API`, `network`, `retry`) stoją **za** dziedzinowymi, żeby nie podkradać wpisów
o MCP, modelach czy uprawnieniach. Do kategorii „Pozostałe" wpada ok. 5% zmian.

Kamienie milowe nie są wykrywane automatycznie - to ręcznie wybrana lista
zakotwiczona w konkretnych wersjach, zweryfikowana przez wyszukanie pierwszego
wystąpienia danej funkcji w changelogu.

## Aktualizacja

Strona odświeża się sama. Codzienne zadanie pobiera changelog, tłumaczy nowe wpisy,
przebudowuje stronę i publikuje ją automatycznie. Bez nowych wydań nic się nie zmienia.

---

## English

An interactive timeline of every Claude Code release, built from the public
Anthropic changelog and npm publication dates. The interface and the full changelog
are available in both Polish and English; light and dark themes; full-text search
that matches across both languages at once.

The site updates itself: a daily job fetches the changelog, translates new entries,
rebuilds the page and publishes it. Nothing changes on days without a release.

Data belongs to Anthropic; this repository only reorganises and translates it.
