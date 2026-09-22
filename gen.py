"""Regenerate img/fetch.svg: ASCII art of pets.png (dog + cat) + neofetch-style info + live GitHub stats.
Run: python3 gen.py   (set GITHUB_TOKEN to raise API rate limits; the Action does)"""
import io, json, os, urllib.request
from PIL import Image, ImageOps

USER = "dwenking"
W = 62                         # right-column width in chars
CW, LH, FS = 7.8, 17, 13       # char width, line height, font size (px)
AFS = 7                        # art font size; smaller cells → more detail in the same pixel width as the text column
ACW, ALH = AFS * .6, AFS * 1.05
COLS = int(W * CW / ACW)       # art column is exactly as wide as the text column
RAMP = " .:-=+*#%@"            # by brightness: white fur → dense glyphs on the dark card

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json",
          **({"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {})})
    return urllib.request.urlopen(req, timeout=30).read()

def ascii_art():
    im = Image.open("pets.png").convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    rows = round(COLS * ACW / ALH * im.height / im.width)       # keep the photo's aspect in character cells
    im = im.resize((COLS, rows), Image.BOX)
    lum = ImageOps.autocontrast(im.convert("L"), cutoff=3, mask=im.getchannel("A")).tobytes()  # stretch fur tones so faces read
    alpha = im.getchannel("A").tobytes()
    ch = lambda l, a: " " if a < 128 else RAMP[min(len(RAMP) - 1, int((l / 255) ** .9 * len(RAMP)))]
    return ["".join(ch(lum[y*COLS + x], alpha[y*COLS + x]) for x in range(COLS)) for y in range(rows)]

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
        kv("Uptime", "coding since 2019"),
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
    n = max(len(art), len(txt)) + 1
    H = int(n * LH + 40)
    x_txt = PAD + W * CW + 40
    W_px = int(x_txt + W * CW + PAD)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_px}" height="{H}" viewBox="0 0 {W_px} {H}" font-family="SF Mono,Menlo,Consolas,monospace" font-size="{FS}">',
           f'<rect width="{W_px}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           '<style>.a{fill:#c9d1d9}.k{fill:#f2a65a}.d{fill:#484f58}.v{fill:#79c0ff}.t{fill:#e6edf3;font-weight:700}</style>']
    y0 = PAD + 12 + ((n - 1) * LH - len(art) * ALH) / 2  # vertically centre the art against the text block
    for i, row in enumerate(art):
        out.append(f'<text class="a" font-size="{AFS}" x="{PAD}" y="{y0 + i*ALH:.1f}" xml:space="preserve">{esc(row)}</text>')
    for i, parts in enumerate(txt):
        if parts:
            out.append(f'<text x="{x_txt}" y="{PAD + 12 + i*LH}" xml:space="preserve">' +
                       "".join(f'<tspan class="{c}">{esc(s)}</tspan>' for c, s in parts) + "</text>")
    out.append("</svg>")
    os.makedirs("img", exist_ok=True); open("img/fetch.svg", "w").write("\n".join(out))

if __name__ == "__main__": main()
