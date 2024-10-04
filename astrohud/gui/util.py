from typing import Dict
from typing import Tuple
from typing import List
from typing import Union
from typing import Optional
from typing import Set
from enum import Enum
from collections import defaultdict
import math
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from astrohud.astro.model import Horoscope
from astrohud.astro.enums import Aspect
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Sign
from astrohud.gui.model import RenderSettings
from astrohud.gui.model import UnionFind


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
BUBBLE_RADIUS = MAX_RADIUS * 0.005
BRIDGE_RADIUS = MAX_RADIUS * 0.02


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


def draw_line(draw: ImageDraw.Draw, r1: float, r2: float, phi1: float, phi2: float, width: float):
    a = polar_to_xy(r1, phi1)
    b = polar_to_xy(r2, phi2)
    draw.line(a + b, fill=COLOR_WHITE, width=width)


def draw_chord(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float):
    a = polar_to_xy(r, phi1)
    b = polar_to_xy(r, phi2)
    draw.line(a + b, fill=COLOR_WHITE, width=width)


def draw_arc(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float):
    box_min = polar_to_xy(r * math.sqrt(2) + (width / 2), 315)
    box_max = polar_to_xy(r * math.sqrt(2) + (width / 2), 135)

    draw.arc(box_min + box_max, 180 - phi1, 180 - phi2, fill=COLOR_WHITE, width=width)


def draw_circle_cord(draw: ImageDraw.Draw, r: float, phi1: float, phi2: float, width: float, min_size: float):
    a = polar_to_xy(r, phi1)
    b = polar_to_xy(r, phi2)
    mid = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    #r2 = math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    #actual_r2 = max(r2 / 2, min_size)

    draw.circle(mid, min_size, width=width, fill=COLOR_WHITE, outline=COLOR_WHITE)


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
    if comp_start < 0:
        cross = compare_angles(arc1[0], arc2[1]) + NUDGE_ANGLE
    else:
        cross = compare_angles(arc2[0], arc1[1]) + NUDGE_ANGLE
    return cross > 0


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


def merge_conjunctions(draw: ImageDraw.Draw, horoscope: Horoscope, settings: RenderSettings) -> Dict[Planet, float]:
    positions = {p:  horoscope.planets[p].position.abs_angle - settings.asc_angle for p in horoscope.planets}
    uf = UnionFind()
    for planets, aspect in horoscope.aspects.items():
        if aspect.aspect == Aspect.CONJUNCTION:
            uf.union(planets.planet1, planets.planet2)
    for conjoined in uf.members.values():
        anchor = positions[list(conjoined)[0]]
        conjoined_pos = [close_angles(positions[p], anchor)[0] for p in conjoined]
        avg_pos = sum(conjoined_pos) / len(conjoined_pos)

        for p in conjoined:
            a2, a1 = sort_angles(positions[p], avg_pos)
            draw_arc(draw, HOUSE_IN_RADIUS - 8, a1, a2, 8)
            positions[p] = avg_pos

        draw_circle_cord(draw, HOUSE_IN_RADIUS, avg_pos, avg_pos, 8, TIP_RADIUS)
    return positions


def get_aspect_arcs(positions: Dict[Planet, float], horoscope: Horoscope) -> Tuple[List[Tuple[float, float]], List[Aspect]]:
    arcs = list()
    aspects = list()
    for planets, aspect in horoscope.aspects.items():
        a1 = positions[planets.planet1]
        a2 = positions[planets.planet2]

        a2, a1 = sort_angles(a1, a2)
        if aspect.aspect != Aspect.CONJUNCTION:
            arc = close_angles(a1, a2)
            if arc not in arcs:
                arcs.append(arc)
                aspects.append(aspect.aspect)
    return arcs, aspects


def get_arc_groups(arcs: List[Tuple[float, float]], collision_matrix: List[List[bool]]) -> List[List[int]]:
    arc_order = sorted(list(range(len(arcs))), key=lambda i: arcs[i][0] - arcs[i][1])
    arc_groups: List[List[int]] = [[]]
    for i in arc_order:
        level = 0
        while sum([collision_matrix[i][j] for j in arc_groups[level]]) > 0:
            level += 1
            if level >= len(arc_groups):
                arc_groups.append([])

        arc_groups[level].append(i)
    return arc_groups


def get_arc_bridged_segments(arcs: List[Tuple[float, float]], collision_matrix: List[List[bool]], arc_groups: List[List[int]]) -> Dict[float, List[int]]:
    segments: Dict[float, List[int]] = defaultdict(list)
    for level, group in enumerate(arc_groups):
        for i in group:
            for level2 in range(level):
                for j in arc_groups[level2]:
                    if collision_matrix[i][j]:
                        for spoke in arcs[i]:
                            if abs(compare_angles(spoke, arcs[j][0])) < 0.1:
                                continue
                            if abs(compare_angles(spoke, arcs[j][1])) < 0.1:
                                continue
                            if(check_arc_collision(arcs[j], (spoke, spoke))):
                                segments[spoke].append(level2 + 1)
    return segments


def draw_arc_aspects(draw: ImageDraw.Draw, arcs: List[Tuple[float, float]], arc_groups: List[List[int]], aspects: List[Aspect], segments: Dict[float, List[int]]):
    radius = HOUSE_IN_RADIUS
    radii = [HOUSE_IN_RADIUS]
    step_radius = HOUSE_IN_RADIUS / (len(arc_groups) + 1)
    for group in arc_groups:
        radius -= step_radius
        radii += [radius]
        for i in group:
            phi1, phi2 = arcs[i]
            draw_arc(draw, radius, phi1, phi2, 8)
            draw_circle_cord(draw, radius, phi1, phi1, 8, BUBBLE_RADIUS)
            draw_circle_cord(draw, radius, phi2, phi2, 8, BUBBLE_RADIUS)

            #if aspects[i] == Aspect.TRINE:
            #    draw_line(draw, radius, radius - )

            for angle in arcs[i]:
                parts = [0] + sorted(set(segments[angle])) + [-1]
                for l1, l2 in zip(parts[:-1], parts[1:]):
                    if l2 >= len(radii):
                        break
                    r1 = radii[l1]
                    r2 = radii[l2]
                    if r1 != HOUSE_IN_RADIUS:
                        r1 -= min(BRIDGE_RADIUS, step_radius / 4)
                    if r2 != radius:
                        r2 += min(BRIDGE_RADIUS, step_radius / 4)
                    draw_spoke(draw, r1, r2, angle, 8)


def draw_improved_aspects(draw: ImageDraw.Draw, horoscope: Horoscope, settings: RenderSettings):
    positions = merge_conjunctions(draw, horoscope, settings)    
    arcs, aspects = get_aspect_arcs(positions, horoscope)

    collision_matrix = [[check_arc_collision(a1, a2) for a1 in arcs] for a2 in arcs]
    arc_groups = get_arc_groups(arcs, collision_matrix)

    segments = get_arc_bridged_segments(arcs, collision_matrix, arc_groups)
    draw_arc_aspects(draw, arcs, arc_groups, aspects, segments)


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