import re


def points(lines):
    points = []
    subset_points = []
    lines = [line.split("#")[0] for line in lines]
    for line in lines:
        numbers = re.findall(r"\d+", line)
        if len(numbers) == 2:
            x, y = numbers
            point = (int(x), int(y))
            subset_points.append(point)
        elif len(numbers) == 1:
            points.append(subset_points)
            subset_points = []

    points.remove([])
    [print(p) for p in points]
    return points


if __name__ == "__main__":
    with open("./vd_testdata.in", encoding="big5") as f:
        lines = f.readlines()
        points(lines)