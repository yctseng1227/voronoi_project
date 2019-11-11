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
#Config.set("graphics", "width", "800")
#Config.set("graphics", "height", "647")

gPoints = []

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
            stream.write(str(gPoints))
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
            imgDisplay = np.hstack([self.ids.my_canvas.image])
            cv2.imshow("Sample", imgDisplay)
            cv2.waitKey(500)
        cv2.destroyAllWindows()

    def step_by_step(self):
        pass
        # draw line

class MainApp(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()
