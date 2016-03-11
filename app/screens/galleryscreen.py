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

from models import db, Gallery, Pagelink


class GalleryScreen(Screen):

    db_id = NumericProperty(0)
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagelinks = ListProperty([])
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    nextpage = NumericProperty(0)
    current_page = NumericProperty()

    global data_dir

    def on_enter(self):
        self.ids.gallery_carousel.clear_widgets()
        gallery = db.query(Gallery).order_by(Gallery.id.desc()).first()
        self.db_id = gallery.id
        self.gallery_id = gallery.gallery_id
        self.gallery_token = gallery.gallery_token
        self.pagecount = gallery.pagecount
        self.gallery_name = gallery.gallery_name
        self.populate_gallery()

    def on_leave(self):
        self.ids.gallery_carousel.clear_widgets()
        self.db_id = 0
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
                existpageurl = db.query(Pagelink).filter_by(pagelink=a["href"]).first()
                if existpageurl:
                    pass
                else:
                    pageurl = Pagelink(galleryid=self.db_id, pagelink=a["href"])
                    db.add(pageurl)
                    db.commit()

        # pagetimer = 0
        # for page in self.pagelinks:
        #   Clock.schedule_once(partial(self.grab_image, page), 2*pagetimer)
        #    pagetimer += 1

        self.next_page = 1
        self.grab_image(self.pagelinks[0])

    def load_next(self):
        currentslide = self.ids.gallery_carousel.current_slide
        children = self.ids.gallery_carousel.slides
        self.current_page += 1
        if self.current_page > children.index(currentslide):
            print self.current_page, "current page"
            print children.index(currentslide), "current slide"
            print "gone back"
            #excesspos = children.index(currentslide) + 3
            #excesswidget = children[excesspos]
            #try:
            #    self.ids.gallery_carousel.slides.remove(excesswidget)
            #    self.ids.gallery_carousel.load_next()
            #except:
            #    print "Nothing to remove"
        elif self.current_page < children.index(currentslide):
            print "gone forwards"
            excesspos = children.index(currentslide) - 3
            if excesspos >= 0:
                try:
                    excesswidget = children[excesspos]
                    self.ids.gallery_carousel.slides.remove(excesswidget)
                    self.ids.gallery_carousel.load_previous()
                except:
                    print "Nothing to remove"
        try:
            nextpage_url = self.pagelinks[self.next_page]
            Clock.schedule_once(partial(self.grab_image, nextpage_url))
            self.next_page += 1
        except:
            print "test"

    def grab_image(self, i, *largs):
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
        gallerycontainer = GalleryContainerLayout(id=src)
        gallerycontainer.add_widget(imageroot)
        self.ids.gallery_carousel.add_widget(gallerycontainer)
