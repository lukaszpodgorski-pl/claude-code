# -*- coding: utf-8 -*-
"""Buduje oś czasu Claude Code: changelog + daty npm + tłumaczenia -> strona.

Wyjście:
  public/timeline/index.html  pełny dokument serwowany przez Cloudflare Pages
  build/artifact.html         sama treść, do okazjonalnej publikacji jako Artifact

Uruchomienie:  python src/build.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from parse_changelog import load  # noqa: E402
from milestones import MILESTONES, ERAS  # noqa: E402
import i18n  # noqa: E402
import translations  # noqa: E402

TOPICS = i18n.TOPICS
TIDX = {t[0]: i for i, t in enumerate(TOPICS)}

TRANSLATIONS = os.path.join(HERE, "data", "translations.json")
OUT_PAGE = os.path.join(ROOT, "public", "timeline", "index.html")
OUT_ARTIFACT = os.path.join(ROOT, "build", "artifact.html")

# --- reguły klasyfikacji: pierwsza pasująca wygrywa ------------------------
RULES = [
    ("sdk", r"Agent SDK|Claude Code SDK|\bSDK\b|Bedrock|Vertex|Foundry|Team plan|[Ee]nterprise"
            r"|managed settings|OTEL|telemetry|\bAPI key|/usage\b|usage limit|rate limit|billing"
            r"|pricing|subscription|Max plan|Pro plan|--print\b|headless|\bproxy\b|gateway|/cost"),
    ("mcp", r"\bMCP\b|Model Context Protocol|\.mcp\.json|MCPSearch|\bconnectors?\b"),
    ("model", r"\b(Opus|Sonnet|Haiku|Fable)\b|claude-(opus|sonnet|haiku|fable)|/model\b|\bmodels?\b"
              r"|\beffort\b|fast mode|thinking|ultrathink|reasoning|1M[- ]?(token|context)|output token"),
    ("hooks", r"\bhooks?\b|PreToolUse|PostToolUse|SessionStart|SessionEnd|PreCompact|SubagentStop"
              r"|UserPromptSubmit|PermissionDenied|\bcron\b|Cron[A-Z]|scheduled? (agent|task|prompt|run)"),
    ("skills", r"\bskills?\b|SKILL\.md|\bplugins?\b|marketplace|slash command|/commands?\b"
               r"|custom commands?|output styles?"),
    ("agents", r"subagents?|sub-agents?|/agents\b|\bagents?\b|teammate|agent teams?|\bworkflows?\b"
               r"|Task tool|SendMessage|ListAgents|plan mode|/plan\b|Monitor tool|orchestrat"
               r"|background (task|agent)"),
    ("security", r"permissions?|sandbox|security|credentials?|OAuth|secrets?|redact|\btrust\b|allowlist"
                 r"|allowedTools|disallowedTools|bypassPermissions|dangerously|vulnerab|CVE|\bauth\b"
                 r"|authenticat|hardening|injection"),
    ("ide", r"VS ?Code|VSCode|JetBrains|IntelliJ|\bIDE\b|[Dd]esktop|Chrome|browser|claude\.ai/code"
            r"|on the web|Remote Control|/teleport|remote-env|remote session|\bphone\b|mobile"),
    # warstwa transportowa/API — po kategoriach dziedzinowych, żeby im nie podkradać
    ("sdk", r"prompt cach|\bretry\b|\bretries\b|ECONNRESET|\bstreaming\b|non-streaming|\bHTTP\b"
            r"|\bmTLS\b|x-client-request|apiKeyHelper|ANTHROPIC_|\bAPI\b|\bnetwork\b|\bquota\b"),
    ("context", r"compact|CLAUDE\.md|AGENTS\.md|\bmemory\b|/memory|checkpoints?|/rewind|--continue"
                r"|--resume|/resume\b|\bcontext\b|\bsessions?\b|conversation|@-mention|transcript size"
                r"|\bhistory\b"),
    ("ui", r"render|terminal|spinner|scroll|keybinding|key binding|\bvim\b|shortcut|paste|clipboard"
           r"|dialog|transcript|markdown|theme|statusline|status line|footer|Ctrl[-+]|Alt\+|Shift\+"
           r"|\bEsc\b|fullscreen|/tui\b|ink2|\bUI\b|cursor|emoji|autocomplete|selection|prompt input"
           r"|/config\b|notification|display|tooltip|badge|animation|colou?r|queue[ds]?\b|/copy\b"
           r"|/voice\b|\bvoice\b|drag.and.drop|\bmenu\b|highlight|indicator|\bhint\b|popup"
           r"|AskUserQuestion|screen reader|\bicon\b|\bwrap\w*\b|/feedback|/stats\b|\bpicker\b"
           r"|\bfocus\b|\btext\b|\bpress\b|\bkey\b"),
    ("core", r"performance|startup|install|native|Windows|WSL|macOS|Linux|\bnpm\b|[Nn]ode|update"
             r"|upgrade|version|migrat|crash|memory leak|\bgit\b|\bdiff\b|\bLSP\b|Jupyter|notebook"
             r"|\bfiles?\b|Bash|shell|environment variable|\benv\b|encoding|Unicode|CJK"
             r"|\btools?\b|Grep|ripgrep|NotebookEdit|\bPDF\b|PowerShell|WebFetch|TaskCreate"
             r"|worktree|CLAUDE_CONFIG_DIR|bundle size|\bsettings?\b|PersistentShell|caffeinate"
             r"|Ghostty|tmux|\blogs?\b|logging|/doctor|/checkup|\bimages?\b|directory|directories"),
]
RULES = [(TIDX[k], re.compile(p)) for k, p in RULES]

PREFIX = re.compile(r"^\s*(\[[^\]]{1,24}\]|[A-Z][A-Za-z0-9 /.]{0,18}:)\s*")
FIX = re.compile(r"^\s*(\*\*)?(Fixed|Fix|Fixes|Resolved|Reverted)\b", re.I)
IMP = re.compile(r"^\s*(\*\*)?(Improved?|Reduced?|Changed?|Updated?|Removed?|Renamed?|Increased?"
                 r"|Decreased?|Simplified|Optimiz\w*|Refactor\w*|Deprecat\w*|Moved?|Replaced?"
                 r"|Disabled?|Enabled?|Made|Clarified|Bumped|Raised|Lowered|Unshipped|Restored"
                 r"|Tweaked|Polished|Relaxed|Expanded?|Extended?|Better)\b", re.I)


def topic_of(text):
    for ti, rx in RULES:
        if rx.search(text):
            return ti
    return TIDX["other"]


def kind_of(text):
    """2 = nowość, 1 = ulepszenie, 0 = poprawka"""
    core = PREFIX.sub("", text, count=1)
    for probe in (text, core):
        if FIX.search(probe):
            return 0
    for probe in (text, core):
        if IMP.search(probe):
            return 1
    return 2


def make_data(offline=False):
    """Skleja changelog, klasyfikację, tłumaczenia i teksty w jeden ładunek."""
    rel = load(offline=offline)
    by_v = {r["version"]: i for i, r in enumerate(rel)}
    store = translations.load(TRANSLATIONS)

    releases = []
    for r in rel:
        ents = []
        for e in r["entries"]:
            # pusty łańcuch zamiast braku klucza: strona pokaże oryginał
            ents.append([topic_of(e), kind_of(e), e, store.get(translations.key(e), "")])
        releases.append([r["version"], r["date"], 1 if r["date_exact"] else 0, ents])

    miles = []
    for m in MILESTONES:
        if m["v"] not in by_v:
            raise SystemExit("Kamień milowy wskazuje na nieistniejącą wersję: " + m["v"])
        miles.append({"i": by_v[m["v"]], "topic": m["topic"], "big": bool(m["big"]),
                      "title": {"pl": m["title_pl"], "en": m["title_en"]},
                      "desc": {"pl": m["desc_pl"], "en": m["desc_en"]}})
    miles.sort(key=lambda m: m["i"])

    eras = []
    for e in ERAS:
        idx = [i for i, r in enumerate(rel) if r["version"].startswith(e["prefix"])]
        if not idx:
            continue
        eras.append({"name": {"pl": e["name_pl"], "en": e["name_en"]},
                     "sub": {"pl": e["sub_pl"], "en": e["sub_en"]},
                     "from": idx[0], "to": idx[-1]})

    wpisy = [e for r in rel for e in r["entries"]]
    przetlumaczone, unikalne = translations.coverage(wpisy, store)

    return {
        "topics": [list(t) for t in TOPICS],
        "eras": eras,
        "milestones": miles,
        "releases": releases,
        "ui": i18n.UI,
        "meta": {
            "releases": len(releases),
            "entries": len(wpisy),
            "generated": rel[-1]["date"],
            "translated": przetlumaczone,
            "unique": unikalne,
        },
    }


def build(offline=False):
    data = make_data(offline=offline)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    with open(os.path.join(HERE, "template.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    if "/*__DATA__*/" not in tpl:
        raise SystemExit("Brak znacznika /*__DATA__*/ w template.html")
    body = tpl.replace("/*__DATA__*/", payload)

    head, rest = body.split("\n", 1)
    full = ('<!doctype html>\n<html lang="pl">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<meta name="description" content="Interaktywna oś czasu wszystkich wydań Claude Code. '
            'Interactive timeline of every Claude Code release.">\n'
            + head + "\n</head>\n<body>\n" + rest + "\n</body>\n</html>\n")

    for path, tresc in ((OUT_PAGE, full), (OUT_ARTIFACT, body)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(tresc)

    return data, len(full)


def report(data, rozmiar):
    per_topic = {t[0]: 0 for t in TOPICS}
    per_kind = [0, 0, 0]
    for r in data["releases"]:
        for e in r[3]:
            per_topic[TOPICS[e[0]][0]] += 1
            per_kind[e[1]] += 1
    m = data["meta"]
    print("wydań: %d   zmian: %d   kamieni milowych: %d   er: %d"
          % (m["releases"], m["entries"], len(data["milestones"]), len(data["eras"])))
    print("rodzaje: nowości %d | ulepszenia %d | poprawki %d" % (per_kind[2], per_kind[1], per_kind[0]))
    print("tłumaczenia: %d/%d unikalnych (%.1f%%)"
          % (m["translated"], m["unique"], 100.0 * m["translated"] / max(m["unique"], 1)))
    for t in TOPICS:
        n = per_topic[t[0]]
        print("  %-9s %5d  %s" % (t[0], n, "#" * int(n / 40)))
    print("strona: %.1f kB -> %s" % (rozmiar / 1024, os.path.relpath(OUT_PAGE, ROOT)))


if __name__ == "__main__":
    offline = "--offline" in sys.argv
    data, rozmiar = build(offline=offline)
    report(data, rozmiar)
