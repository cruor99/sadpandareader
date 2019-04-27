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
    unviewed_gallery_images = ListProperty([])
    adding_image = BooleanProperty(False)
    gallery_pages = NumericProperty(0)
    gallery_pages_raw_html = DictProperty({})
    gallery_images = ListProperty([])
    page_grab_schedule = ListProperty([])
    current_page = NumericProperty(0)
    gathered_images = DictProperty({})
    loading_new_page = BooleanProperty(False)
    base_headers = {
        'User-agent': 'Mozilla/5.0',
        "Cookie": "",
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        self.base_headers["Cookie"] = App.get_running_app().root.cookies
        self.ids.gal_rv.bind(scroll_y=self.manage_gallery_scroll)

    def on_enter(self):
        gallery = App.get_running_app().root.current_gallery
        self.gallery_id = gallery.gallery_id
        self.gallery_token = gallery.gallery_token
        self.pagecount = gallery.pagecount
        self.gallery_name = gallery.gallery_name
        self.gallery_pages = float(self.pagecount) / float(40)
        if self.gallery_pages.is_integer():
            pass
        else:
            self.gallery_pages += 1
        self.gathered_images[0] = []
        Clock.schedule_once(self.grab_all_image_pages)

    def on_leave(self, *args):
        self.db_id = 0
        self.gallery_id = ""
        self.gallery_token = ""
        self.pagelinks = {}
        self.pagecount = 0
        self.gallery_name = ""
        self.nextpage = 0
        self.title = self.gallery_name
        self.scrollstopper = False
        self.gotpageresultcounter = 99
        self.unviewed_gallery_images = []
        self.adding_image = False
        self.gallery_pages = 0
        self.gallery_pages_raw_html = []
        self.gallery_images = []
        self.page_grab_schedule = []
        self.current_page = 0
        self.gathered_images = {}
        self.ids.gal_rv.scroll_y = 1
        self.loading_new_page = False

    def grab_all_image_pages(self, *args):
        for i in range(int(self.gallery_pages)):
            url = "http://{}.org/g/{}/{}/?p={}".format(App.get_running_app().root.baseurl, self.gallery_id,
                                                       self.gallery_token, i)
            gallery_pages_request = UrlRequest(url, on_success=self.got_url_page, req_headers=self.base_headers)

    def got_url_page(self, req, r):
        Logger.info("Gallery Page URL: {}".format(req.url))
        self.gallery_pages_raw_html[int(req.url.split("=")[-1])] = r
        if len(self.gallery_pages_raw_html.keys()) == int(self.gallery_pages):
            Logger.info("All Gallery Pages aquired")
            Logger.info("All Gallery Page Keys: {}".format(self.gallery_pages_raw_html.keys()))
            Clock.schedule_once(partial(self.find_image_pages_for_page, self.current_page))

    def find_image_pages_for_page(self, page, *args):
        Logger.info("Finding imagepages for: Page {}".format(page))
        # TODO: Set Loading spinner here
        try:
            if len(self.gathered_images[self.current_page]) > 0:
                Clock.schedule_once(partial(self.set_new_viewdata, self.gathered_images[self.current_page]))
            else:
                page_html = self.gallery_pages_raw_html[page]
                image_page_pattern = re.compile('http\S?://' + App.get_running_app()
                                                .root.baseurl + '.org/s/\S{10}/\d{0,10}-\d+')
                soup = BS(page_html, features="html.parser")
                pagelinks = []
                for a in soup.findAll(name="a", attrs={"href": image_page_pattern}):
                    pagelink = a["href"]
                    pagenumber = a["href"].split("-")[-1]
                    pagelinks.append(pagelink)

                self.gathered_images[self.current_page] = []
                Clock.schedule_once(partial(self.gather_images, pagelinks))
        except KeyError as e:
            Logger.exception(e)
            page_html = self.gallery_pages_raw_html[page]
            image_page_pattern = re.compile('http\S?://' + App.get_running_app()
                                            .root.baseurl + '.org/s/\S{10}/\d{0,10}-\d+')
            soup = BS(page_html, features="html.parser")
            pagelinks = []
            for a in soup.findAll(name="a", attrs={"href": image_page_pattern}):
                pagelink = a["href"]
                pagenumber = a["href"].split("-")[-1]
                pagelinks.append(pagelink)

            self.gathered_images[self.current_page] = []
            Clock.schedule_once(partial(self.gather_images, pagelinks))

    """
    gathered_images data structure:
    {
        0: [
            {69156825: "http://109.247.137.118:32512/h/8d4cc11e0919552c2db3f09855d2a0f67f208d07-264081-1280-1813-jpg/keystamp=1556392500-f995059836;fileindex=69156825;xres=1280/74408685_p0.jpg"},
            {69035695: "http://46.246.123.94:28979/h/80b885784fd06a27e12baf8ccf023c4a63def709-270036-1280-1813-jpg/keystamp=1556392500-f9c793de09;fileindex=69035695;xres=1280/74331271_p0.jpg"}
        ]
    }
    """


    def gather_images(self, pagelinks, *args):
        Logger.info("Amount of pages to process: {}".format(len(pagelinks)))
        for page in pagelinks:
            pagerequest = UrlRequest(page, on_success=self.image_loaded, req_headers=self.base_headers)

    def image_loaded(self, req, r):
        ipmatch = r'^http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

        soup = BS(r, features="html.parser")

        srctag = soup.findAll(name="img")
        for each in srctag:
            if re.match(ipmatch, each['src']):
                src = each['src']
        Logger.info("Direct Image File: {}".format(src))
        split_link = src.split(";")
        for component in split_link:
            key, value = component.split("=")
            if key == "fileindex":
                self.gathered_images[self.current_page].append({int(value): src})
        # TODO: The or clause here needs to be fixed.
        if len(self.gathered_images[self.current_page]) % 40 == 0 or self.current_page == int(self.gallery_pages - 1):
            Logger.info("Fully gathered images: {}".format(self.gathered_images))
            sorted_list = sorted(self.gathered_images[self.current_page], key=lambda d: list(d.keys()))
            self.gathered_images[self.current_page] = sorted_list
            Logger.info("Sorted list: {}".format(sorted_list))
            Clock.schedule_once(partial(self.set_new_viewdata, sorted_list))

    def set_new_viewdata(self, sorted_list, *args):
        # TODO: Remove loading spinner here
        self.gallery_images = []
        for imagedict in sorted_list:
            for fileindex, imagelink in imagedict.items():
                new_gallery_image = {}
                new_gallery_image["scale"] = 1
                new_gallery_image["post"] = self.pos
                new_gallery_image["source"] = imagelink
                new_gallery_image["fileindex"] = fileindex
                Logger.info("Appending final image to viewdata: {}".format(new_gallery_image))
                self.gallery_images.append(new_gallery_image)
        self.loading_new_page = False

    def manage_gallery_scroll(self, instance, scroll):
        Logger.info("Scroll: {}".format(scroll))
        if scroll < -0.004 and not self.loading_new_page:
            Logger.info("Triggering new page")
            Logger.info("Current page: {}".format(self.current_page))
            total_pages_comparison = self.gallery_pages - 1
            print(int(total_pages_comparison))
            if int(total_pages_comparison) > self.current_page:
                self.loading_new_page = True
                self.ids.gal_rv.scroll_y = 1
                self.current_page += 1
                Logger.info("Going to new page: {}".format(self.current_page))
                Clock.schedule_once(partial(self.find_image_pages_for_page, self.current_page))
        elif scroll > 1.1 and not self.loading_new_page:
            Logger.info("Triggering previous page")
            Logger.info("Current page: {}".format(self.current_page))
            if self.current_page > 0:
                self.ids.gal_rv.scroll_y = 0
                self.loading_new_page = True
                self.current_page -= 1
                Logger.info("Going to previous page: {}".format(self.current_page))
                Clock.schedule_once(partial(self.find_image_pages_for_page, self.current_page))

