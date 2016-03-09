from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage as Image
from kivy.uix.stencilview import StencilView
from kivy.uix.button import Button


class ThumbButton(ButtonBehavior, Image):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    gallery_tags = ListProperty([])
    gallery_name = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_thumb = StringProperty("")


class GalleryButtonContainer(BoxLayout, StencilView):
    pass


class TagButton(Button):

    tagname = StringProperty("")
