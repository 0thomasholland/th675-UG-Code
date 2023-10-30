# Age (thousands of vears) Depth (m)
# 12.05 1.85
# 17.85 2.2
# 24.11 3
# 43.88 6.2
# 50.21 6.65
# 55.45 7.2
# 58.96 7.45
# 64.09 8
# 73.91 8.7
# 79.25 9.8
# 90.95 10.55
# 96.21 11.15
# 103.29 11.8
# 110.79 12.55
# 122.56 13.45
# 123.82 13.75
# 125.19 14.05
# 129.84 14.45
# 142.28 16.75
# 152.58 17.5
# 161.34 18.5

# Path: General plot/Earth plots/Age-MarineIsotope-Depth/main.py
# Age (thousands of vears) Depth (m)

import numpy as np
import matplotlib.pyplot as plt

#import keras and tensorflow
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

depth = np.array([1.85, 2.2, 3, 6.2, 6.65, 7.2, 7.45, 8, 8.7, 9.8, 10.55, 11.15, 11.8, 12.55, 13.45, 13.75, 14.05, 14.45, 16.75, 17.5, 18.5])
age = np.array([12.05, 17.85, 24.11, 43.88, 50.21, 55.45, 58.96, 64.09, 73.91, 79.25, 90.95, 96.21, 103.29, 110.79, 122.56, 123.82, 125.19, 129.84, 142.28, 152.58, 161.34])

#build a linear regression model with learning rate 0.001

model = tf.keras.Sequential()
model.add(layers.Dense(1, input_shape=(1,)))
model.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss='mse', metrics=['mae'])

#train the model with verbose=1
model.fit(depth, age, epochs=10000, verbose=1)

#predict the age of the sample with depth 5.5
print(model.predict([5.5]))

#plot the data with the model

plt.scatter(age, depth)
plt.xlabel('Age (thousands of years)')
plt.ylabel('Depth (m)')
plt.plot(model.predict(depth), depth, color='red')
plt.show()

# print linear regression model parameters

print('Linear regression model parameters:')
print('y = {:.2f}x + {:.2f}'.format(model.layers[0].get_weights()[0][0][0], model.layers[0].get_weights()[1][0]))

# Path: General plot/Earth plots/Age-MarineIsotope-Depth/main.py
# save model
model.save('/General plot/Earth plots/Age-MarineIsotope-Depth/model.h5')
