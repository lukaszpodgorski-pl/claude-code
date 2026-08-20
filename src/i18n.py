# -*- coding: utf-8 -*-
"""Teksty interfejsu i etykiety kategorii w obu jezykach.

Wszystko, co widzi uzytkownik, siedzi tutaj. W szablonie nie ma ani jednego
zaszytego napisu — dzieki temu przelaczenie jezyka jest pelne, a nie polowiczne.
"""

# klucz, etykieta PL, etykieta EN, kolor na ciemnym tle, kolor na jasnym tle
TOPICS = [
    ("model",    "Modele i rozumowanie",        "Models and reasoning",      "#D97757", "#B4502C"),
    ("agents",   "Agenci, workflow, plan mode", "Agents, workflows, plan mode", "#F5B841", "#9A6B06"),
    ("mcp",      "MCP i konektory",             "MCP and connectors",        "#45C8E0", "#0E7C93"),
    ("skills",   "Skille, pluginy, komendy",    "Skills, plugins, commands", "#7FD858", "#3C8A22"),
    ("hooks",    "Hooki i harmonogramy",        "Hooks and schedules",       "#B588F0", "#6E3FB0"),
    ("security", "Uprawnienia i sandbox",       "Permissions and sandbox",   "#F2545B", "#C0202A"),
    ("ide",      "IDE, desktop, web",           "IDE, desktop, web",         "#5B8DEF", "#2A55B8"),
    ("sdk",      "SDK, API, plany",             "SDK, API, plans",           "#2DD4A7", "#0A8C6A"),
    ("context",  "Kontekst i pamięć",           "Context and memory",        "#9BA6F5", "#4F5CC4"),
    ("ui",       "Interfejs terminala",         "Terminal interface",        "#F27DB0", "#B62A6B"),
    ("core",     "Rdzeń i platformy",           "Core and platforms",        "#A0AEC0", "#5A6676"),
    ("other",    "Pozostałe",                   "Other",                     "#6E675E", "#6E675E"),
]

UI = {
    "pl": {
        "title": "Oś czasu Claude Code",
        "htmlLang": "pl",
        "searchPlaceholder": "Szukaj w changelogu…",
        "searchAria": "Szukaj w treści zmian",
        "prevMile": "Poprzedni kamień milowy (M)",
        "nextMile": "Następny kamień milowy (N)",
        "milesBtn": "Kamienie",
        "lanesBtn": "Pasy",
        "lanesTitle": "Pokaż lub ukryj pasy kategorii",
        "tableBtn": "Tabela",
        "tableTitle": "Changelog w tabeli (T)",
        "tableHead": "Changelog Claude Code",
        "colVersion": "Wersja",
        "colDate": "Data",
        "colTopic": "Kategoria",
        "colKind": "Rodzaj",
        "colChange": "Zmiana",
        "allTopics": "Wszystkie kategorie",
        "homeTitle": "Strona główna: lukaszpodgorski.pl",
        "themeTitle": "Motyw: {v}",
        "themeAuto": "auto",
        "themeLight": "jasny",
        "themeDark": "ciemny",
        "langTitle": "Switch to English",
        "langBtn": "EN",
        "close": "Zamknij (Esc)",
        "estimated": "(data szacowana)",
        "kinds": ["poprawka", "ulepszenie", "nowość"],
        "months": ["sty", "lut", "mar", "kwi", "maj", "cze",
                   "lip", "sie", "wrz", "paź", "lis", "gru"],
        "changes": ["zmiana", "zmiany", "zmian"],
        "releases": ["wydanie", "wydania", "wydań"],
        # miejscownik po „w”: „w 85 wydaniach”, nie „w 85 wydań”
        "releasesIn": ["wydaniu", "wydaniach", "wydaniach"],
        "hits": ["trafienie", "trafienia", "trafień"],
        "inReleases": "w {n} {word}",
        "noHits": "brak trafień",
        "resultsMore": "pokazano {shown} z {total}",
        "searchHint": "Wpisz co najmniej 2 znaki",
        "hint": "Przewijaj kółkiem w bok · <kbd>←</kbd><kbd>→</kbd> ruch · "
                "<kbd>N</kbd> następny kamień milowy · <kbd>/</kbd> szukaj · "
                "kliknij słupek po szczegóły",
        # widoczny podpis pod tytułem: adres ma się opatrzeć, nie chować w tooltipie
        "brand": "lukaszpodgorski.pl",
        "stats": "{r} {rw} · {e} {ew} · {v1} → {v2} · {d1} → {d2}",
        "milestone": "Kamień milowy",
        "untranslated": "brak tłumaczenia, tekst oryginalny",
        "matchedIn": "szukana fraza trafiła w tej wersji językowej",
        # newsletter: przycisk w nagłówku, belka po 20 s i modal z formularzem
        "nlBtn": "Newsletter",
        "nlBtnTitle": "Zapisz się do newslettera",
        "nlBarText": "Zainteresowany tym tematem? Dołącz do mojego newslettera "
                     "i bądź na bieżąco z tego typu nowościami.",
        "nlBarCta": "Kliknij tutaj",
        "nlBarClose": "Zamknij na 14 dni",
        "nlTitle": "Newsletter",
        "nlLead": "Piszę o Claude Code, AI i automatyzacji pracy. Jeden mail, gdy jest o czym. "
                  "Wypisujesz się jednym kliknięciem.",
        "nlEmail": "Adres e-mail",
        "nlEmailPh": "ty@przyklad.pl",
        "nlConsent": "Zgadzam się na otrzymywanie newslettera i przetwarzanie mojego adresu "
                     "w tym celu.",
        "nlPrivacy": "Polityka prywatności",
        "nlConsentReq": "Zaznacz zgodę, żeby kontynuować.",
        "nlSubmit": "Zapisz się",
        "nlSending": "Wysyłam…",
        "nlOkTitle": "Jeszcze jeden krok",
        "nlOkText": "Wysłałem link potwierdzający na podany adres. Kliknij go, "
                    "żeby dokończyć zapis.",
        "nlErrEmail": "To nie wygląda na poprawny adres e-mail.",
        "nlErrDup": "Ten adres jest już na liście.",
        "nlErrGeneric": "Nie udało się zapisać. Spróbuj ponownie za chwilę.",
    },
    "en": {
        "title": "Claude Code Timeline",
        "htmlLang": "en",
        "searchPlaceholder": "Search the changelog…",
        "searchAria": "Search change descriptions",
        "prevMile": "Previous milestone (M)",
        "nextMile": "Next milestone (N)",
        "milesBtn": "Milestones",
        "lanesBtn": "Lanes",
        "lanesTitle": "Show or hide category lanes",
        "tableBtn": "Table",
        "tableTitle": "Changelog as a table (T)",
        "tableHead": "Claude Code changelog",
        "colVersion": "Version",
        "colDate": "Date",
        "colTopic": "Category",
        "colKind": "Kind",
        "colChange": "Change",
        "allTopics": "All categories",
        "homeTitle": "Home page: lukaszpodgorski.pl",
        "themeTitle": "Theme: {v}",
        "themeAuto": "auto",
        "themeLight": "light",
        "themeDark": "dark",
        "langTitle": "Przełącz na polski",
        "langBtn": "PL",
        "close": "Close (Esc)",
        "estimated": "(estimated date)",
        "kinds": ["fix", "improvement", "new"],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "changes": ["change", "changes", "changes"],
        "releases": ["release", "releases", "releases"],
        "releasesIn": ["release", "releases", "releases"],
        "hits": ["hit", "hits", "hits"],
        "inReleases": "in {n} {word}",
        "noHits": "no matches",
        "resultsMore": "showing {shown} of {total}",
        "searchHint": "Type at least 2 characters",
        "hint": "Scroll sideways with the wheel · <kbd>←</kbd><kbd>→</kbd> move · "
                "<kbd>N</kbd> next milestone · <kbd>/</kbd> search · "
                "click a bar for details",
        # widoczny podpis pod tytułem: adres ma się opatrzeć, nie chować w tooltipie
        "brand": "lukaszpodgorski.pl",
        "stats": "{r} {rw} · {e} {ew} · {v1} → {v2} · {d1} → {d2}",
        "milestone": "Milestone",
        "untranslated": "not translated, original text",
        "matchedIn": "the search phrase matched this language version",
        # newsletter: przycisk w nagłówku, belka po 20 s i modal z formularzem
        "nlBtn": "Newsletter",
        "nlBtnTitle": "Subscribe to the newsletter",
        "nlBarText": "Interested in this topic? Join my newsletter and keep up "
                     "with news like this.",
        "nlBarCta": "Click here",
        "nlBarClose": "Dismiss for 14 days",
        "nlTitle": "Newsletter",
        "nlLead": "I write about Claude Code, AI and automating work. One email when there is "
                  "something worth sending. One click to unsubscribe.",
        "nlEmail": "Email address",
        "nlEmailPh": "you@example.com",
        "nlConsent": "I agree to receive the newsletter and to my address being processed "
                     "for that purpose.",
        "nlPrivacy": "Privacy policy",
        "nlConsentReq": "Tick the consent box to continue.",
        "nlSubmit": "Subscribe",
        "nlSending": "Sending…",
        "nlOkTitle": "One more step",
        "nlOkText": "I sent a confirmation link to that address. Click it to finish "
                    "signing up.",
        "nlErrEmail": "That does not look like a valid email address.",
        "nlErrDup": "That address is already on the list.",
        "nlErrGeneric": "Could not sign you up. Please try again in a moment.",
    },
}


def check():
    """Sanity: kazdy klucz interfejsu istnieje w obu jezykach i nie jest pusty."""
    braki = []
    for lang, other in (("pl", "en"), ("en", "pl")):
        for k, v in UI[lang].items():
            if k not in UI[other]:
                braki.append("%s brakuje w %s" % (k, other))
            if isinstance(v, str) and not v.strip():
                braki.append("%s.%s jest puste" % (lang, k))
            if isinstance(v, list) and not all(str(x).strip() for x in v):
                braki.append("%s.%s ma pusta pozycje" % (lang, k))
    return braki
