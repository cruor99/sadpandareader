from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.properties import StringProperty


class GalleryTitle(BoxLayout, StencilView):

    titletext = StringProperty("")
