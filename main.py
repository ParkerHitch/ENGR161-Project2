import stats
import math

def galToM3(gal):
    return gal / 264.2
def M3ToGal(m3):
    return m3 * 264.2
def perDayToPerSec(pDay):
    return pDay / 24 / 60 / 60

PUMP_ID = 0
FERM_ID = 1
FILT_ID = 2
DIST_ID = 3
DEHY_ID = 4

ETH_ID = 0
WAT_ID = 1
SUG_ID = 2
FIB_ID = 3

SITE3_SEGNUM = 5
SITE3_SEGMNT_LENS = [50, 20, 20, 35, 10]
SITE3_BENDS = [ [90, 90], [], [], [90, 90], [] ]

FERM_T = 0 # EFF 50
DIST_T = 0 # EFF 81
FILT_T = 0
DEHY_T = 0
PIPE_T = 0

LOCATIONS = [FERM_ID, FILT_ID, DIST_ID, DEHY_ID]

def calcMasses(segnum, locations, ferm, dist, filt, dehy):
    if len(locations) != segnum-1:
        print("ERROR")
        return
    masses = []
    for i in range(segnum):
        masses.append([0, 0, 0, 0, 0])
    masses[0] = [0, .6, .2, .2, 1]
    # for m in masses:
    #     print(m)
    # print()
    i = 0
    for type in locations:
        if type==FERM_ID:
            masses[i+1][FIB_ID] = masses[i][FIB_ID]
            masses[i+1][WAT_ID] = masses[i][WAT_ID]

            sugar_conv = masses[i][SUG_ID] * stats.FRMT_EFF[ferm]
            masses[i+1][SUG_ID] = masses[i][SUG_ID] - sugar_conv
            
            masses[i+1][ETH_ID] += sugar_conv * stats.FRMT_ETH_PER_SUG
            # Do stoich to figure out masses
        elif type==FILT_ID:
            masses[i+1][ETH_ID] = masses[i][ETH_ID]
            masses[i+1][WAT_ID] = masses[i][WAT_ID]
            masses[i+1][SUG_ID] = masses[i][SUG_ID]
            masses[i+1][FIB_ID] = masses[i][FIB_ID] * (1 - stats.FILT_EFF[filt])
        elif type==DEHY_ID:
            masses[i+1][ETH_ID] = masses[i][ETH_ID]
            masses[i+1][FIB_ID] = masses[i][FIB_ID]
            masses[i+1][SUG_ID] = masses[i][SUG_ID]
            masses[i+1][WAT_ID] = masses[i][WAT_ID] * (1 - stats.FILT_EFF[dehy])
        elif type==DIST_ID:
            masses[i+1][ETH_ID] = masses[i][ETH_ID]
            coeff = (1-stats.DIST_EFF[dist]) * masses[i][ETH_ID] / (stats.DIST_EFF[dist] * (masses[i][WAT_ID] + masses[i][FIB_ID] + masses[i][SUG_ID]))
            for j in range(1,4):
                masses[i+1][j] = masses[i][j] * coeff
        else:
            print("ERROR")
            return
        s = sum(masses[i+1])
        masses[i+1][4] = s
        # for m in masses:
        #     print(m)
        # print()
        i+=1
    return masses

# makes it such that the amount of mass is in kg
def correctMassUnits(segnum, masses, densities):
    # k * mass / dens = 100000
    # k = 100000 * dens / mass
    coeff = galToM3(100000) * densities[segnum-1] / masses[segnum-1][4]
    for i in range(len(masses)):
        masses[i] = [ms * coeff for ms in masses[i]]
    return masses

def calcDensity(mass):
    return (stats.DENS_ETH * mass[ETH_ID]/mass[4] +
            stats.DENS_WAT * mass[WAT_ID]/mass[4] +
            stats.DENS_SUG * mass[SUG_ID]/mass[4] +
            stats.DENS_FIB * mass[FIB_ID]/mass[4])

def calcVolVels(masses, densities):
    volvels = [ masses[i][4] / densities[i] for i in range(len(masses)) ]

    return volvels

def calcFluidVels(volvels, pipeType):
    a = math.pi * stats.PIPE_IND[pipeType] * stats.PIPE_IND[pipeType] / 4
    flvels = [ perDayToPerSec(volvels[i] / a) for i in range(len(volvels)) ]
    return flvels

masses = calcMasses(SITE3_SEGNUM, LOCATIONS, 0, 0, 0, 0)
# for m in masses:
#     print(m, sum(m))
# print()
densities = [calcDensity(m) for m in masses]
# densities[-1] = stats.DENS_ETH
# print(densities)

masses = correctMassUnits(SITE3_SEGNUM, masses, densities)
for m in masses:
    print(m, sum(m))
print()

volumetricVels = calcVolVels(masses, densities)
print(volumetricVels)
fluidVels = calcFluidVels(volumetricVels, PIPE_T)
print(fluidVels)
