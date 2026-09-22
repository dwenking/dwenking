"""Regenerate img/fetch.svg: pixel-art Shanghai skyline (Oriental Pearl) with a 0/1 reflection + neofetch-style info + live GitHub stats.
Run: python3 gen.py   (set GITHUB_TOKEN to raise API rate limits; the Action does)"""
import io, json, os, urllib.request
import random
from PIL import Image, ImageDraw

USER = "dwenking"
W = 62                         # right-column width in chars
CW, LH, FS = 7.8, 17, 13       # char width, line height, font size (px)
PC, PR = 80, 40                # pixel-art grid: columns, rows (sky + skyline)
PX = W * CW / PC               # square pixel size → art column exactly as wide as the text column
AFS = 7                        # reflection font size
ACW, ALH = AFS * .6, AFS * 1.0
COLS, RR = int(W * CW / ACW), 22   # reflection grid: 0/1 columns, rows

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json",
          **({"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {})})
    return urllib.request.urlopen(req, timeout=30).read()

BG = "#0d1117"
# cyberpunk palette: dark bodies, neon cyan / magenta / purple / yellow lights
NEO_C, NEO_M, NEO_P, NEO_Y, DK1, DK2, DK3 = "#00f0ff", "#ff2bd6", "#9d4edd", "#ffe600", "#23264d", "#2f3670", "#3e478f"
SAL, PK, MAG, CY, PU = NEO_P, NEO_C, NEO_M, NEO_C, "#5a189a"                    # Oriental Pearl
GOLD, WIN, BRN, BRN2, BGRY, BWIN, STEEL, GRN, ROAD = DK2, NEO_Y, DK1, DK2, DK3, NEO_C, DK2, NEO_M, NEO_C
STARS = [NEO_C, NEO_M, NEO_P, NEO_Y]
PALETTE = list(dict.fromkeys([SAL, PK, MAG, CY, PU, GOLD, WIN, BRN, BRN2, BGRY, BWIN, STEEL, GRN, ROAD] + STARS))
CLS = {c: f"c{i}" for i, c in enumerate(PALETTE)}          # colour → css class of its dimmed reflection
CLS.update({DK1: "a", DK2: "a", DK3: "a"})                  # dark bodies reflect as plain grey, not near-black
rgb = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
dim = lambda c: "#%02x%02x%02x" % tuple(int(a * .7 + b * .3) for a, b in zip(rgb(c), rgb(BG)))

def pixel_sky():
    """Coloured pixel-art Lujiazui night skyline drawn directly at PC×PR cells (one cell = one square pixel)."""
    im = Image.new("RGB", (PC, PR), BG); d = ImageDraw.Draw(im); rnd = random.Random(7)
    g = PR - 1                                            # ground row
    for _ in range(24):                                   # stars: dots, some as small plus shapes
        x, y, c = rnd.randrange(PC), rnd.randrange(g - 10), rnd.choice(STARS)
        d.point((x, y), c)
        if rnd.random() < .25: d.line([(x - 1, y), (x + 1, y)], c); d.line([(x, y - 1), (x, y + 1)], c)
    def windows(x0, y0, x1, y1, body, win, step=2):       # lit windows on cells that are still body-coloured
        for y in range(y0 + 1, y1, 2):
            for x in range(x0 + 1, x1, step):
                if im.getpixel((x, y)) == rgb(body) and rnd.random() < .65: d.point((x, y), win)
    def bld(x0, x1, h, body, win):
        d.rectangle([x0, g - h, x1, g], fill=body); windows(x0, g - h, x1, g, body, win)
    for x0, w, h, body in [(0, 5, 6, BRN), (6, 5, 9, BRN2), (34, 5, 8, BRN), (40, 4, 11, BRN2), (52, 4, 7, BRN), (66, 2, 9, BRN2)]:
        bld(x0, x0 + w, h, body, rnd.choice([NEO_M, NEO_C, NEO_Y]))
    d.ellipse([40, g - 14, 44, g - 10], fill=GRN)         # a small green dome, Bund style
    for hw, h in [(5, 16), (4, 22), (3, 27), (2, 31)]: bld(46 - hw, 46 + hw, h, GOLD, WIN)   # Jin Mao tiers
    d.line([(46, g - 31), (46, g - 35)], fill=GOLD)
    d.polygon([(55, g), (64, g), (62, g - 33), (57, g - 33)], fill=BGRY); windows(55, g - 33, 64, g, BGRY, BWIN)  # SWFC
    d.rectangle([59, g - 32, 60, g - 26], fill=BG)        # its trapezoid aperture
    d.polygon([(68, g), (78, g), (76, g - 37), (70, g - 37)], fill=STEEL); windows(68, g - 37, 78, g, STEEL, NEO_M)  # Shanghai Tower
    cx = 22                                               # Oriental Pearl
    for x0 in (15, 22, 29): d.line([(x0, g), (cx, g - 7)], fill=SAL, width=2)   # tripod legs
    d.rectangle([cx - 1, g - 30, cx + 1, g - 18], fill=SAL)                       # column
    for y in range(g - 29, g - 18, 2): d.point((cx, y), PK)
    def sphere(box):
        d.ellipse(box, fill=MAG)
        for y in range(box[1], box[3] + 1):
            for x in range(box[0], box[2] + 1):
                if im.getpixel((x, y)) == rgb(MAG) and (x + y) % 3 == 0: d.point((x, y), rnd.choice([PK, CY, PU]))
    sphere([16, g - 19, 28, g - 7]); sphere([19, g - 34, 25, g - 28])
    d.ellipse([cx - 1, g - 37, cx + 1, g - 35], fill=PK)
    d.line([(cx, g - 38), (cx, g - 35)], fill=CY)                                 # antenna
    d.line([(0, g), (PC - 1, g)], fill=ROAD)                                      # waterfront
    return im

def reflection(sky):
    """Mirror of the skyline as 0/1 characters, dense at the waterline and dripping away downward."""
    flip = sky.crop((0, PR - 27, PC, PR)).transpose(Image.FLIP_TOP_BOTTOM).resize((COLS, RR), Image.NEAREST)  # mirror the lower 27 rows
    rnd = random.Random(42)                             # fixed seed → the Action only commits when stats change
    drip = [rnd.uniform(.7, 1.0) ** .5 for _ in range(COLS)]
    rows = []
    for y in range(RR):
        depth, row = y / RR, []
        for x in range(COLS):
            c = "#%02x%02x%02x" % flip.getpixel((x, y))
            pr = max(0.0, 1 - depth / drip[x]) ** .3 * (1 - .15 * depth) if c != BG else .15 * (1 - depth)
            if y < 2: pr = 1                            # solid band right under the horizon
            row.append((rnd.choice("01") if rnd.random() < pr else " ", CLS.get(c, "a")))
        rows.append(row)
    return rows

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
    sky, txt = pixel_sky(), lines(stats())
    ref = reflection(sky)
    PAD = 28
    n = len(txt) + 1
    art_h = PR * PX + RR * ALH
    H = int(max(n * LH, art_h + 2 * PAD) + 40)
    x_txt = PAD + W * CW + 40
    W_px = int(x_txt + W * CW + PAD)
    style = ".a{fill:#8b949e}.k{fill:#ff2bd6}.d{fill:#3e478f}.v{fill:#00f0ff}.t{fill:#ffe600;font-weight:700}" + \
            "".join(f".{k}{{fill:{dim(c)}}}" for c, k in CLS.items())
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_px}" height="{H}" viewBox="0 0 {W_px} {H}" font-family="SF Mono,Menlo,Consolas,monospace" font-size="{FS}">',
           f'<rect width="{W_px}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>', f"<style>{style}</style>"]
    ay = (H - art_h) / 2
    px = sky.load()
    for y in range(PR):                                   # pixel rows → one rect per run of equal colour
        x = 0
        while x < PC:
            c, x0 = px[x, y], x
            while x < PC and px[x, y] == c: x += 1
            if c != rgb(BG):
                out.append(f'<rect x="{PAD + x0*PX:.2f}" y="{ay + y*PX:.2f}" width="{(x - x0)*PX + .3:.2f}" height="{PX + .3:.2f}" fill="#%02x%02x%02x"/>' % c)
    for i, row in enumerate(ref):
        spans, run = [], None
        for ch, cls in row:  # merge neighbours of the same class into one tspan
            if run and run[0] == cls: run[1] += ch
            else:
                if run: spans.append(run)
                run = [cls, ch]
        spans.append(run)
        out.append(f'<text font-size="{AFS}" x="{PAD}" y="{ay + PR*PX + (i + 1)*ALH - 1:.1f}" xml:space="preserve">' +
                   "".join(f'<tspan class="{c}">{esc(t)}</tspan>' for c, t in spans) + "</text>")
    for i, parts in enumerate(txt):
        if parts:
            out.append(f'<text x="{x_txt}" y="{PAD + 12 + i*LH}" xml:space="preserve">' +
                       "".join(f'<tspan class="{c}">{esc(s)}</tspan>' for c, s in parts) + "</text>")
    out.append("</svg>")
    os.makedirs("img", exist_ok=True); open("img/fetch.svg", "w").write("\n".join(out))

if __name__ == "__main__": main()
