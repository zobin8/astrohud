import swisseph as swe
import time
from datetime import datetime, timedelta

FORMAT = '%Y-%m-%dT%H:%M:%S%z'
date = datetime.strptime(time.strftime(FORMAT, time.localtime()),FORMAT)
LOCALTIMEDIFF = timedelta(hours = int(date.tzname()[3:6]))

swe.set_ephe_path('submodules/swisseph')

SIGNKEY=(
    'Aries', #0
    'Taurus', #1
    'Gemini', #2
    'Cancer', #3
    'Leo', #4
    'Virgo', #5
    'Libra', #6
    'Scorpio', #7
    'Sagittarius', #8
    'Capricorn', #9
    'Aquarius', #10
    'Pisces' #11
)

PLANETKEY=(
    'Sun', #0
    'Moon', #1
    'Mercury', #2
    'Venus', #3
    'Mars', #4
    'Jupiter', #5
    'Saturn', #6
    'Uranus', #7
    'Neptune', #8
    'Pluto', #9
)

def getPlanetPositions(dt):
    dt_tup = dt.timetuple()[:6]
    jt = swe.utc_to_jd(*dt_tup,swe.GREG_CAL)
    planetPos = list(swe.calc_ut(jt[1], i, flags=swe.FLG_SPEED) for i in range(len(PLANETKEY)))
    planetSigns = list(swe.split_deg(planetPos[i][0][0],8) for i in range(len(planetPos)))

    return planetPos, planetSigns

def printPlanetPositions(dt):
    planetPos, planetSigns = getPlanetPositions(dt)
    for i in range(len(PLANETKEY)):
        print(PLANETKEY[i]+':',str(planetSigns[i][0])+'°',str(planetSigns[i][1])+"'"+\
        str(planetSigns[i][2])+'"',SIGNKEY[planetSigns[i][4]],'   speed:',round(planetPos[i][0][3],3),'deg/day')

printPlanetPositions(datetime.utcnow())
print('♈︎')
