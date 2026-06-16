from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "opoenai carousel"
SLIDE_DIR = OUT_DIR / "slides"
SLIDE_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350

COLORS = {
    "bg": "#f6f7f3",
    "paper": "#ffffff",
    "ink": "#17211c",
    "muted": "#5f6f67",
    "green": "#2d6a4f",
    "teal": "#287271",
    "blue": "#0b74ba",
    "orange": "#f97316",
    "amber": "#e9c46a",
    "red": "#c44536",
    "line": "#dce4de",
    "soft_green": "#e8f3ed",
    "soft_orange": "#fff1df",
}

LOGO = ROOT / "assets" / "impact_bridge_logo.png"
FIGURES = ROOT / "reports" / "figures"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F = {
    "eyebrow": font(25, True),
    "title": font(66, True),
    "title_small": font(54, True),
    "subtitle": font(34, False),
    "body": font(31, False),
    "body_bold": font(31, True),
    "small": font(23, False),
    "small_bold": font(23, True),
    "tiny": font(18, False),
}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def new_slide() -> Image.Image:
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    for i in range(0, H, 18):
        alpha = i / H
        r = int(246 * (1 - alpha) + 238 * alpha)
        g = int(247 * (1 - alpha) + 247 * alpha)
        b = int(243 * (1 - alpha) + 239 * alpha)
        draw.rectangle([0, i, W, i + 18], fill=(r, g, b))
    return img


def rounded(draw: ImageDraw.ImageDraw, box, radius=24, fill=COLORS["paper"], outline=COLORS["line"], width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, text, font_obj, fill=COLORS["ink"], max_width=None, line_spacing=10):
    x, y = xy
    if not max_width:
        draw.text((x, y), text, font=font_obj, fill=fill)
        return y + draw.textbbox((x, y), text, font=font_obj)[3] - y

    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font_obj) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font_obj)
        y += bbox[3] - bbox[1] + line_spacing
    return y


def bullet_list(draw, x, y, items, max_width=820, bullet_color=COLORS["orange"]):
    for item in items:
        draw.ellipse([x, y + 12, x + 12, y + 24], fill=bullet_color)
        y = text(draw, (x + 30, y), item, F["body"], max_width=max_width, line_spacing=8) + 10
    return y


def paste_logo(img: Image.Image, box=(830, 58, 985, 213)):
    if not LOGO.exists():
        return
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([0, 0, logo.width - 1, logo.height - 1], radius=20, fill=(0, 0, 0, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img.paste(shadow, (box[0] + 4, box[1] + 8), shadow)
    img.paste(logo, (box[0], box[1]), logo)


def footer(draw, slide_no: int):
    draw.line([70, 1265, 1010, 1265], fill=COLORS["line"], width=2)
    draw.text((70, 1285), "Sudan Humanitarian AI Insights", font=F["tiny"], fill=COLORS["muted"])
    draw.text((908, 1285), f"{slide_no:02d}/09", font=F["tiny"], fill=COLORS["muted"])


def pill(draw, x, y, label, fill=COLORS["paper"], outline=COLORS["line"], text_color=COLORS["ink"]):
    pad_x, pad_y = 18, 9
    width = int(draw.textlength(label, font=F["small_bold"]) + pad_x * 2)
    height = 42
    rounded(draw, [x, y, x + width, y + height], radius=21, fill=fill, outline=outline, width=2)
    draw.text((x + pad_x, y + pad_y), label, font=F["small_bold"], fill=text_color)
    return x + width + 12


def network(draw, cx, cy, scale=1.0):
    pts = [
        (-145, -40), (-95, -80), (-35, -52), (25, -100), (92, -62), (145, -20),
        (-132, 35), (-72, 18), (-15, 52), (48, 20), (108, 60), (160, 92),
        (-88, 112), (-20, 132), (58, 110), (132, 142),
    ]
    pts = [(cx + int(x * scale), cy + int(y * scale)) for x, y in pts]
    links = [(0, 1), (1, 2), (2, 3), (2, 8), (3, 4), (4, 5), (0, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (7, 12), (12, 13), (13, 14), (14, 15)]
    for a, b in links:
        draw.line([pts[a], pts[b]], fill=COLORS["blue"], width=max(2, int(3 * scale)))
    for idx, (x, y) in enumerate(pts):
        color = COLORS["orange"] if idx in {3, 5, 10, 15} else COLORS["blue"]
        r = int(9 * scale) if idx % 3 else int(14 * scale)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=COLORS["paper"], width=3)


def add_chart_card(img, path, box, title=None):
    draw = ImageDraw.Draw(img)
    rounded(draw, box, radius=24, fill=COLORS["paper"], outline=COLORS["line"], width=2)
    if title:
        draw.text((box[0] + 26, box[1] + 22), title, font=F["small_bold"], fill=COLORS["green"])
        top = box[1] + 62
    else:
        top = box[1] + 20
    if Path(path).exists():
        chart = Image.open(path).convert("RGB")
        chart.thumbnail((box[2] - box[0] - 42, box[3] - top - 22), Image.Resampling.LANCZOS)
        img.paste(chart, (box[0] + 22, top))


def slide_1():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "RESPONSIBLE AI FOR HUMANITARIAN ACTION", font=F["eyebrow"], fill=COLORS["green"])
    y = text(draw, (70, 185), "Can AI Help Humanitarian Teams Turn Crisis Signals Into Action?", F["title"], max_width=650, line_spacing=14)
    y += 25
    text(draw, (70, y), "Sudan Humanitarian AI Insights", F["subtitle"], fill=COLORS["teal"], max_width=720)
    text(draw, (70, 1115), "Created by Shireen El Sabea", F["body_bold"], fill=COLORS["ink"])
    paste_logo(img, (765, 120, 1000, 355))
    network(draw, 760, 780, 1.28)
    x = 70
    for label in ["No paid APIs", "Synthetic demo data", "Human oversight"]:
        x = pill(draw, x, 1010, label)
    footer(draw, 1)
    return img


def slide_2():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "THE PROBLEM", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "Humanitarian teams make decisions under pressure", F["title_small"], max_width=880)
    cards = [
        ("Displacement changes quickly", COLORS["blue"]),
        ("Feedback arrives in many formats", COLORS["orange"]),
        ("Resources are limited", COLORS["red"]),
        ("Teams need fast, explainable insight", COLORS["teal"]),
    ]
    x0, y0 = 70, 390
    for i, (label, color) in enumerate(cards):
        x = x0 + (i % 2) * 470
        y = y0 + (i // 2) * 275
        rounded(draw, [x, y, x + 420, y + 205], radius=28, fill=COLORS["paper"])
        draw.ellipse([x + 28, y + 28, x + 84, y + 84], fill=color)
        text(draw, (x + 28, y + 112), label, F["body_bold"], max_width=350)
    footer(draw, 2)
    return img


def slide_3():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "THE IDEA", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "From scattered signals to decision support", F["title_small"], max_width=880)
    text(draw, (70, 300), "This prototype shows how AI-assisted analysis can organize crisis context, classify feedback, rank hotspots, and generate action briefs.", F["body"], fill=COLORS["muted"], max_width=860)
    steps = [
        ("Data", COLORS["blue"]),
        ("NLP triage", COLORS["teal"]),
        ("Priority score", COLORS["amber"]),
        ("Dashboard", COLORS["orange"]),
        ("Action brief", COLORS["red"]),
    ]
    y = 585
    for i, (label, color) in enumerate(steps):
        x = 80 + i * 195
        rounded(draw, [x, y, x + 150, y + 140], radius=22, fill=COLORS["paper"], outline=color, width=4)
        text(draw, (x + 18, y + 45), label, F["small_bold"], max_width=118)
        if i < len(steps) - 1:
            draw.line([x + 154, y + 70, x + 190, y + 70], fill=COLORS["muted"], width=4)
            draw.polygon([(x + 190, y + 70), (x + 175, y + 60), (x + 175, y + 80)], fill=COLORS["muted"])
    paste_logo(img, (805, 945, 960, 1100))
    footer(draw, 3)
    return img


def slide_4():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "WHAT I BUILT", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "Sudan Humanitarian AI Insights Dashboard", F["title_small"], max_width=850)
    bullet_list(draw, 70, 325, [
        "Hotspot ranking",
        "Sector pressure matrix",
        "Synthetic feedback intelligence",
        "Trend and scenario view",
        "AI Action Brief per location",
    ], max_width=430)
    add_chart_card(img, FIGURES / "priority_hotspots.png", [560, 315, 1000, 690], "Hotspot ranking")
    add_chart_card(img, FIGURES / "sector_pressure_heatmap.png", [560, 725, 1000, 1115], "Sector matrix")
    footer(draw, 4)
    return img


def slide_5():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "THE AI LAYER", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "Transparent AI, not black-box decisions", F["title_small"], max_width=850)
    text(draw, (70, 300), "The prototype uses local NLP-style classification and explainable scoring to support human review.", F["body"], fill=COLORS["muted"], max_width=820)
    rounded(draw, [70, 470, 1010, 830], radius=32, fill=COLORS["paper"])
    text(draw, (110, 520), "Message", F["small_bold"], fill=COLORS["green"])
    text(draw, (110, 570), "The water point is broken and children are sick after unsafe water.", F["body"], max_width=800)
    y = 705
    x = 110
    for label, color in [("Sector: WASH", COLORS["blue"]), ("Urgency: Critical", COLORS["red"]), ("Action: Field validation", COLORS["teal"])]:
        x = pill(draw, x, y, label, fill=COLORS["bg"], outline=color)
    rounded(draw, [150, 930, 930, 1050], radius=28, fill=COLORS["soft_orange"], outline=COLORS["orange"], width=3)
    text(draw, (190, 965), "No paid APIs. No PII. No private field data.", F["body_bold"], max_width=700)
    footer(draw, 5)
    return img


def slide_6():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "HOTSPOT ACTION BRIEF", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "The most important output is action", F["title_small"], max_width=850)
    rounded(draw, [90, 330, 990, 1030], radius=34, fill=COLORS["paper"])
    draw.text((135, 385), "AI Action Brief: South Darfur", font=F["subtitle"], fill=COLORS["green"])
    bullet_list(draw, 140, 480, [
        "Why it was prioritized",
        "Top risk drivers",
        "Suggested next steps",
        "Field validation needs",
    ], max_width=720)
    x = 140
    for label in ["IDP volume", "Food", "WASH", "Access"]:
        x = pill(draw, x, 835, label, fill=COLORS["soft_green"], outline=COLORS["teal"])
    text(draw, (140, 930), "Decision-support note, not automated allocation.", F["small_bold"], fill=COLORS["muted"], max_width=700)
    footer(draw, 6)
    return img


def slide_7():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "ETHICAL GUARDRAILS", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "Humanitarian AI must be careful by design", F["title_small"], max_width=850)
    items = ["Privacy first", "Synthetic demo data", "Human oversight", "Explainable scoring", "Do no harm", "Field validation before action"]
    y = 345
    for i, item in enumerate(items):
        x = 90 + (i % 2) * 455
        yy = y + (i // 2) * 185
        rounded(draw, [x, yy, x + 390, yy + 125], radius=24, fill=COLORS["paper"])
        draw.text((x + 32, yy + 38), "✓", font=font(42, True), fill=COLORS["green"])
        text(draw, (x + 92, yy + 43), item, F["body_bold"], max_width=260)
    footer(draw, 7)
    return img


def slide_8():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "WHY IT MATTERS", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "AI should help teams listen better and prioritize faster", F["title_small"], max_width=850)
    text(draw, (70, 335), "This kind of dashboard can help NGOs discuss needs, risks, and tradeoffs with more transparency.", F["body"], fill=COLORS["muted"], max_width=850)
    center = (540, 780)
    nodes = [("People", 290, 650, COLORS["orange"]), ("Data", 790, 650, COLORS["blue"]), ("Action", 540, 980, COLORS["green"])]
    for label, x, y, color in nodes:
        draw.line([center, (x, y)], fill=COLORS["line"], width=5)
        draw.ellipse([x - 85, y - 85, x + 85, y + 85], fill=COLORS["paper"], outline=color, width=5)
        text(draw, (x - 60, y - 18), label, F["body_bold"], max_width=130)
    rounded(draw, [155, 1115, 925, 1205], radius=26, fill=COLORS["soft_green"], outline=COLORS["green"], width=3)
    text(draw, (195, 1142), "AI supports decisions. It should not replace humanitarian judgment.", F["small_bold"], max_width=690)
    footer(draw, 8)
    return img


def slide_9():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    draw.text((70, 80), "CALL TO ACTION", font=F["eyebrow"], fill=COLORS["green"])
    text(draw, (70, 155), "Let's build responsible AI for social impact", F["title_small"], max_width=850)
    text(draw, (70, 310), "I am open to collaboration with NGOs, humanitarian data teams, and social-impact organizations working on responsible AI, community feedback, and needs analysis.", F["body"], fill=COLORS["muted"], max_width=850)
    rounded(draw, [90, 600, 990, 980], radius=34, fill=COLORS["paper"])
    paste_logo(img, (125, 655, 305, 835))
    draw.text((350, 655), "Shireen El Sabea", font=F["subtitle"], fill=COLORS["green"])
    draw.text((350, 725), "linkedin.com/in/shireenalsabea", font=F["body"], fill=COLORS["teal"])
    draw.text((350, 785), "sabeashireen@gmail.com", font=F["body"], fill=COLORS["teal"])
    rounded(draw, [350, 870, 850, 930], radius=30, fill=COLORS["green"], outline=COLORS["green"])
    text(draw, (432, 884), "Reach out for collaboration", F["small_bold"], fill=COLORS["paper"])
    text(draw, (90, 1125), "Sources: IOM DTM Sudan, HDX, OCHA, ReliefWeb, ACLED.", F["tiny"], fill=COLORS["muted"], max_width=840)
    footer(draw, 9)
    return img


def main() -> None:
    slides = [slide_1(), slide_2(), slide_3(), slide_4(), slide_5(), slide_6(), slide_7(), slide_8(), slide_9()]
    paths = []
    for i, slide in enumerate(slides, start=1):
        path = SLIDE_DIR / f"slide_{i:02d}.png"
        slide.save(path, quality=95)
        paths.append(path)

    pdf_path = OUT_DIR / "sudan_humanitarian_ai_linkedin_carousel.pdf"
    rgb_slides = [Image.open(path).convert("RGB") for path in paths]
    rgb_slides[0].save(pdf_path, save_all=True, append_images=rgb_slides[1:], resolution=100.0)
    print(f"Generated {len(paths)} slides")
    print(pdf_path)


if __name__ == "__main__":
    main()
