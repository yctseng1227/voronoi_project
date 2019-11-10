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


Window.size = (800,647)
#Config.set("graphics", "width", "800")
#Config.set("graphics", "height", "647")

points = []

class Voronoi(Image):
    def __init__(self, img):
        self.img = img

    def draw_voronoi(self, subdiv):
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
            cv2.fillConvexPoly(self.img, ifacet, color, cv2.LINE_AA, 0)

            # Draw facet boundary
            ifacets = np.array([ifacet])
            cv2.polylines(self.img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)

            # Draw centers.
            cv2.circle(self.img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), -1, cv2.LINE_AA, 0)
 

class FullImage(Image):
    def __init__(self, **kwargs):
        super(FullImage, self).__init__(**kwargs)

        width, height = 800, 600
        self.image = 255 * np.ones(shape=[height, width, 3], dtype=np.uint8)
        self.Image = "image.png"
        cv2.imwrite(self.Image, self.image)
        self.source = self.Image

    def on_touch_down(self, pos):
        position = int(pos.x), 600 - int(pos.y)
        cv2.circle(self.image, position, 1, (0, 0, 255), 2)
        cv2.imwrite(self.Image, self.image)

        # lock bar : (x, -y)
        if position[0] > 0 and position[1] > 0:
            points.append(position)
            print("draw:", position)
        self.reload()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
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
            
            line = stream.readline()
            while line:
                if len(line) > 0 and line[0] != "#":
                    if len(line.split()) == 1:
                        n = int(line.split()[0])
                        if n == 0:
                            exit()
                        points = []
                        for _ in range(n):
                            tmp = stream.readline()
                            points.append(tuple(map(int, tmp.split())))
                        print(points)
                line = stream.readline()

        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(str(points))

        self.dismiss_popup()

    def clean_canvas(self):
        # self.canvas.clear() # also clear bar
        with self.canvas:
            Color(rgba=[1,1,1,1])
            Rectangle(pos=self.pos, size=(800,600))
        points.clear()
    
    def draw_voronoi(self):
        print(points)

        img = FullImage()
        #imgVoronoi = np.zeros(img.image.shape, dtype=img.image.dtype)
        subdiv = cv2.Subdiv2D(rect = (0, 0, img.image.shape[1], img.image.shape[0]))
        v = Voronoi(img.image)

        for p in points:
            subdiv.insert(p)
            v.draw_voronoi(subdiv)

            # Display as an animation
            imgDisplay = np.hstack([img.image])
            cv2.imshow("Voro", imgDisplay)
            cv2.waitKey(500)
        sys.exit() # TODO


# class CustomBtn(Widget):

#     pressed = ListProperty([0, 0])

#     def on_touch_down(self, touch):
#         if self.collide_point(*touch.pos):

#             # draw point
#             with self.canvas:
#                 Color(1, 0, 0)
#                 d = 5.0
#                 Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
#             self.pressed = touch.pos

#             # we consumed the touch. return False here to propagate
#             # the touch further to the children.
#             return True
#         return super(CustomBtn, self).on_touch_down(touch)

#     def on_pressed(self, instance, pos):
#         print("pressed at {pos}".format(pos=pos))


class MainApp(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()
