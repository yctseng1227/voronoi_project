from tkinter import Canvas
from itertools import combinations
import tkinter as tk
import numpy as np
import random
import math

from scipy.spatial import ConvexHull, convex_hull_plot_2d


class VCanvas(Canvas):
    def __init__(self, **kwargs):
        Canvas.__init__(self, **kwargs)
        self.width = kwargs.get("width", 800)
        self.height = kwargs.get("height", 600)

        self.subset_points = iter([])
        self.visible_points = []
        self.visible_lines = []
        self.bind("<Button-1>", self.click_point)

    def draw_point(self, point, color="black"):
        x0, y0 = point
        (x0, y0), (x1, y1) = (x0 - 2, y0 - 2), (x0 + 2, y0 + 2)
        self.create_oval(x0, y0, x1, y1, fill=color)

    def draw_edge(self, point1, point2, color="black"):
        x0, y0 = point1
        x1, y1 = point2
        self.create_line(x0, y0, x1, y1, fill=color, width=3)

    def click_point(self, event):
        point = (event.x, event.y)
        self.add_visible_points(point)
        self.draw_point(point)
        print("(x, y) = (" + str(event.x) + ", " + str(event.y) + ")")
        return event
    
    def add_visible_points(self, point):
        self.visible_points.append(point)
    
    def clean_canvas(self):
        self.delete("all")
        self.visible_points = []
        self.visible_lines = []
    
    def set_subset_points(self, points):
        self.subset_points = iter(points)
        
    def next_points(self):     
        subset_points = next(self.subset_points, None)
        print(subset_points)

        if subset_points is None:
            self.clean_canvas()
            return
        self.clean_canvas()
        for point in subset_points:
            self.draw_point(point)
        self.visible_points = subset_points

    def random_points(self):
        # self.clean_canvas()
        for _ in range(6):
            points = ((int(random.random()*800), int(random.random()*600)))
            self.add_visible_points(points)
            self.draw_point(points)


    # voronoi--------------------------------------------------------------------------
    def cercle_circonscrit(self, points):
        (x1, y1), (x2, y2), (x3, y3) = points
        A = np.array([[x3-x1,y3-y1],[x3-x2,y3-y2]])
        Y = np.array([(x3**2 + y3**2 - x1**2 - y1**2),(x3**2+y3**2 - x2**2-y2**2)])
        if np.linalg.det(A) == 0:
            return False
        Ainv = np.linalg.inv(A)
        X = 0.5*np.dot(Ainv,Y)
        x,y = X[0],X[1]

        #(10, 20), (20, 40), (200, 400): x,y == inf,-inf
        if x > 1e9 or x < -1e9 or y > 1e9 or y < -1e9:    
            return False
        return x, y

    def slope_intercept(self, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        midx = (x1 + x2) / 2
        midy = (y1 + y2) / 2

        if y2 - y1 == 0:
            return (midx, midy), -1e9, -1e9
        a = (x1 - x2) / (y2 - y1)
        b = midy - a * midx

        return (midx, midy), a, b

    # False: obtuse angle
    def which_triangle(self, p1, p2, p3):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        res = (x1-x2) * (x1-x3) + (y1-y2) * (y1-y3)

        return False if res < 0 else True

    def line_distance(self, p1, p2):
        return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

    # Draw voronoi diagram
    def drawVoronoi(self, img, subdiv):

        # Get facets and centers
        (facets, centers) = subdiv.getVoronoiFacetList([])

        for i in range(0, len(facets)):
            ifacetArr = []
            for f in facets[i]:
                ifacetArr.append(f)

            # Extract ith facet
            ifacet = np.array(ifacetArr, np.int)

            # Generate random color
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Fill facet with a random color
            cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0)

            # Draw facet boundary
            ifacets = np.array([ifacet])
            cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)

            # Draw centers.
            cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), -1, cv2.LINE_AA, 0)

    def voronoi_sample(self):
        pass

    def v3points(self, points):
        # self.visible_points = sorted(self.visible_points , key=lambda k: [k[0], k[1]])
        all_line = []

        if len(points) == 3:
            center = self.cercle_circonscrit(points)
            if not center:
                if points[0][0] == points[1][0] == points[2][0]: # 3 points collinearity -x
                    
                    mid = (points[0][1]+points[1][1]) / 2
                    point1, point2 = (0, mid), (800, mid)
                    all_line.append([point1, point2])

                    mid = (points[1][1]+points[2][1]) / 2
                    point1, point2 = (0, mid), (800, mid)
                    all_line.append([point1, point2])

                elif points[0][1] == points[1][1] == points[2][1]: # 3 points collinearity -y

                    mid = (points[0][0]+points[1][0]) / 2
                    point1, point2 = (mid, 0), (mid, 600)
                    all_line.append([point1, point2])

                    mid = (points[1][0]+points[2][0]) / 2
                    point1, point2 = (mid, 0), (mid, 600)
                    all_line.append([point1, point2])
        
                else:
                    mid, a, b = self.slope_intercept(points[0], points[1])
                    point1, point2 = (0, b), (800, a*800+b)
                    all_line.append([point1, point2])

                    mid, a, b = self.slope_intercept(points[1], points[2])
                    point1, point2 = (0, b), (800, a*800+b)
                    all_line.append([point1, point2])
                   
            else:
                mid, a, b = self.slope_intercept(points[0], points[1])
                angle = self.which_triangle(points[2], points[0], points[1])
                if a != -1e9:
                    if center[0] < mid[0]:
                        x = 800
                    elif center[0] > mid[0]:
                        x = 0
                    else:
                        x = 800 if points[2][0]+points[2][1]<mid[0]+mid[1] else 0

                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    point1, point2 = center, (x, a*x+b)
                    all_line.append([point1, point2, points[0], points[1]])
                else: # |
                    y = 600 if center[1]<mid[1] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        y = abs(y - 600)
                    point1, point2 = center, (center[0], y)
                    all_line.append([point1, point2], points[0], points[1])

                mid, a, b = self.slope_intercept(points[0], points[2])
                angle = self.which_triangle(points[1], points[0], points[2])
                if a != -1e9: 
                    if center[0] < mid[0]:
                        x = 800
                    elif center[0] > mid[0]:
                        x = 0
                    else:
                        x = 800 if points[1][0]+points[1][1]<mid[0]+mid[1] else 0

                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    point1, point2 = center, (x, a*x+b)
                    all_line.append([point1, point2, points[0], points[2]])
                else: # |
                    y = 600 if center[1]<mid[1] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        y = abs(y - 600)
                    point1, point2 = center, (center[0], y)
                    all_line.append([point1, point2, points[0], points[2]])

                mid, a, b = self.slope_intercept(points[1], points[2])
                angle = self.which_triangle(points[0], points[1], points[2])
                if a != -1e9:
                    if center[0] < mid[0]:
                        x = 800
                    elif center[0] > mid[0]:
                        x = 0
                    else:
                        x = 800 if points[0][0]+points[0][1]<mid[0]+mid[1] else 0

                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    point1, point2 = center, (x, a*x+b)
                    all_line.append([point1, point2, points[1], points[2]])
                else: # |
                    y = 600 if center[1]<mid[1] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        y = abs(y - 600)
                    point1, point2 = center, (center[0], y)
                    all_line.append([point1, point2, points[1], points[2]])

        elif len(points) == 2:
            mid, a, b = self.slope_intercept(points[0], points[1])
            if a != -1e9:
                point1, point2 = (0, b), (800, a*800+b)
                all_line.append([point1, point2])
            else:
                point1, point2 = (mid[0], 0), (mid[0], 600)
                all_line.append([point1, point2])
        else:
            pass

        # for i in all_line:
        #     self.draw_edge(i[0], i[1])
        #     self.visible_lines.append((i[0][0], i[0][1], i[1][0], i[1][1]))
        return all_line

    def find_intersection(self, line1, line2):
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        if not ( min(x1,x2)<=max(x3,x4) and min(y3,y4)<=max(y1,y2)\
            and min(x3,x4)<=max(x1,x2) and min(y1,y2)<=max(y3,y4) ):
            return None
        # if x1-x2 == 0 or x3-x4 == 0:
        #     return None


        # find line1: y = a1 * x + b1
        a1 = (y1-y2) / (x1-x2)
        b1 = y1 - a1 * x1
        
        # find line2: y = a2 * x + b2
        a2 = (y3-y4) / (x3-x4)
        b2 = y3 - a2 * x3

        x = (b1-b2) / (a2 - a1)
        y = a1 * x + b1
        if 0 <= x <= 800 and 0 <= y <= 600:
            return (x, y)
        else:
            return None
        

    def merge(self, p_set1, l_set1, p_set2, l_set2):
        if len(p_set1) < 3:
            if len(p_set1) == 2:
                self.draw_edge(p_set1[0], p_set1[1], "blue")
        else:
            hull = ConvexHull(p_set1)
            _list = list(hull.vertices)
            for x1, x2 in zip(_list, _list[1:] + _list[:1]):
                self.draw_edge(p_set1[x1], p_set1[x2], "blue")

        if len(p_set2) < 3:
            if len(p_set2) == 2:
                self.draw_edge(p_set2[0], p_set2[1], "blue")
        else:
            hull = ConvexHull(p_set2)
            _list = list(hull.vertices)
            for x1, x2 in zip(_list, _list[1:] + _list[:1]):
                self.draw_edge(p_set2[x1], p_set2[x2], "blue")

        # if len(p_set1) >= 6:
        #     return

        p_set1 = sorted(list(p_set1) , key=lambda k: [k[1], k[0]])
        p_set2 = sorted(list(p_set2) , key=lambda k: [k[1], k[0]])
        #p_set = sorted(list(p_set1+p_set2) , key=lambda k: [k[0], k[1]])
        result = []
        hyperplane = []
        ref_point = [ p_set1[0], p_set2[0] ]
        #ref_point = [ p_set[int(len(p_set)/2)-1], p_set[int(len(p_set)/2)] ]
        all_line = l_set1 + l_set2

        # decide the first line
        mid, a, b = self.slope_intercept(ref_point[0], ref_point[1])
        if a != -1e9:
            if a > 0:
                point1, point2 = (0, b), (mid[0], mid[1])
            else:
                point1, point2 = (mid[0], mid[1]), (800, a*800+b)
            hyperplane.append([point1, point2, ref_point[0], ref_point[1]])
        else:
            point1, point2 = (mid[0], 0), (mid[0], 600)
            hyperplane.append([point1, point2, ref_point[0], ref_point[1]])

        while True:
        #for _ in range(3):
            # decide the order with p_set1 & p_set2
            cross_point = (1e9, 1e9)
            which_line = []

            for i in all_line:
                tmp = self.find_intersection((hyperplane[-1][0], hyperplane[-1][1]), (i[0], i[1]))
                if tmp != None and tmp[1] < cross_point[1]:
                    cross_point = tmp
                    which_line = i
            
            if cross_point == (1e9, 1e9):
                break
            hyperplane[-1][1] = cross_point


            for i in all_line:
                if which_line == i:
                    if self.line_distance(i[0], i[3]) < self.line_distance(i[1], i[3]):
                        i[1] = cross_point
                    else:
                        i[0] = cross_point
                    result.append(i)
                    all_line.remove(i)
                    break

            if ref_point[0] == which_line[2]:
                ref_point[0] = which_line[3]
            elif ref_point[0] == which_line[3]:
                ref_point[0] = which_line[2]
            elif ref_point[1] == which_line[2]:
                ref_point[1] = which_line[3]
            else:
                ref_point[1] = which_line[2]
            # self.draw_edge(ref_point[0], ref_point[1], "green")

            # decide the next line
            mid, a, b = self.slope_intercept(ref_point[0], ref_point[1])
            if a != -1e9:
                if a > 0:
                    point1, point2 = cross_point, (800, a*800+b)
                else:
                    point1, point2 = cross_point, (0, b), 
                hyperplane.append([point1, point2, ref_point[0], ref_point[1]])
            else:
                point1, point2 = (cross_point[0], 0), (cross_point[0], 600)
                hyperplane.append([point1, point2, ref_point[0], ref_point[1]])
            
        for i in all_line:
            result.append(i)
        for i in hyperplane:
            self.draw_edge(i[0], i[1], "red")
        for i in result:
            self.draw_edge(i[0], i[1], "green")

        return hyperplane+result

    def recursive(self, point_set):
        if len(point_set) <= 3:
            return self.v3points(point_set)

        p_set1, p_set2 = point_set[:int(len(point_set)/2)], point_set[int(len(point_set)/2):]

        l_set1 = self.recursive(p_set1)
        l_set2 = self.recursive(p_set2)

        return self.merge(p_set1, l_set1, p_set2, l_set2)

    def voronoi_step(self):
        if len(self.visible_points) == 0:
            return

        s = set(self.visible_points) # keep out same points
        gPoints = sorted(list(s) , key=lambda k: [k[0], k[1]])
        
        self.recursive(gPoints)

if __name__ == "__main__":
    pass
    # app = tk.Tk()
    # canvas = VCanvas(width=800, height=600, bg="white")
    # canvas.pack()
    # app.mainloop()
