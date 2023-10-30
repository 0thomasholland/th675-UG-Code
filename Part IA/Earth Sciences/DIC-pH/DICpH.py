import numpy as np
import matplotlib.pyplot as plt

##### ALL VALUES:
## TEMP deg C
# Ka x K-a = Kw = 10**-14


### generate DIC species pH model

## define finite state machine matrix for set of equilibrium

# CO2 + H2O ⇌ H+ + HCO−3 (forward = k1, reverse = 10**14/k1)
# HCO−3 ⇌ H+ + CO2−3 (forward = k2, reverse = 10**14/k2)
# k1 = 10**-6.3
# k2 = 10**-10.3
 
def dCO2dt(kw, k1, k2, CO2, H, HCO3):
    return -k1 * CO2 + kw/k1 * H * HCO3

def dHdt(kw, k1, k2, CO2, H, HCO3, CO3):
    return k1 * CO2 - kw/k1 * H * HCO3 +k2 * HCO3 - kw/k2 * H * CO3

def dHCO3dt(kw, k1, k2, CO2, H, HCO3, CO3):
    return k1 * CO2 - kw/k1 * H * HCO3 - k2 * HCO3 + kw/k2 * H * CO3

def dCO3dt(kw, k2, H, HCO3, CO3):
    return k2 * HCO3 - kw/k2 * H * CO3


def model(_params):
    # initial conditions
    kw = _params['kw']
    CO2 = _params['pCO2']
    H = _params['H']
    HCO3 = _params['HCO3']
    CO3 = _params['CO3']
    k1 = _params['k1']
    k2 = _params['k2']
    dt = _params['dt']
    time = _params['time']
    # generate model
    CO2_model = np.zeros(len(time))
    H_model = np.zeros(len(time))
    HCO3_model = np.zeros(len(time))
    CO3_model = np.zeros(len(time))
    for i in range(len(time)):
        CO2_model[i] = CO2
        H_model[i] = H
        HCO3_model[i] = HCO3
        CO3_model[i] = CO3
        CO2 += dCO2dt(kw, k1, k2, CO2, H, HCO3) * dt
        H += dHdt(kw, k1, k2, CO2, H, HCO3, CO3) * dt
        HCO3 += dHCO3dt(kw, k1, k2, CO2, H, HCO3, CO3) * dt
        CO3 += dCO3dt(kw, k2, H, HCO3, CO3) * dt

    return CO2_model, H_model, HCO3_model, CO3_model