import datetime

import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy import signal
from utility import readConfig, findProbe

# use NASA API https://ssd.jpl.nasa.gov/horizons/app.html
# color https://matplotlib.org/stable/gallery/color/named_colors.html
class Horizon:
    def __init__(self):
        self.dates = []
        self.x = []
        self.y = []
        self.z = []
        self.v_x = []
        self.v_y = []
        self.v_z = []
        self.const_conversion_ua_km = 1.496e+8 # from UA in km
        self.const_conversion_ua_km_s = 1731.46# from AU/day in km/s

    def _parse_pos_line(self, line):
        sx, sy, sz = line[4:26], line[30:52], line[56:78]
        return float(sx), float(sy), float(sz)

    def _parse_velocity_line(self, line):
        vx, vy, vz = line[5:26], line[30:52], line[56:78]
        return float(vx), float(vy), float(vz)

    def get_ephemeris(self, filename, state_vector):
        with open(filename) as fi:
            while not fi.readline().strip() == "$$SOE":
                pass
            while True:
                line = fi.readline().rstrip()
                if line == "$$EOE":
                    break
                if "A.D." in line:
                    date = line[25:36]
                    self.dates.append(date)
                elif line.startswith(" X =") and (state_vector == 'position'):
                    sx, sy, sz = self._parse_pos_line(line)
                    self.x.append(sx)
                    self.y.append(sy)
                    self.z.append(sz)
                elif line.startswith(" VX=")and (state_vector == 'velocity'):
                    svx, svy, svz = self._parse_velocity_line(line)
                    self.v_x.append(svx * self.const_conversion_ua_km_s)
                    self.v_y.append(svy * self.const_conversion_ua_km_s)
                    self.v_z.append(svz * self.const_conversion_ua_km_s) # from  AU/day in km/s

    def get_position(self):
        return self.dates, self.x, self.y, self.z

    def get_velocity(self):
        return self.dates, self.v_x, self.v_y, self.v_z

    def get_module_velocity(self):
        v_square = np.sqrt (np.square(self.v_x) + np.square(self.v_y) + np.square(self.v_z))
        return self.dates, v_square


def plotTrajectory (corpse):
    angles = [(20, 90), (90, 0), (45, 45), (20, 160), (-5, 20), (-5, -130), (20, -90), (10, -90)]

    print(f"Plotting trajectory")
    for angle in angles:
        fig = plt.figure(figsize=(25,16))
        ax = fig.add_subplot(projection='3d')
        ax.view_init(angle[0], angle[1])

        legend_list = []
        for body_index in range (0, len(corpse['bodies'])):
            for body, param in corpse['bodies'][body_index].items():
                print(f"Working on body: {body}")
                legend_list.append(body)
                body_lower_name = body.lower()
                pos_body_dec = []

                horizon = Horizon()
                horizon.get_ephemeris(f"./Horizons/{body_lower_name}.txt", 'position')
                pos_body = horizon.get_position()

                pos_body_dec.append(pos_body[0])
                if 'decimate' in param:
                    pos_body_dec.append(signal.decimate(pos_body[1], param['decimate']))
                else:
                    pos_body_dec.append(pos_body[1])
                if 'decimate' in param:
                    pos_body_dec.append(signal.decimate(pos_body[2], param['decimate']))
                else:
                    pos_body_dec.append(pos_body[2])
                if 'decimate' in param:
                    pos_body_dec.append(signal.decimate(pos_body[3], param['decimate']))
                else:
                    pos_body_dec.append(pos_body[3])

                # bullet size
                if body == 'Sun':
                    size = [49 for element in range(len(pos_body_dec[1]))]
                else:
                    size = [4 for element in range(len(pos_body_dec[1]))]
                ax.scatter(pos_body_dec[1], pos_body_dec[2], pos_body_dec[3], '.', color=param['color'], sizes=size)

                if body_lower_name != 'earth':
                    for i in range(0, len(pos_body[1])):
                        if (i % 500) == 0:
                            ax.text(pos_body[1][i], pos_body[2][i], pos_body[3][i], pos_body[0][i], fontsize=7)

            ax.set_xlabel('x (UA)', fontsize = 20)
            ax.set_ylabel('y (UA)', fontsize = 20)
            ax.set_zlabel('z (UA)', fontsize = 20)

        legend = ax.legend(legend_list,  loc = 'center left', fontsize = 20)
        plt.title(f'Trajectories of the Voyager probes from ({angle[0]}, {angle[1]})', fontsize = 40)
        plt.savefig(f'voyager_trajectory_{angle[0]}_{angle[1]}.png')
        plt.show()


def plotVelocity (cel_bodies):
    print(f"Plotting velocity")
    legend_list = []
    bodies = findProbe(cel_bodies)

    min_y = 200
    max_y = 0
    fig = plt.figure(figsize=(20, 16))
    plt.title(f'Velocity of Voyager probes', fontsize=40)
    for body, body_lower_name in bodies.items():
        print(f"Working on body: {body}")
        horizon = Horizon()
        horizon.get_ephemeris(f"./Horizons/{body_lower_name}.txt", 'velocity')
        vel_body = horizon.get_module_velocity()
        plt.plot(vel_body[0][0:8140], vel_body[1][0:8140])
        plt.xlabel('Date', fontsize = 20)
        plt.ylabel('Velocity (km/s)', fontsize=20)
        tick_label = ['x' if (i % 400) != 0 else str(val) for i, val in enumerate(vel_body[0][0:8137])]
        plt.xticks(tick_label, tick_label, rotation=45, fontsize='20')
        if min(vel_body[1]) < min_y:
            min_y = min(vel_body[1])
        if max(vel_body[1]) > max_y:
            max_y = max(vel_body[1])
        legend_list.append(f"{body.replace('_', '')}")

    listOf_Yticks = np.arange(int(min_y), int(max_y), step = 2)
    plt.yticks(listOf_Yticks, listOf_Yticks, fontsize='20')
    plt.legend(legend_list,  loc = 'upper center', fontsize = 20)
    plt.grid(True)
    plt.savefig(f'Voyager_probes_velocity.png')
    plt.show()


if __name__ == "__main__":
    bodies = readConfig("bodies.yaml")
    if bodies is None:
        print ("Bodies not found.")
        sys.exit(-1)

    #plotTrajectory(bodies)
    plotVelocity (bodies)
