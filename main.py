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
import sys
import os
import cv2
import numpy as np


Window.size = (800, 647)

class draw_voronoi:
    pass


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class RootWidget(BoxLayout):
    # def __init__(self, **kwargs):
    #     super(RootWidget, self).__init__(**kwargs)
    #     cb = CustomBtn()
    #     # cb.bind(pressed=self.btn_pressed)
    #     self.add_widget(cb)

    # def btn_pressed(self, instance, pos):
    #    print("pos: printed from root widget: {pos}".format(pos=pos))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as f:
            print("load: ", os.path.join(path, filename[0]))
            # print(f.read())
            
            line = f.readline()
            while line:
                if len(line) > 0 and line[0] != "#":
                    if len(line.split()) == 1:
                        n = int(line.split()[0])
                        if n == 0:
                            exit()
                        points = []
                        for _ in range(n):
                            tmp = f.readline()
                            points.append(tuple(map(int, tmp.split())))
                        print(points)

                line = f.readline()

        self.dismiss_popup()

    def clean_canvas(self):
        # self.canvas.clear() # also clear bar
        with self.canvas:
            Color(rgba=[1,1,1,1])
            Rectangle(pos=self.pos, size=(800,600))


class CustomBtn(Widget):

    pressed = ListProperty([0, 0])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):

            # draw point
            with self.canvas:
                Color(1, 0, 0)
                d = 5.0
                Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            self.pressed = touch.pos

            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            return True
        return super(CustomBtn, self).on_touch_down(touch)

    def on_pressed(self, instance, pos):
        print("pressed at {pos}".format(pos=pos))


class ReadFile:
    def __init__(self):
        file = open(sys.argv[1], "r", encoding="UTF-8")
        line = file.readline()

        while line:
            if len(line) > 0 and line[0] != "#":
                if len(line.split()) == 1:
                    n = int(line.split()[0])
                    if n == 0:
                        exit()
                    points = []
                    for _ in range(n):
                        tmp = file.readline()
                        points.append(tuple(map(int, tmp.split())))
                    print(points)
            line = file.readline()
        file.close()


class MainApp(App):
    def build(self):
        if len(sys.argv) > 1:
            return ReadFile()
        else:
            return RootWidget()


if __name__ == "__main__":
    MainApp().run()
