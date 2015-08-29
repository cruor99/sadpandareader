from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.image import AsyncImage as Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar

from os.path import join
from functools import partial
#from bs4 import BeautifulSoup as BS

import requests
import json
import time


data_dir = ""


class ThumbButton(ButtonBehavior, Image):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")


class FrontScreen(Screen):

    global data_dir


    pb = ProgressBar(max=1500)
    gallery_thumbs = ListProperty([])
    gidlist = ListProperty([])

    def on_enter(self):

        for galleries in self.gallery_thumbs:
            self.ids.main_layout.remove_widget(galleries)

        self.pb.value = 0
        self.gallery_thumbs = []

        for i in range(15):
            Clock.schedule_once(self.increasepb, i)

        self.ids.main_layout.add_widget(self.pb)

        Clock.schedule_once(self.populate_front, 15)

    def increasepb(self, state):
        self.pb.value += 100
        if self.pb.value == 1500:
            self.ids.main_layout.remove_widget(self.pb)

    def enter_gallery(self, state):
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        galleryinfo = [state.gallery_id, state.gallery_token]
        gallery_store.put("current_gallery", galleryinfo=galleryinfo)
        self.manager.current="gallery_screen"

    def populate_front(self, state):
        """
        # ehentai link
        r = requests.get("")
        # pure html of ehentai link
        data = r.text

        soup = BS(data)
        gallerylinks = []

        # grabs all the divs with class it5 which denotes the gallery on the
        # page
        for link in soup.find_all('div', {'class': 'it5'})
            # grabs all the links, should only be gallery links as of 29th of
            # august 2015
            gallerylinks.append(link.find('a')["href"])

        for link in gallerylinks:
            splitlink = link.split('/')
            #grab the gallery token
            gtoken = splitlink[:-2]
            #grab the gallery id
            gid = splitlink[:-3]
            gidlist.append[gid, gtoken]

        """
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        payload = {
            "method": "gdata",
            "gidlist": self.gidlist
            }


        Clock.schedule_once(partial(self.grabthumbs, headers, payload), 5)

    def grabthumbs(self, headers, payload, *largs):
        """
        r = requests.post("http://g.e-hentai.org/api.php",
                          data=json.dumps(payload), headers=headers)
        print(r.content)
        requestjson = json.loads(str(r.content))
        print(requestjson[0]["thumb"])
        for gallery in requestjson["gmetadata"]:
            gallerybutton = ThumbButton(
                    source=gallery["thumb"], gallery_id=gallery["gid"],
                    gallery_token=gallery["token"])
            gallerybutton.bind(on_press=self.enter_gallery)
            self.ids.main_layout.add_widget(gallerybutton)
        """
        placeholderbutton = ThumbButton(
                source="img/sadpanda.jpeg", gallery_id="gid",
                gallery_token="gtok")
        placeholderbutton.bind(on_press=self.enter_gallery)
        self.gallery_thumbs.append(placeholderbutton)

        for galleries in self.gallery_thumbs:
            self.ids.main_layout.add_widget(galleries)








class GalleryScreen(Screen):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")

    global data_dir

    def on_enter(self):
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        if gallery_store.exists("current_gallery"):
            galleryinfo = gallery_store.get("current_gallery")
            self.gallery_id = galleryinfo["galleryinfo"][0]
            self.gallery_token = galleryinfo["galleryinfo"][1]
        self.populate_gallery()

    def populate_gallery(self):
        # change placehold.it with 
        src = "http://placehold.it/480x270.png&text=slide-1&png" 
        image = Image(source=src, allow_stretch=True)
        self.ids.gallery_carousel.add_widget(image)


        for i in range(13):
            i+=1
            Clock.schedule_once(partial(self.grab_image, i), 15*i)

    def grab_image(self, i, *largs):
        print(i)
        src = "http://placehold.it/480x270.png&text=slide-%d&png" % i
        image = Image(source=src, allow_stretch=True)
        self.ids.gallery_carousel.add_widget(image)



class SadpandaRoot(BoxLayout):

    def __init__(self, **kwargs):
        super(SadpandaRoot, self).__init__(**kwargs)
        # list of previous screens
        self.screen_list = []

    def next_screen(self, neoscreen):

        if self.ids.sadpanda_screen_manager.current not in self.screen_list:
            self.screen_list.append(self.ids.sadpanda_screen_manager.current)

        self.ids.sadpanda_screen_manager.current = neoscreen


class SadpandaApp(App):

    def __init__(self, **kwargs):
        super(SadpandaApp, self).__init__(**kwargs)
        global data_dir
        data_dir = getattr(self, 'user_data_dir')

    def on_pause(self):
        return True

    def build(self):
        return SadpandaRoot()

if __name__ == "__main__":
    SadpandaApp().run()
