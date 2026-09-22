"""Regenerate img/fetch.svg (neofetch-style card). Usage: python3 gen.py path/to/portrait.png"""
import sys
from PIL import Image, ImageOps

COLS, ROWS = 56, 30           # ASCII art size in characters
CW, LH, FS = 7.8, 17, 13      # char width, line height, font size (px)
RAMP = " .:-=+*#%@"

def ascii_art(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    im = im.crop((0, int(h * .25), int(w * .75), h))  # frame the figure (lower-left of the 4:3 portrait)
    im = ImageOps.autocontrast(im).resize((COLS, ROWS), Image.LANCZOS)
    # Subject is dark on a bright sky: keep only dark tones as glyphs so the figure reads as an outline on the terminal.
    tone = lambda p: RAMP[min(len(RAMP) - 1, int((max(0, 150 - p) / 150) ** 1.4 * (len(RAMP) - 1)))]
    return ["".join(tone(p) for p in im.crop((0, y, COLS, y + 1)).tobytes()) for y in range(ROWS)]

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

W = 62  # right-column width in chars
def kv(k, v):
    dots = W - len(k) - len(v) - 4
    return [("k", f". {k}:"), ("d", " " + "." * max(dots, 1) + " "), ("v", v)]
def hd(t): return [("t", f"- {t} " + "—" * (W - len(t) - 3))]

LINES = [
    [("t", "wenqian.deng " + "—" * (W - 13))], [],
    kv("OS", "macOS, Linux"),
    kv("Host", "NVIDIA"),
    kv("Kernel", "Software Developer"),
    kv("Uptime", "coding since 2019"),
    kv("IDE", "VS Code, Cursor, IntelliJ"),
    kv("Languages.Programming", "Java, Go, Python, TypeScript, C#"),
    kv("Languages.Frameworks", "Spring Boot, Vue, Kitex"),
    kv("Languages.Data", "MongoDB, Redis, DynamoDB, SQL"),
    kv("Languages.Real", "Mandarin, English"),
    [("k", ".")],
    kv("Interests.Software", "AI agents, DBMS testing"),
    kv("Interests.Cloud", "AWS, Azure"),
    [("k", ".")],
    hd("Contact"),
    kv("Email", "dengwenking@gmail.com"),
    kv("Website", "dwenking.github.io"),
    kv("Scholar", "Wenqian Deng"),
    kv("LinkedIn", "wenqian-deng"),
]

def main(portrait):
    art = ascii_art(portrait)
    rows = max(len(art), len(LINES)) + 2
    H, PAD = int(rows * LH + 40), 28
    x_txt = PAD + COLS * CW + 40
    W_px = int(x_txt + W * CW + PAD)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_px}" height="{H}" viewBox="0 0 {W_px} {H}" font-family="SF Mono,Menlo,Consolas,monospace" font-size="{FS}">',
           f'<rect width="{W_px}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           '<style>.a{fill:#8b949e}.k{fill:#f2a65a}.d{fill:#484f58}.v{fill:#79c0ff}.t{fill:#e6edf3;font-weight:700}</style>']
    for i, l in enumerate(art):
        out.append(f'<text class="a" x="{PAD}" y="{PAD + 12 + i*LH}" xml:space="preserve">{esc(l)}</text>')
    for i, parts in enumerate(LINES):
        if not parts: continue
        spans = "".join(f'<tspan class="{c}">{esc(s)}</tspan>' for c, s in parts)
        out.append(f'<text x="{x_txt}" y="{PAD + 12 + i*LH}" xml:space="preserve">{spans}</text>')
    out.append("</svg>")
    open("img/fetch.svg", "w").write("\n".join(out))

if __name__ == "__main__":
    import os; os.makedirs("img", exist_ok=True); main(sys.argv[1])
