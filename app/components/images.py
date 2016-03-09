from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage as Image


class GalleryContainerLayout(BoxLayout, StencilView):
    pass


class GalleryScatter(ScatterLayout):
    pass


class GalleryImage(Image):
    pass
