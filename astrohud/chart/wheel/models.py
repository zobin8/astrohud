"""Models for Wheel chart"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
import math

from astrohud.chart._base.const import IMAGE_PAD
from astrohud.chart._base.const import MAX_RADIUS
from astrohud.chart._base.models import BaseChart
from astrohud.chart._base.models import BaseCoord
from astrohud.chart._base.models import XY
from astrohud.chart.shapes.models import Arc
from astrohud.chart.shapes.models import Circle
from astrohud.chart.shapes.models import Label
from astrohud.chart.shapes.models import Line
from astrohud.lib.ephemeris.enums import House
from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.horoscope.enums import Aspect
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.horoscope.const import ESSENTIAL_SCORE
from astrohud.lib.horoscope.models import Horoscope


ZODIAC_OUT_RADIUS = MAX_RADIUS * 1.0
ZODIAC_IN_RADIUS = MAX_RADIUS * 0.8


HOUSE_OUT_RADIUS = MAX_RADIUS * 0.5
HOUSE_IN_RADIUS = MAX_RADIUS * 0.4


PLANET_1_RADIUS = MAX_RADIUS * 0.7
PLANET_2_RADIUS = MAX_RADIUS * 0.6
TIP_1_RADIUS = MAX_RADIUS * 0.77
TIP_2_RADIUS = MAX_RADIUS * 0.53
TIP_RADIUS = MAX_RADIUS * 0.015
BUBBLE_RADIUS = MAX_RADIUS * 0.005
BRIDGE_RADIUS = MAX_RADIUS * 0.02
ASPECT_TIP_RADIUS = MAX_RADIUS * 0.02


NUDGE_ANGLE = 5
COLLISION_ANGLE = 5
CONJUNCTION_ANGLE = 2


# ZTODO: Move to math submodule
def close_angles(phi1: float, phi2: float) -> Tuple[float, float]:
    while phi1 - phi2 > 180:
        phi1 -= 360
    while phi2 - phi1 > 180:
        phi1 += 360

    return phi1, phi2


def find_collision(phi: float, avoid: List[float]) -> Optional[float]:
    for a in avoid:
        a, phi = close_angles(a, phi)

        if abs(a - phi) < NUDGE_ANGLE:
            return a
    return None


def nudge_coords(phi: float, avoid: List[float]) -> float:
    a = find_collision(phi, avoid)
    if a is None:
        return phi
    if a > phi:
        return a - NUDGE_ANGLE
    return a + NUDGE_ANGLE


def get_center(phi1: float, phi2: float) -> float:
    while phi1 - 180 > phi2:
        phi2 += 360
    while phi1 + 180 < phi2:
        phi2 -= 360

    return (phi1 + phi2) / 2


def compare_angles(phi1: float, phi2: float) -> float:
    a1, a2 = close_angles(phi1, phi2)
    return a1 - a2


def sort_angles(phi1: float, phi2: float) -> Tuple[float, float]:
    if compare_angles(phi1, phi2) > 0:
        return phi2, phi1
    return phi1, phi2


def check_arc_collision(arc1: Tuple[float, float], arc2: Tuple[float, float], add: float = COLLISION_ANGLE) -> bool:
    comp_start = compare_angles(arc1[1], arc2[1])
    if comp_start < 0:
        cross = compare_angles(arc1[1], arc2[0]) + add
    else:
        cross = compare_angles(arc2[1], arc1[0]) + add
    return cross > 0


class UnionFind:
    parents: Dict[Any, Any]
    members: Dict[Any, set]

    def __init__(self) -> None:
        self.parents = dict()
        self.members = dict()

    def add(self, item: Any):
        if item not in self.parents:
            self.parents[item] = item
            self.members[item] = {item}

    def find(self, item: Any) -> Any:
        parent = self.parents.get(item, None)
        if parent is None or parent == item:
            return parent
        self.parents[item] = self.find(parent)
        return self.parents[item]
    
    def union(self, item1: Any, item2: Any):
        self.add(item1)
        self.add(item2)
        item1 = self.find(item1)
        item2 = self.find(item2)

        if item1 == item2:
            return
        
        if len(self.members[item1]) < len(self.members[item2]):
            item1, item2 = item2, item1

        self.parents[item2] = item1
        self.members[item1] = self.members[item1].union(self.members.pop(item2))
# END ZTODO


@dataclass(frozen=True)
class WheelCoord(BaseCoord):
    """Class for ecliptic coordinates in wheel chart."""

    rho: float = 0  # Radius in wheel


class WheelChart(BaseChart):
    """Standard natal chart designed as an ecliptic wheel"""
    
    asc_angle: float
    main_signs: int
    signs: List[Tuple[int, Sign, float, float]]
    sign_radius: Dict[int, int]
    sign_coll: Dict[int, int]
    sign_mid_coll: Dict[int, int]
    cusps: List[Tuple[House, float]]

    def __init__(self, horoscope: Horoscope):
        """Constructor"""
        super().__init__()

        self.asc_angle = horoscope.ascending.abs_angle
        self.cusps = list(sorted([(k, v) for k, v in horoscope.houses.items()], key=lambda t: t[1]))
        self.signs = [(i, t[0], *close_angles(*sort_angles(t[1], t[2]))) for i, t in enumerate(horoscope.signs)]
        self.main_signs = len(horoscope.sign_splitter.ring[0].ring.values())
        self.sign_radius = {i: 0 for i in range(len(self.signs))}
        self.sign_coll = {i: 1 for i in range(len(self.signs))}
        self.sign_mid_coll = dict(self.sign_coll)

        self._draw_structure()
        self._draw_houses()
        self._draw_planets(horoscope)
        self._draw_aspects(horoscope)
    
    def convert_coord(self, coord: WheelCoord) -> XY:
        """Convert an ecliptic coordinate to chart XY."""

        angle = (coord.ra + 180) * math.pi / 180
        x = coord.rho * math.cos(angle)
        y = coord.rho * math.sin(angle)

        offset = MAX_RADIUS + IMAGE_PAD

        return XY(x + offset, offset - y)

    def _label_quad(self, c1: WheelCoord, c2: WheelCoord, label: Any, small: bool = False):
        """Create a label centered in a rounded quadrilateral"""

        rho = (c1.rho + c2.rho) / 2
        phi = get_center(c1.ra, c2.ra)

        self.shapes.add(Label(
            center=WheelCoord(ra=phi, rho=rho, dec=0),
            label=label,
            small=small,
        ))

    def _get_sign_collisions(self):
        """Calculate sign collisions"""
        for i, _, a, b in self.signs:
            if i < self.main_signs:
                continue
            for j, _, a2, b2 in self.signs:
                if j == i:
                    continue

                if not check_arc_collision((a, b), (a2, b2), add=0):
                    continue

                # ZTODO 2024-08-01, 2024-05-01
                self.sign_coll[j] = 2
                self.sign_coll[i] = 2
                self.sign_radius[i] = 1
                self.sign_mid_coll[i] = 2

                mid = (a2 + b2) / 2
                if check_arc_collision((a, b), (mid, mid)):
                   self.sign_mid_coll[j] = 2

    def _get_zodiac_radius(self, sign: int) -> Tuple[float, float, float]:
        """Get the inside and outside radius for a sign"""
        radius = self.sign_radius[sign]
        coll = self.sign_coll[sign]
        mid_coll = self.sign_mid_coll[sign]

        width = ZODIAC_OUT_RADIUS - ZODIAC_IN_RADIUS
        in_radius = ZODIAC_IN_RADIUS + (width * radius / coll)
        out_radius = in_radius + (width / coll)
        mid_radius = in_radius + (width / mid_coll)

        return in_radius, mid_radius, out_radius

    def _draw_structure(self):
        """Draw the general wheel structure"""

        self.shapes.add(Circle(center=WheelCoord(), edge=WheelCoord(rho=ZODIAC_OUT_RADIUS)))
        self.shapes.add(Circle(center=WheelCoord(), edge=WheelCoord(rho=ZODIAC_IN_RADIUS)))
        self.shapes.add(Circle(center=WheelCoord(), edge=WheelCoord(rho=HOUSE_OUT_RADIUS)))
        self.shapes.add(Circle(center=WheelCoord(), edge=WheelCoord(rho=HOUSE_IN_RADIUS)))

        self._get_sign_collisions()
        
        for i, sign, a, b in self.signs:
            phi = a - self.asc_angle
            phi2 = b - self.asc_angle

            in_radius, mid_radius, out_radius = self._get_zodiac_radius(i)

            c1 = WheelCoord(rho=in_radius, ra=phi)
            c2 = WheelCoord(rho=out_radius, ra=phi2)
            c3 = WheelCoord(rho=out_radius, ra=phi)
            c4 = WheelCoord(rho=in_radius, ra=phi2)
            c5 = WheelCoord(rho=mid_radius, ra=phi2)

            if self.sign_radius[i] > 0:
                self.shapes.add(Arc(c1, c4, WheelCoord()))
            
            small = self.sign_mid_coll[i] > 1
            self._label_quad(c1, c5, label=sign, small=small)
            self.shapes.add(Line(c1, c3))
            self.shapes.add(Line(c4, c2))

    def _draw_houses(self):
        """Draw segmentations for the houses"""

        next_cusps = self.cusps[1:] + [self.cusps[0]]
        spoke_labels = ['A', 'I', 'D', 'M']
        for x, cusp in enumerate(self.cusps):
            phi = cusp[1] - self.asc_angle
            phi2 = next_cusps[x][1] - self.asc_angle
            width = 8

            c1 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=phi)
            c2 = WheelCoord(rho=HOUSE_OUT_RADIUS, ra=phi2)
            c3 = WheelCoord(rho=HOUSE_OUT_RADIUS, ra=phi)
            c4 = WheelCoord(rho=ZODIAC_IN_RADIUS, ra=phi)

            if (cusp[0].value - 1) % 3 == 0:
                width = 15
                label_width = (HOUSE_OUT_RADIUS - HOUSE_IN_RADIUS) / 3
                label =  spoke_labels[(cusp[0].value - 1) // 3]

                c5 = WheelCoord(rho=HOUSE_IN_RADIUS + label_width, ra=phi)
                c6 = WheelCoord(rho=HOUSE_OUT_RADIUS - label_width, ra=phi)

                self._label_quad(c1, c3, label, small=True)
                self.shapes.add(Line(c1, c5, width=width))
                self.shapes.add(Line(c4, c6, width=width))
            else:
                self.shapes.add(Line(c1, c4))
            self._label_quad(c1, c2, str(cusp[0].value))

    def _draw_tip(self, coord: WheelCoord, direction: float):
        """Draw a small planetary position tip"""

        coord2 = WheelCoord(
            rho=coord.rho + (direction * TIP_RADIUS),
            ra=coord.ra
        )
        self.shapes.add(Line(coord, coord2))

    def _draw_planets(self, horoscope: Horoscope):
        """Draw planets to the chart"""

        placed_planets = []
        avoid = [v for _, v in self.cusps]
        for planet, horo in horoscope.planets.items():
            phi = horo.position.abs_angle - self.asc_angle
            nudge_phi = nudge_coords(horo.position.abs_angle, avoid) - self.asc_angle
            planet_radius = PLANET_1_RADIUS
            tip_radius = TIP_1_RADIUS
            if find_collision(nudge_phi, placed_planets):
                planet_radius = PLANET_2_RADIUS
                tip_radius = TIP_2_RADIUS

            signs = [i for i, s, a, b, in self.signs if s == horo.position.sign]
            sign_index = signs[0]
            if horo.position.sign != horoscope.sign_splitter.split(horo.position.abs_angle, 0):
                sign_index = signs[-1]

            in_radius, _, _ = self._get_zodiac_radius(sign_index)
            c1 = WheelCoord(rho=planet_radius, ra=nudge_phi)
            c2 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=phi)
            c3 = WheelCoord(rho=HOUSE_OUT_RADIUS, ra=phi)
            c4 = WheelCoord(rho=in_radius, ra=phi)
            c5 = WheelCoord(rho=tip_radius, ra=nudge_phi)

            label = ''
            if horo.dignity != Dignity.NORMAL:
                label += f'{ESSENTIAL_SCORE[horo.dignity][0]:+2}'
            if horo.retrograde:
                label += 'R'
            
            self.shapes.add(Label(c1, planet))
            self.shapes.add(Label(c5, label, small=True))
            self._draw_tip(c2, 1)
            self._draw_tip(c3, -1)
            self._draw_tip(c4, 1)
            placed_planets.append(nudge_phi)

    def _merge_conjunctions(self, horoscope: Horoscope) -> Dict[Planet, float]:
        """Merge aspects for conjunction planets"""

        positions = {p:  horoscope.planets[p].position.abs_angle - self.asc_angle for p in horoscope.planets}
        uf = UnionFind()
        for planets, aspect in horoscope.aspects.items():
            if aspect.aspect == Aspect.CONJUNCTION:
                uf.union(planets.planet1, planets.planet2)
        for conjoined in uf.members.values():
            anchor = positions[list(conjoined)[0]]
            conjoined_pos = [close_angles(positions[p], anchor)[0] for p in conjoined]
            avg_pos = sum(conjoined_pos) / len(conjoined_pos)

            for p in conjoined:
                positions[p] = avg_pos

        return positions

    def _draw_aspects(self, horoscope: Horoscope):
        """Draw basic aspects to the chart. Only includes conjunctions."""

        positions = self._merge_conjunctions(horoscope)

        for planets, aspect in horoscope.aspects.items():
            if aspect.aspect != Aspect.CONJUNCTION:
                continue
            
            a1 = horoscope.planets[planets.planet1].position.abs_angle - self.asc_angle
            a2 = horoscope.planets[planets.planet2].position.abs_angle - self.asc_angle
            center = positions[planets.planet1]

            c1 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=center)
            c2 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=center + CONJUNCTION_ANGLE)
            c3 = WheelCoord(rho=HOUSE_IN_RADIUS + 8, ra=a1)
            c4 = WheelCoord(rho=HOUSE_IN_RADIUS + 8, ra=a2)

            self.shapes.add(Circle(c1, c2, fill=True))
            self.shapes.add(Arc(c3, c4, center=WheelCoord()))


class ClassicWheelChart(WheelChart):
    """A wheel chart with classic aspects"""

    def _draw_aspects(self, horoscope: Horoscope):
        """Draw simple lines to denote all aspects"""

        super()._draw_aspects(horoscope)

        positions = self._merge_conjunctions(horoscope)

        for planets, aspect in horoscope.aspects.items():
            if aspect.aspect == Aspect.CONJUNCTION:
                continue

            a1 = positions[planets.planet1]
            a2 = positions[planets.planet2]

            c1 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=a1)
            c2 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=a2)
            
            self.shapes.add(Line(c1, c2))


class ModernWheelChart(WheelChart):
    """A wheel chart with modern aspects"""

    def _draw_aspect_tip(self, coord: WheelCoord, aspect: Aspect, dir: int):
        """Draw a small indicator of aspect type"""

        tip_radius = ASPECT_TIP_RADIUS
        if aspect == Aspect.TRINE:
            tip_radius *= 1.3
        
        angle_diff = dir * (tip_radius * 180 / math.pi / coord.rho)
        a = coord
        b = WheelCoord(rho=a.rho + tip_radius, ra=a.ra)
        c = WheelCoord(rho=a.rho, ra=a.ra + angle_diff)
        d = WheelCoord(rho=a.rho + tip_radius, ra=a.ra + angle_diff)
        e = WheelCoord(rho=d.rho + 3, ra=d.ra)

        if aspect == Aspect.SQUARE:
            self.shapes.add(Line(b, d))
            self.shapes.add(Line(c, d))
            self.shapes.add(Circle(d, e))
        elif aspect == Aspect.TRINE:
            self.shapes.add(Line(b, c))
        elif aspect == Aspect.OPPOSITION:
            self.shapes.add(Arc(b, c, a))

    def _get_aspect_arcs(self, positions: Dict[Planet, float], horoscope: Horoscope) -> Tuple[List[Tuple[float, float]], List[Aspect]]:
        """Get arcs for all aspects"""

        arcs = list()
        aspects = list()
        for planets, aspect in horoscope.aspects.items():
            a1 = positions[planets.planet1]
            a2 = positions[planets.planet2]

            a1, a2 = sort_angles(a1, a2)
            if aspect.aspect != Aspect.CONJUNCTION:
                arc = close_angles(a1, a2)
                if arc not in arcs:
                    arcs.append(arc)
                    aspects.append(aspect.aspect)
        return arcs, aspects

    def _get_arc_groups(self, arcs: List[Tuple[float, float]], collision_matrix: List[List[bool]]) -> List[List[int]]:
        """Create groups for arcs so they don't collide"""

        arc_order = sorted(list(range(len(arcs))), key=lambda i: arcs[i][1] - arcs[i][0])
        arc_groups: List[List[int]] = [[]]
        for i in arc_order:
            level = 0
            while sum([collision_matrix[i][j] for j in arc_groups[level]]) > 0:
                level += 1
                if level >= len(arc_groups):
                    arc_groups.append([])

            arc_groups[level].append(i)
        return arc_groups

    def _get_arc_bridged_segments(self, arcs: List[Tuple[float, float]], collision_matrix: List[List[bool]], arc_groups: List[List[int]]) -> Dict[float, List[int]]:
        """Find crossovers in arcs"""

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

    def _draw_arc_aspects(self, arcs: List[Tuple[float, float]], arc_groups: List[List[int]], aspects: List[Aspect], segments: Dict[float, List[int]]):
        """Draw arcs for aspects"""

        radius = HOUSE_IN_RADIUS
        radii = [HOUSE_IN_RADIUS]
        step_radius = HOUSE_IN_RADIUS / (len(arc_groups) + 1)
        for group in arc_groups:
            radius -= step_radius
            radii += [radius]
            for i in group:
                phi2, phi1 = arcs[i]

                c1 = WheelCoord(rho=radius, ra=phi1)
                c2 = WheelCoord(rho=radius, ra=phi2)
                c3 = WheelCoord(rho=radius + BUBBLE_RADIUS, ra=phi1)
                c4 = WheelCoord(rho=radius + BUBBLE_RADIUS, ra=phi2)

                self.shapes.add(Arc(c1, c2, WheelCoord()))
                self.shapes.add(Circle(c1, c3))
                self.shapes.add(Circle(c2, c4))
                self._draw_aspect_tip(c1, aspects[i], -1)
                self._draw_aspect_tip(c2, aspects[i], 1)

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

                        c3 = WheelCoord(rho=r1, ra=angle)
                        c4 = WheelCoord(rho=r2, ra=angle)
                        self.shapes.add(Line(c3, c4))

    def _draw_aspects(self, horoscope: Horoscope):
        """Draw all aspects with non-crossing arcs"""

        super()._draw_aspects(horoscope)

        positions = self._merge_conjunctions(horoscope)    
        arcs, aspects = self._get_aspect_arcs(positions, horoscope)

        collision_matrix = [[check_arc_collision(a1, a2) for a1 in arcs] for a2 in arcs]
        arc_groups = self._get_arc_groups(arcs, collision_matrix)

        segments = self._get_arc_bridged_segments(arcs, collision_matrix, arc_groups)
        self._draw_arc_aspects(arcs, arc_groups, aspects, segments)