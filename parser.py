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


def points_and_edges(lines):
    points = []
    edges = []
    for line in lines:
        numbers = re.findall(r"\d+", line)
        numbers = tuple([int(number) for number in numbers])
        if "P" in line:
            points.append(numbers)
        elif "E" in line:
            point_1 = numbers[:2]
            point_2 = numbers[2:]
            edges.append((point_1, point_2))

    return points, edges
