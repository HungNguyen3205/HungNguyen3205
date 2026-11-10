"""Generate the animated SVG assets used by README.md.

Run:  python scripts/build.py  [path/to/My_Portfolio]
Needs Pillow. Edit the DATA section below, re-run, commit.
Design tokens mirror the live portfolio (slate · mauve · rose · teal).
"""
import base64, io, os, sys
from xml.sax.saxutils import escape
from PIL import Image, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
PORTFOLIO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "Portfolio", "My_Portfolio")
PA = os.path.join(PORTFOLIO, "assets")

# ── tokens ────────────────────────────────────────────────────────────────
BG, SURF, SURF2 = "#191d23", "#1f242b", "#262c34"
INK, MUTED, DIM = "#f1eff1", "#a3a8b4", "#6b7280"
MAUVE, ROSE, TEAL, PLUM = "#c5bac4", "#e0a8d6", "#7fc4d4", "#8a4f82"
LINE = "rgba(197,186,196,.16)"
SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
SERIF_VI = "Cambria, 'Noto Serif', 'Times New Roman', serif"  # full Vietnamese glyph coverage
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"

FONTS = "C:/Windows/Fonts"
def _f(name, size):
    try: return ImageFont.truetype(os.path.join(FONTS, name), size)
    except OSError: return ImageFont.load_default()
def tw(text, size, bold=False, serif=False, mono=False):
    name = "consola.ttf" if mono else ("georgiai.ttf" if serif else ("segoeuib.ttf" if bold else "segoeui.ttf"))
    return _f(name, size).getlength(text)

def wrap(text, size, width, **kw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(t, size, **kw) > width and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur] if cur else lines

def e(s): return escape(s)

def img64(path, w, h, crop_top=False, fmt="WEBP", q=82):
    im = Image.open(path).convert("RGBA" if fmt == "PNG" or fmt == "WEBP" else "RGB")
    sw, sh = im.size; r = max(w / sw, h / sh)
    im = im.resize((round(sw * r), round(sh * r)), Image.LANCZOS)
    x = (im.width - w) // 2; y = 0 if crop_top else (im.height - h) // 2
    im = im.crop((x, y, x + w, y + h))
    b = io.BytesIO(); im.save(b, fmt, quality=q, method=6)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()

BASE_CSS = """
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
.up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.pulse{animation:pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
"""
def svg(w, h, body, css="", title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(title)}"><title>{e(title)}</title><style>{BASE_CSS}{css}</style>{body}</svg>')

def grain(w, h, id_="g"):
    return (f'<filter id="{id_}"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0"/></filter>'
            f'<rect width="{w}" height="{h}" filter="url(#{id_})"/>')

def chips(items, x, y, size=15, gap=8, pad=14, h=32, fill="rgba(197,186,196,.08)", stroke=LINE, color=MAUVE, maxw=None):
    out, cx, cy = [], x, y
    for it in items:
        w = tw(it, size, bold=True) + pad * 2
        if maxw and cx + w > x + maxw: cx = x; cy += h + gap
        out.append(f'<rect x="{cx}" y="{cy}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}"/>'
                   f'<text x="{cx + w/2:.0f}" y="{cy + h/2 + size*.36:.0f}" text-anchor="middle" font-family="{SANS}" '
                   f'font-size="{size}" font-weight="600" fill="{color}">{e(it)}</text>')
        cx += w + gap
    return "".join(out)

# Transparent assets get a light-theme twin (name-light.svg), swapped via <picture> in README.
LIGHT = {"#f1eff1": "#191d23", "#a3a8b4": "#57707a", "#e0a8d6": "#8a4f82", "#c5bac4": "#7b919c",
         "#191d23": "#ffffff", "rgba(197,186,196,.16)": "rgba(25,29,35,.16)"}
def light(content):
    import re
    return re.sub("|".join(re.escape(k) for k in LIGHT), lambda m: LIGHT[m.group(0)], content)

def write(name, content, twin=False):
    if twin: write(name.replace(".svg", "-light.svg"), light(content))
    p = os.path.join(OUT, name); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    print(f"  {name:28s} {len(content.encode())//1024:>4} KB")

# ── DATA ──────────────────────────────────────────────────────────────────
GH = "https://github.com/HungNguyen3205/"
MARQUEE = ["Interface design", "Web development", "Data & APIs", "Applied AI", "Ideas into products"]
STATS = [("15", "Projects shipped", "Landing pages, brand sites,", "management systems, AI tools."),
         ("06", "Websites live", "Open the link and use it —", "not just a screenshot."),
         ("05", "AI products", "Chatbots, computer vision,", "generation, auto video editing."),
         ("25", "Technologies", "Frontend, backend, data,", "AI and real deployment.")]
FEATURED = [
    dict(id="work", n="01", cat="Web application", status="live", name="DANAVA Work", host="workspace.danava.com.vn",
         tag="When work needs a shared space.", img="danava-work-poster.jpg",
         rows=[("Problem", "Tasks, members and progress live in too many places to follow."),
               ("Approach", "One shared system in React, TypeScript and Laravel — many views over one source of data."),
               ("Signature", "The team moves between Kanban, list and calendar without losing the thread.")],
         stack=["React", "TypeScript", "Laravel", "PWA"]),
    dict(id="go", n="02", cat="Travel & ticketing", status="live", name="DANAVA Go", host="danavago.com",
         tag="Booking a ticket becomes the start of the trip.", img="shots/go.webp",
         rows=[("Problem", "Coach booking is dry, multi-step and hard to picture."),
               ("Approach", "The homepage is a journey: a bus drives the road, landmarks change with every destination."),
               ("Signature", "One platform, many operators — each with its own branded app and domain.")],
         stack=["React 19", "TypeScript", "Vite", "Framer Motion", "Laravel 13"]),
    dict(id="coach", n="03", cat="Computer vision · AI", status="source", name="DANAVA AI Coach", host="CAMERA_PhanTichTuThe",
         tag="The camera doesn't just see — it understands motion.", img=None,
         rows=[("Problem", "Timer or raw-threshold counting misfires on shaky arms, planks and standing up."),
               ("Approach", "A motion state machine that counts once per full cycle, smoothed with EMA + hysteresis."),
               ("Signature", "10/10 tests passing, identical results at 15, 30 and 60 FPS.")],
         stack=["JavaScript", "MediaPipe", "WebRTC", "Node Test"]),
    dict(id="run", n="04", cat="Event landing page", status="live", name="Bước Chạy Nhịp Sống", host="buoc-chay-nhip-song.vercel.app",
         tag="From inspiration to sign-up in a single scroll.", img="shots/run.webp",
         rows=[("Problem", "A city race needs a page that inspires and still reads clearly."),
               ("Approach", "Opens on an illustrated Da Nang and Dragon Bridge, then guides you to details and the form."),
               ("Signature", "Emotion leads, information holds, the sign-up button is always in reach.")],
         stack=["HTML", "CSS", "JavaScript", "Vercel"]),
]
TILES = [
    ("glg", "GLG — 3D Café", "3D café site + admin · Three.js", "live"),
    ("danava", "DANAVA — Brand site", "Corporate website · Next.js + GSAP", "source"),
    ("omachi", "Omachi — Concept", "E-commerce concept · React 19", "source"),
    ("car", "Car Rental — Midnight", "Rental platform with AI assistant", "source"),
    ("touch", "Touch Art — Slow Garden", "Bilingual wellness website", "source"),
    ("bds", "Real-estate Landing", "Landing page · React + TS", "live"),
    ("nq", "Như Quỳnh — Portfolio", "Graphic designer portfolio", "live"),
    ("wello", "Wellosophy", "Product landing page", "live"),
    ("vif", "VIF — VisionFit", "AI fitness assistant", "demo"),
    ("studio", "DANAVA Video Studio", "AI auto video editing · FFmpeg", "source"),
    ("mkt", "TOOL MKT", "AI content & scheduling · MVP", "source"),
    ("news", "News Reading Tracker", "Chrome extension + dashboard", "source"),
]
STATUS = {"live": ("LIVE", TEAL), "source": ("SOURCE", MAUVE), "demo": ("DEMO", ROSE)}
CHAPTERS = [
    ("about", "01", "The person behind the screen", "Beyond the lines of code."),
    ("numbers", "02", "Progress, through products", "Counted from the work itself."),
    ("featured", "03", "From a problem to a product", "Every project, a different story."),
    ("collection", "04", "Explore the work", "Many problems. Many answers."),
    ("process", "05", "Intention before implementation", "Beautiful is only the start."),
    ("stats", "06", "Still shipping", "The commit log doesn't lie."),
]
STACK = [("Frontend", ["React", "TypeScript", "Vue.js", "Next.js", "Vite", "Framer Motion", "GSAP", "Three.js"]),
         ("Backend", ["Laravel", "PHP", "Node.js", "FastAPI", "Python", "REST API"]),
         ("Data & AI", ["MySQL", "SQLite", "MediaPipe", "Ollama", "OpenAI API"]),
         ("Ship", ["Git", "Vercel", "cPanel", "PWA", "FFmpeg", "n8n"])]
PROCESS = [("01", "Understand", ["Who is the user, what do", "they need, what must", "this product solve?"]),
           ("02", "Design the journey", ["Content, flows and UI", "for desktop and phone", "alike."]),
           ("03", "Build the product", ["Frontend, backend, APIs", "and database — sized to", "the problem."]),
           ("04", "Test & refine", ["Ship to a real environment,", "check every feature, keep", "improving from feedback."])]

# ── HERO ──────────────────────────────────────────────────────────────────
def hero():
    W, H = 1200, 600
    avatar = img64(os.path.join(PA, "hero-frames", "000.webp"), 520, 425, fmt="WEBP", q=86)
    mq = "   ✦   ".join(MARQUEE * 2) + "   ✦   "
    mqw = tw("   ✦   ".join(MARQUEE) + "   ✦   ", 18, bold=True)
    css = f"""
.float{{animation:float 6s ease-in-out infinite}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-12px)}}}}
.spin{{animation:spin 40s linear infinite;transform-box:fill-box;transform-origin:center}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.orb{{animation:orb 12s ease-in-out infinite alternate}}
@keyframes orb{{to{{transform:translate(-60px,40px)}}}}
.mq{{animation:mq 28s linear infinite}}
@keyframes mq{{to{{transform:translateX(-{mqw:.1f}px)}}}}
.caret{{animation:pulse 1s steps(1) infinite}}
"""
    d = [f'<defs><radialGradient id="o1"><stop offset="0" stop-color="{ROSE}" stop-opacity=".35"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="o2"><stop offset="0" stop-color="{TEAL}" stop-opacity=".28"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="nm" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{MAUVE}"/></linearGradient>'
         f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="28"/></clipPath>'
         f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="rgba(197,186,196,.05)"/></pattern></defs>',
         f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>',
         f'<g class="orb"><circle cx="900" cy="230" r="330" fill="url(#o1)"/></g><circle cx="1080" cy="470" r="240" fill="url(#o2)"/>',
         grain(W, H),
         # HUD
         f'<text x="48" y="58" font-family="{SANS}" font-size="20" font-weight="800" fill="{INK}" letter-spacing="1">HÙNG<tspan fill="{ROSE}" font-size="13" dy="-8">®</tspan></text>',
         f'<circle cx="440" cy="51" r="4" fill="{TEAL}" class="pulse"/><text x="454" y="56" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="2">PLAYER 1: READY</text>',
         f'<text x="{W-48}" y="56" text-anchor="end" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="2">PORTFOLIO / 2026 · LVL 21</text>',
         f'<line x1="48" y1="84" x2="{W-48}" y2="84" stroke="{LINE}"/>',
         # intro copy
         f'<g class="up" style="animation-delay:.1s"><text x="48" y="146" font-family="{MONO}" font-size="14" fill="{ROSE}" letter-spacing="3">FULLSTACK DEVELOPER · DA NANG, VIET NAM</text></g>',
         f'<g class="up" style="animation-delay:.25s"><text x="44" y="236" font-family="{SANS}" font-size="92" font-weight="800" fill="url(#nm)" letter-spacing="-3">Nguyễn</text></g>',
         f'<g class="up" style="animation-delay:.4s"><text x="44" y="330" font-family="{SANS}" font-size="92" font-weight="800" fill="url(#nm)" letter-spacing="-3">Nam Hùng<tspan fill="{ROSE}">.</tspan></text></g>',
         f'<g class="up" style="animation-delay:.6s"><text x="48" y="384" font-family="{SERIF_VI}" font-style="italic" font-size="26" fill="{MAUVE}">Biến ý tưởng thành những trải nghiệm có dấu ấn.</text>'
         f'<text x="48" y="418" font-family="{SANS}" font-size="17" fill="{MUTED}">Turning ideas into experiences that leave a mark<tspan class="caret" fill="{ROSE}"> ▍</tspan></text></g>',
         f'<g class="up" style="animation-delay:.8s">' + chips(["DESIGN", "CODE", "EXPERIENCE"], 48, 446, size=13, h=30, color=INK) + '</g>',
         # avatar
         f'<g class="spin"><circle cx="905" cy="300" r="215" fill="none" stroke="{MAUVE}" stroke-opacity=".35" stroke-dasharray="2 10"/></g>',
         f'<circle cx="905" cy="300" r="170" fill="none" stroke="{ROSE}" stroke-opacity=".18"/>',
         f'<g class="float"><image href="{avatar}" x="645" y="96" width="520" height="425"/></g>',
         # marquee
         f'<rect y="{H-64}" width="{W}" height="64" fill="{SURF}"/><line x1="0" y1="{H-64}" x2="{W}" y2="{H-64}" stroke="{LINE}"/>',
         f'<g class="mq"><text x="24" y="{H-25}" font-family="{SANS}" font-size="18" font-weight="700" fill="{MAUVE}" letter-spacing=".5">'
         + e(mq).replace("✦", f'</tspan><tspan fill="{ROSE}">✦</tspan><tspan>').join(["<tspan>", "</tspan>"]) + '</text></g>',
         f'</g><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{LINE}"/>']
    write("hero.svg", svg(W, H, "".join(d), css, "Nguyễn Nam Hùng — Fullstack Developer. Turning ideas into experiences that leave a mark."))

# ── BUTTONS ───────────────────────────────────────────────────────────────
def button(name, label, primary):
    w = tw(label, 17, bold=True) + 72; h = 56
    fill = f'url(#bg)' if primary else "rgba(197,186,196,.06)"
    color = BG if primary else INK
    css = ".sh{animation:sh 3.2s ease-in-out infinite}@keyframes sh{0%{transform:translateX(-120px)}60%,100%{transform:translateX(" + f"{w+40:.0f}" + "px)}}"
    body = (f'<defs><linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>'
            f'<linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="c"><rect width="{w:.0f}" height="{h}" rx="{h/2}"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><rect width="{w:.0f}" height="{h}" fill="{BG}"/><rect width="{w:.0f}" height="{h}" fill="{fill}"/>'
            + (f'<rect class="sh" y="0" width="80" height="{h}" fill="url(#gl)" transform="skewX(-20)"/>' if primary else "")
            + f'</g><rect x=".5" y=".5" width="{w-1:.0f}" height="{h-1}" rx="{(h-1)/2}" fill="none" stroke="{MAUVE if not primary else "none"}" stroke-opacity=".5"/>'
            f'<text x="{w/2:.0f}" y="{h/2+6}" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="700" fill="{color}">{e(label)}</text>')
    write(name, svg(round(w), h, body, css, label))

# ── CHAPTER HEADINGS ──────────────────────────────────────────────────────
def chapter(key, n, kicker, title):
    W, H = 1200, 150
    css = ".ln{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:ln 1.6s .3s cubic-bezier(.6,0,.2,1) forwards}@keyframes ln{to{transform:scaleX(1)}}"
    body = (f'<text x="0" y="96" font-family="{SANS}" font-size="96" font-weight="800" fill="none" stroke="{MAUVE}" stroke-opacity=".45" letter-spacing="-2">{n}</text>'
            f'<g class="up"><text x="140" y="54" font-family="{MONO}" font-size="14" fill="{ROSE}" letter-spacing="3">CHAPTER {n} — {e(kicker.upper())}</text>'
            f'<text x="138" y="100" font-family="{SERIF}" font-style="italic" font-size="40" fill="{INK}">{e(title)}</text></g>'
            f'<rect class="ln" x="0" y="133.5" width="1200" height="1" fill="{MAUVE}" fill-opacity=".35"/>'
            f'<circle cx="1196" cy="134" r="4" fill="{ROSE}" class="pulse"/>')
    write(f"chapters/{key}.svg", svg(W, H, body, css, f"{n} — {kicker}: {title}"), twin=True)

# ── ABOUT ─────────────────────────────────────────────────────────────────
def about():
    W, H = 1200, 520
    photo = img64(os.path.join(PA, "hung-camera.webp"), 380, 472, q=84)
    para = [("Hi, I'm Hùng — a Software Engineering student at Duy Tan University.", INK, True),
            ("I started by building websites for myself, then moved on to real problems: brand sites, a coach-booking platform, management tools and products with AI inside.", MUTED, False),
            ("To me a landing page must tell the right story, an app must run clearly — and an idea only matters once someone can actually use it.", MUTED, False),
            ("So I work the full loop: interface, backend and data — each product a little better than the last.", MUTED, False)]
    y, txt = 112, []
    for i, (p, c, b) in enumerate(para):
        for ln in wrap(p, 19 if b else 17, 660, bold=b):
            txt.append(f'<text x="470" y="{y}" font-family="{SANS}" font-size="{19 if b else 17}" font-weight="{700 if b else 400}" fill="{c}">{e(ln)}</text>')
            y += 30 if b else 27
        y += 14
    facts = [("EDUCATION", "Software Engineering · DTU"), ("ROLE", "Fullstack Developer"),
             ("STRENGTH", "Story-driven UI · Admin systems"), ("EXPLORING", "AI, computer vision, automation")]
    fy = y + 6; fx = [470, 810]
    fk = []
    for i, (k, v) in enumerate(facts):
        x = fx[i % 2]; yy = fy + (i // 2) * 62
        fk.append(f'<text x="{x}" y="{yy}" font-family="{MONO}" font-size="12" fill="{ROSE}" letter-spacing="2">{k}</text>'
                  f'<text x="{x}" y="{yy+24}" font-family="{SANS}" font-size="16" font-weight="600" fill="{INK}">{e(v)}</text>')
    body = (f'<defs><clipPath id="ph"><rect x="24" y="24" width="380" height="472" rx="20"/></clipPath>'
            f'<linearGradient id="fd" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" rx="28" fill="{SURF}"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{LINE}"/>'
            f'<g clip-path="url(#ph)"><image href="{photo}" x="24" y="24" width="380" height="472"/><rect x="24" y="24" width="380" height="472" fill="url(#fd)"/></g>'
            f'<text x="48" y="448" font-family="{SERIF_VI}" font-style="italic" font-size="22" fill="{INK}">Nguyễn Nam Hùng</text>'
            f'<text x="48" y="474" font-family="{MONO}" font-size="12" fill="{MAUVE}" letter-spacing="2">FULLSTACK DEVELOPER ✦ 2026</text>'
            f'<g class="up" style="animation-delay:.1s"><text x="470" y="72" font-family="{SERIF}" font-style="italic" font-size="30" fill="{MAUVE}">Curious to start. Stubborn to finish.</text></g>'
            f'<g class="up" style="animation-delay:.3s">{"".join(txt)}</g>'
            f'<line x1="470" y1="{fy-30}" x2="1150" y2="{fy-30}" stroke="{LINE}"/>'
            f'<g class="up" style="animation-delay:.5s">{"".join(fk)}</g>')
    write("about.svg", svg(W, H, body, "", "About Nguyễn Nam Hùng — Software Engineering student at Duy Tan University, fullstack developer."))

# ── NUMBERS ───────────────────────────────────────────────────────────────
def numbers():
    W, H = 1200, 250; cw = (W - 3 * 20) / 4
    css = ".bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar 1.2s cubic-bezier(.2,.7,.2,1) forwards}@keyframes bar{to{transform:scaleX(1)}}"
    cols = [TEAL, ROSE, MAUVE, TEAL]
    d = []
    for i, (n, lab, l1, l2) in enumerate(STATS):
        x = i * (cw + 20); dl = .15 * i
        d.append(f'<g class="up" style="animation-delay:{dl:.2f}s"><rect x="{x:.0f}" y="0" width="{cw:.0f}" height="{H}" rx="22" fill="{SURF}" stroke="{LINE}"/>'
                 f'<text x="{x+28:.0f}" y="104" font-family="{SANS}" font-size="78" font-weight="800" fill="{INK}" letter-spacing="-3">{n}</text>'
                 f'<rect class="bar" style="animation-delay:{dl+.4:.2f}s" x="{x+28:.0f}" y="124" width="{cw-56:.0f}" height="3" rx="1.5" fill="{cols[i]}"/>'
                 f'<text x="{x+28:.0f}" y="160" font-family="{SANS}" font-size="18" font-weight="700" fill="{INK}">{e(lab)}</text>'
                 f'<text x="{x+28:.0f}" y="190" font-family="{SANS}" font-size="14.5" fill="{MUTED}">{e(l1)}</text>'
                 f'<text x="{x+28:.0f}" y="212" font-family="{SANS}" font-size="14.5" fill="{MUTED}">{e(l2)}</text></g>')
    write("numbers.svg", svg(W, H, "".join(d), css, "15 projects shipped · 6 websites live · 5 AI products · 25 technologies"))

# ── FEATURED CARDS ────────────────────────────────────────────────────────
def coach_visual(x, y, w, h):
    cx, cy, r = x + w / 2, y + h / 2 - 10, 120
    states = [("TOP", "arm ≥ 160°", -90), ("DESCENDING", "lowering", 0), ("BOTTOM", "touch down", 90), ("ASCENDING", "pushing up", 180)]
    import math
    d = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#10201f"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#a8eee3" stroke-opacity=".25" stroke-dasharray="4 8"/>',
         f'<path id="ring" d="M{cx},{cy-r} a{r},{r} 0 1,1 0,{2*r} a{r},{r} 0 1,1 0,{-2*r}" fill="none"/>',
         f'<circle r="9" fill="#a8eee3"><animateMotion dur="4s" repeatCount="indefinite"><mpath href="#ring"/></animateMotion></circle>',
         f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-family="{SANS}" font-size="40" font-weight="800" fill="#a8eee3">+1</text>',
         f'<text x="{cx}" y="{cy+34}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#a8eee3" fill-opacity=".7" letter-spacing="1">ONLY ON A FULL CYCLE</text>']
    for name, sub, ang in states:
        a = math.radians(ang); px, py = cx + (r + 0) * math.cos(a), cy + r * math.sin(a)
        bw = tw(name, 13, bold=True) + 26
        bx = px - bw / 2 + (bw / 2 + 18) * math.cos(a) * (1 if abs(math.cos(a)) > .5 else 0)
        by = py - 16 + (34 * math.sin(a) if abs(math.sin(a)) > .5 else 0)
        d.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="5" fill="#10201f" stroke="#a8eee3" stroke-width="2"/>'
                 f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="32" rx="8" fill="#16302e" stroke="#a8eee3" stroke-opacity=".4"/>'
                 f'<text x="{bx+bw/2:.0f}" y="{by+21:.0f}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="#a8eee3">{name}</text>')
    my = y + h - 46
    for i, (k, v) in enumerate([("10/10", "tests pass"), ("15–60", "FPS stable"), ("EMA", "+ hysteresis")]):
        mx = x + 30 + i * (w - 60) / 3
        d.append(f'<text x="{mx:.0f}" y="{my}" font-family="{SANS}" font-size="20" font-weight="800" fill="#a8eee3">{k}</text>'
                 f'<text x="{mx:.0f}" y="{my+20}" font-family="{MONO}" font-size="11" fill="#a8eee3" fill-opacity=".6">{v}</text>')
    return "".join(d)

def featured(p, flip):
    W, H = 1200, 560; pad = 28
    vw, vh = 640, 400 + 40  # visual box incl. browser chrome
    vx = W - pad - vw if flip else pad; vy = (H - vh) // 2
    tx = pad + 28 if flip else vx + vw + 44; tw_ = W - vw - pad * 2 - 44 - 28
    st, sc = STATUS[p["status"]]
    vis = [f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="18" fill="{SURF2}" stroke="{LINE}"/>']
    if p["img"]:
        src = img64(os.path.join(PA, p["img"]), vw, vh - 40, crop_top=True, q=80)
        vis += [f'<circle cx="{vx+22}" cy="{vy+20}" r="5" fill="#ff5f57"/><circle cx="{vx+40}" cy="{vy+20}" r="5" fill="#febc2e"/><circle cx="{vx+58}" cy="{vy+20}" r="5" fill="#28c840"/>',
                f'<rect x="{vx+vw/2-150}" y="{vy+9}" width="300" height="22" rx="11" fill="{BG}"/>',
                f'<text x="{vx+vw/2}" y="{vy+24}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">🔒 {e(p["host"])}</text>',
                f'<clipPath id="sc{p["id"]}"><path d="M{vx},{vy+40}h{vw}v{vh-58}a18,18 0 0 1 -18,18h{-(vw-36)}a18,18 0 0 1 -18,-18z"/></clipPath>',
                f'<image clip-path="url(#sc{p["id"]})" href="{src}" x="{vx}" y="{vy+40}" width="{vw}" height="{vh-40}"/>']
    else:
        vis.append(coach_visual(vx, vy, vw, vh))
    y = 104
    t = [f'<text x="{tx}" y="{y}" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="2">{p["n"]} · {e(p["cat"].upper())}</text>']
    pw = tw(st, 12, bold=True) + 36
    t.append(f'<rect x="{tx+tw_-pw:.0f}" y="{y-17}" width="{pw:.0f}" height="26" rx="13" fill="none" stroke="{sc}" stroke-opacity=".5"/>'
             f'<circle cx="{tx+tw_-pw+14:.0f}" cy="{y-4}" r="4" fill="{sc}" class="pulse"/>'
             f'<text x="{tx+tw_-pw+24:.0f}" y="{y+1}" font-family="{MONO}" font-size="12" font-weight="700" fill="{sc}" letter-spacing="1">{st}</text>')
    nsize = 44 if tw(p["name"], 44, bold=True) < tw_ else 36
    t.append(f'<text x="{tx}" y="{y+58}" font-family="{SANS}" font-size="{nsize}" font-weight="800" fill="{INK}" letter-spacing="-1">{e(p["name"])}</text>')
    yy = y + 96
    for ln in wrap(p["tag"], 21, tw_, serif=True):
        t.append(f'<text x="{tx}" y="{yy}" font-family="{SERIF}" font-style="italic" font-size="21" fill="{MAUVE}">{e(ln)}</text>'); yy += 28
    yy += 14
    for k, v in p["rows"]:
        t.append(f'<line x1="{tx}" y1="{yy-4}" x2="{tx+tw_}" y2="{yy-4}" stroke="{LINE}"/>'
                 f'<text x="{tx}" y="{yy+20}" font-family="{MONO}" font-size="11.5" fill="{ROSE}" letter-spacing="2">{k.upper()}</text>')
        ly = yy + 20
        for ln in wrap(v, 15, tw_ - 108):
            t.append(f'<text x="{tx+108}" y="{ly}" font-family="{SANS}" font-size="15" fill="{INK}" fill-opacity=".86">{e(ln)}</text>'); ly += 22
        yy = ly + 12
    t.append(chips(p["stack"], tx, max(yy + 4, H - 92), size=13, h=28, gap=6, pad=12, maxw=tw_))
    body = (f'<rect width="{W}" height="{H}" rx="28" fill="{SURF}"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{LINE}"/>'
            + "".join(vis) + '<g class="up">' + "".join(t) + '</g>')
    write(f"featured/{p['id']}.svg", svg(W, H, body, "", f'{p["name"]} — {p["tag"]}'))

# ── TILES ─────────────────────────────────────────────────────────────────
def tile(pid, name, kick, status):
    W, H = 600, 470; iw, ih = 600, 375
    src = img64(os.path.join(PA, "shots", pid + ".webp"), iw, ih, crop_top=True, q=74)
    st, sc = STATUS[status]; pw = tw(st, 11, bold=True) + 34
    body = (f'<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
            f'<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="{SURF}" stop-opacity="0"/><stop offset="1" stop-color="{SURF}"/></linearGradient></defs>'
            f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{SURF}"/><image href="{src}" width="{iw}" height="{ih}"/>'
            f'<rect width="{iw}" height="{ih}" fill="url(#f)"/></g>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{LINE}"/>'
            f'<rect x="18" y="18" width="{pw:.0f}" height="26" rx="13" fill="{BG}" fill-opacity=".85"/>'
            f'<circle cx="32" cy="31" r="4" fill="{sc}" class="pulse"/>'
            f'<text x="42" y="35.5" font-family="{MONO}" font-size="11" font-weight="700" fill="{sc}" letter-spacing="1">{st}</text>'
            f'<text x="26" y="{H-56}" font-family="{SANS}" font-size="27" font-weight="800" fill="{INK}" letter-spacing="-.5">{e(name)}</text>'
            f'<text x="26" y="{H-24}" font-family="{SANS}" font-size="18" fill="{MUTED}">{e(kick)}</text>'
            f'<text x="{W-26}" y="{H-56}" text-anchor="end" font-family="{SANS}" font-size="26" fill="{ROSE}">↗</text>')
    write(f"tiles/{pid}.svg", svg(W, H, body, "", f"{name} — {kick}"))

# ── PROCESS ───────────────────────────────────────────────────────────────
def process():
    W, H = 1200, 290; cw = 1200 / 4
    css = (".ln{stroke-dasharray:1100;stroke-dashoffset:1100;animation:ln 2.4s .2s cubic-bezier(.6,0,.2,1) forwards}@keyframes ln{to{stroke-dashoffset:0}}"
           ".dot{opacity:0;animation:dot .4s forwards}@keyframes dot{to{opacity:1}}")
    d = [f'<line class="ln" x1="40" y1="40" x2="1140" y2="40" stroke="{MAUVE}" stroke-opacity=".5" stroke-dasharray="1100"/>']
    for i, (n, t, ls) in enumerate(PROCESS):
        x = i * cw + 40; dl = .2 + .55 * i
        d.append(f'<g class="dot" style="animation-delay:{dl:.2f}s"><circle cx="{x}" cy="40" r="15" fill="{BG}" stroke="{ROSE}" stroke-width="2"/>'
                 f'<circle cx="{x}" cy="40" r="5" fill="{ROSE}"/></g>'
                 f'<g class="up" style="animation-delay:{dl+.1:.2f}s"><text x="{x-2}" y="104" font-family="{MONO}" font-size="13" fill="{ROSE}" letter-spacing="2">STEP {n}</text>'
                 f'<text x="{x-2}" y="140" font-family="{SANS}" font-size="24" font-weight="800" fill="{INK}">{e(t)}</text>'
                 + "".join(f'<text x="{x-2}" y="{176+j*25}" font-family="{SANS}" font-size="16" fill="{MUTED}">{e(l)}</text>' for j, l in enumerate(ls)) + '</g>')
    write("process.svg", svg(W, H, "".join(d), css, "Process: understand, design the journey, build the product, test and refine."), twin=True)

def stack():
    W = 1200; rh = 64; H = rh * len(STACK) + 30
    d = [f'<rect width="{W}" height="{H}" rx="24" fill="{SURF}" stroke="{LINE}"/>']
    for i, (k, items) in enumerate(STACK):
        y = 22 + i * rh
        if i: d.append(f'<line x1="32" y1="{y-6}" x2="{W-32}" y2="{y-6}" stroke="{LINE}"/>')
        d.append(f'<g class="up" style="animation-delay:{.12*i:.2f}s"><text x="36" y="{y+30}" font-family="{MONO}" font-size="13" fill="{ROSE}" letter-spacing="2">{e(k.upper())}</text>'
                 + chips(items, 230, y + 8, size=14.5, h=32, gap=8, color=INK) + '</g>')
    write("stack.svg", svg(W, H, "".join(d), "", "Stack: " + "; ".join(k + ": " + ", ".join(v) for k, v in STACK)))

def cta():
    W, H = 1200, 340
    css = ".gr{animation:gr 8s ease-in-out infinite alternate}@keyframes gr{to{transform:translateX(-300px)}}"
    body = (f'<defs><linearGradient id="t" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".5" stop-color="{ROSE}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>'
            f'<radialGradient id="o"><stop offset="0" stop-color="{PLUM}" stop-opacity=".55"/><stop offset="1" stop-color="{PLUM}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="c"><rect width="{W}" height="{H}" rx="28"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{SURF}"/><g class="gr"><circle cx="900" cy="300" r="420" fill="url(#o)"/></g>{grain(W, H)}</g>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{LINE}"/>'
            f'<text x="600" y="78" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{ROSE}" letter-spacing="3">CHAPTER 07 — LET\'S MAKE SOMETHING MEANINGFUL</text>'
            f'<g class="up"><text x="600" y="170" text-anchor="middle" font-family="{SERIF_VI}" font-style="italic" font-size="64" fill="url(#t)">Dấu ấn tiếp theo, cùng bạn.</text></g>'
            f'<g class="up" style="animation-delay:.3s"><text x="600" y="222" text-anchor="middle" font-family="{SANS}" font-size="19" fill="{MUTED}">The next mark — made together. Got an idea? Let\'s turn it into a product.</text>'
            f'<text x="600" y="278" text-anchor="middle" font-family="{MONO}" font-size="17" fill="{INK}">namhung03022005@gmail.com</text></g>')
    write("cta.svg", svg(W, H, body, css, "The next mark — made together. namhung03022005@gmail.com"))

def footer():
    W, H = 1200, 70
    body = (f'<line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/>'
            f'<text x="0" y="44" font-family="{SANS}" font-size="18" font-weight="800" fill="{INK}">HÙNG<tspan fill="{ROSE}" font-size="11" dy="-7">®</tspan></text>'
            f'<text x="600" y="44" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="17" fill="{MAUVE}">Built with code. Made with feeling.</text>'
            f'<text x="{W}" y="44" text-anchor="end" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="1">© 2026 NGUYỄN NAM HÙNG</text>')
    write("footer.svg", svg(W, H, body, "", "Built with code. Made with feeling. © 2026 Nguyễn Nam Hùng"), twin=True)

if __name__ == "__main__":
    print("building ->", OUT)
    hero(); about(); numbers(); process(); stack(); cta(); footer()
    button("btn-portfolio.svg", "Enter the portfolio  ↗", True)
    button("btn-email.svg", "Say hello  ✉", False)
    button("btn-github.svg", "Browse all repos  →", False)
    for c in CHAPTERS: chapter(*c)
    for i, p in enumerate(FEATURED): featured(p, i % 2 == 1)
    for t in TILES: tile(*t)
