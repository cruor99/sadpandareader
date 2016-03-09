from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, NumericProperty

from os.path import join
from functools import partial

from BeautifulSoup import BeautifulSoup as BS

# Self made components
from components import GalleryScatter, GalleryImage, GalleryContainerLayout

import requests
import re


class GalleryScreen(Screen):

    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagelinks = ListProperty([])
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    nextpage = NumericProperty(0)
    current_page = NumericProperty(0)

    global data_dir

    def on_enter(self):
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]
        self.ids.gallery_carousel.clear_widgets()
        gallery_store = JsonStore(join(data_dir, 'gallerystore.json'))
        if gallery_store.exists("current_gallery"):
            galleryinfo = gallery_store.get("current_gallery")
            self.gallery_id = galleryinfo["galleryinfo"][0]
            self.gallery_token = galleryinfo["galleryinfo"][1]
            self.pagecount = galleryinfo["galleryinfo"][2]
            self.gallery_name = galleryinfo["galleryinfo"][3]
        self.populate_gallery()

    def on_leave(self):
        self.ids.gallery_carousel.clear_widgets()
        self.gallery_id = ""
        self.gallery_token = ""
        self.pagelinks = []
        self.pagecount = 0
        self.gallery_name = ""

    def populate_gallery(self):
        # change placehold.it with
        gallerypages = float(self.pagecount) / float(40)
        pageregex = re.compile('http://'+App.get_running_app().root.baseurl+'.org/s/\S{10}/\d{6}-\d+')

        if gallerypages.is_integer():
            pass
        else:
            gallerypages += 1

        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        for i in range(int(gallerypages)):
            galleryrequest = requests.get("http://"+App.get_running_app().root.baseurl+".org/g/{}/{}/?p={}\
                                          ".format(self.gallery_id,
                                          self.gallery_token, i),
                                          headers=headers, cookies=cookies)

            soup = BS(galleryrequest.text)

            for a in soup.findAll(name="a", attrs={"href": pageregex}):
                self.pagelinks.append(a["href"])

        # pagetimer = 0
        # for page in self.pagelinks:
        #   Clock.schedule_once(partial(self.grab_image, page), 2*pagetimer)
        #    pagetimer += 1

        self.next_page = 1
        self.grab_image(self.pagelinks[0])

    def load_next(self):
        try:
            nextpage_url = self.pagelinks[self.next_page]
            Clock.schedule_once(partial(self.grab_image, nextpage_url))
            self.next_page += 1
            nextpage_url = self.pagelinks[self.next_page]
            Clock.schedule_once(partial(self.grab_image, nextpage_url))
            self.next_page += 1
        except:
            print "test"

    def grab_image(self, i, *largs):
        gallerycontainer = GalleryContainerLayout()
        self.ids.gallery_carousel.add_widget(gallerycontainer)
        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        pagerequest = requests.get(url=i, headers=headers, cookies=cookies)

        soup = BS(pagerequest.text)

        srctag = soup.findAll(name="img", attrs={"id": "img"})
        for each in srctag:
            src = each["src"]
        image = GalleryImage(source=src, allow_stretch=True)
        imageroot = GalleryScatter()
        imageroot.add_widget(image)
        gallerycontainer.add_widget(imageroot)
