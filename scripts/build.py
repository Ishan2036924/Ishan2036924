"""Build the profile README images from live public data.

Writes assets/banner.svg, assets/dashboard.svg, assets/card-*.svg and refreshes
the Medium list in README.md. Standard library only. Needs GITHUB_TOKEN for the
GitHub GraphQL API; reads only public data. If any source fails, the script
stops before writing anything, so the last good images stay in place.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

LOGIN = "Ishan2036924"
NAME = "Ishan Srivastava"
MEDIUM = "ishansri13"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

BG = "#0d1117"
PANEL = "#111720"
LINE = "#222a35"
TEXT = "#e6edf3"
MUTED = "#8b949e"
FAINT = "#5c6672"
ACCENT = "#3fb950"
GREENS = ["#1c2430", "#0e4429", "#006d32", "#26a641", "#39d353"]

UA = {"User-Agent": f"{LOGIN}-profile-build"}


def get(url: str, headers: dict | None = None, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def graphql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    body = json.dumps({"query": query, "variables": variables}).encode()
    out = json.loads(
        get("https://api.github.com/graphql", {"Authorization": f"bearer {token}"}, body)
    )
    if out.get("errors"):
        sys.exit(f"GraphQL error: {out['errors'][0].get('type', 'unknown')}")
    return out["data"]


QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def pkg_versions() -> dict:
    out = {}
    for pkg in ("open-action-consent", "open-pseudonym"):
        pypi = json.loads(get(f"https://pypi.org/pypi/{pkg}/json"))["info"]["version"]
        npm = json.loads(get(f"https://registry.npmjs.org/{pkg}/latest"))["version"]
        out[pkg] = {"pypi": pypi, "npm": npm}
    return out


def medium_posts(limit: int = 4) -> list[dict]:
    xml = get(f"https://medium.com/feed/@{MEDIUM}").decode("utf-8", "replace")
    posts = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item, re.S)
        link = re.search(r"<link>(.*?)</link>", item, re.S)
        date = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
        if not (title and link and date):
            continue
        when = dt.datetime.strptime(date.group(1).strip()[:16], "%a, %d %b %Y")
        posts.append(
            {
                "title": html.unescape(title.group(1).strip()),
                "url": link.group(1).strip().split("?")[0],
                "date": when.strftime("%b %Y"),
            }
        )
    if not posts:
        sys.exit("Medium feed returned no posts")
    return posts[:limit]


# ---------------------------------------------------------------- helpers


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def no_dash(s: str) -> str:
    return s.replace(chr(0x2014), ", ").replace(chr(0x2013), "-")


def fmt(n: int) -> str:
    return f"{n:,}"


def svg(w: int, h: int, body: str, title: str, extra_css: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">
<title id="t">{esc(title)}</title>
<style>
.sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
.h{{fill:{TEXT};font-weight:600}} .m{{fill:{MUTED}}} .f{{fill:{FAINT}}} .a{{fill:{ACCENT}}}
.k{{font-family:{MONO};font-size:11px;letter-spacing:.08em;fill:{FAINT}}}
.rise{{opacity:0;animation:rise .6s ease-out forwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce){{.rise{{animation:none;opacity:1}}}}
{extra_css}
</style>
{body}
</svg>
"""


def panel(x, y, w, h, r=14) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{PANEL}" stroke="{LINE}"/>'


# ---------------------------------------------------------------- banner


def banner() -> str:
    w, h = 880, 230
    lines = [
        "I build AI agents people can trust.",
        "Founder of Atlas Intelligent Workspace.",
        "Author of Open Action Consent and Open Pseudonym.",
        "HACK1984: 2nd place, Most Startup-able.",
    ]
    cw, fs, slot = 10.8, 18, 4.0
    total = slot * len(lines)
    x0, y0 = 56, 156
    typed = []
    for i, line in enumerate(lines):
        n = len(line)
        # keyTimes across the whole cycle: hidden, type in, hold, delete, hidden
        start = i * slot
        times, widths = [0.0], [0.0]
        type_t, del_t, hold_end = 1.7, 0.5, slot - 0.35
        for c in range(1, n + 1):
            times.append(start + type_t * c / n)
            widths.append(c * cw)
        times.append(start + hold_end - del_t)
        widths.append(n * cw)
        steps = 8
        for s in range(1, steps + 1):
            times.append(start + hold_end - del_t + del_t * s / steps)
            widths.append(n * cw * (1 - s / steps))
        if times[-1] < total:
            times.append(total)
            widths.append(0.0)
        kt = ";".join(f"{t / total:.4f}" for t in times)
        wv = ";".join(f"{v:.1f}" for v in widths)
        xv = ";".join(f"{x0 + v + 2:.1f}" for v in widths)
        typed.append(
            f"""<clipPath id="c{i}"><rect x="{x0}" y="{y0 - 20}" height="28" width="0">
<animate attributeName="width" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{wv}"/></rect></clipPath>
<text clip-path="url(#c{i})" x="{x0}" y="{y0}" class="mono a" font-size="{fs}" textLength="{n * cw:.1f}" lengthAdjust="spacing">{esc(line)}</text>
<rect y="{y0 - 15}" width="2" height="19" fill="{ACCENT}" opacity="0" x="{x0}">
<animate attributeName="x" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{xv}"/>
<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{start / total:.4f};{(start + slot) / total:.4f}" values="0;1;0"/></rect>"""
        )
    dots = (
        '<pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{LINE}"/></pattern>'
    )
    # small isometric block cluster on the right, echoing the calendar below
    blocks = []
    cx0, cy0 = 735, 128
    heights = [[18, 30, 12], [42, 64, 26], [22, 38, 50]]
    for a in range(3):
        for b in range(3):
            hgt = heights[a][b]
            bx = cx0 + (a - b) * 26
            by = cy0 + (a + b) * 15
            shade = GREENS[min(4, 1 + hgt // 16)]
            blocks.append(iso_prism(bx, by, 26, 15, hgt, shade))
    body = f"""<defs>{dots}
<radialGradient id="glow" cx="80%" cy="40%" r="60%"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".10"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="{BG}" stroke="{LINE}"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#g)"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#glow)"/>
<text x="{x0}" y="62" class="k">~/ISHAN2036924  ·  BOSTON, MA</text>
<text x="{x0 - 2}" y="112" class="sans h" font-size="46" letter-spacing="-1">{esc(NAME)}</text>
{"".join(typed)}
<text x="{x0}" y="196" class="sans m" font-size="14">AI engineer  ·  agents, retrieval, privacy and consent for AI that acts</text>
<g class="rise">{"".join(blocks)}</g>"""
    return svg(w, h, body, f"{NAME}: I build AI agents people can trust.")


def iso_prism(x, y, dx, dy, hgt, color, edge=None) -> str:
    """Top rhombus centred at (x, y - hgt); faces drop to the ground at y."""
    top = f"{x},{y - hgt - dy} {x + dx},{y - hgt} {x},{y - hgt + dy} {x - dx},{y - hgt}"
    left = f"{x - dx},{y - hgt} {x},{y - hgt + dy} {x},{y + dy} {x - dx},{y}"
    right = f"{x + dx},{y - hgt} {x},{y - hgt + dy} {x},{y + dy} {x + dx},{y}"
    return (
        f'<polygon points="{top}" fill="{color}"/>'
        f'<polygon points="{left}" fill="{shade(color, .72)}"/>'
        f'<polygon points="{right}" fill="{shade(color, .52)}"/>'
    )


# ---------------------------------------------------------------- dashboard


def shade(color: str, k: float) -> str:
    c = color.lstrip("#")
    r, g, b = (int(c[i : i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def level(n: int, q: list[int]) -> int:
    if n <= 0:
        return 0
    for i, cut in enumerate(q, start=1):
        if n <= cut:
            return i
    return 4


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    cur = 0
    seq = days[:]
    if seq and seq[-1]["contributionCount"] == 0:
        seq = seq[:-1]  # today may not have started yet
    for d in reversed(seq):
        if d["contributionCount"] > 0:
            cur += 1
        else:
            break
    return cur, longest


def dashboard(user: dict, versions: dict) -> str:
    w, h = 880, 540
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for wk in weeks for d in wk["contributionDays"]]
    counts = sorted(d["contributionCount"] for d in days if d["contributionCount"] > 0)
    q = [counts[int(len(counts) * p)] for p in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]
    cur, longest = streaks(days)
    best = max(days, key=lambda d: d["contributionCount"])
    active = sum(1 for d in days if d["contributionCount"] > 0)
    joined = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    years = (dt.datetime.now(dt.timezone.utc) - joined).days // 365

    parts = [f'<rect width="{w}" height="{h}" rx="18" fill="{BG}" stroke="{LINE}"/>']

    # ---- profile column
    px, py = 24, 24
    parts.append(panel(px, py, 236, 270))
    parts.append(
        f'<circle cx="{px + 54}" cy="{py + 58}" r="32" fill="{shade(ACCENT, .22)}" stroke="{ACCENT}" stroke-opacity=".5"/>'
        f'<text x="{px + 54}" y="{py + 65}" text-anchor="middle" class="sans h" font-size="20" fill="{TEXT}">IS</text>'
        f'<text x="{px + 20}" y="{py + 122}" class="sans h" font-size="19">{esc(NAME)}</text>'
        f'<text x="{px + 20}" y="{py + 142}" class="mono m" font-size="12">@{LOGIN}</text>'
    )
    facts = [
        ("Boston, MA", ""),
        (f"On GitHub for {years} years", ""),
        (f"{user['repositories']['totalCount']} public repositories", ""),
        ("2 open standards on PyPI + npm", ""),
        ("Building Atlas (atlasiw.com)", ""),
    ]
    for i, (t, _) in enumerate(facts):
        y = py + 174 + i * 20
        parts.append(
            f'<circle cx="{px + 24}" cy="{y - 4}" r="2.5" fill="{FAINT}"/>'
            f'<text x="{px + 34}" y="{y}" class="sans m" font-size="12.5">{esc(t)}</text>'
        )

    # ---- stat tiles
    sx, sy = 276, 24
    tiles = [
        (fmt(cal["totalContributions"]), "contributions"),
        (fmt(cc["totalCommitContributions"]), "commits"),
        (f"{cur} days", "current streak"),
        (f"{longest} days", "longest streak"),
        (f"{active}/{len(days)}", "active days"),
        (fmt(best["contributionCount"]), "busiest day"),
    ]
    tw, th = 112, 82
    for i, (big, small) in enumerate(tiles):
        tx = sx + (i % 2) * (tw + 10)
        ty = sy + (i // 2) * (th + 12)
        parts.append(panel(tx, ty, tw, th, 12))
        parts.append(
            f'<text x="{tx + 14}" y="{ty + 38}" class="sans h" font-size="22" letter-spacing="-.5">{esc(big)}</text>'
            f'<text x="{tx + 14}" y="{ty + 60}" class="sans m" font-size="11">{esc(small)}</text>'
        )

    # ---- 3D calendar
    gx, gy = 520, 24
    parts.append(panel(gx, gy, 336, 270))
    parts.append(f'<text x="{gx + 18}" y="{gy + 28}" class="k">CONTRIBUTIONS · 3D CALENDAR</text>')
    wv, dv = (4.6, 2.0), (-5.2, 3.3)
    ox, oy = gx + 26 + 7 * 5.2, gy + 74
    cells = []
    nweeks = len(weeks)
    for wi, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            di = d["weekday"]
            n = d["contributionCount"]
            lv = level(n, q)
            hgt = 0 if n == 0 else 3 + 33 * (n / max(1, best["contributionCount"])) ** 0.6
            x = ox + wi * wv[0] + di * dv[0]
            y = oy + wi * wv[1] + di * dv[1]
            cells.append((wi + di, x, y, hgt, GREENS[lv], wi))
    cells.sort(key=lambda c: (c[0], c[1]))
    blocks = []
    for _, x, y, hgt, color, wi in cells:
        delay = 0.15 + wi / nweeks * 0.9
        blocks.append(
            f'<g class="rise" style="animation-delay:{delay:.2f}s">{iso_cell(x, y, wv, dv, hgt, color)}</g>'
        )
    parts.append("".join(blocks))
    first = dt.date.fromisoformat(days[0]["date"]).strftime("%b %Y")
    last = dt.date.fromisoformat(days[-1]["date"]).strftime("%b %Y")
    parts.append(
        f'<text x="{gx + 18}" y="{gy + 254}" class="sans m" font-size="11">{first} to {last}</text>'
    )
    lg = gx + 220
    parts.append(f'<text x="{lg - 8}" y="{gy + 254}" class="sans f" font-size="11" text-anchor="end">less</text>')
    for i, c in enumerate(GREENS):
        parts.append(f'<rect x="{lg + i * 14}" y="{gy + 245}" width="10" height="10" rx="2" fill="{c}"/>')
    parts.append(f'<text x="{lg + 74}" y="{gy + 254}" class="sans f" font-size="11">more</text>')

    # ---- monthly bars
    by_month: dict[str, int] = {}
    for d in days:
        key = d["date"][:7]
        by_month[key] = by_month.get(key, 0) + d["contributionCount"]
    months = list(by_month.items())[-12:]
    mx, my, mw, mh = 24, 310, 416, 206
    parts.append(panel(mx, my, mw, mh))
    parts.append(f'<text x="{mx + 18}" y="{my + 28}" class="k">CONTRIBUTIONS PER MONTH</text>')
    peak = max(v for _, v in months) or 1
    bw = (mw - 36) / len(months)
    base = my + mh - 34
    for i, (k, v) in enumerate(months):
        bh = max(2, (mh - 86) * v / peak)
        bx = mx + 18 + i * bw
        delay = 0.2 + i * 0.05
        parts.append(
            f'<g class="rise" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{bx + 4:.1f}" y="{base - bh:.1f}" width="{bw - 8:.1f}" height="{bh:.1f}" rx="3" fill="{ACCENT if v == peak else GREENS[2]}"/>'
            + (f'<text x="{bx + bw / 2:.1f}" y="{base - bh - 6:.1f}" text-anchor="middle" class="sans m" font-size="10">{fmt(v)}</text>' if v else "")
            + "</g>"
            f'<text x="{bx + bw / 2:.1f}" y="{base + 18}" text-anchor="middle" class="sans f" font-size="10">{dt.date.fromisoformat(k + "-01").strftime("%b")}</text>'
        )

    # ---- languages
    lx, ly, lw, lh = 456, 310, 400, 98
    parts.append(panel(lx, ly, lw, lh))
    parts.append(f'<text x="{lx + 18}" y="{ly + 28}" class="k">LANGUAGES · PUBLIC REPOS</text>')
    langs: dict[str, list] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name in ("Jupyter Notebook",):
                continue
            item = langs.setdefault(name, [0, e["node"]["color"] or MUTED])
            item[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:4]
    tot = sum(v[0] for _, v in top) or 1
    barx, bary, barw = lx + 18, ly + 44, lw - 36
    parts.append(f'<clipPath id="lb"><rect x="{barx}" y="{bary}" width="{barw}" height="8" rx="4"/></clipPath><g clip-path="url(#lb)">')
    cx = barx
    for name, (size, color) in top:
        seg = barw * size / tot
        parts.append(f'<rect x="{cx:.1f}" y="{bary}" width="{seg + 0.5:.1f}" height="8" fill="{color}"/>')
        cx += seg
    parts.append("</g>")
    cx = barx
    for name, (size, color) in top:
        label = f"{name} {100 * size / tot:.0f}%"
        parts.append(
            f'<circle cx="{cx + 4}" cy="{ly + 76}" r="4" fill="{color}"/>'
            f'<text x="{cx + 13}" y="{ly + 80}" class="sans m" font-size="11.5">{esc(label)}</text>'
        )
        cx += 13 + len(label) * 6.4 + 16

    # ---- packages
    kx, ky, kw, kh = 456, 418, 400, 98
    parts.append(panel(kx, ky, kw, kh))
    parts.append(f'<text x="{kx + 18}" y="{ky + 28}" class="k">OPEN SOURCE · RELEASED</text>')
    for i, (pkg, label) in enumerate((("open-action-consent", "Open Action Consent"), ("open-pseudonym", "Open Pseudonym"))):
        yy = ky + 54 + i * 24
        v = versions[pkg]
        parts.append(
            f'<text x="{kx + 18}" y="{yy}" class="sans h" font-size="13">{label}</text>'
            f'<text x="{kx + 196}" y="{yy}" class="mono m" font-size="11.5">PyPI {esc(v["pypi"])}</text>'
            f'<text x="{kx + 292}" y="{yy}" class="mono m" font-size="11.5">npm {esc(v["npm"])}</text>'
        )

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    parts.append(f'<text x="{w - 24}" y="{h - 8}" text-anchor="end" class="sans f" font-size="9.5">last 12 months · updated {stamp} from the GitHub, PyPI and npm APIs</text>')
    return svg(w, h, "\n".join(parts), f"GitHub activity for {NAME}: {fmt(cal['totalContributions'])} contributions in the last year")


def iso_cell(x, y, wv, dv, hgt, color) -> str:
    """Prism on the parallelogram spanned by the week and day vectors, lifted by hgt."""
    k = 0.82  # face size; the rest is the gap between cells
    W = (wv[0] * k, wv[1] * k)
    D = (dv[0] * k, dv[1] * k)
    p0 = (x, y)
    p1 = (x + W[0], y + W[1])
    p2 = (x + W[0] + D[0], y + W[1] + D[1])
    p3 = (x + D[0], y + D[1])

    def lifted(*ps):
        return " ".join(f"{px:.1f},{py - hgt:.1f}" for px, py in ps)

    def side(u, v):
        return f"{u[0]:.1f},{u[1] - hgt:.1f} {v[0]:.1f},{v[1] - hgt:.1f} {v[0]:.1f},{v[1]:.1f} {u[0]:.1f},{u[1]:.1f}"

    top = f'<polygon points="{lifted(p0, p1, p2, p3)}" fill="{color}"/>'
    if hgt <= 0:
        return top
    return (
        f'<polygon points="{side(p3, p2)}" fill="{shade(color, .62)}"/>'
        f'<polygon points="{side(p1, p2)}" fill="{shade(color, .80)}"/>'
        + top
    )


# ---------------------------------------------------------------- project cards


def card(kicker: str, title: str, lines: list[str], chips: list[str], tag: str) -> str:
    w, h = 430, 190
    body = [
        f'<rect width="{w}" height="{h}" rx="16" fill="{BG}" stroke="{LINE}"/>',
        f'<text x="24" y="36" class="k">{esc(kicker)}</text>',
        f'<text x="{w - 24}" y="36" class="k" text-anchor="end" fill="{ACCENT}" style="fill:{ACCENT}">{esc(tag)}</text>',
        f'<text x="24" y="70" class="sans h" font-size="21" letter-spacing="-.3">{esc(title)}</text>',
    ]
    for i, line in enumerate(lines):
        body.append(f'<text x="24" y="{98 + i * 19}" class="sans m" font-size="13">{esc(line)}</text>')
    cx = 24
    for c in chips:
        cw = 14 + len(c) * 6.6
        body.append(
            f'<rect x="{cx}" y="{h - 40}" width="{cw:.0f}" height="22" rx="11" fill="{PANEL}" stroke="{LINE}"/>'
            f'<text x="{cx + cw / 2:.0f}" y="{h - 25}" text-anchor="middle" class="mono m" font-size="11">{esc(c)}</text>'
        )
        cx += cw + 8
    return svg(w, h, "\n".join(body), f"{title}: {' '.join(lines)}")


def cards(versions: dict) -> dict[str, str]:
    oac, opn = versions["open-action-consent"], versions["open-pseudonym"]
    return {
        "card-atlas.svg": card(
            "PRODUCT · ATLASIW.COM",
            "Atlas Intelligent Workspace",
            ["One AI workspace for docs, sheets, boards, tasks,", "calendar and mail, with agents that ask before", "anything leaves. Private beta."],
            ["agents", "approvals", "undo", "masking"],
            "BUILDING",
        ),
        "card-oac.svg": card(
            "OPEN STANDARD · SPEC 0.2",
            "Open Action Consent",
            ["A verifiable yes for actions AI agents take for", "people: signed previews, consents, mandates,", "hash-chained receipts and Undo."],
            [f"PyPI {oac['pypi']}", f"npm {oac['npm']}", "MCP", "Apache-2.0"],
            "RELEASED",
        ),
        "card-pseudonym.svg": card(
            "OPEN STANDARD · PRIVACY",
            "Open Pseudonym",
            ["Keeps personal data away from AI models without", "making them worse at the task: task-aware stand-ins,", "local restore, signed egress receipts."],
            [f"PyPI {opn['pypi']}", f"npm {opn['npm']}", "Apache-2.0"],
            "RELEASED",
        ),
        "card-hack1984.svg": card(
            "HACK1984 · NOV 2026",
            "2nd place, Most Startup-able",
            ["Solo build over one weekend on top of Atlas:", "phone Agent mode, privacy masking with signed", "receipts, approval-gated payments, natural voice."],
            ["153 commits", "solo", "judges' repo"],
            "AWARD",
        ),
    }


# ---------------------------------------------------------------- readme


def update_readme(posts: list[dict]) -> None:
    path = ROOT / "README.md"
    text = path.read_text()
    rows = "\n".join(
        f'<tr><td><a href="{esc(p["url"])}"><b>{esc(no_dash(p["title"]))}</b></a></td><td align="right"><sub>{p["date"]}</sub></td></tr>'
        for p in posts
    )
    block = f"<!-- medium:start -->\n<table>\n{rows}\n</table>\n<!-- medium:end -->"
    new = re.sub(r"<!-- medium:start -->.*?<!-- medium:end -->", block, text, flags=re.S)
    path.write_text(new)


def main() -> None:
    user = graphql(QUERY, {"login": LOGIN})["user"]
    versions = pkg_versions()
    posts = medium_posts()
    files = {"banner.svg": banner(), "dashboard.svg": dashboard(user, versions), **cards(versions)}
    for name, content in files.items():
        if chr(0x2014) in content:
            sys.exit(f"em dash in {name}")
    ASSETS.mkdir(exist_ok=True)
    for name, content in files.items():
        (ASSETS / name).write_text(content)
    update_readme(posts)
    print(f"wrote {len(files)} images, {len(posts)} posts")


if __name__ == "__main__":
    main()
