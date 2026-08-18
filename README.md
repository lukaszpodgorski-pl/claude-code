# Claude Code — oś czasu wydań

Interaktywna, przewijana w poziomie mapa całej historii Claude Code: **366 wydań,
4489 zmian, 43 kamienie milowe**, od `0.2.21` (3 marca 2025) do dziś.

Strona: **https://lukaszpodgorski.pl/claude-code/timeline**

Dwa języki (polski i angielski), tryb jasny i ciemny, wyszukiwarka pełnotekstowa
po obu wersjach językowych naraz. Cały changelog jest przetłumaczony na polski.

## Skąd dane

| Co | Źródło |
|---|---|
| treść changelogu | `raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` |
| daty wydań | rejestr npm — `registry.npmjs.org/@anthropic-ai/claude-code` |
| tłumaczenie na polski | Claude Code w trybie headless, wsadami po 40 wpisów |

Changelog nie zawiera dat, dlatego doklejane są daty publikacji paczek z npm.
Osiem wersji (m.in. `0.2.21`, `1.0.97`, `2.1.43`) nigdy nie trafiło do rejestru —
ich daty są interpolowane z sąsiednich wydań i oznaczone w panelu jako „data szacowana".

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
| szukanie | `/` albo pole w nagłówku; `↑` `↓` po wynikach, `Enter` otwiera |
| filtr kategorii | kliknięcie w chip legendy (ponowne zdejmuje filtr) |
| język, motyw | przyciski `PL`/`EN` i ikona motywu (auto → jasny → ciemny) |
| szczegóły wydania | kliknięcie w słupek; `Esc` zamyka panel |

Wybór języka i motywu zostaje w `localStorage`. Język można wymusić parametrem
`?lang=en` albo `?lang=pl`.

## Budowa

```powershell
python src\build.py            # pobiera źródła, buduje public\timeline\index.html
python src\build.py --offline  # to samo, ale wyłącznie z kopii w .cache
python src\translate.py        # dotłumacza wpisy, których nie ma w pamięci
python -m pytest tests -q      # testy
```

## Pliki

| Plik | Rola |
|---|---|
| `src/fetch_sources.py` | pobranie changelogu i dat z npm, kopia w `.cache` |
| `src/parse_changelog.py` | parser changelogu + doklejenie i interpolacja dat |
| `src/build.py` | klasyfikacja zmian, sklejenie danych z szablonem |
| `src/translate.py` | tłumaczenie wsadowe przez `claude -p` |
| `src/translations.py` | pamięć tłumaczeń kluczowana sha1 oryginału |
| `src/milestones.py` | kuratorowana lista 43 kamieni milowych i 4 er, dwujęzyczna |
| `src/i18n.py` | teksty interfejsu i etykiety kategorii w obu językach |
| `src/template.html` | szablon strony (CSS + JS), znacznik `/*__DATA__*/` na dane |
| `public/` | to, co serwuje Cloudflare Pages |

## Kategorie

Każda zmiana trafia do jednej z 12 kategorii przez uporządkowaną listę reguł
(pierwsza pasująca wygrywa) w `build.py`. Kolejność reguł ma znaczenie: wzorce ogólne
(`API`, `network`, `retry`) stoją **za** dziedzinowymi, żeby nie podkradać wpisów
o MCP, modelach czy uprawnieniach. Do kategorii „Pozostałe" wpada ok. 5% zmian.

Kamienie milowe nie są wykrywane automatycznie — to ręcznie wybrana lista
zakotwiczona w konkretnych wersjach, zweryfikowana przez wyszukanie pierwszego
wystąpienia danej funkcji w changelogu.

## Wdrożenie na Cloudflare

Strona stoi na **Workerze ze statycznymi zasobami**, nie na Pages. Powód: Pages
przypina się do całej nazwy hosta, a ta strona ma żyć pod ścieżką
`/claude-code/` na istniejącej domenie, której korzeń obsługuje co innego.
Worker przechwytuje tylko dwie trasy, reszta domeny idzie na stary origin bez zmian.

Pierwsze wdrożenie, raz:

```powershell
npx wrangler login     # logowanie do konta Cloudflare z tą domeną
npx wrangler deploy    # tworzy Workera, wysyła public/ i rejestruje trasy
```

Kolejne wdrożenia robi GitHub Actions przy każdym pushu do `main`
(`.github/workflows/deploy.yml`). Wymaga dwóch sekretów w repozytorium:

| Sekret | Skąd |
|---|---|
| `CLOUDFLARE_API_TOKEN` | panel Cloudflare, szablon **Edit Cloudflare Workers** |
| `CLOUDFLARE_ACCOUNT_ID` | `npx wrangler whoami` po zalogowaniu |

```powershell
gh secret set CLOUDFLARE_API_TOKEN --repo lukaszpodgorski-pl/claude-code-timeline-changelog
gh secret set CLOUDFLARE_ACCOUNT_ID --repo lukaszpodgorski-pl/claude-code-timeline-changelog
```

Trasy są w `wrangler.toml`. Są dwie, bo wzorzec `/claude-code/*` nie łapie adresu
bez kończącego ukośnika. Warunkiem działania tras jest rekord DNS domeny
proxowany przez Cloudflare (pomarańczowa chmurka).

## Aktualizacja

Strona odświeża się sama. Zadanie `claude_code_timeline` w kontenerze `automation`
raz dziennie pobiera changelog, tłumaczy nowe wpisy, przebudowuje stronę i wypycha
commit do tego repozytorium; Cloudflare Pages wdraża go automatycznie.
Bez nowych wydań zadanie kończy się bez commita.

---

## English

An interactive timeline of every Claude Code release, built from the public
Anthropic changelog and npm publication dates. The interface and the full changelog
are available in both Polish and English; light and dark themes; full-text search
that matches across both languages at once.

The site updates itself: a daily job fetches the changelog, translates new entries,
rebuilds the page and pushes a commit, which Cloudflare Pages deploys.

Data belongs to Anthropic; this repository only reorganises and translates it.
