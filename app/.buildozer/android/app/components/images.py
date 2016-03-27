from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage as Image
from kivy.uix.screenmanager import Screen


class GalleryImageScreen(Screen):
    pass


class GalleryContainerLayout(FloatLayout, StencilView):
    pass


class GalleryScatter(ScatterLayout):
    pass


class GalleryImage(Image):
    pass
