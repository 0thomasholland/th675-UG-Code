import numpy as np
import matplotlib.pyplot as plt


runs = 10000
iterations = 100

origin = np.array([0, 0])

current = np.array([0.01, 0.03])  # 3 m/s in the y direction
boat_speed = 0.2  # 2 m/s speed in any direction

paths = np.zeros((iterations, runs, 2))


for i in range(iterations):
    boat_position = np.zeros((runs, 2))
    boat = np.array([i, 0])
    for x in range(runs):
        # calculate the vector from the boat to the origin
        boat_to_origin = origin - boat
        # calculate the angle between the boat and the origin
        angle = np.arctan2(boat_to_origin[1], boat_to_origin[0])

        # boat points towards the origin, calculate the new boat position
        boat = (
            boat
            + boat_speed * np.array([np.cos(angle), np.sin(angle)])
            + current
        )

        # print(boat)
        boat_position[x] = boat
    # save the boat position for each iteration
    paths[i] = boat_position

print(paths)

# plot the paths

for i in range(iterations):
    plt.plot(paths[i, :, 0], paths[i, :, 1])

plt.show()