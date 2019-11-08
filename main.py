from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty

from kivy.graphics import Color, Ellipse

import sys

from kivy.lang import Builder


class draw_voronoi():
    pass

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        cb = CustomBtn()
        # cb.bind(pressed=self.btn_pressed)
        self.add_widget(cb)

    def btn_pressed(self, instance, pos):
        print("pos: printed from root widget: {pos}".format(pos=pos))


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
    from kivy.base import runTouchApp
    from kivy.lang import Builder

    runTouchApp(Builder.load_string('''
ActionBar:
    background_color:0,191,255,0.5
    pos_hint: {'top':1}
    ActionView:
        use_separator: True
        ActionPrevious:
            title: 'M083140005'
            with_previous: False
        ActionOverflow:
        ActionButton:
            important: True
            text: 'LOAD'
        ActionButton:
            text: 'RESET'
        ActionButton:
            text: 'RUN'
        ActionButton:
            text: 'OUTPUT'
        ActionButton:
            text: 'QUIT'
'''))
    MainApp().run()
