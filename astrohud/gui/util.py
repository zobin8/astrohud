from typing import Tuple
from typing import List
from typing import Union
from typing import Optional
from typing import Set
from enum import Enum
import math
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from astrohud.astro.model import Horoscope
from astrohud.astro.enums import Aspect
from astrohud.astro.enums import Sign
from astrohud.gui.model import RenderSettings


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
TIP_RADIUS = MAX_RADIUS * 0.015


NUDGE_ANGLE = 4


FONT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'font/HackNerdFont-Regular.ttf')
IMG_FOLDER =  os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img')
BIG_FONT = ImageFont.truetype(FONT_FILE, size=96, encoding='unic')
SMALL_FONT = ImageFont.truetype(FONT_FILE, size=48, encoding='unic')


def get_symbol(name: str) -> Image.Image:
    img = Image.open(os.path.join(IMG_FOLDER, f'{name.lower()}.png'))

    return img.convert('RGBA').resize((150, 150))


def polar_to_xy(rho: float, phi: float) -> Tuple[float, float]:
    angle = (phi + 180) * math.pi / 180
    x = rho * math.cos(angle)
    y = rho * math.sin(angle)

    offset = MAX_RADIUS + IMAGE_PAD

    return (x + offset, offset - y)


def draw_circle(draw: ImageDraw.Draw, radius: float):
    draw.circle(polar_to_xy(0, 0), radius, width=8, outline=COLOR_WHITE)


def draw_spoke(draw: ImageDraw.Draw, r1: float, r2: float, phi: float, width: float):
    a = polar_to_xy(r1, phi)
    b = polar_to_xy(r2, phi)
    draw.line(a + b, fill=COLOR_WHITE, width=width)


def draw_chord(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float):
    a = polar_to_xy(r, phi1)
    b = polar_to_xy(r, phi2)
    draw.line(a + b, fill=COLOR_WHITE, width=width)


def draw_arc(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float):
    box_min = polar_to_xy(r * math.sqrt(2), 315)
    box_max = polar_to_xy(r * math.sqrt(2), 135)
    draw.arc(box_min + box_max, phi1 + 180, phi2 + 180, fill=COLOR_WHITE, width=width)


def draw_circle_cord(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float):
    a = polar_to_xy(r, phi1)
    b = polar_to_xy(r, phi2)
    mid = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    r2 = math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    draw.circle(mid, max(r2 / 2, TIP_RADIUS), width=width, fill=COLOR_WHITE, outline=COLOR_WHITE)


def label_point(draw: ImageDraw.Draw, rho: float, phi: float, label: Union[str, Enum], small: bool = False):
    xy = polar_to_xy(rho, phi)
    font = SMALL_FONT if small else BIG_FONT
    if isinstance(label, str):
        draw.text(xy, label, font=font, fill=COLOR_WHITE, anchor='mm')
    else:
        img = get_symbol(label.name)
        draw.bitmap((xy[0] - (img.width / 2), xy[1] - (img.width / 2)), img, fill=COLOR_WHITE)


def label_quad(draw: ImageDraw.Draw, r1: float, r2: float, a1: float, a2: float, label: str, small: bool = False):
    while a1 - 180 > a2:
        a2 += 360
    while a1 + 180 < a2:
        a2 -= 360
    rho = (r1 + r2) / 2
    phi = (a1 + a2) / 2
    label_point(draw, rho, phi, label, small)


def close_angles(phi1: float, phi2: float) -> Tuple[float, float]:
    while phi1 - phi2 > 180:
        phi1 -= 360
    while phi2 - phi1 > 180:
        phi1 += 360

    return phi1, phi2


def compare_angles(phi1: float, phi2: float) -> float:
    a1, a2 = close_angles(phi1, phi2)
    return a1 - a2


def sort_angles(phi1: float, phi2: float) -> Tuple[float, float]:
    if compare_angles(phi1, phi2) > 0:
        return phi2, phi1
    return phi1, phi2


def find_collision(phi: float, avoid: List[float]) -> Optional[float]:
    for a in avoid:
        a, phi = close_angles(a, phi)

        if abs(a - phi) < NUDGE_ANGLE:
            return a
    return None


def check_arc_collision(arc1: Tuple[float, float], arc2: Tuple[float, float]) -> bool:
    comp_start = compare_angles(arc1[0], arc2[0])
    if comp_start > 0:
        cross = compare_angles(arc1[0], arc2[1]) - NUDGE_ANGLE
    else:
        cross = compare_angles(arc2[0], arc1[1]) - NUDGE_ANGLE
    return cross < 0


def nudge_coords(phi: float, avoid: float) -> float:
    a = find_collision(phi, avoid)
    if a is None:
        return phi
    if a > phi:
        return a - NUDGE_ANGLE
    return a + NUDGE_ANGLE


def get_pixels(img: Image.Image) -> Set[Tuple[int, int]]:
    pixels = set()
    for i, pix in enumerate(img.getdata()):
        if pix != COLOR_ALPHA:
            xy = i % img.width, i // img.width
            pixels.add(xy)
    return pixels


def apply_outline(img: Image.Image) -> Image.Image:
    pixels = {xy: 0 for xy in get_pixels(img)}
    
    fringe = set(pixels.keys())
    while len(fringe) > 0:
        x, y = fringe.pop()
        level = pixels[(x, y)] + 1
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            xy2 = x + offset[0], y + offset[1]
            if pixels.get(xy2, 100) <= level or level > 5 or \
                xy2[0] < 0 or xy2[1] < 0 or \
                xy2[0] >= img.width or xy2[1] >= img.height:
                continue
            pixels[xy2] = level
            fringe.add(xy2)
            img.putpixel(xy2, COLOR_BLACK)

    return img


def draw_structure(draw: ImageDraw.Draw, settings: RenderSettings):
    draw_circle(draw, ZODIAC_OUT_RADIUS)
    draw_circle(draw, ZODIAC_IN_RADIUS)
    draw_circle(draw, HOUSE_OUT_RADIUS)
    draw_circle(draw, HOUSE_IN_RADIUS)
    
    for x in range(12):
        phi = (x * 30) - settings.asc_angle
        draw_spoke(draw, ZODIAC_IN_RADIUS, ZODIAC_OUT_RADIUS, phi, 8)
        label_quad(draw, ZODIAC_IN_RADIUS, ZODIAC_OUT_RADIUS, phi, phi + 30, Sign(x))


def draw_houses(draw: ImageDraw.Draw, settings: RenderSettings):
    next_cusps = settings.cusps[1:] + [settings.cusps[0]]
    spoke_labels = ['A', 'I', 'D', 'M']
    for x in range(len(settings.cusps)):
        phi = settings.cusps[x] - settings.asc_angle
        phi_2 = next_cusps[x] - settings.asc_angle
        width = 8
        if x % 3 == 0:
            width = 15
            label_width = (HOUSE_OUT_RADIUS - HOUSE_IN_RADIUS) / 3
            label_quad(draw, HOUSE_IN_RADIUS, HOUSE_OUT_RADIUS, phi, phi, spoke_labels[x // 3], True)
            draw_spoke(draw, HOUSE_OUT_RADIUS - label_width, ZODIAC_IN_RADIUS, phi, width)
            draw_spoke(draw, HOUSE_IN_RADIUS + label_width, HOUSE_IN_RADIUS, phi, width)
        else:
            draw_spoke(draw, HOUSE_IN_RADIUS, ZODIAC_IN_RADIUS, phi, width)
        label_quad(draw, HOUSE_IN_RADIUS, HOUSE_OUT_RADIUS, phi, phi_2, str(x + 1))


def draw_planets(draw: ImageDraw.Draw, horoscope: Horoscope, settings: RenderSettings):
    placed_planets = []
    for planet, horo in horoscope.planets.items():
        phi = horo.position.abs_angle - settings.asc_angle
        nudge_phi = nudge_coords(horo.position.abs_angle, settings.cusps) - settings.asc_angle
        planet_radius = PLANET_1_RADIUS
        if find_collision(nudge_phi, placed_planets):
            planet_radius = PLANET_2_RADIUS
        label_point(draw, planet_radius, nudge_phi, planet)
        draw_spoke(draw, ZODIAC_IN_RADIUS, ZODIAC_IN_RADIUS + TIP_RADIUS, phi, 8)
        draw_spoke(draw, HOUSE_OUT_RADIUS, HOUSE_OUT_RADIUS - TIP_RADIUS, phi, 8)
        draw_spoke(draw, HOUSE_IN_RADIUS, HOUSE_IN_RADIUS + TIP_RADIUS, phi, 8)
        placed_planets.append(nudge_phi)


def draw_classic_aspects(draw: ImageDraw.Draw, horoscope: Horoscope, settings: RenderSettings):
    for planets, aspect in horoscope.aspects.items():
        a1 = horoscope.planets[planets.planet1].position.abs_angle - settings.asc_angle
        a2 = horoscope.planets[planets.planet2].position.abs_angle - settings.asc_angle

        r = HOUSE_IN_RADIUS
        if aspect.aspect == Aspect.CONJUNCTION:
            draw_circle_cord(draw, r, a1, a2, 8)
        else:
            draw_chord(draw, r, a1, a2, 8)


def draw_improved_aspects(draw: ImageDraw.Draw, horoscope: Horoscope, settings: RenderSettings):
    arcs = list()
    for planets, aspect in horoscope.aspects.items():
        a1 = horoscope.planets[planets.planet1].position.abs_angle - settings.asc_angle
        a2 = horoscope.planets[planets.planet2].position.abs_angle - settings.asc_angle

        if aspect.aspect == Aspect.CONJUNCTION:
            draw_circle_cord(draw, HOUSE_IN_RADIUS, a1, a2, 8)
        else:
            a1, a2 = sort_angles(-a1, -a2)
            arcs.append((a1, a2))

    collision_matrix = [[check_arc_collision(a1, a2) for a1 in arcs] for a2 in arcs]
    #collisions = sorted(enumerate([sum(row) for row in collision_matrix]), key=lambda t: t[1])
    remaining_arcs = list(range(len(arcs)))
    arc_order = sorted(remaining_arcs, key=lambda i: arcs[i][0] - arcs[i][1])
    arc_groups = []
    for i in arc_order:
        group = [i]
        if i not in remaining_arcs:
            continue
        remaining_arcs.remove(i)
        for j in remaining_arcs:
            if sum(collision_matrix[k][j] for k in group) == 0:
                remaining_arcs.remove(j)
                group.append(j)
        arc_groups.append(group)

    radius = HOUSE_IN_RADIUS
    for group in arc_groups:
        radius -= HOUSE_IN_RADIUS / (len(arc_groups) + 1)
        for i in group:
            phi1, phi2 = arcs[i]
            draw_arc(draw, radius, phi1, phi2, 8)
            draw_spoke(draw, HOUSE_IN_RADIUS, radius, -phi1, 8)
            draw_spoke(draw, HOUSE_IN_RADIUS, radius, -phi2, 8)


def draw_horoscope(horoscope: Horoscope) -> Image.Image:
    width = (MAX_RADIUS + IMAGE_PAD) * 2 + 1
    img = Image.new("RGBA", (width, width), COLOR_ALPHA)
    draw = ImageDraw.Draw(img)
    asc_angle = horoscope.ascending.abs_angle
    cusps = [horoscope.cusps[h] for h in sorted(horoscope.cusps.keys(), key=lambda x: x.value)]

    settings = RenderSettings(
        asc_angle=asc_angle,
        cusps=cusps,
    )

    draw_structure(draw, settings)
    draw_houses(draw, settings)
    draw_planets(draw, horoscope, settings)
    #draw_classic_aspects(draw, horoscope, settings)
    draw_improved_aspects(draw, horoscope, settings)

    return apply_outline(img)


def overlay_image(background: str, overlay: Image.Image) -> Image.Image:
    img = Image.open(background)
    size = min(img.height, img.width)
    overlay = overlay.resize((size, size))
    x = (img.width - size) // 2
    y = (img.height - size) // 2
    img.alpha_composite(overlay, (x, y))
    return img