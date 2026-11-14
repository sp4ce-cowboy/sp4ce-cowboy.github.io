"""Build index.html for rubesh.dev from the GitHub profile README, so the two never drift apart.

Reads from github.com/sp4ce-cowboy/sp4ce-cowboy (main):
  README.md               the bio (the whoami code block)
  .github/techstack.txt   the tech stack
  .github/projects.txt    the projects, with dates (newest first)

Run `python3 build.py`, check index.html, then commit and push. No dependencies.
"""
import datetime as dt, html, pathlib, re, urllib.request

RAW = "https://raw.githubusercontent.com/sp4ce-cowboy/sp4ce-cowboy/main/"
OUT = pathlib.Path(__file__).resolve().parent / "index.html"
LINKS = [("github", "https://github.com/sp4ce-cowboy"), ("linkedin", "https://www.linkedin.com/in/rubesh-suresh/")]

def fetch(path):
    return urllib.request.urlopen(RAW + path, timeout=30).read().decode()

def bio(readme):
    """The paragraphs of the whoami block, lines joined."""
    block = re.search(r"```sh\n(.*?)```", readme, re.S).group(1)
    return [" ".join(p.split("\n")).strip() for p in block.strip().split("\n\n")]

def newest_first(dates):
    if not dates:
        return (1, 0, 0)
    month = lambda d: int(d[:4]) * 12 + (int(d[5:7]) if len(d) >= 7 else 12)
    start, _, end = dates.partition("..")
    return (0, -month(end or start), -month(start))

def lists(text):
    """[(label, [(name, link)], starts_group)] from a techstack.txt-style list."""
    cats, new_group = [], False
    for line in text.splitlines():
        if not line.strip():
            new_group = True
        elif not line.startswith(" "):
            cats.append((line.strip(), [], new_group and bool(cats)))
            new_group = False
        else:
            name, link, dates = (line.strip().split("|") + ["", ""])[:3]
            cats[-1][1].append((name.strip(), link.strip(), dates.strip()))
    for _, items, _ in cats:
        items.sort(key=lambda item: newest_first(item[2]))
    return cats

def render_list(cats):
    rows = []
    for label, items, group in cats:
        parts = [f'<a href="{html.escape(l)}">{html.escape(n)}</a>' if l else html.escape(n) for n, l, _ in items]
        # each name keeps its separator, so a line never starts with "·" and no name breaks in two
        names = " ".join(f'<span>{part}{"&nbsp;·" if i < len(parts) - 1 else ""}</span>' for i, part in enumerate(parts))
        cls = ' class="gap"' if group else ""
        rows.append(f'  <dt{cls}>{html.escape(label)}</dt><dd{cls}>{names}</dd>')
    return "<dl>\n" + "\n".join(rows) + "\n</dl>"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>rubesh s.</title>
<meta name="description" content="Software engineering for Apple platforms, and agentic systems.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%23111'/><text x='50' y='68' font-size='56' text-anchor='middle' fill='white' font-family='-apple-system,Helvetica,Arial'>R</text></svg>">
<style>
  :root { --fg: #1a1a1a; --muted: #6b6b6b; --bg: #fffefa; --link: #0b57d0; }
  @media (prefers-color-scheme: dark) { :root { --fg: #e8e6e1; --muted: #9a978f; --bg: #141414; --link: #8ab4f8; } }
  html { background: var(--bg); }
  body { max-width: 640px; margin: 0 auto; padding: 56px 20px 72px; color: var(--fg);
         font: 17px/1.6 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }
  h1 { font-size: 1.6em; font-weight: normal; margin: 0 0 4px; }
  h2 { font-size: 1em; font-weight: bold; margin: 2.4em 0 0.6em; }
  nav { color: var(--muted); margin-bottom: 2em; }
  a { color: var(--link); text-decoration: none; }
  a:hover { text-decoration: underline; }
  p { margin: 0 0 1em; }
  dl { display: grid; grid-template-columns: max-content 1fr; column-gap: 1.4em; row-gap: 0.15em; margin: 0; }
  dt { color: var(--muted); }
  dd { margin: 0; }
  dd span { white-space: nowrap; }
  .gap { margin-top: 0.9em; }
  @media (max-width: 480px) { body { font-size: 16px; padding-top: 36px; } dl { column-gap: 1em; } }
  footer { margin-top: 3.5em; color: var(--muted); font-size: 0.85em; }
</style>
</head>
<body>
<header>
<h1>rubesh s.</h1>
<nav>{links}</nav>
</header>

<main>
{bio}

<h2>my tech stack</h2>
{stack}

<h2>my projects</h2>
{projects}
</main>

<footer>updated {date} · <a href="https://github.com/sp4ce-cowboy/sp4ce-cowboy.github.io">source</a></footer>
</body>
</html>
"""

def main():
    readme = fetch("README.md")
    page = PAGE
    for key, value in {
        "links": " · ".join(f'<a href="{u}">{n}</a>' for n, u in LINKS),
        "bio": "\n".join(f"<p>{html.escape(p)}</p>" for p in bio(readme)),
        "stack": render_list(lists(fetch(".github/techstack.txt"))),
        "projects": render_list(lists(fetch(".github/projects.txt"))),
        "date": dt.date.today().strftime("%-d %b %Y").lower(),
    }.items():
        page = page.replace("{" + key + "}", value)
    OUT.write_text(page)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
