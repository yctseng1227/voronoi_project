from tkinter import Canvas
from itertools import combinations
import tkinter as tk
import numpy as np
import random
import math


class VCanvas(Canvas):
    def __init__(self, **kwargs):
        Canvas.__init__(self, **kwargs)
        self.width = kwargs.get("width", 800)
        self.height = kwargs.get("height", 600)

        self.subset_points = iter([])
        self.visible_points = []
        self.subset_voronoi = iter([])
        self.visible_voronoi = []
        self.voronoi_final = []
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
        self.visible_voronoi = []
    
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

    def next_voronoi(self):
        if len(self.visible_points) != 0 and (len(self.visible_voronoi) == 0):
            self.voronoi_step()
            self.subset_voronoi = iter(self.visible_voronoi)

        subset_voronoi = next(self.subset_voronoi, None)

        # 把線清除 重畫points
        self.delete("all")
        for point in self.visible_points:
            self.draw_point(point)

        # voronoi 按到底
        if subset_voronoi is None:
            # canvas上沒有points
            if len(self.visible_points) == 0:
                return
            # final
            for v in self.voronoi_final:
                self.draw_edge(v[0], v[1], "brown")
            return
        # step by step
        for line in subset_voronoi:
            self.draw_edge(line[0], line[1], "blue")

    def random_points(self):
        # self.clean_canvas()
        for _ in range(6):
            points = ((int(random.random()*800), int(random.random()*600)))
            self.add_visible_points(points)
            self.draw_point(points)


    # voronoi--------------------------------------------------------------------------

    # 找三個點的外心
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

    # 找某線段的鉛錘線
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

    # False: obtuse angle(鈍角)
    def which_triangle(self, p1, p2, p3):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        res = (x1-x2) * (x1-x3) + (y1-y2) * (y1-y3)

        return False if res < 0 else True

    def line_distance(self, p1, p2):
        return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

    def voronoi_sample(self):
        # canvas上沒有points
        if len(self.visible_points) == 0:
            return

        # final
        self.voronoi_step()

        # 把線清除 重畫points
        self.delete("all")
        for point in self.visible_points:
            self.draw_point(point)

        for v in self.voronoi_final:
            self.draw_edge(v[0], v[1], "brown")
        return

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
                    all_line.append([point1, point2, points[0], points[1]])

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
                all_line.append([point1, point2, points[0], points[1]])
            else:
                point1, point2 = (mid[0], 0), (mid[0], 600)
                all_line.append([point1, point2, points[0], points[1]])
        else:
            pass

        # for i in all_line:
        #     self.draw_edge(i[0], i[1])
        return all_line

    # 拿掉多餘的HP
    def prune_check(self, point, all_line):
        if len(all_line) < 3:
            return None
        lines = []
        for i in all_line:
            if point == i[0] or point == i[1]:
                lines.append(i)
        if len(lines) == 1:
            return lines[-1]
        return None

    # 找兩線段間交點
    def find_intersection(self, line1, line2):
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        # 用向量判斷是否有交點
        v1 = ( (x3-x1), (y3-y1) )
        v2 = ( (x4-x1), (y4-y1) )
        vm = ( (x2-x1), (y2-y1) )
        if (v1[0]*vm[1] - vm[0]*v1[1]) * (v2[0]*vm[1] - vm[0]*v2[1]) > 0:
            return None
        # 用點座標的相對位置判斷是否有交點
        if not ( min(x1,x2)<=max(x3,x4) and min(y3,y4)<=max(y1,y2)\
            and min(x3,x4)<=max(x1,x2) and min(y1,y2)<=max(y3,y4) ):
            return None

        # 用線方程式找交點

        # 其中一邊為垂直線
        if x1 - x2 == 0:
            x = x1
            a2 = (y3-y4) / (x3-x4)
            b2 = y3 - a2 * x3
            y = a2 * x + b2
            
        elif x3 - x4 == 0:
            x = x3
            a1 = (y1-y2) / (x1-x2)
            b1 = y1 - a1 * x1
            y = a1 * x + b1
        else:
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
        return None

    def convex_hull(self, points):
        points = sorted(set(points))

        if len(points) <= 1:
            return points

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        # Build lower hull 
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        # Build upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]


    def convex_order(self, p_set):
        # 如果p_set都在同y=k上, 則不做convex hull
        do_convex_y = False
        check_x = p_set[0][0]
        for i in p_set:
            if check_x != i[0]:
                do_convex_x = True
                break

        # 如果p_set都在同x=k上, 則不做convex hull
        do_convex_x = False
        check_y = p_set[0][1]
        for i in p_set:
            if check_y != i[1]:
                do_convex_y = True
                break
        
        _list = []
        if do_convex_x == False:
            sorted(list(p_set) , key=lambda k: [k[1], k[0]])
            for i in range(len(p_set)):
                _list.append(i)
        elif do_convex_y == False:
            sorted(list(p_set) , key=lambda k: [k[0], k[1]])
            for i in range(len(p_set)):
                _list.append(i)
        else:
            hull = self.convex_hull(p_set)
            _list = list(hull)

        return _list

    def merge(self, p_set1, l_set1, p_set2, l_set2):

        # # convex hull
        if len(p_set1) < 3:
            if len(p_set1) == 2:
                self.draw_edge(p_set1[0], p_set1[1], "blue")
        else:
            _list = self.convex_order(p_set1)
            for x1, x2 in zip(_list, _list[1:] + _list[:1]):
                self.draw_edge(p_set1[x1], p_set1[x2], "blue")

        if len(p_set2) < 3:
            if len(p_set2) == 2:
                self.draw_edge(p_set2[0], p_set2[1], "blue")
        else:
            _list = self.convex_order(p_set2)
            for x1, x2 in zip(_list, _list[1:] + _list[:1]):
                self.draw_edge(p_set2[x1], p_set2[x2], "blue")

        # 將所有point排序後 找左區塊最右點and右區塊最左點 的中垂線x=k
        p_set1 = sorted(list(p_set1) , key=lambda k: [k[0], k[1]])
        p_set2 = sorted(list(p_set2) , key=lambda k: [k[0], k[1]])
        mid_point = ((p_set1[-1][0] + p_set2[0][0]) / 2, 0)

        # 利用(k, 0)和所有點比較距離 找左右區塊最近的點當作最初ref_point
        arr = []
        for i in p_set1:
            arr.append(self.line_distance(mid_point, i))
        p_set1 = [x for _,x in sorted(zip(arr, p_set1))]
        arr = []
        for i in p_set2:
            arr.append(self.line_distance(mid_point, i))
        p_set2 = [x for _,x in sorted(zip(arr, p_set2))]
        
        # init
        result = []
        hyperplane = []
        ref_point = [ p_set1[0], p_set2[0] ]
        for i in l_set1:
            if i[0][0] > i[1][0]:
                i[0], i[1] = i[1], i[0]
        for i in l_set2:
            if i[0][0] > i[1][0]:
                i[0], i[1] = i[1], i[0]
        all_line = l_set1 + l_set2
        

        # decide the first line
        mid, a, b = self.slope_intercept(ref_point[0], ref_point[1])
        if a != -1e9:
            point1, point2 = (0, b), (800, a*800+b)
            # y: p1[1] need smaller than p2[1]
            if point1[1] > point2[1]:
                point1, point2 = point2, point1
            hyperplane.append([point1, point2, ref_point[0], ref_point[1]])
        else:
            point1, point2 = (mid[0], 0), (mid[0], 600)
            hyperplane.append([point1, point2, ref_point[0], ref_point[1]])

        while True:
            # decide the order with p_set1 & p_set2
            cross_point = (1e9, 1e9)
            which_line = []
            which_line2 = []   
            
            
            # 找出 HP和所有線段的交點, 取y值最小交點
            for i in all_line:
                tmp = self.find_intersection((hyperplane[-1][0], hyperplane[-1][1]), (i[0], i[1]))
                if tmp == cross_point:
                    which_line2 = i
                if tmp != None and (tmp[1] < cross_point[1]):
                    cross_point = tmp
                    which_line = i
                

            # 找無交點
            if cross_point == (1e9, 1e9):
                break
            # 有交點, 修正HP線段終點
            hyperplane[-1][1] = cross_point

            for i in l_set1:
                if which_line == i:
                    tmp = i
                    all_line.remove(i)
                    # 從cross_point 和 畫出該線段的中點mid 決定如何修正
                    mid = ( ((tmp[2][0]+tmp[3][0]) / 2), ((tmp[2][1]+tmp[3][1]) / 2) )
                    # tmp[0] -> mid -> cross_point : 銳角, 線段tmp[0]-cross_point

                    replace = -1
                    if mid[0] > cross_point[0] and mid[1] > cross_point[1]:
                        replace = 1
                    elif mid[0] > cross_point[0] and mid[1] < cross_point[1]:
                        replace = 0
                    elif mid[0] < cross_point[0] and mid[1] > cross_point[1]:
                        replace = 1
                    else:
                        replace = 1
                    #---
                    if replace == 0:
                        res = self.prune_check(tmp[0], all_line+result)
                        if res != None:
                            all_line.remove(res)

                        res = self.prune_check(tmp[1], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        else:
                            tmp[0] = cross_point
                            result.append(tmp)
                    else:
                        res = self.prune_check(tmp[1], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        res = self.prune_check(tmp[0], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        else:
                            tmp[1] = cross_point
                            result.append(tmp)
                    break
            
            for i in l_set2:
                if which_line == i:
                    tmp = i
                    all_line.remove(i)

                    mid = ( ((tmp[2][0]+tmp[3][0]) / 2), ((tmp[2][1]+tmp[3][1]) / 2) )
                    replace = -1
                    if mid[0] > cross_point[0] and mid[1] > cross_point[1]:
                        replace = 0
                    elif mid[0] > cross_point[0] and mid[1] < cross_point[1]:
                        replace = 0
                    elif mid[0] < cross_point[0] and mid[1] > cross_point[1]:
                        replace = 1
                    else:
                        replace = 1
                    #---
                    if replace == 0:
                        res = self.prune_check(tmp[0], all_line+result)
                        if res != None:
                            all_line.remove(res)

                        res = self.prune_check(tmp[1], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        else:
                            tmp[0] = cross_point
                            result.append(tmp)
                    else:
                        res = self.prune_check(tmp[1], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        res = self.prune_check(tmp[0], all_line+result)
                        if res != None:
                            all_line.remove(res)
                        else:
                            tmp[1] = cross_point
                            result.append(tmp)
                    break
            
            # decide the next ref_point
            # HP同時撞到兩條線，兩個參考點往下移動
            if len(which_line2) != 0:
                for i in l_set2:
                    if which_line2 == i:
                        tmp = i
                        all_line.remove(i)
                        tmp[0] = cross_point
                        result.append(tmp)
                        
                        break
                if ref_point[0] == which_line[2]:
                    ref_point[0] = which_line[3]
                else:
                    ref_point[0] = which_line[2]

                if ref_point[1] == which_line2[2]:
                    ref_point[1] = which_line2[3]
                else:
                    ref_point[1] = which_line2[2]
            # HP紙撞到一條線，移動一個參考點
            else:
                if ref_point[0] == which_line[2]:
                    ref_point[0] = which_line[3]
                elif ref_point[0] == which_line[3]:
                    ref_point[0] = which_line[2]
                elif ref_point[1] == which_line[2]:
                    ref_point[1] = which_line[3]
                else:
                    ref_point[1] = which_line[2]

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

        # 將剩下沒用到的線段放入result
        for i in all_line:
            result.append(i)

        # debug
        for i in p_set1+p_set2:
            self.draw_point(i)
        for i in hyperplane:
            self.draw_edge(i[0], i[1], "red")
        for i in result:
            self.draw_edge(i[0], i[1], "green")

        return hyperplane+result

    def recursive(self, point_set):

        # 小於3個點直接回傳voronoi
        if len(point_set) <= 3:
            result = self.v3points(point_set)
            self.visible_voronoi.append(result)
            return result
        
        # 點全都在x=k上
        same_xline = True
        check_x = point_set[0][0]
        for i in point_set:
            if check_x != i[0]:
                same_xline = False
                break
        if same_xline:
            sorted(list(point_set) , key=lambda k: [k[1], k[0]])
            _list = []
            result = []
            for i in range(len(point_set)):
                _list.append(i)
            for x1, x2 in zip(_list, _list[1:] + _list[:1]):
                self.draw_edge(point_set[x1], point_set[x2], "blue")
                mid = (point_set[x1][1] + point_set[x2][1]) / 2
                result.append([(0, mid), (800, mid), point_set[x1], point_set[x2]])
            self.visible_voronoi.append(result)
            return result
            
        midx = (point_set[0][0] + point_set[-1][0]) / 2
        idx = int(len(point_set) / 2)
        for i in range(len(point_set)):
            if point_set[i][0] > midx:
                idx = i
                break
            
        # _list = self.convex_order(point_set)
        # for x1, x2 in zip(_list, _list[1:] + _list[:1]):
        #     self.draw_edge(point_set[x1], point_set[x2], "blue")

        p_set1, p_set2 = point_set[:idx], point_set[idx:]
        # print(len(p_set1), len(p_set2))
        l_set1 = self.recursive(p_set1)
        l_set2 = self.recursive(p_set2)

        result = self.merge(p_set1, l_set1, p_set2, l_set2)
        self.visible_voronoi.append(result)
        return result

    def voronoi_step(self):
        if len(self.visible_points) == 0:
            return

        s = set(self.visible_points) # keep out same points
        gPoints = sorted(list(s) , key=lambda k: [k[0], k[1]])
        self.voronoi_final = self.recursive(gPoints)
        _list = self.convex_order(gPoints)

if __name__ == "__main__":
    pass
    # app = tk.Tk()
    # canvas = VCanvas(width=800, height=600, bg="white")
    # canvas.pack()
    # app.mainloop()
