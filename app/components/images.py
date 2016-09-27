from kivy.uix.floatlayout import FloatLayout
from kivy.uix.carousel import Carousel
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage as Image
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_file("kv/images.kv")


class GalleryImageScreen(Screen):
    pass


class GalleryContainerLayout(FloatLayout, StencilView):
    pass


class GalleryCarousel(Carousel):

    def startmove(self, *args):
        try:
            self.parent.parent.parent.parent.parent.testmove(self._offset, self.min_move, self.direction)
        except:
            print "Not attached to parent yet"


class GalleryImage(Image):
    pass
