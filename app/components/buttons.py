from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage as Image
from kivy.uix.stencilview import StencilView
from kivy.uix.button import Button
from kivymd.button import MDFlatButton, MDRaisedButton
from kivymd.list import TwoLineAvatarListItem, ILeftBodyTouch


class ThumbButton(TwoLineAvatarListItem):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    gallery_tags = ListProperty([])
    gallery_name = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_thumb = StringProperty("")
    filesize = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ThumbButton, self).__init__(**kwargs)
        if len(self.gallery_name) > 110:
            self.secondary_text = self.gallery_name[:110] + "..."
        else:
            self.secondary_text = self.gallery_name


class AvatarSampleWidget(ILeftBodyTouch, Image):
    pass


class TagButton(MDRaisedButton):

    tagname = StringProperty("")


class GalleryNavButton(Button):
    pass
