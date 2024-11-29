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
from astrohud.lib.math.models import Angle
from astrohud.lib.math.models import AngleSegment
from astrohud.lib.math.models import UnionFind

from .enums import Collision


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
# END ZTODO


@dataclass(frozen=True)
class WheelCoord(BaseCoord):
    """Class for ecliptic coordinates in wheel chart."""

    rho: float = 0  # Radius in wheel


@dataclass
class CollisionState:
    """Class for the collision state of a sign.
    """

    begin: Collision = Collision.NONE    # For beginning of arc
    middle: Collision = Collision.NONE   # For symbol in the middle of the arc
    end: Collision = Collision.NONE      # For end of arc


class WheelChart(BaseChart):
    """Standard natal chart designed as an ecliptic wheel"""
    
    asc_angle: float
    main_signs: int
    signs: List[Tuple[int, Sign, float, float]]
    sign_collisions: Dict[int, CollisionState]
    cusps: List[Tuple[House, float]]

    def __init__(self, horoscope: Horoscope):
        """Constructor"""
        super().__init__()

        self.asc_angle = horoscope.ascending.abs_angle
        self.cusps = list(sorted([(k, v) for k, v in horoscope.houses.items()], key=lambda t: t[1]))
        self.signs = [(i, t[0], *close_angles(*sort_angles(t[1], t[2]))) for i, t in enumerate(horoscope.signs)]
        self.main_signs = len(horoscope.sign_splitter.ring[0].ring.values())
        self.sign_collisions = defaultdict(CollisionState)

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
        phi = Angle(c1.ra).average(Angle(c2.ra)).value

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

            self.sign_collisions[i] = CollisionState(
                Collision.OUTER,
                Collision.OUTER,
                Collision.OUTER,
            )

            for j, _, a2, b2 in self.signs:
                if j == i:
                    continue

                mid = (a2 + b2) / 2

                if check_arc_collision((a, b), (a2, a2), add=0):
                    self.sign_collisions[j].begin = Collision.INNER
                if check_arc_collision((a, b), (b2, b2), add=0):
                    self.sign_collisions[j].end = Collision.INNER
                if check_arc_collision((a, b), (mid, mid), add=COLLISION_ANGLE):
                   self.sign_collisions[j].middle = Collision.INNER

    def _get_zodiac_radius(self, coll: Collision) -> Tuple[float, float]:
        """Get the inside and outside radius for a sign"""
        radius = 1 if coll == Collision.OUTER else 0
        total = 1 if coll == Collision.NONE else 2

        width = ZODIAC_OUT_RADIUS - ZODIAC_IN_RADIUS
        in_radius = ZODIAC_IN_RADIUS + (width * radius / total)
        out_radius = in_radius + (width / total)

        return in_radius, out_radius

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

            r_in_begin, r_out_begin = self._get_zodiac_radius(self.sign_collisions[i].begin)
            r_in_mid, r_out_mid = self._get_zodiac_radius(self.sign_collisions[i].middle)
            r_in_end, r_out_end = self._get_zodiac_radius(self.sign_collisions[i].end)

            c1_begin = WheelCoord(rho=r_in_begin, ra=phi)
            c2_begin = WheelCoord(rho=r_out_begin, ra=phi)
            c1_mid = WheelCoord(rho=r_in_mid, ra=phi)
            c2_mid = WheelCoord(rho=r_out_mid, ra=phi2)
            c1_end = WheelCoord(rho=r_in_end, ra=phi2)
            c2_end = WheelCoord(rho=r_out_end, ra=phi2)
            
            if self.sign_collisions[i].middle == Collision.OUTER:
                self.shapes.add(Arc(c1_begin, c1_end, WheelCoord()))

            small = self.sign_collisions[i].middle != Collision.NONE
            self._label_quad(c1_mid, c2_mid, label=sign, small=small)
            self.shapes.add(Line(c1_begin, c2_begin))
            self.shapes.add(Line(c1_end, c2_end))

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

            in_radius, _ = self._get_zodiac_radius(self.sign_collisions[sign_index].middle)
            c1 = WheelCoord(rho=planet_radius, ra=nudge_phi)
            c2 = WheelCoord(rho=HOUSE_IN_RADIUS, ra=phi)
            c3 = WheelCoord(rho=HOUSE_OUT_RADIUS, ra=phi)
            c4 = WheelCoord(rho=in_radius, ra=phi)
            c5 = WheelCoord(rho=tip_radius, ra=nudge_phi)

            label = ''
            if horo.dignity != Dignity.NORMAL:
                label += f'{ESSENTIAL_SCORE[horo.dignity][0]:1}'
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

    def _get_aspect_arcs(self, positions: Dict[Planet, float], horoscope: Horoscope) -> Tuple[List[AngleSegment], List[Aspect]]:
        """Get arcs for all aspects"""

        arcs = list()
        aspects = list()
        for planets, aspect in horoscope.aspects.items():
            a1 = positions[planets.planet1]
            a2 = positions[planets.planet2]

            if aspect.aspect != Aspect.CONJUNCTION:
                arc = AngleSegment(a1, a2)
                if arc not in arcs:
                    arcs.append(arc)
                    aspects.append(aspect.aspect)
        return arcs, aspects

    def _get_arc_groups(self, arcs: List[AngleSegment], collision_matrix: List[List[bool]]) -> List[List[int]]:
        """Create groups for arcs so they don't collide"""

        arc_order = sorted(list(range(len(arcs))), key=lambda i: arcs[i].length())
        arc_groups: List[List[int]] = [[]]
        for i in arc_order:
            level = 0
            while sum([collision_matrix[i][j] for j in arc_groups[level]]) > 0:
                level += 1
                if level >= len(arc_groups):
                    arc_groups.append([])

            arc_groups[level].append(i)
        return arc_groups

    def _get_arc_bridged_segments(self, arcs: List[AngleSegment], collision_matrix: List[List[bool]], arc_groups: List[List[int]]) -> Dict[Angle, List[int]]:
        """Find crossovers in arcs"""

        segments: Dict[Angle, List[int]] = defaultdict(list)
        for level, group in enumerate(arc_groups):
            for i in group:
                for level2 in range(level):
                    for j in arc_groups[level2]:
                        if collision_matrix[i][j]:
                            for spoke in arcs[i]:
                                if spoke.distance(arcs[j].a1) < 0.1:
                                    continue
                                if spoke.distance(arcs[j].a2) < 0.1:
                                    continue
                                if arcs[j].check_collision(spoke, limit=COLLISION_ANGLE):
                                    segments[spoke].append(level2 + 1)
        return segments

    def _draw_arc_aspects(self, arcs: List[AngleSegment], arc_groups: List[List[int]], aspects: List[Aspect], segments: Dict[Angle, List[int]]):
        """Draw arcs for aspects"""

        radius = HOUSE_IN_RADIUS
        radii = [HOUSE_IN_RADIUS]
        step_radius = HOUSE_IN_RADIUS / (len(arc_groups) + 1)
        for group in arc_groups:
            radius -= step_radius
            radii += [radius]
            for i in group:
                phi2, phi1 = arcs[i].a1.value, arcs[i].a2.value

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

                        c3 = WheelCoord(rho=r1, ra=angle.value)
                        c4 = WheelCoord(rho=r2, ra=angle.value)
                        self.shapes.add(Line(c3, c4))

    def _draw_aspects(self, horoscope: Horoscope):
        """Draw all aspects with non-crossing arcs"""

        super()._draw_aspects(horoscope)

        positions = self._merge_conjunctions(horoscope)    
        arcs, aspects = self._get_aspect_arcs(positions, horoscope)

        collision_matrix = [[a1.check_collision(a2, limit=COLLISION_ANGLE) for a1 in arcs] for a2 in arcs]
        arc_groups = self._get_arc_groups(arcs, collision_matrix)

        segments = self._get_arc_bridged_segments(arcs, collision_matrix, arc_groups)
        self._draw_arc_aspects(arcs, arc_groups, aspects, segments)