from kivy.base import runTouchApp
from kivy.lang import Builder
runTouchApp(Builder.load_string('''
ActionBar:
    pos_hint: {'top':1}
    ActionView:
        use_separator: True
        ActionPrevious:
            title: 'M083140005'
            with_previous: False
        ActionButton:
            important: True
            text: 'READ'
        ActionButton:
            text: 'RESET'
        ActionButton:
            text: 'RUN'
        ActionButton:
            text: 'OUTPUT'
        ActionButton:
            text: 'QUIT'
'''))