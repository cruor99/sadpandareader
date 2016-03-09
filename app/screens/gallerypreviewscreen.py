from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import ListProperty, StringProperty, NumericProperty

from os.path import join

# Self made components
from components import TagButton


class GalleryPreviewScreen(Screen):

    gallery_tags = ListProperty([])
    gallery_id = StringProperty("")
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    gallery_token = StringProperty("")
    gallery_thumb = StringProperty("")

    global data_dir

    def on_enter(self):
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        gallery_store = JsonStore(join(data_dir, "gallerystore.json"))
        if gallery_store.exists("current_gallery"):
            galleryinfo = gallery_store.get("current_gallery")
            self.gallery_id = galleryinfo["galleryinfo"][0]
            self.gallery_token = galleryinfo["galleryinfo"][1]
            self.pagecount = galleryinfo["galleryinfo"][2]
            self.gallery_name = galleryinfo["galleryinfo"][3]
            self.gallery_tags = galleryinfo["galleryinfo"][4]
            self.gallery_thumb = galleryinfo["galleryinfo"][5]

        Clock.schedule_once(self.populate_tags)

    def populate_tags(self, *args):
        self.ids.tag_layout.clear_widgets()
        for tag in self.gallery_tags:
            taglabel = TagButton(tagname=tag)
            taglabel.bind(on_press=self.search_tag)
            self.ids.tag_layout.add_widget(taglabel)

    def view_gallery(self):
        App.get_running_app().root.next_screen("gallery_screen")

    def search_tag(self, instance):

        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        search_store = JsonStore(join(data_dir, "search_store.json"))
        tag = instance.text
        search_store.put("searchstring", searchphrase=tag)
        App.get_running_app().root.next_screen("front_screen")
