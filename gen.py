"""Regenerate img/fetch.svg: binary-art Shanghai skyline (Oriental Pearl) + neofetch-style info + live GitHub stats.
Run: python3 gen.py   (set GITHUB_TOKEN to raise API rate limits; the Action does)"""
import io, json, os, urllib.request
import random
from PIL import Image, ImageDraw

USER = "dwenking"
W = 62                         # right-column width in chars
CW, LH, FS = 7.8, 17, 13       # char width, line height, font size (px)
AFS = 7                        # art font size; smaller cells → more detail in the same pixel width as the text column
ACW, ALH = AFS * .6, AFS * 1.0
COLS = int(W * CW / ACW)       # art column is exactly as wide as the text column
ROWS = 54                      # art rows; ~58% skyline above the horizon, the rest binary rain

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json",
          **({"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {})})
    return urllib.request.urlopen(req, timeout=30).read()

def skyline_mask():
    """Lujiazui silhouette drawn at cell resolution ×(8,14). Returns (city mask, pearl mask, ground row)."""
    sx, sy = 8, 14
    Wp, Hp = COLS * sx, ROWS * sy
    g = int(Hp * .58)                                   # horizon (ground line) in px
    city = Image.new("L", (Wp, Hp), 0); d = ImageDraw.Draw(city)
    def box(x0, x1, h): d.rectangle([int(x0 * Wp), g - int(h * g), int(x1 * Wp), g], fill=255)
    rnd = random.Random(7)
    for i in range(14):                                  # background blocks, kept clear of the Pearl
        x = i / 14 + rnd.uniform(-.02, .02)
        if .08 < x < .46: continue
        box(x, x + rnd.uniform(.04, .08), rnd.uniform(.14, .34))
    for w, h in [(.075, .40), (.058, .52), (.042, .62), (.026, .72)]: box(.56 - w / 2, .56 + w / 2, h)  # Jin Mao tiers
    d.line([(.56 * Wp, g - .72 * g), (.56 * Wp, g - .82 * g)], fill=255, width=3)
    d.polygon([(.68 * Wp, g), (.82 * Wp, g), (.785 * Wp, g - .80 * g), (.715 * Wp, g - .80 * g)], fill=255)  # SWFC
    d.polygon([(.735 * Wp, g - .79 * g), (.765 * Wp, g - .79 * g), (.758 * Wp, g - .66 * g), (.742 * Wp, g - .66 * g)], fill=0)
    d.polygon([(.87 * Wp, g), (.98 * Wp, g), (.95 * Wp, g - .92 * g), (.90 * Wp, g - .92 * g)], fill=255)  # Shanghai Tower
    d.rectangle([0, g, Wp, g + sy], fill=255)                                                              # ground band
    pearl = Image.new("L", (Wp, Hp), 0); p = ImageDraw.Draw(pearl)
    cx = .27 * Wp
    for dx in (-.13, 0, .13): p.line([(cx + dx * Wp, g), (cx, g - .36 * g)], fill=255, width=7)          # tripod legs
    p.rectangle([cx - .016 * Wp, g - 1.0 * g, cx + .016 * Wp, g], fill=255)                              # mast
    p.ellipse([cx - .14 * Wp, g - .58 * g, cx + .14 * Wp, g - .22 * g], fill=255)                        # lower sphere
    p.ellipse([cx - .08 * Wp, g - .90 * g, cx + .08 * Wp, g - .70 * g], fill=255)                        # upper sphere
    p.ellipse([cx - .03 * Wp, g - 1.02 * g, cx + .03 * Wp, g - .95 * g], fill=255)                       # top sphere
    p.line([(cx, g - 1.0 * g), (cx, g - 1.14 * g)], fill=255, width=3)                                   # antenna
    cell = lambda im: [im.resize((COLS, ROWS), Image.BOX).crop((0, y, COLS, y + 1)).tobytes() for y in range(ROWS)]
    return cell(city), cell(pearl), int(g / sy)

def ascii_art():
    """Rows of (char, css class): 'a' grey city, 'p' highlighted Pearl, rain in grey."""
    city, pearl, ground = skyline_mask()
    rnd = random.Random(42)                             # fixed seed → the Action only commits when stats change
    drip = [rnd.uniform(.25, 1.0) ** .6 for _ in range(COLS)]  # per-column drip length → vertical streaks
    art = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            if y <= ground:
                if pearl[y][x] > 100: row.append((rnd.choice("01"), "p"))
                elif city[y][x] > 100: row.append((rnd.choice("01"), "a"))
                else: row.append((" ", "a"))
            else:
                depth = (y - ground) / (ROWS - ground)
                pr = max(0.0, 1 - depth / drip[x]) ** .6 * (1 - .3 * depth)
                row.append((rnd.choice("01") if rnd.random() < pr else " ", "a"))
        art.append(row)
    return art

def stats():
    try:
        u = json.loads(get(f"https://api.github.com/users/{USER}"))
        repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100"))
        commits = json.loads(get(f"https://api.github.com/search/commits?q=author:{USER}"))["total_count"]
        return dict(repos=u["public_repos"], stars=sum(r["stargazers_count"] for r in repos),
                    commits=commits, followers=u["followers"])
    except Exception as e:  # keep the card renderable even if the API is down
        print("stats unavailable:", e); return dict(repos="?", stars="?", commits="?", followers="?")

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def kv(k, v):
    v = str(v); return [("k", f". {k}:"), ("d", " " + "." * max(W - len(k) - len(v) - 4, 1) + " "), ("v", v)]
def hd(t): return [("t", f"- {t} " + "—" * (W - len(t) - 3))]
def cells(*pairs):  # "Repos: .... 7 | Stars: ... 7" style row; pairs=(key, value)
    per = (W - 2 - 3 * (len(pairs) - 1)) // len(pairs); out = [("k", ". ")]
    for i, (k, v) in enumerate(pairs):
        v = str(v); out += [("k", f"{k}:"), ("d", " " + "." * max(per - len(k) - len(v) - 3, 1) + " "), ("v", v)]
        if i < len(pairs) - 1: out.append(("d", " | "))
    return out

def lines(s):
    return [
        [("t", "wenqian.deng " + "—" * (W - 13))], [],
        kv("OS", "macOS, Linux"),
        kv("Host", "NVIDIA"),
        kv("Kernel", "Software Developer"),
        kv("Uptime", "2019"),
        kv("IDE", "VS Code, Cursor, IntelliJ"),
        kv("Languages.Programming", "Java, Go, Python, TypeScript, C#"),
        kv("Languages.Frameworks", "Spring Boot, Vue, Kitex"),
        kv("Languages.Storage", "MongoDB, Redis, DynamoDB, SQL"),
        kv("Languages.Cloud", "AWS, Azure"),
        kv("Languages.Real", "Mandarin, English"),
        [("k", ".")],
        kv("Interests", "Agents & Full stack development"),
        kv("Hobbies", "Swimming, Travel"),
        [("k", ".")],
        hd("Contact"),
        kv("Email", "dengwenking@gmail.com"),
        kv("Website", "dwenking.github.io"),
        [("k", ".")],
        hd("GitHub Stats"),
        cells(("Repos", s["repos"]), ("Stars", s["stars"])),
        cells(("Commits", s["commits"]), ("Followers", s["followers"])),
    ]

def main():
    art, txt = ascii_art(), lines(stats())
    PAD = 28
    n = len(txt) + 1
    H = int(max(n * LH, len(art) * ALH + 2 * PAD) + 40)  # art rows use the smaller art line height
    x_txt = PAD + W * CW + 40
    W_px = int(x_txt + W * CW + PAD)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_px}" height="{H}" viewBox="0 0 {W_px} {H}" font-family="SF Mono,Menlo,Consolas,monospace" font-size="{FS}">',
           f'<rect width="{W_px}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           '<style>.a{fill:#8b949e}.p{fill:#e6edf3}.k{fill:#f2a65a}.d{fill:#484f58}.v{fill:#79c0ff}.t{fill:#e6edf3;font-weight:700}</style>']
    y0 = PAD + 12 + ((n - 1) * LH - len(art) * ALH) / 2  # vertically centre the art against the text block
    for i, row in enumerate(art):
        spans, run = [], None
        for ch, cls in row:  # merge neighbours of the same class into one tspan
            if run and run[0] == cls: run[1] += ch
            else:
                if run: spans.append(run)
                run = [cls, ch]
        spans.append(run)
        out.append(f'<text font-size="{AFS}" x="{PAD}" y="{y0 + i*ALH:.1f}" xml:space="preserve">' +
                   "".join(f'<tspan class="{c}">{esc(t)}</tspan>' for c, t in spans) + "</text>")
    for i, parts in enumerate(txt):
        if parts:
            out.append(f'<text x="{x_txt}" y="{PAD + 12 + i*LH}" xml:space="preserve">' +
                       "".join(f'<tspan class="{c}">{esc(s)}</tspan>' for c, s in parts) + "</text>")
    out.append("</svg>")
    os.makedirs("img", exist_ok=True); open("img/fetch.svg", "w").write("\n".join(out))

if __name__ == "__main__": main()
