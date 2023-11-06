import stats
import math

def galToM3(gal):
    return gal / 264.2
def M3ToGal(m3):
    return m3 * 264.2
def perDayToPerHour(pDay):
    return pDay / 24
def perDayToPerSec(pDay):
    return pDay / 24 / 60 / 60
def getAngIndex(ang):
    if ang == 90:
        return 5
    elif ang == 75:
        return 4
    elif ang == 60:
        return 3
    elif ang == 45:
        return 2
    elif ang == 30:
        return 1
    elif ang == 20:
        return 0
    return -1
def ftToM(arrayOfM):
    return [0.3048 * m for m in arrayOfM]
def angToPLC(ang):
    return stats.BEND_PLC[getAngIndex(ang)]
def kWHtoJ(KWH):
    return KWH * 3.6e6

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
SITE3_SEGMNT_LENS = ftToM([15, 10, 10, 10, 60])
SITE3_WASTE_LENS = ftToM([10,10,10,10])
SITE3_BENDS = [ [90], [], [], [], [90] ]
# SITE3_SEGMNT_LENS = ftToM([50, 0, 0, 10, 0])
# SITE3_BENDS = [ [90, 90], [], [], [90, 90], [] ]

LOCATIONS = [FERM_ID, FILT_ID, DIST_ID, DEHY_ID]
FERM_T = 0 # EFF 50
DIST_T = 0 # EFF 81
FILT_T = 0
DEHY_T = 0
PUMP_T = 0
PIPE_DIAM_T = 0
PIPE_DFF_T = 3
VALVE_FC_T = 0

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
            
            masses[i+1][ETH_ID] = sugar_conv * stats.FRMT_ETH_PER_SUG
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

# makes it such that the amount of mass is in kg per day
def correctMassUnits(segnum, masses, densities):
    # k * mass / dens = 100000
    # k = 100000 * dens / mass
    coeff = galToM3(100000) * densities[segnum-1] / masses[segnum-1][4]
    for i in range(len(masses)):
        masses[i] = [ms * coeff for ms in masses[i]]
    return masses

# kg / m3
def calcDensity(mass):
    return (stats.DENS_ETH * mass[ETH_ID]/mass[4] +
            stats.DENS_WAT * mass[WAT_ID]/mass[4] +
            stats.DENS_SUG * mass[SUG_ID]/mass[4] +
            stats.DENS_FIB * mass[FIB_ID]/mass[4])

# m3 / day
def calcVolVels(masses, densities):
    volvels = [ masses[i][4] / densities[i] for i in range(len(masses)) ]
    return volvels

# m / day
def calcFluidVels(volvels, pipeType):
    a = math.pi * stats.PIPE_IND[pipeType] * stats.PIPE_IND[pipeType] / 4
    flvels = [ (volvels[i] / a) for i in range(len(volvels)) ]
    return flvels

def calcEnergyOut():
    return (100000 * stats.ETH_NGR_DENS)

# joules per day
def calcPipeLosses(segLens, bends, pipediam, pipedff, valveType, fluidvels, masses, wasteLens, locations):
    
    # nrgReleased = (masses[-1][ETH_ID] / stats.ETH_MOLAR_MASS) * stats.FRMT_NRG_RELEASED_PER_MOL

    losses = 0
    for i in range(len(segLens)):

        v2 = fluidvels[i] * fluidvels[i]
        # print("V^2", v2)

        # Note that gravity has been factored out of all of these head losses 
        # as it would be superficial because it cancels when we convert to energy
        H_pipefriction = (stats.PIPE_DFF[pipedff] * segLens[i] * v2) / (stats.PIPE_IND[pipediam] * 2 )

        # print(H_pipefriction / stats.GRAV)

        H_bends = 0
        for ang in bends[i]:
            H_bends += (angToPLC(ang) * v2) / (2)

        # print(H_bends / stats.GRAV)

        H_valve = (stats.VALVE_FC[valveType] * v2) / (2)
        H_valve *= 1 if (i==0 or i==len(segLens)-1) else 2 # only do 1 valve if 1st or last segment

        # print(H_valve / stats.GRAV)

        # Should be in jouls per day as masses is measured in kg per day
        losses += masses[i][4] * (H_pipefriction + H_bends + H_valve)

    for i in range(len(wasteLens)):
        if locations[i]==FERM_ID: # CO2 is negligible
            continue
        H_pipefriction = (stats.PIPE_DFF[pipedff] * wasteLens[i] * v2) / (stats.PIPE_IND[pipediam] * 2 )
        losses += (masses[i+1][4]-masses[i][4]) * -H_pipefriction
    
    return losses

def totalMachineLosses(fermT, flitT, dehyT, distT):
    return kWHtoJ(  stats.FERM_KWH[fermT] + 
                    stats.FILT_KWH[flitT] +
                    stats.FILT_KWH[dehyT] +
                    stats.DIST_KWH[distT] )
    
def calcPipeCost(segLens, bends, pipeDiamType, pipeFricType, valveType, wasteLens, locations):
    cost = 0
    for i in range(len(segLens)):
        cost += segLens[i] * stats.PIPE_CPM_MTRX[pipeFricType][pipeDiamType]
        for bend in bends[i]:
            cost += stats.BEND_CPB_MTRX[getAngIndex(bend)][pipeDiamType]
        cost += 8 * stats.VALVE_CPV_MTRX[valveType][pipeDiamType]
    for i in range(len(wasteLens)):
        if(locations[i]==FERM_ID):
            cost += wasteLens[i] * stats.DUCT_CPM[0]
        else:
            cost += wasteLens[i] * stats.PIPE_CPM_MTRX[pipeFricType][pipeDiamType]
    return cost

def calcMechCost(locations, pumpType, fermType, distType, filtType, dehyType, volVels):
    cost = perDayToPerHour(volVels[0]) * stats.PUMP_CPM_MTRX[pumpType][0]
    i = 0
    for loc in locations:
        if loc==FERM_ID:
            cost += perDayToPerHour(volVels[i]) * stats.FRMT_CPH[fermType]
        elif loc==FILT_ID:
            cost += perDayToPerHour(volVels[i]) * stats.FILT_CPH[filtType]
        elif loc==DEHY_ID:
            cost += perDayToPerHour(volVels[i]) * stats.FILT_CPH[dehyType]
        elif loc==DIST_ID:
            cost += perDayToPerHour(volVels[i]) * stats.DIST_CPH[distType]
        else:
            print("ERROR")
            return
        i+=1
    return cost

if __name__ == "__main__":
    masses = calcMasses(SITE3_SEGNUM, LOCATIONS, 0, 0, 0, 0)
    # for m in masses:
    #     print(m, sum(m))
    # print()
    densities = [calcDensity(m) for m in masses]
    densities[-1] = stats.DENS_ETH
    # print(densities)

    masses = correctMassUnits(SITE3_SEGNUM, masses, densities)
    for m in masses:
        print(m, sum(m))
    print()

    out = calcEnergyOut()
    print("OUT:", out, "J")

    volumetricVels = calcVolVels(masses, densities)
    print("VOLVELS:", volumetricVels)
    fluidVels = calcFluidVels(volumetricVels, PIPE_DIAM_T)
    print("FLUIDVELS/DAY:", fluidVels)
    fluidVels = [perDayToPerSec(fv) for fv in fluidVels]
    print("FLUIDVELS/SEC:", fluidVels)

    pipeLoss = calcPipeLosses(SITE3_SEGMNT_LENS, SITE3_BENDS, PIPE_DIAM_T, PIPE_DFF_T, VALVE_FC_T, fluidVels, masses, SITE3_WASTE_LENS, LOCATIONS)
    pupmNrg = pipeLoss / stats.PUMP_EFF[PUMP_T]
    machineNrg = totalMachineLosses(FERM_T, FILT_T, DEHY_T, DIST_T)
    totalNrgIn = pupmNrg + machineNrg
    ratio = out / totalNrgIn
    print(ratio)

    pipeCost = calcPipeCost(SITE3_SEGMNT_LENS, SITE3_BENDS, PIPE_DIAM_T, PIPE_DFF_T, VALVE_FC_T, SITE3_WASTE_LENS, LOCATIONS)
    mechCost = calcMechCost(LOCATIONS, PUMP_T, FERM_T, DIST_T, FILT_T, DEHY_T, volumetricVels)
    print(pipeCost, "<pipe|mech>",mechCost)
    print("Total Cost: ", pipeCost+mechCost)