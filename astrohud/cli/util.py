from astrohud.lib.horoscope.models import Horoscope


def print_horoscope(horoscope: Horoscope):
    divider = ['=' * 20] * 8

    # Planets
    table = [['Planet', 'Sign', 'House', 'Dignity', 'RA', 'Dec', 'Speed', 'Score', ]]
    table.append(divider)
    for planet, signHoro in horoscope.planets.items():
        signPos = signHoro.position
        table.append([
            planet.name,
            f'{signPos.sign.name} {signPos.face}',
            signPos.house.name,
            signHoro.dignity.name,
            f'{signPos.abs_angle:4.1f}°',
            f'{signPos.declination:4.1f}°',
            f'{signPos.speed:+6.2f} deg/day',
            f'{signHoro.score:+03}',
        ])

    table.append([
        'Ascending',
        f'{horoscope.ascending.sign.name} {horoscope.ascending.face}',
        horoscope.ascending.house.name,
        '',
        f'{horoscope.ascending.abs_angle:4.1f}°',
        ''
    ])

    # Middle
    table.append([])

    # Aspects
    table.append(['Planet 1', 'Planet 2', 'Aspect', 'Orb'])
    table.append(divider)
    for planets, aspectHoro in horoscope.aspects.items():
        table.append([
            planets.planet1.name,
            planets.planet2.name,
            aspectHoro.aspect.name,
            f'{aspectHoro.orb:4.1f}°'
        ])

    # Display
    for row in table:
        row = [f'{cell:<20}' for cell in row]
        print(''.join(row))

