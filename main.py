import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import yaml
import sys
from scipy import signal

# use NASA API https://ssd.jpl.nasa.gov/horizons/app.html
# color https://matplotlib.org/stable/gallery/color/named_colors.html
def get_ephemeris(filename):
    def parse_line(line):
        sx, sy, sz = line[4:26], line[30:52], line[56:78]
        return float(sx), float(sy), float(sz)

    dates = []
    x = []
    y = []
    z = []
    with open(filename) as fi:
        while not fi.readline().strip() == "$$SOE":
            pass
        while True:
            line = fi.readline().rstrip()
            if line == "$$EOE":
                break
            if "A.D." in line:
                date = line[25:36]
                if date.startswith("1999-Dec"):
                    # Stop reading data at this date.
                    break
                dates.append(date)
            elif line.startswith(" X ="):
                sx, sy, sz = parse_line(line)
                x.append(sx)
                y.append(sy)
                z.append(sz)
    return dates, x, y, z


if __name__ == "__main__":
    bodies = None
    with open("bodies.yaml") as stream:
        try:
            bodies = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(-1)

    angles = []
    angles.append((20,90))
    angles.append((90, 0))
    angles.append((45, 45))
    angles.append((20, 160))
    angles.append((-5, 20))
    for angle in angles:
        fig = plt.figure(figsize=(25,25))
        ax = fig.add_subplot(projection='3d')
        ax.view_init(angle[0], angle[1])

        legend_list = []
        color_list = []
        for body_index in range (0, len(bodies['bodies'])):
            for body, param in bodies['bodies'][body_index].items():
                print(f"Working on body: {body}")
                legend_list.append(body)

                body_lower_name = body.lower()
                pos_voyager = get_ephemeris(f"./Horizons/{body_lower_name}.txt")
                pos_voyager_dec = []
                pos_voyager_dec.append(pos_voyager[0])
                pos_voyager_dec.append(signal.decimate(pos_voyager[1], param['decimate']))
                print (f"# point(s) for {body}: {len(pos_voyager_dec[1])}")
                pos_voyager_dec.append(signal.decimate(pos_voyager[2], param['decimate']))
                pos_voyager_dec.append(signal.decimate(pos_voyager[3], param['decimate']))

                # bullet size
                size = [4 for element in range(len(pos_voyager_dec[1]))]
                ax.scatter(pos_voyager_dec[1], pos_voyager_dec[2], pos_voyager_dec[3], '.', color=param['color'], sizes=size)

                if body_lower_name != 'earth':
                    for i in range(0, len(pos_voyager[1])):
                        if (i % 500) == 0:
                            dt = datetime.datetime.strptime(pos_voyager[0][i], '%Y-%b-%d')
                            new_format_date = str(dt.year) + str(dt.month).zfill(2) + str(dt.day).zfill(2)
                            #print (new_date)
                            ax.text(pos_voyager[1][i], pos_voyager[2][i], pos_voyager[3][i], new_format_date, fontsize=7)

            ax.set_xlabel('X (UA)', fontsize = 20)
            ax.set_ylabel('Y (UA)', fontsize = 20)
            ax.set_zlabel('Z (UA)', fontsize = 20)

        legend = ax.legend(legend_list,  loc = 'center left', fontsize = 20)
        plt.title(f'Trajectories of the Voyager probes from ({angle[0]}, {angle[1]})', fontsize = 40)
        plt.savefig(f'voyager_trajectory_{angle[0]}_{angle[1]}.png')
        plt.show()

