from typing import Tuple
from typing import Union
from typing import Optional
from enum import Enum
import math
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageFont

from astrohud.astro.model import Horoscope
from astrohud.astro.enums import Sign


COLOR_ALPHA = (255, 255, 255, 0)
COLOR_BLACK = (0, 0, 0, 255)
COLOR_WHITE = (255, 255, 255, 255)


MAX_RADIUS = 1500
IMAGE_PAD = 100

ZODIAC_OUT_RADIUS = MAX_RADIUS * 1.0
ZODIAC_IN_RADIUS = MAX_RADIUS * 0.8

HOUSE_OUT_RADIUS = MAX_RADIUS * 0.5
HOUSE_IN_RADIUS = MAX_RADIUS * 0.4

PLANET_1_RADIUS = MAX_RADIUS * 0.7
PLANET_2_RADIUS = MAX_RADIUS * 0.6
TIP_RADIUS = MAX_RADIUS * 0.02

NUDGE_ANGLE = 4

FONT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'font/HackNerdFont-Regular.ttf')
IMG_FOLDER =  os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img')
BIG_FONT = ImageFont.truetype(FONT_FILE, size=96, encoding='unic')
SMALL_FONT = ImageFont.truetype(FONT_FILE, size=48, encoding='unic')


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


def label_point(draw: ImageDraw.Draw, rho: float, phi: float, label: Union[str, Enum], small: bool = False):
    xy = polar_to_xy(rho, phi)
    font = SMALL_FONT if small else BIG_FONT
    if isinstance(label, str):
        draw.text(xy, label, font=font, fill=COLOR_WHITE, anchor='mm')
    else:
        img = get_symbol(label.name).resize((150, 150))
        draw.bitmap((xy[0] - 75, xy[1] - 75), img, fill=COLOR_WHITE)


def label_quad(draw: ImageDraw.Draw, r1: float, r2: float, a1: float, a2: float, label: str, small: bool = False):
    while a1 - 180 > a2:
        a2 += 360
    while a1 + 180 < a2:
        a2 -= 360
    rho = (r1 + r2) / 2
    phi = (a1 + a2) / 2
    label_point(draw, rho, phi, label, small)


def find_collision(phi: float, avoid: float) -> Optional[float]:
    for a in avoid:
        if a - phi > 180:
            a -= 360
        if phi - a > 180:
            a += 360

        if abs(a - phi) < NUDGE_ANGLE:
            return a
    return None


def nudge_coords(phi: float, avoid: float) -> float:
    a = find_collision(phi, avoid)
    if a is None:
        return phi
    if a > phi:
        return a - NUDGE_ANGLE
    return a + NUDGE_ANGLE


def apply_outline(img: Image.Image) -> Image.Image:
    pixels = dict()
    for i, pix in enumerate(img.getdata()):
        if pix != COLOR_ALPHA:
            xy = i % img.width, i // img.width
            pixels[xy] = 0
    
    fringe = set(pixels.keys())
    while len(fringe) > 0:
        x, y = fringe.pop()
        level = pixels[(x, y)] + 1
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            xy2 = x + offset[0], y + offset[1]
            if pixels.get(xy2, 100) <= level or level > 3 or \
                xy2[0] < 0 or xy2[1] < 0 or \
                xy2[0] >= img.width or xy2[1] >= img.height:
                continue
            pixels[xy2] = level
            fringe.add(xy2)
            img.putpixel(xy2, COLOR_BLACK)

    return img


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
    spoke_labels = ['A', 'I', 'D', 'M']
    for x in range(len(cusps)):
        phi = cusps[x] - asc_angle
        phi_2 = next_cusps[x] - asc_angle
        width = 5
        if x % 3 == 0:
            width = 9
            label_width = (HOUSE_OUT_RADIUS - HOUSE_IN_RADIUS) / 3
            label_quad(draw, HOUSE_IN_RADIUS, HOUSE_OUT_RADIUS, phi, phi, spoke_labels[x // 3], True)
            draw_spoke(draw, HOUSE_OUT_RADIUS - label_width, ZODIAC_IN_RADIUS, phi, width)
            draw_spoke(draw, HOUSE_IN_RADIUS + label_width, HOUSE_IN_RADIUS, phi, width)
        else:
            draw_spoke(draw, HOUSE_IN_RADIUS, ZODIAC_IN_RADIUS, phi, width)
        label_quad(draw, HOUSE_IN_RADIUS, HOUSE_OUT_RADIUS, phi, phi_2, str(x + 1))

    placed_planets = []
    for planet, horo in horoscope.planets.items():
        phi = horo.position.abs_angle - asc_angle
        nudge_phi = nudge_coords(horo.position.abs_angle, cusps) - asc_angle
        planet_radius = PLANET_1_RADIUS
        if find_collision(nudge_phi, placed_planets):
            planet_radius = PLANET_2_RADIUS
        label_point(draw, planet_radius, nudge_phi, planet)
        draw_spoke(draw, ZODIAC_IN_RADIUS, ZODIAC_IN_RADIUS + TIP_RADIUS, phi, 5)
        draw_spoke(draw, HOUSE_OUT_RADIUS, HOUSE_OUT_RADIUS - TIP_RADIUS, phi, 5)
        placed_planets.append(nudge_phi)

    return apply_outline(img)


def overlay_image(background: str, overlay: Image.Image) -> Image.Image:
    img = Image.open(background)
    size = min(img.height, img.width)
    overlay = overlay.resize((size, size))
    x = (img.width - size) // 2
    y = (img.height - size) // 2
    img.alpha_composite(overlay, (x, y))
    return img