# Algorithm project by m083140005
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, ObjectProperty
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image

import sys
import os
import cv2
import random
import numpy as np
# import parser

Window.size = (800, 647)

gPoints = []
gEdges = []

class NoNextPointsError(RuntimeError):
    pass

class Painter(Image):
    def __init__(self, **kwargs):
        super(Painter, self).__init__(**kwargs)
        self.h = 600
        self.w = 800
        self.Image = "image.png"
        self.fill_white().save()
        self.source = self.Image
        self.subset_points = iter([])
        
    def save(self):
        cv2.imwrite(self.Image, self.image)

    def draw_point(self, point):
        cv2.circle(self.image, point, 1, (0, 0, 255), 2)
        return self

    def points(self, points):
        for point in points:
            self.draw_point(point)
        return self

    def edge(self, point_1, point_2):
        cv2.line(self.image, point_1, point_2, (255, 0, 0), 2)
        return self
        
    def fill_white(self):
        self.image = 255 * np.ones(shape=[self.h, self.w, 3], dtype=np.uint8)
        return self

    def on_touch_down(self, pos):
        if self.collide_point(*pos.pos):
            position = int(pos.x), 600 - int(pos.y)
            print(position)
            gPoints.append(position)
            self.draw_point(position).save()
            self.reload()

    def set_subset_points(self, points):
        self.subset_points = iter(points)

    def next_points(self):
        self.fill_white()
        subset_points = next(self.subset_points, None)
        print(subset_points)

        if subset_points is None:
            raise NoNextPointsError("error...")

        self.points(subset_points)
        global gPoints 
        gPoints = subset_points

        return self
    
    def voronoi_sample(self, subdiv):
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
            cv2.fillConvexPoly(self.image, ifacet, color, cv2.LINE_AA, 0)

            # Draw facet boundary
            ifacets = np.array([ifacet])
            cv2.polylines(self.image, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)

            # Draw centers.
            cv2.circle(self.image, (centers[i][0], centers[i][1]), 3, (0, 0, 0), -1, cv2.LINE_AA, 0)
    
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
    def reload_mycanvas(self):
        self.ids.my_canvas.reload()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            print("load: ", os.path.join(path, filename[0]))
            # print(stream.read())

            all_points = []
            line = stream.readline()
            while line:
                if len(line) > 0 and line[0] != "#" and len(line.split()) == 1:
                    n = int(line.split()[0])
                    if n == 0:
                        break
                    
                    points = []
                    for _ in range(n):
                        tmp = stream.readline()
                        subpoint = tuple(map(int, tmp.split()))
                        points.append(subpoint)

                    all_points.append(points)
                    print(points)
                line = stream.readline()
        print(all_points)
        self.ids.my_canvas.set_subset_points(all_points)
        self.next()
        self.ids.next_button.disabled = False
        self.dismiss_popup()

    def next(self):
        try:
            self.ids.my_canvas.next_points().save()
        except NoNextPointsError:
            self.ids.my_canvas.save()
            self.ids.next_button.disabled = True
            self.clean_canvas()
        self.reload_mycanvas()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            string = '\n'.join([f'P {x} {y}' for (x, y) in gPoints])
            stream.write(string+'\n')
            string = '\n'.join([f'E {x1} {y1} {x2} {y2}' for (x1, y1, x2, y2) in gEdges])
            stream.write(string)

        self.dismiss_popup()

    def clean_canvas(self):
        self.ids.my_canvas.fill_white().save()
        self.reload_mycanvas()
        gPoints.clear()

    def draw_voronoi(self):
        print(gPoints)

        #imgVoronoi = np.zeros(img.image.shape, dtype=img.image.dtype)
        subdiv = cv2.Subdiv2D(rect = (0, 0, self.ids.my_canvas.image.shape[1], self.ids.my_canvas.image.shape[0]))

        for p in gPoints:
            subdiv.insert(p)
            self.ids.my_canvas.voronoi_sample(subdiv)

            # Display as an animation
            # imgDisplay = np.hstack([self.ids.my_canvas.image])
            # cv2.imshow("Sample", imgDisplay)
            # cv2.waitKey(500)
        cv2.destroyAllWindows()
        self.ids.my_canvas.save()
        self.reload_mycanvas()

    def cercle_circonscrit(self, points):
        (x1, y1), (x2, y2), (x3, y3) = points
        A = np.array([[x3-x1,y3-y1],[x3-x2,y3-y2]])
        Y = np.array([(x3**2 + y3**2 - x1**2 - y1**2),(x3**2+y3**2 - x2**2-y2**2)])
        if np.linalg.det(A) == 0:
            return False
        Ainv = np.linalg.inv(A)
        X = 0.5*np.dot(Ainv,Y)
        x,y = X[0],X[1]
        return (int(x), int(y))

    def slope_intercept(self, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        midx = (x1 + x2) / 2
        midy = (y1 + y2) / 2

        if y2 - y1 == 0:
            return (midx, -1), -1, -1
        a = (x1 - x2) / (y2 - y1)
        b = midy - a * midx

        return (midx, midy), a, b

    # False: obtuse angle
    def which_triangle(self, p1, p2, p3):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        res = (x1-x2) * (x1-x3) + (y1-y2) * (y1-y3)
        return False if res < 0 else True

    def step_by_step(self):
        global gPoints
        s = set(gPoints) # keep out same points
        gPoints = list(s)

        if len(gPoints) == 3:
            center = self.cercle_circonscrit(gPoints)
            if not center:
                if gPoints[0] == gPoints[1] == gPoints[2]:
                    pass
                elif gPoints[0][0] == gPoints[1][0] == gPoints[2][0]: # 3 points collinearity -x
                    l = [ gPoints[0][1], gPoints[1][1], gPoints[2][1] ]
                    l.sort()
                    mid = (l[0]+l[1]) / 2
                    self.ids.my_canvas.edge((0, int(mid)), (800, int(mid))).save()
                    gEdges.append((0, int(mid), 800, int(mid)))

                    mid = (l[1]+l[2]) / 2
                    self.ids.my_canvas.edge((0, int(mid)), (800, int(mid))).save()
                    gEdges.append((0, int(mid), 800, int(mid)))
                elif gPoints[0][1] == gPoints[1][1] == gPoints[2][1]: # 3 points collinearity -y
                    l = [ gPoints[0][0], gPoints[1][0], gPoints[2][0] ]
                    l.sort()
                    mid = (l[0]+l[1]) / 2
                    self.ids.my_canvas.edge((int(mid), 0), (int(mid), 600)).save()
                    gEdges.append((int(mid), 0, int(mid), 600))

                    mid = (l[1]+l[2]) / 2
                    self.ids.my_canvas.edge((int(mid), 0), (int(mid), 600)).save()
                    gEdges.append((int(mid), 0, int(mid), 600))
                else:
                    pass
                   
            else:
                mid, a, b = self.slope_intercept(gPoints[0], gPoints[1])
                angle = self.which_triangle(gPoints[2], gPoints[0], gPoints[1])
                if mid[1] != -1:
                    x = 800 if center[0]<mid[0] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    self.ids.my_canvas.edge(center, (x, int(a*x+b))).save()
                    gEdges.append((center[0], center[1], x, int(a*x+b)))
                else: # |
                    y = 600 if center[1]>mid[1] else 0
                    self.ids.my_canvas.edge(center, (center[0], y)).save()
                    gEdges.append((center[0], center[1], center[0], y))

                mid, a, b = self.slope_intercept(gPoints[0], gPoints[2])
                angle = self.which_triangle(gPoints[1], gPoints[0], gPoints[2])
                if mid[1] != -1: 
                    x = 800 if center[0]<mid[0] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    self.ids.my_canvas.edge(center, (x, int(a*x+b))).save()
                    gEdges.append((center[0], center[1], x, int(a*x+b)))
                else: # |
                    y = 600 if center[1]>mid[1] else 0
                    self.ids.my_canvas.edge(center, (center[0], y)).save()
                    gEdges.append((center[0], center[1], center[0], y))

                mid, a, b = self.slope_intercept(gPoints[1], gPoints[2])
                angle = self.which_triangle(gPoints[0], gPoints[1], gPoints[2])
                if mid[1] != -1:
                    x = 800 if center[0]<mid[0] else 0
                    if(not angle): # if obtuse angle, reverse direction
                        x = abs(x - 800)
                    self.ids.my_canvas.edge(center, (x, int(a*x+b))).save()
                    gEdges.append((center[0], center[1], x, int(a*x+b)))
                else: # |
                    y = 600 if center[1]>mid[1] else 0
                    self.ids.my_canvas.edge(center, (center[0], y)).save()
                    gEdges.append((center[0], center[1], center[0], y))

            self.reload_mycanvas()

        elif len(gPoints) == 2:
            mid, a, b = self.slope_intercept(gPoints[0], gPoints[1])
            if mid[1] != -1:
                self.ids.my_canvas.edge((0, int(b)), (800, int(a*800+b))).save()
                gEdges.append((0, int(b), 800, int(a*800+b)))
            else:
                self.ids.my_canvas.edge((int(mid[0]), 0), (int(mid[0]), 600)).save()
                gEdges.append((int(mid[0]), 0, int(mid[0]), 600))
            self.reload_mycanvas()
        else:
            pass

class MainApp(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()