import mainMath as m
import stats
import datetime

def permutation(lst):

    # If lst is empty then there are no permutations
    if len(lst) == 0:
        return []
 
    # If there is only one element in lst then, only
    # one permutation is possible
    if len(lst) == 1:
        return [lst]
 
    # Find the permutations for lst if there are
    # more than 1 characters
 
    l = [] # empty list that will store current permutation
 
    # Iterate the input(lst) and calculate the permutation
    for i in range(len(lst)):
       m = lst[i]
 
       # Extract lst[i] or m from the list.  remLst is
       # remaining list
       remLst = lst[:i] + lst[i+1:]
 
       # Generating all permutations where m is first
       # element
       for p in permutation(remLst):
           l.append([m] + p)
    
    return l
    
def processString(locations, fermType, distType, filtType, dehyType):
    str = ""
    for loc in locations:
        if loc == m.FERM_ID:
            str += "Fermentor,"+stats.MECH_NAMES[fermType]+","
        if loc == m.FILT_ID:
            str += "Filter,"+stats.MECH_NAMES[filtType]+","
        if loc == m.DEHY_ID:
            str += "Dehydrator,"+stats.MECH_NAMES[dehyType]+","
        if loc == m.DIST_ID:
            str += "Distiller,"+stats.MECH_NAMES[distType]+","
    return str

def writeFailedConfig(file, num, locations, fermType, distType, filtType, dehyType, purity):
    file.write(f"{num},{processString(locations, fermType, distType, filtType, dehyType)}n/a,n/a,n/a,n/a,{purity},n/a,n/a,n/a\n")

def writeSuccessConfig(file, num, locations, fermType, distType, filtType, dehyType, pumpType, pipeDiam, pipeDff, valveFC, purity, cost, roi, volSlur):
    file.write(f"{num},{processString(locations, fermType, distType, filtType, dehyType)}{stats.PUMP_NAMES[pumpType]},{stats.PIPE_IND[pipeDiam]},{stats.PIPE_NAMES[pipeDff]},{stats.VALVE_NAMES[valveFC]},{purity},{cost},{roi},{volSlur}\n")

outFile = open("output_"+datetime.datetime.now().strftime("%d-%m_%H:%M")+".csv", "w")
outFile.write("Config Number, 1-Type, 1-Quality, 2-Type, 2-Quality, 3-Type, 3-Quality, 4-Type, 4-Quality, Pump Quality, Pipe Diameter, Pipe Quality, Valve Quality, Purity, Cost, Energy ROI, Input Slurry Vol(m3/day)\n")
i = 0

nrgOut = m.calcEnergyOut()

POSSIBLE_LOCATIONS = permutation([m.FERM_ID, m.FILT_ID, m.DIST_ID, m.DEHY_ID])
numMechConfigs = len(POSSIBLE_LOCATIONS) * len(stats.FRMT_EFF) * len(stats.DIST_EFF) * len(stats.FILT_EFF) * len(stats.FILT_EFF)
numPipeConfigs = len(stats.PIPE_IND) * len(stats.PIPE_DFF) * len(stats.VALVE_FC) * len(stats.PUMP_EFF)
totalNumConfigs = numMechConfigs * numPipeConfigs
for LOCATIONS in POSSIBLE_LOCATIONS:
    for FERM_T in range(len(stats.FRMT_EFF)):
        for DIST_T in range(len(stats.DIST_EFF)):
            for FILT_T in range(len(stats.FILT_EFF)):
                for DEHY_T in range(len(stats.FILT_EFF)):
                    masses = m.calcMasses(m.SITE3_SEGNUM, LOCATIONS, FERM_T, DIST_T, FILT_T, DEHY_T)
                   
                    purity = 0
                    if(masses[-1][m.ETH_ID] > 0):
                        purity = masses[-1][m.ETH_ID] / masses[-1][4]
                    else:
                        purity = 0

                    if(purity < 0.98):
                        writeFailedConfig(outFile,i,LOCATIONS, FERM_T,DIST_T,FILT_T,DEHY_T,purity)
                        i+=numPipeConfigs
                        print(i,"/",totalNumConfigs)
                        continue

                    densities = [m.calcDensity(mas) for mas in masses]
                    densities[-1] = stats.DENS_ETH
                    masses = m.correctMassUnits(m.SITE3_SEGNUM, masses, densities)

                    volumetricVels = m.calcVolVels(masses, densities)
                    # print("VOLVELS:", volumetricVels)
                    
                    print(i,"/",totalNumConfigs)

                    for PIPE_DIAM_T in range(len(stats.PIPE_IND)):
                        fluidVels = m.calcFluidVels(volumetricVels, PIPE_DIAM_T)
                        # print("FLUIDVELS/DAY:", fluidVels)
                        fluidVels = [m.perDayToPerSec(fv) for fv in fluidVels]
                        # print("FLUIDVELS/SEC:", fluidVels)
                        for PIPE_DFF_T in range(len(stats.PIPE_DFF)):
                            for VALVE_FC_T in range(len(stats.VALVE_FC)):
                                pipeLoss = m.calcPipeLosses(m.SITE3_SEGMNT_LENS, m.SITE3_BENDS, PIPE_DIAM_T, PIPE_DFF_T, VALVE_FC_T, fluidVels, masses, m.SITE3_WASTE_LENS, LOCATIONS)
                                machineNrg = m.totalMachineLosses(FERM_T, FILT_T, DEHY_T, DIST_T)
                                pipeCost = m.calcPipeCost(m.SITE3_SEGMNT_LENS, m.SITE3_BENDS, PIPE_DIAM_T, PIPE_DFF_T, VALVE_FC_T, m.SITE3_WASTE_LENS, LOCATIONS)
                                for PUMP_T in range(len(stats.PUMP_EFF)):
                                    pupmNrg = pipeLoss / stats.PUMP_EFF[PUMP_T]
                                    totalNrgIn = pupmNrg + machineNrg
                                    ratio = nrgOut / totalNrgIn

                                    mechCost = m.calcMechCost(LOCATIONS, PUMP_T, FERM_T, DIST_T, FILT_T, DEHY_T, volumetricVels)
                                    totalCost = pipeCost + mechCost

                                    writeSuccessConfig(outFile,i,LOCATIONS, FERM_T,DIST_T,FILT_T,DEHY_T,PUMP_T,PIPE_DIAM_T,PIPE_DFF_T,VALVE_FC_T,
                                                       purity,totalCost,ratio,volumetricVels[0])
                                    i += 1