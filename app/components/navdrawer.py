from kivy.app import App
from YourApp.kivymd.navigationdrawer import MDNavigationDrawer
from YourApp.kivymd.navigationdrawer import NavigationLayout
from YourApp.kivymd.navigationdrawer import NavigationDrawerIconButton
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_file("kv/navdrawer.kv")


class SadpandaNavdrawer(MDNavigationDrawer):
    pass
