from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


OUT = Path(__file__).with_name("astra_character_sheet.png")
W, H = 1800, 1120
im = Image.new("RGB", (W, H), "#0e1728")
d = ImageDraw.Draw(im)

FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_B = r"C:\Windows\Fonts\seguisb.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def rounded(box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)


# Background grid and restrained cyan light
for x in range(30, W, 56):
    d.line((x, 0, x, H), fill="#142239", width=1)
for y in range(20, H, 56):
    d.line((0, y, W, y), fill="#142239", width=1)
d.ellipse((1240, -300, 2050, 520), fill="#172e43")
d.ellipse((1370, -190, 1900, 340), fill="#1b3448")

rounded((54, 44, 1746, 1076), 28, "#101c30", "#31465e", 2)
d.text((94, 77), "ASTRA  /  CHARACTER LAB", font=font(24, True), fill="#eef7ff")
d.text((94, 118), "HUMANOID OPERATOR     •     MODEL TURNAROUND     •     MK-06", font=font(15), fill="#83a0bd")
d.line((94, 160, 1700, 160), fill="#35516b", width=2)

# View panels
for x0, title, sub in [(102, "01  FRONT", "NEUTRAL POSE"), (690, "02  PROFILE", "EQUIPMENT READ"), (1278, "03  REAR", "ARMOR SILHOUETTE")]:
    rounded((x0, 196, x0 + 500, 1000), 22, "#111f34", "#293f58", 2)
    d.text((x0 + 28, 220), title, font=font(18, True), fill="#7be4dc")
    d.text((x0 + 28, 251), sub, font=font(12), fill="#879db5")
    d.line((x0 + 28, 281, x0 + 472, 281), fill="#293f58", width=1)
    d.line((x0 + 50, 880, x0 + 450, 880), fill="#49627d", width=2)
    d.ellipse((x0 + 116, 866, x0 + 384, 896), fill="#243b51")


def draw_person(cx, ground, direction="front"):
    # proportions are shared by all turnaround views
    flip = -1 if direction == "rear" else 1
    # back leg and boot
    for dx, leg_color in [(-42, "#263752"), (42, "#263752")]:
        d.rounded_rectangle((cx + dx - 25, ground - 246, cx + dx + 25, ground - 88), 22, fill=leg_color, outline="#5b748d", width=3)
        d.rounded_rectangle((cx + dx - 31, ground - 108, cx + dx + 38, ground - 73), 10, fill="#d6a95f", outline="#f4cf8a", width=2)
        d.line((cx + dx - 13, ground - 208, cx + dx - 13, ground - 132), fill="#46637f", width=4)
    # body silhouette and waist
    d.polygon([(cx - 64, ground - 480), (cx - 100, ground - 397), (cx - 82, ground - 278), (cx + 82, ground - 278), (cx + 100, ground - 397), (cx + 64, ground - 480)], fill="#293b57", outline="#90b9c9")
    d.rounded_rectangle((cx - 80, ground - 332, cx + 80, ground - 300), 9, fill="#d6a95f", outline="#f4d393", width=2)
    if direction == "rear":
        d.polygon([(cx - 51, ground - 455), (cx, ground - 420), (cx + 51, ground - 455), (cx + 36, ground - 344), (cx, ground - 318), (cx - 36, ground - 344)], fill="#344964", outline="#80a5bb", width=3)
        d.line((cx, ground - 415, cx, ground - 340), fill="#65dacf", width=8)
        for y in (ground - 440, ground - 402, ground - 364):
            d.line((cx - 28, y, cx + 28, y), fill="#5c7590", width=4)
    else:
        d.polygon([(cx - 58, ground - 456), (cx, ground - 432), (cx + 58, ground - 456), (cx + 38, ground - 340), (cx, ground - 318), (cx - 38, ground - 340)], fill="#3a516e", outline="#83aebb", width=3)
        if direction == "front":
            d.polygon([(cx - 31, ground - 420), (cx + 31, ground - 420), (cx + 24, ground - 370), (cx, ground - 351), (cx - 24, ground - 370)], fill="#65dacf", outline="#d0fff7", width=2)
            d.rounded_rectangle((cx - 23, ground - 306, cx + 23, ground - 294), 5, fill="#16263c")
            d.ellipse((cx - 9, ground - 305, cx + 9, ground - 296), fill="#f4c873")
        else:
            d.line((cx - 26, ground - 414, cx + 27, ground - 414), fill="#d8b875", width=5)
    # arms and gauntlets, offset for a readable T-pose-like neutral stance
    for side in (-1, 1):
        sx = cx + side * 82
        d.line((sx, ground - 438, cx + side * 112, ground - 357), fill="#728ba4", width=31)
        d.line((sx, ground - 438, cx + side * 112, ground - 357), fill="#30435f", width=24)
        d.ellipse((cx + side * 112 - 17, ground - 376, cx + side * 112 + 17, ground - 340), fill="#65dacf", outline="#bcf5ec", width=2)
        d.line((cx + side * 112, ground - 352, cx + side * 113, ground - 295), fill="#30435f", width=22)
        d.line((cx + side * 112, ground - 352, cx + side * 113, ground - 295), fill="#5d7893", width=3)
    # neck, head and distinctive crest
    d.rounded_rectangle((cx - 18, ground - 520, cx + 18, ground - 468), 9, fill="#b88772")
    d.ellipse((cx - 47, ground - 596, cx + 47, ground - 495), fill="#c99780", outline="#ebc4ae", width=3)
    d.polygon([(cx - 53, ground - 560), (cx - 44, ground - 618), (cx, ground - 642), (cx + 44, ground - 618), (cx + 53, ground - 560), (cx, ground - 578)], fill="#d1a85f", outline="#f3d58c", width=3)
    if direction == "front":
        d.rounded_rectangle((cx - 46, ground - 568, cx + 46, ground - 539), 8, fill="#111b2e", outline="#8eabbc", width=2)
        d.line((cx - 27, ground - 554, cx + 27, ground - 554), fill="#72f0e3", width=6)
    elif direction == "profile":
        d.rounded_rectangle((cx - 5, ground - 565, cx + 42, ground - 541), 8, fill="#111b2e", outline="#8eabbc", width=2)
        d.line((cx + 5, ground - 553, cx + 35, ground - 553), fill="#72f0e3", width=5)
        # compact blade carried at the side
        d.line((cx + 154, ground - 385, cx + 169, ground - 546), fill="#b8fff4", width=9)
        d.line((cx + 142, ground - 389, cx + 169, ground - 385), fill="#e5bf72", width=9)
    else:
        d.polygon([(cx - 21, ground - 563), (cx, ground - 548), (cx + 21, ground - 563), (cx + 11, ground - 535), (cx, ground - 527), (cx - 11, ground - 535)], fill="#17263c", outline="#8eabbc", width=2)


draw_person(352, 858, "front")
draw_person(940, 858, "profile")
draw_person(1528, 858, "rear")

d.text((126, 923), "AURORA-CLASS SCOUT", font=font(16, True), fill="#eef7ff")
d.text((126, 952), "Ceramic armor  /  Pulse core  /  Training blade", font=font(12), fill="#91a9c1")
d.text((714, 923), "MOBILITY PROFILE", font=font(16, True), fill="#eef7ff")
d.text((714, 952), "Balanced stance  /  Light kit  /  Forward visor", font=font(12), fill="#91a9c1")
d.text((1302, 923), "REAR ARMOR", font=font(16, True), fill="#eef7ff")
d.text((1302, 952), "Back plate  /  Spine light  /  Modular joints", font=font(12), fill="#91a9c1")

d.text((98, 1022), "CUSTOM CHARACTER CONCEPT  •  READY FOR GODOT DEMO", font=font(12, True), fill="#72e0d8")
d.text((1470, 1022), "GAME LAB 06", font=font(12, True), fill="#839bb3")
im.save(OUT, optimize=True)
print(OUT)
