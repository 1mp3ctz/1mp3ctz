#!/usr/bin/env python3
"""Generate aurora-styled SVG cards (favourite languages + repo pins) into dist/."""
import json
import math
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "1mp3ctz"
PINS = ["spuk", "codex-coach"]
MAX_LANGS = 8

BG = "#0B1020"
BORDER = "#223055"
TITLE = "#22D3EE"
TEXT = "#C4CEE8"
MUTED = "#9BA8C4"
ACCENT = "#8B5CF6"

MONO = "'SF Mono',SFMono-Regular,ui-monospace,Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif"

# github linguist colors; AppleScript's official #101F1F is invisible on the dark card
LANG_COLORS = {
    "Python": "#3572A5", "Swift": "#F05138", "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A", "Go": "#00ADD8", "HTML": "#E34C26",
    "CSS": "#663399", "SCSS": "#C6538C", "Shell": "#89E051",
    "AppleScript": "#5E739E", "C#": "#178600", "C++": "#F34B7D",
    "C": "#555555", "Ruby": "#701516", "Kotlin": "#A97BFF",
    "Rust": "#DEA584", "Dart": "#00B4AB", "Vue": "#41B883",
    "Java": "#B07219", "PHP": "#4F5D95", "Makefile": "#427819",
    "Dockerfile": "#384D54", "Objective-C": "#438EFF", "Lua": "#000080",
}
FALLBACKS = ["#8B5CF6", "#22D3EE", "#F472B6", "#4ADE80", "#2DD4BF"]

STAR_PATH = ("M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 "
             ".416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 "
             "1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 "
             ".416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z")
REPO_PATH = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 "
             "0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 "
             "11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 "
             ".25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 "
             "0L5.4 15.7a.25.25 0 0 1-.4-.2Z")


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def lang_color(name, index):
    return LANG_COLORS.get(name, FALLBACKS[index % len(FALLBACKS)])


def card_shell(width, height, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
{body}
</svg>
"""


def languages_card(langs):
    total = sum(b for _, b in langs) or 1
    width, bar_x, bar_w = 420, 24, 372
    rows = math.ceil(len(langs) / 2)
    height = 96 + rows * 24

    parts = [f'  <text x="24" y="36" font-family="{SANS}" font-size="16" font-weight="700" fill="{TITLE}">favourite languages</text>']

    x = float(bar_x)
    for i, (name, size) in enumerate(langs):
        w = bar_w * size / total
        parts.append(
            f'  <rect x="{x:.2f}" y="52" width="{max(w - 1.5, 2):.2f}" height="10" rx="3" fill="{lang_color(name, i)}">\n'
            f'    <animate attributeName="width" from="0" to="{max(w - 1.5, 2):.2f}" dur="0.7s" begin="{0.1 + i * 0.08:.2f}s" fill="freeze"/>\n'
            f'  </rect>'
        )
        x += w

    for i, (name, size) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 24 + col * 196, 92 + row * 24
        pct = 100 * size / total
        parts.append(
            f'  <g opacity="0">\n'
            f'    <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{0.3 + i * 0.07:.2f}s" fill="freeze"/>\n'
            f'    <circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{lang_color(name, i)}"/>\n'
            f'    <text x="{lx + 17}" y="{ly}" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{escape(name)} '
            f'<tspan fill="{MUTED}">{pct:.2f}%</tspan></text>\n'
            f'  </g>'
        )

    return card_shell(width, height, "favourite languages", "\n".join(parts))


def wrap(text, limit=52, max_lines=3):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= limit:
            current = candidate
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(lines + [current])) > len(" ".join(lines)):
        lines[-1] = lines[-1][: limit - 1].rstrip() + "…"
    return lines


def pin_card(repo):
    width, height = 420, 150
    name = escape(repo["name"])
    desc_lines = wrap(repo.get("description") or "")
    lang = repo.get("language") or "-"
    stars = repo.get("stargazers_count", 0)

    parts = [
        f'  <path transform="translate(24,20)" d="{REPO_PATH}" fill="{MUTED}"/>',
        f'  <text x="50" y="33" font-family="{SANS}" font-size="16" font-weight="700" fill="{TITLE}">{name}</text>',
    ]
    for i, line in enumerate(desc_lines):
        parts.append(f'  <text x="24" y="{62 + i * 19}" font-family="{SANS}" font-size="12.5" fill="{MUTED}">{escape(line)}</text>')

    lang_w = len(lang) * 7.6 + 22
    parts.append(f'  <circle cx="29" cy="{height - 25}" r="5" fill="{lang_color(lang, 0)}"/>')
    parts.append(f'  <text x="41" y="{height - 21}" font-family="{MONO}" font-size="12" fill="{TEXT}">{escape(lang)}</text>')
    parts.append(f'  <path transform="translate({41 + lang_w},{height - 33}) scale(0.8)" d="{STAR_PATH}" fill="{ACCENT}"/>')
    parts.append(f'  <text x="{59 + lang_w}" y="{height - 21}" font-family="{MONO}" font-size="12" fill="{TEXT}">{stars}</text>')

    return card_shell(width, height, f"{repo['name']} — pinned repository", "\n".join(parts))


def main():
    os.makedirs("dist", exist_ok=True)

    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    totals = {}
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        for lang, size in api(f"/repos/{USER}/{repo['name']}/languages").items():
            totals[lang] = totals.get(lang, 0) + size
    langs = sorted(totals.items(), key=lambda kv: -kv[1])[:MAX_LANGS]

    with open("dist/languages.svg", "w") as f:
        f.write(languages_card(langs))
    print(f"languages.svg: {', '.join(f'{n} {100 * s / sum(totals.values()):.1f}%' for n, s in langs)}")

    for pin in PINS:
        repo = api(f"/repos/{USER}/{pin}")
        with open(f"dist/pin-{pin}.svg", "w") as f:
            f.write(pin_card(repo))
        print(f"pin-{pin}.svg: ★{repo.get('stargazers_count', 0)} {repo.get('language')}")


if __name__ == "__main__":
    main()
