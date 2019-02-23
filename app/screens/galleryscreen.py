from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.properties import BooleanProperty, DictProperty
from kivy.clock import Clock
import urllib
from kivy.network.urlrequest import UrlRequest
from kivymd.snackbar import Snackbar
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.recycleview import RecycleView

Builder.load_file("kv/galleryscreen.kv")

from bs4 import BeautifulSoup as BS

# Self made components
from components.images import GalleryCarousel, GalleryImage, GalleryContainerLayout, GalleryImageScreen
from components.buttons import GalleryNavButton

import re
import time
from functools import partial

from models import Gallery, Pagelink


class GalleryScreen(Screen):

    db_id = NumericProperty(0)
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagelinks = DictProperty({})
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    nextpage = NumericProperty(0)
    current_page = NumericProperty(1)
    title = gallery_name
    scrollstopper = BooleanProperty(False)
    galleryscreen = ObjectProperty()
    gotpageresultcounter = NumericProperty(99)
    gallery_images = ListProperty([])
    page_grab_schedule = ListProperty([])

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        # list of previous screens
        self.bind(galleryscreen=self.on_galleryscreen)

    def on_galleryscreen(self, instance, value):
        self.ids.gallery_manager.switch_to(value)

    def on_enter(self):
        gallery = App.get_running_app().root.current_gallery
        Logger.info("Gallery: {}".format(gallery))
        self.gallery_id = gallery.gallery_id
        self.gallery_token = gallery.gallery_token
        self.pagecount = gallery.pagecount
        self.gallery_name = gallery.gallery_name
        self.populate_gallery()

    def on_leave(self):
        self.gallery_images = []
        try:
            for scheduled_page in self.page_grab_schedule:
                Clock.unschedule(scheduled_page)
        except Exception as e:
            Logger.exception(e)
        self.gallery_id = ""
        self.gallery_token = ""
        self.pagelinks = []
        self.pagecount = 0
        self.gallery_name = ""
        self.current_page = 1
        self.page_grab_schedule = []

    def populate_gallery(self):
        gallerypages = float(self.pagecount) / float(40)
        if gallerypages.is_integer():
            pass
        else:
            gallerypages += 1

        headers = {'User-agent': 'Mozilla/5.0',
                   "Cookie": "",
                   "Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        cookies = App.get_running_app().root.cookies
        headers["Cookie"] = cookies
        for i in range(int(gallerypages)):
            url = str("http://" + App.get_running_app(
            ).root.baseurl + ".org/g/{}/{}/?p={}\ "
                      .format(self.gallery_id, self.gallery_token, i))
            galleryrequest = UrlRequest(
                url, on_success=self.got_result, req_headers=headers)

    def on_gotpageresultcounter(self, result, something):
        if int(something) == 0:
            for pagenumber, page in self.pagelinks.items():
                Logger.info("Page {}: {}".format(pagenumber, page))
                self.page_grab_schedule.append(Clock.schedule_once(partial(self.construct_image, page), int(pagenumber)/2))

    def got_result(self, req, r):
        pageregex = re.compile('http\S?://' + App.get_running_app()
                               .root.baseurl + '.org/s/\S{10}/\d{0,10}-\d+')
        soup = BS(r, features="html.parser")
        for a in soup.findAll(name="a", attrs={"href": pageregex}):
            pagelink = a["href"]
            pagenumber = a["href"].split("-")[-1]
            self.pagelinks[pagenumber] = pagelink
        self.gotpageresultcounter = req.url[:-2][-1:]

    def construct_image(self, pagelink, *args):
        src = self.grab_image(pagelink)
        self.temppagelink = pagelink

    def push_image(self, src):
        new_gal_img = {}
        new_gal_img["scale"] = 1
        new_gal_img["pos"] = self.pos
        new_gal_img["source"] = src
        self.gallery_images.append(new_gal_img)

    def grab_image(self, i):
        headers = {'User-agent': 'Mozilla/5.0',
                   "Cookie": "",
                   "Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        cookies = App.get_running_app().root.cookies
        headers["Cookie"] = cookies
        pagerequest = UrlRequest(
            url=i, on_success=self.got_image, req_headers=headers)

    def got_image(self, req, r):
        ipmatch = r'^http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

        soup = BS(r, features="html.parser")

        srctag = soup.findAll(name="img")

        for each in srctag:
            if re.match(ipmatch, each['src']):
                src = each['src']

        self.push_image(src)
