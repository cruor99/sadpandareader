from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.properties import StringProperty
from kivy.uix.label import Lable
from kivymd.label import MDLabel


class GalleryTitle(BoxLayout, StencilView, Label, MDLabel):

    titletext = StringProperty("")
