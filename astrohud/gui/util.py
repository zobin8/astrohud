from typing import Tuple
from typing import Union
from enum import Enum
import math
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from astrohud.astro.model import Horoscope
from astrohud.astro.enums import Sign


COLOR_ALPHA = (255, 255, 255, 0)
COLOR_WHITE = (255, 255, 255, 255)


MAX_RADIUS = 1500
IMAGE_PAD = 100

ZODIAC_OUT_RADIUS = MAX_RADIUS * 1.0
ZODIAC_IN_RADIUS = MAX_RADIUS * 0.8

HOUSE_OUT_RADIUS = MAX_RADIUS * 0.5
HOUSE_IN_RADIUS = MAX_RADIUS * 0.4

PLANET_RADIUS = MAX_RADIUS * 0.7

FONT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'font/HackNerdFont-Regular.ttf')
IMG_FOLDER =  os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img')
FONT = ImageFont.truetype(FONT_FILE, size=96, encoding='unic')


def get_symbol(name: str) -> Image.Image:
    img = Image.open(os.path.join(IMG_FOLDER, f'{name.lower()}.png'))
    return img.convert('RGBA')


def polar_to_xy(rho: float, phi: float) -> Tuple[float, float]:
    angle = (phi + 180) * math.pi / 180
    x = rho * math.cos(angle)
    y = rho * math.sin(angle)

    offset = MAX_RADIUS + IMAGE_PAD

    return (x + offset, offset - y)


def draw_circle(draw: ImageDraw.Draw, radius: float):
    draw.circle(polar_to_xy(0, 0), radius, width=5, fill=COLOR_ALPHA, outline=COLOR_WHITE)


def draw_spoke(draw: ImageDraw.Draw, r1: float, r2: float, angle: float, width: float):
    a = polar_to_xy(r1, angle)
    b = polar_to_xy(r2, angle)
    draw.line(a + b, fill=COLOR_WHITE, width=width)


def label_point(draw: ImageDraw.Draw, rho: float, phi: float, label: Union[str, Enum]):
    xy = polar_to_xy(rho, phi)
    if isinstance(label, str):
        draw.text(xy, label, font=FONT, fill=COLOR_WHITE, anchor='mm')
    else:
        img = get_symbol(label.name).resize((150, 150))
        draw.bitmap((xy[0] - 75, xy[1] - 75), img, fill=COLOR_WHITE)


def label_quad(draw: ImageDraw.Draw, r1: float, r2: float, a1: float, a2: float, label: str):
    while a1 - 180 > a2:
        a2 += 360
    while a1 + 180 < a2:
        a2 -= 360
    rho = (r1 + r2) / 2
    phi = (a1 + a2) / 2
    label_point(draw, rho, phi, label)


def draw_horoscope(horoscope: Horoscope) -> Image.Image:
    width = (MAX_RADIUS + IMAGE_PAD) * 2 + 1
    img = Image.new("RGBA", (width, width), COLOR_ALPHA)
    draw = ImageDraw.Draw(img)

    draw_circle(draw, ZODIAC_OUT_RADIUS)
    draw_circle(draw, ZODIAC_IN_RADIUS)
    draw_circle(draw, HOUSE_OUT_RADIUS)
    draw_circle(draw, HOUSE_IN_RADIUS)

    asc_angle = horoscope.ascending.abs_angle
    for x in range(12):
        phi = (x * 30) - asc_angle
        draw_spoke(draw, ZODIAC_IN_RADIUS, ZODIAC_OUT_RADIUS, phi, 5)
        label_quad(draw, ZODIAC_IN_RADIUS, ZODIAC_OUT_RADIUS, phi, phi + 30, Sign(x))

    cusps = [horoscope.cusps[h] for h in sorted(horoscope.cusps.keys(), key=lambda x: x.value)]
    next_cusps = cusps[1:] + [cusps[0]]
    for x in range(len(cusps)):
        width = 9 if x % 3 == 0 else 2
        phi = cusps[x] - asc_angle
        phi_2 = next_cusps[x] - asc_angle
        draw_spoke(draw, HOUSE_IN_RADIUS, ZODIAC_IN_RADIUS, phi, width)
        label_quad(draw, HOUSE_IN_RADIUS, HOUSE_OUT_RADIUS, phi, phi_2, str(x + 1))

    for planet, horo in horoscope.planets.items():
        phi = horo.position.abs_angle - asc_angle
        label_point(draw, PLANET_RADIUS, phi, planet)

    return img


def overlay_image(background: str, overlay: Image.Image) -> Image.Image:
    img = Image.open(background)
    size = min(img.height, img.width)
    overlay = overlay.resize((size, size))
    x = (img.width - size) // 2
    y = (img.height - size) // 2
    img.alpha_composite(overlay, (x, y))
    return img