"""
This module generates the z layer for the contour plot. It is capable of
plotting the sensor data according to the sensor"s position on the chair.
"""
import polars as pl

from copy import deepcopy

# Coordinates of sensor positions in the range [-1, 1]
coords = {
    "p00": (0.3, 0.35), "p01": (-0.3, 0.35), "p02": (0.3, -0.35), "p03": (-0.3, -0.35),
    "p04": (0.35, 0.6), "p05": (-0.35, 0.6), "p06": (0.35, 0), "p07": (-0.35, 0),
    "p08": (0.6, -0.5), "p09": (-0.6, -0.5), "p10": (0.45, -0.8), "p11": (-0.45, -0.8)
}
scale_y: float = 25.0
scale_x = round(scale_y * (7 / 10))

# Actual size and data points of the plot calculated using the scale factors
size = (round(scale_y * 2 + 1), (scale_x * 2 + 1))
points = {
    key: (
        round(coords[key][1] * scale_y + scale_y),
        round(coords[key][0] * scale_x + scale_x)
    ) for key in coords.keys()
}

# Base matrix for the contour plot
z_base = [[None for _ in range(size[1])] for _ in range(size[0])]

for i in range(size[0]):
    z_base[i][0] = 0
    z_base[i][1] = 0
    z_base[i][-1] = 0
    z_base[i][-2] = 0
for j in range(size[1]):
    z_base[0][j] = 0
    z_base[1][j] = 0
    z_base[-1][j] = 0
    z_base[-2][j] = 0

def is_back_point(key: str) -> bool:
    """
    Checks if the point is a backrest point.

    Parameters
    ----------
    key : str
        The key of the point.

    Returns
    -------
    bool
    """
    return int(key[1:]) < 4

def generate_z(data: pl.DataFrame) -> tuple[list[list[int]]]:
    """
    Generates the z layer for the contour plot by marking points
    as 3x3 spaces on the plot, leaving the rest for interpolation.

    Parameters
    ----------
    data : pl.DataFrame
        The data to be plotted.

    Returns
    -------
    tuple[list[list[int]]]
        The z layers for the contour plot: seat and backrest, respectively.
    """
    global z_base
    z = (deepcopy(z_base), deepcopy(z_base))

    global size, points

    for key, value in zip(data.columns, data.rows()[0]):
        point = points[key]
        # 0 for seat, 1 for back
        index = int(is_back_point(key))

        for i in range(point[0] - 1, point[0] + 2):
            for j in range(point[1] - 1, point[1] + 2):
                current_value = z[index][i][j]
                z[index][i][j] = max(value, current_value if current_value is not None else 0)

    return z

if __name__ == "__main__":
    # Uses a dictionary to simulate the data
    z = generate_z({
        "p00": 1, "p01": 2, "p02": 3, "p03": 4, "p04": 5, "p05": 6,
        "p06": 7,"p07": 8, "p08": 9, "p09": 10, "p10": 11, "p11": 12
    })
    print(z)
