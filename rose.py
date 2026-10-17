import math as m
import random as r
import tkinter as tk
import tkinter.font as tkf

W, H = 800, 800
DURATION = 10          # секунд
TICK = 16              # мс
ANIM = 38              # нэг үгийн гарч ирэх фрейм
LIFT = 32              # доороос дээш хөөрөх зай (px)
RIM_NARROW = 200      # энэ өргөнөөс нарийн мөр бүхлээрээ "гадна хүрээ" болно
ROW = 17               # мөр хоорондын зай
BG = "#060208"
FONT_FALLBACKS = ("Georgia", "Times New Roman", "Arial")
SEED = 17

PHRASES = [
    "I LOVE YOU", "I love you", "Te amo", "Ti amo", "Je t'aime",
    "Ich liebe dich", "Eu te amo", "Seni seviyorum", "Я тебя люблю",
    "TE QUIERO", "AMOR", "AMOUR", "LOVE", "Ik hou van jou", "Jeg elsker dig",
    "Jag älskar dig", "Kocham cię", "Szeretlek", "Nakupenda", "Mahal kita",
    "Anh yêu em", "Aku cinta kamu", "Ljubim te", "Miluji tě", "Rakastan sinua",
    "Σ' αγαπώ", "愛してる", "我爱你", "사랑해", "ฉันรักเธอ", "Би чамд хайртай",
    "मैं तुमसे प्यार करता हूँ", "Volim te", "Te iubesc", "Mīlu tevi",
    "Ég elska þig", "Ti voglio bene", "Te quiero", "Mi amas vin",
]


def pick_family():
    avail = set(tkf.families())
    for f in FONT_FALLBACKS:
        if f in avail:
            return f
    return "TkDefaultFont"


# ---------- сарнайн хэлбэр ----------
BX = 400               # голын x
BT, BB = 88, 528       # цэцгийн дээд / доод ирмэг
BCY = 262              # цэцгийн төвийн y (өнгөний спираль)


def in_bloom(x, y):
    # дээд талдаа 3 дэлбээний хонхор, доошоо шовх буурсан аяга хэлбэр
    yy = y + 10 * m.cos((x - BX) / 34)
    t = (yy - BT) / (BB - BT)
    if t <= 0 or t >= 1:
        return False
    half = 292 * m.sin(m.pi * t ** 0.5)
    return abs(x - BX) < half


def in_stem(x, y):
    if y < 505 or y > 792:
        return False
    return abs(x - (BX + 6 * m.sin((y - 505) / 70))) < 30 - (y - 505) * 0.025


def in_leaf(x, y, cx, cy, ang, a=105, b=30):
    dx, dy = x - cx, y - cy
    c, s = m.cos(ang), m.sin(ang)
    u, v = dx * c + dy * s, -dx * s + dy * c
    if abs(u) >= a:
        return False
    return abs(v) < b * 1.25 * (1 - abs(u) / a) ** 0.6


def in_leaves(x, y):
    return (in_leaf(x, y, 300, 625, m.radians(22)) or
            in_leaf(x, y, 505, 590, m.radians(-22)))


def region(x, y):
    if in_bloom(x, y):
        return "bloom"
    if in_stem(x, y) or in_leaves(x, y):
        return "green"
    return None


# ---------- өнгө ----------
def bloom_brightness(x, y):
    # спираль хэлбэрээр давхарласан дэлбээнүүд: ирмэг нь цайвар, хоорондох зай нь бараан
    dx, dy = (x - BX) / 292, (y - BCY) / 200
    d = m.hypot(dx, dy)
    th = m.atan2(dy, dx)
    frac = (d * 3.6 - th / (2 * m.pi) * 2.0 + 0.10 * m.sin(5 * th)) % 1.0
    return 0.16 + 0.84 * frac ** 1.3


def pick_color(x, y, rg):
    if rg == "green":
        base = r.choice([(46, 190, 74), (31, 157, 58), (73, 209, 95)])
        k = 0.65 + 0.35 * r.random()
        return tuple(int(v * k) for v in base)
    b = bloom_brightness(x, y)
    base = (232, 24 + r.randint(-10, 14), 58 + r.randint(-8, 8))
    c = [v * b for v in base]
    if b > 0.88:
        t = (b - 0.88) / 0.12 * 0.45
        c = [a + (z - a) * t for a, z in zip(c, (255, 130, 150))]
    return tuple(int(v) for v in c)


# ---------- үгсийг байрлуулах ----------
def build_words(root):
    r.seed(SEED)
    family = pick_family()
    fonts = {}

    def font(size, bold):
        k = (size, bold)
        if k not in fonts:
            fonts[k] = tkf.Font(root=root, family=family, size=size,
                                weight="bold" if bold else "normal")
        return fonts[k]

    words = []
    y = 80
    while y < H - 6:
        # мөр доторх хүчинтэй хэсгүүд (сегмент)
        segs, start, cur = [], None, None
        for x in range(0, W, 2):
            rg = region(x, y)
            if rg and start is None:
                start, cur = x, rg
            elif start is not None and (not rg or rg != cur):
                segs.append((start, x, cur))
                start, cur = (x, rg) if rg else (None, None)
        if start is not None:
            segs.append((start, W, cur))

        for x0, x1, rg in segs:
            if x1 - x0 < 22:
                continue
            row, x, fails = [], x0, 0
            while fails < 40:
                size = r.randint(8, 12) if rg == "green" else r.randint(9, 15)
                f = font(size, r.random() < 0.55)
                p = r.choice(PHRASES)
                w = f.measure(p)
                if x + w > x1:
                    fails += 1
                    continue
                row.append((p, f, x, w))
                x += w + 6
            if not row:
                continue
            used = row[-1][2] + row[-1][3] - x0
            shift = (x1 - x0 - used) / 2
            narrow = (x1 - x0) < RIM_NARROW
            for i, (p, f, px, w) in enumerate(row):
                cx = px + w / 2 + shift
                rim = (rg == "bloom" and
                       (narrow or i == 0 or i == len(row) - 1))
                words.append({"text": p, "font": f, "x": cx, "y": y,
                              "rg": rg, "rim": rim,
                              "color": pick_color(cx, y, rg)})
        y += ROW
    return words


def mix(c1, c2, t):
    return "#%02x%02x%02x" % tuple(
        int(a + (b - a) * t) for a, b in zip(c1, c2))


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def main():
    root = tk.Tk()
    root.title("1 Rose, Every Language")
    root.resizable(False, False)
    cv = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
    cv.pack()

    title_font = tkf.Font(root=root, family=pick_family(), size=30, weight="bold")
    cv.create_text(W / 2, 38, text="1 Rose, Every Language",
                   font=title_font, fill="#ff3d6e")

    words = build_words(root)

    # дараалал (бүгд доороос дээш):
    # 1) навч, иш  2) цэцгийн гадна хүрээ  3) цэцгийн дотор хэсэг
    def order_key(wd):
        if wd["rg"] == "green":
            grp = 0
        elif wd["rim"]:
            grp = 1
        else:
            grp = 2
        return (grp, -wd["y"], wd["x"])

    words.sort(key=order_key)
    n = len(words)
    bg = hex2rgb(BG)
    total = int(DURATION * 1000 / TICK)
    latest_start = max(1, total - ANIM)
    for i, wd in enumerate(words):
        wd["start"] = int(i / max(1, n - 1) * latest_start)
        wd["item"] = cv.create_text(wd["x"], wd["y"] + LIFT, text=wd["text"],
                                    font=wd["font"], fill=BG)

    state = {"t": 0}

    def tick():
        t = state["t"]
        for wd in words:
            k = (t - wd["start"]) / ANIM
            if k < 0 or k > 1.05:
                continue
            k = min(1.0, k)
            e = 1 - (1 - k) ** 3
            cv.coords(wd["item"], wd["x"], wd["y"] + LIFT * (1 - e))
            cv.itemconfig(wd["item"], fill=mix(bg, wd["color"], e))
        state["t"] += 1
        if state["t"] < total + ANIM + 2:
            root.after(TICK, tick)

    tick()
    root.mainloop()


if __name__ == "__main__":
    main()
