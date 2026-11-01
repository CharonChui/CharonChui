#!/usr/bin/env python3
"""生成 README 里 star / fork 徽章的自托管 SVG。

shields.io 的字号和字重是写死的，没法做到「更大更粗」，所以这里直接画 SVG。
数据从 GitHub API 实时拉取，改完数字后重新跑一遍即可：

    python3 scripts/gen_badges.py
"""

import json
import pathlib
import urllib.request

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "badges"

# Star 用橙金、Fork 用紫罗兰，都是高饱和色，白字加粗在白色页面上最跳
STAR_COLORS = ("#F59E0B", "#D9480F")
FORK_COLORS = ("#8B5CF6", "#5B21B6")

BADGE_W, BADGE_H = 108, 40
FONT_SIZE = 22

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{aria}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{rw}" height="{rh}" rx="9" ry="9" fill="url(#bg)" fill-opacity="1"/>
  <rect x="1" y="1" width="{rw}" height="{rh}" rx="9" ry="9" fill="none" stroke="#000000" stroke-opacity="0.12"/>
  <text x="{cx}" y="{ty}" text-anchor="middle"
        font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
        font-size="{fs}" font-weight="800" fill="#FFFFFF" letter-spacing="0.4">{value}</text>
</svg>
"""

REPOS = [
    ("FullStack-Notes", "star-fullstack-notes", "Star"),
    ("FullStack-Notes", "fork-fullstack-notes", "Fork"),
    ("CyberLink4Android", "star-cyberlink4android", "Star"),
    ("CyberLink4Android", "fork-cyberlink4android", "Fork"),
    ("AIStudyNote", "star-aistudynote", "Star"),
    ("AIStudyNote", "fork-aistudynote", "Fork"),
]


def fetch_counts(repo):
    url = f"https://api.github.com/repos/CharonChui/{repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "badge-generator"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return data["stargazers_count"], data["forks_count"]


def fmt(n):
    return f"{n:,}" if n >= 1000 else str(n)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    for repo, name, kind in REPOS:
        if repo not in cache:
            cache[repo] = fetch_counts(repo)
        stars, forks = cache[repo]
        value = fmt(stars if kind == "Star" else forks)
        c1, c2 = STAR_COLORS if kind == "Star" else FORK_COLORS
        svg = SVG.format(
            w=BADGE_W,
            h=BADGE_H,
            rw=BADGE_W - 2,
            rh=BADGE_H - 2,
            cx=BADGE_W / 2,
            ty=BADGE_H / 2 + FONT_SIZE * 0.36,
            fs=FONT_SIZE,
            c1=c1,
            c2=c2,
            value=value,
            aria=f"{repo} {kind.lower()}s: {value}",
        )
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"{name}.svg -> {value}")


if __name__ == "__main__":
    main()
