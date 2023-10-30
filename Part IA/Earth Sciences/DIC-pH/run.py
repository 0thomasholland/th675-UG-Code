import matplotlib.pyplot as plt
import numpy as np
from DICpH import model
from math import exp
import csv

# initial conditions

# CO2 = 414.72 ppm

params = {
    'pCO2': 0.041472,
    'H': 10**-8.1,
    'HCO3': 0.02,
    'CO3': 0.02,
    'kw': 10**-14,
    'k1': 10**-6.3,
    'k2': 10**-10.3,
    'dt': 0.01,
    'years': 10000,
    'time': 0
}

# calculate time array
params['time'] = np.arange(0, params['years'], params['dt'])

# run model

CO2_model, H_model, HCO3_model, CO3_model = model(params)

# print model in table of every 10 years into csv file

with open('Earth Practicals/Individual/DIC-pH/output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['time', 'CO2', 'H', 'HCO3', 'CO3'])
    for i in range(len(params['time'])):
        writer.writerow([params['time'][i], CO2_model[i], H_model[i], HCO3_model[i], CO3_model[i]])

# plot pH

pH_model = -np.log10(H_model)

plt.plot(params['time'], pH_model)
plt.legend()
plt.xlabel('time (years)')
plt.ylabel('pH')
plt.show()

# normalise CO2, HCO3 and CO3 to their respective starts

CO2_model_normalised = np.divide(CO2_model, CO2_model[0])
HCO3_model_normalised = np.divide(HCO3_model, HCO3_model[0])
CO3_model_normalised = np.divide(CO3_model, CO3_model[0])

CO2_model_normalised = np.exp(np.exp(CO2_model_normalised))
HCO3_model_normalised = np.exp(np.exp(HCO3_model_normalised))
CO3_model_normalised = np.exp(np.exp(CO3_model_normalised))

plt.plot(params['time'], CO2_model_normalised)
plt.plot(params['time'], HCO3_model_normalised)
plt.plot(params['time'], CO3_model_normalised)
plt.legend()
plt.xlabel('time (years)')
plt.ylabel('log_[100]DIC (ppm)')
plt.show()

