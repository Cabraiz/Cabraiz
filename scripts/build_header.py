"""Write assets/header-dark.svg and assets/header-light.svg (run once, then commit)."""

from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
WIDTH, HEIGHT = 1280, 320

THEMES = {
    "dark": dict(
        top="#0d1117", bottom="#131a24", border="#30363d", name="#f0f6fc", role="#c9d1d9", muted="#8b949e",
        accent="#58a6ff", glow_opacity=".20", dots="#30363d", node="#161b22", node_text="#c9d1d9",
        hub="#1f6feb", hub_text="#ffffff", edge="#3d4753",
    ),
    "light": dict(
        top="#ffffff", bottom="#f3f6fa", border="#d0d7de", name="#1f2328", role="#424a53", muted="#59636e",
        accent="#0969da", glow_opacity=".12", dots="#d0d7de", node="#ffffff", node_text="#424a53",
        hub="#0969da", hub_text="#ffffff", edge="#b6c0ca",
    ),
}

PHRASES = (
    "LLMs, RAG and multi-agent systems in production",
    "React · TypeScript · Node.js · Java · AWS",
    "13 years shipping software, remote from Brazil",
)

# What the work looks like: a request reaches the agents, which call out and answer back.
HUB = (985, 160)
REQUEST = (805, 160)
SPOKES = {"LLM": (1165, 76), "RAG": (1165, 160), "Tools": (1165, 244)}


def path_between(start: tuple[int, int], end: tuple[int, int]) -> str:
    (x1, y1), (x2, y2) = start, end
    middle = (x1 + x2) // 2
    return f"M{x1} {y1} C{middle} {y1} {middle} {y2} {x2} {y2}"


def pill(center: tuple[int, int], label: str, colors: dict, hub: bool = False) -> str:
    x, y = center
    width, height = (132, 58) if hub else (104, 46)
    fill = colors["hub"] if hub else colors["node"]
    stroke = colors["hub"] if hub else colors["edge"]
    text = colors["hub_text"] if hub else colors["node_text"]
    weight = 600 if hub else 500
    size = 22 if hub else 20
    return (
        f'<rect x="{x - width / 2}" y="{y - height / 2}" width="{width}" height="{height}" rx="{height / 2}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="{x}" y="{y + size * 0.35:.1f}" text-anchor="middle" font-size="{size}" font-weight="{weight}" fill="{text}">{label}</text>'
    )


def build(colors: dict) -> str:
    links = [(REQUEST, HUB, 0.0)]
    links += [(HUB, end, 1.0 + index * 0.45) for index, end in enumerate(SPOKES.values())]
    edges, pulses = [], []
    for start, end, delay in links:
        path = path_between(start, end)
        edges.append(f'<path d="{path}" fill="none" stroke="{colors["edge"]}" stroke-width="1.5"/>')
        pulses.append(
            f'<circle class="pulse" r="4.5" fill="{colors["accent"]}" opacity="0">'
            f'<animateMotion dur="4.5s" begin="{delay}s" repeatCount="indefinite" path="{path}" '
            f'keyPoints="0;1;1" keyTimes="0;.28;1" calcMode="linear"/>'
            f'<animate attributeName="opacity" dur="4.5s" begin="{delay}s" repeatCount="indefinite" '
            f'values="0;1;1;0;0" keyTimes="0;.04;.25;.28;1"/></circle>'
        )
    phrases = "\n".join(
        f'<text class="phrase" style="animation-delay:{index * 4}s" x="72" y="252" font-size="26" fill="{colors["muted"]}">{text}</text>'
        for index, text in enumerate(PHRASES)
    )
    nodes = [pill(REQUEST, "Request", colors), pill(HUB, "Agents", colors, hub=True)]
    nodes += [pill(center, label, colors) for label, center in SPOKES.items()]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Mateus Cabral, Senior AI Engineer and full-stack developer, based in Fortaleza, Brazil">
<style>
.phrase {{ opacity: 0; animation: phrase 12s linear infinite; }}
@keyframes phrase {{ 0% {{ opacity: 0; }} 3%, 30% {{ opacity: 1; }} 33.3%, 100% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .pulse {{ display: none; }}
  .phrase {{ animation: none; }}
  .phrase:first-of-type {{ opacity: 1; }}
}}
</style>
<defs>
<linearGradient id="surface" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{colors["top"]}"/>
<stop offset="1" stop-color="{colors["bottom"]}"/>
</linearGradient>
<radialGradient id="glow" cx="985" cy="160" r="360" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{colors["accent"]}" stop-opacity="{colors["glow_opacity"]}"/>
<stop offset="1" stop-color="{colors["accent"]}" stop-opacity="0"/>
</radialGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
<circle cx="2" cy="2" r="1.2" fill="{colors["dots"]}"/>
</pattern>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
<stop offset=".5" stop-color="#fff" stop-opacity="0"/>
<stop offset=".8" stop-color="#fff" stop-opacity="1"/>
</linearGradient>
<mask id="dots-mask"><rect width="{WIDTH}" height="{HEIGHT}" fill="url(#fade)"/></mask>
<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#surface)"/>
<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#dots)" mask="url(#dots-mask)"/>
<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#glow)"/>
</g>
<rect x=".75" y=".75" width="{WIDTH - 1.5}" height="{HEIGHT - 1.5}" rx="15.5" fill="none" stroke="{colors["border"]}" stroke-width="1.5"/>
<g font-family="{FONT}">
<text x="72" y="82" font-size="20" font-weight="600" letter-spacing="2.4" fill="{colors["accent"]}">FORTALEZA, BRAZIL · REMOTE</text>
<text x="69" y="158" font-size="78" font-weight="700" letter-spacing="-1.6" fill="{colors["name"]}">Mateus Cabral</text>
<text x="72" y="206" font-size="31" font-weight="500" fill="{colors["role"]}">Senior AI Engineer · Full-Stack Developer</text>
{phrases}
{chr(10).join(edges)}
{chr(10).join(pulses)}
{chr(10).join(nodes)}
</g>
</svg>
"""


for theme, palette in THEMES.items():
    (ASSETS / f"header-{theme}.svg").write_text(build(palette), "utf-8", newline="\n")
