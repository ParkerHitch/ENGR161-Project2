# Fermenters
FERM_KWH = [46600, 47200, 47500, 48000]
FRMT_EFF = [0.5, 0.75, 0.9, 0.95]
FRMT_CPH = [320, 380, 460, 1100]

ETH_MOLAR_MASS = 0.046
FRMT_ETH_PER_SUG = 46*2/180
FRMT_CO2_PER_SUG = 44*2/180
FRMT_NRG_RELEASED_PER_MOL = 84e3


# Distillers
DIST_KWH = [46004, 47812, 48200, 49500]
DIST_EFF = [0.81, 0.9, 0.915, 0.98]
DIST_CPH = [390, 460, 560, 1370]

# Filters & Dehydraters
FILT_KWH = [48800, 49536, 50350, 51000]
FILT_EFF = [0.5, 0.75, 0.9, 0.98]
FILT_CPH = [200, 240, 280, 480]

# Applies to all above
MECH_NAMES = ["Scrap", "Average", "Premium", "World-class"]

# Pump
PUMP_EFF = [0.80, 0.83, 0.89, 0.92]
PUMP_EPR = [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
# PUMP_CPM_MTRX[PUMP_EFF_I, PUMP_EPR_I]
PUMP_CPM_MTRX = [[200, 220, 240, 260, 290, 320, 350, 390, 420, 470, 510],
                 [240, 260, 290, 310, 350, 380, 420, 460, 510, 560, 620],
                 [280, 310, 340, 380, 420, 460, 510, 560, 610, 670, 740],
                 [340, 380, 410, 460, 500, 550, 610, 670, 740, 810, 890],
                 [415, 456, 502, 552, 607, 668, 735, 808, 889, 978, 1076]]
PUMP_NAMES = ["Cheap", "Value", "Standard", "High-Grade", "Premium"]

# Pipes
PIPE_DFF = [0.05, 0.03, 0.02, 0.01, 0.005, 0.002]
PIPE_IND = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
# PIPE_CPM_MTRX[PIPE_DFF_I, PIPE_IND_I]
PIPE_CPM_MTRX = [[1.00, 1.20, 2.57, 6.30, 14, 26],
                 [1.2, 1.44, 3.08, 7.56, 16, 31],
                 [1.44, 1.72, 3.7, 9.07, 20, 37],
                 [2.16, 2.58, 5.55, 14, 29, 55],
                 [2.70, 3.23, 6.94, 17, 37, 69],
                 [2.97, 3.55, 7.64, 19, 40, 76]]
PIPE_NAMES = ["Salvage", "Questionable", "Better", "Nice", "Outstanding", "Glorious"]

# Bends
BEND_PLC = [0.1, 0.15, 0.2, 0.22, 0.27, 0.3]
BEND_CPB_MTRX = [[1, 1.49, 4.93, 14, 32, 62],
                 [1.05,1.57,5.17,15,34,65],
                 [1.1,1.64,5.43,16,36,69],
                 [1.16,1.73,5.7,16,38,72],
                 [1.22,1.81,5.99,17,39,76],
                 [1.28,1.9,7,18,41,80]]

# Valves
VALVE_FC = [800, 700, 600, 500]
VALVE_CPV_MTRX = [[1,1.2,2.57,6.3,14,26],
                  [1.2,1.44,3.08,7.56,16,31],
                  [2.7,3.23,6.94,17,37,69],
                  [2.97,3.55,7.64,19,40,76]]
VALVE_NAMES = ["Salvage", "Questionable", "Outstanding", "Glorious"]

# Ducts
DUCT_IND = [1, 1.25, 1.5]
DUCT_FF = .002
DUCT_CPM = [228, 414, 700]

# Densities
DENS_SUG = 1599
DENS_ETH = 789
DENS_FIB = 1311
DENS_WAT = 997
DENS_CO2 = 1.98

ETH_NGR_DENS = 80.1e6

# Constants
GRAV = 9.81