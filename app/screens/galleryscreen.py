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

from models import Gallery, Pagelink


class GalleryScreen(Screen):

    db_id = NumericProperty(0)
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagelinks = DictProperty([])
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    nextpage = NumericProperty(0)
    current_page = NumericProperty(1)
    title = gallery_name
    scrollstopper = BooleanProperty(False)
    galleryscreen = ObjectProperty()
    gotpageresultcounter = NumericProperty(99)
    gallery_images = ListProperty([])

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        # list of previous screens
        self.bind(galleryscreen=self.on_galleryscreen)

    def on_galleryscreen(self, instance, value):
        self.ids.gallery_manager.switch_to(value)

    def on_enter(self):
        db = App.get_running_app().db
        gallery = db.query(Gallery).filter_by(
            gallery_id=self.gallery_id).first()
        self.db_id = gallery.id
        self.gallery_id = gallery.gallery_id
        self.gallery_token = gallery.gallery_token
        self.pagecount = gallery.pagecount
        self.gallery_name = gallery.gallery_name
        self.populate_gallery()

    def on_leave(self):
        self.db_id = 0
        self.gallery_id = ""
        self.gallery_token = ""
        self.pagelinks = []
        self.pagecount = 0
        self.gallery_name = ""
        self.current_page = 1
        self.ids.gal_image.source = ""

    def populate_gallery(self):
        # change placehold.it with

        db = App.get_running_app().db
        gallerypages = float(self.pagecount) / float(40)
        pageregex = re.compile('http\S{0,1}?://' + App.get_running_app()
                               .root.baseurl + '.org/s/\S{10}/\d{6}-\d+')

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

        self.next_page = 1

    def on_gotpageresultcounter(self, result, something):
        db = App.get_running_app().db
        if int(something) == 0:
            currentexist = db.query(Pagelink).filter_by(
                galleryid=self.db_id, current=1).first()
            pagelinkmodels = db.query(Pagelink).filter_by(
                galleryid=self.db_id).order_by(Pagelink.mainpage).all()
            if currentexist:
                for page in pagelinkmodels:
                    if page.pagelink == currentexist.pagelink:
                        self.current_page = pagelinkmodels.index(page) +1
                self.construct_image(currentexist.pagelink)
            else:

                Clock.schedule_once(self.load_firstpage, 1)

    def load_firstpage(self, *args):

        db = App.get_running_app().db
        firstdbimage = db.query(Pagelink).filter_by(
            galleryid=self.db_id).filter_by(mainpage=0).first()

        self.construct_image(firstdbimage.pagelink)
        firstdbimage.current = 1
        db.commit()
        pagelinkmodels = db.query(Pagelink).filter_by(
            galleryid=self.db_id).order_by(Pagelink.mainpage).all()
        for page in pagelinkmodels:
            pagenumber = page.pagelink.split("-")[-1]
            self.pagelinks[pagenumber] = page.pagelink
        self.gotpageresultcounter = 99
        self.current_page = 1

    def got_result(self, req, r):


        #pageregex = re.compile('http\S{0,1}?://' + App.get_running_app()
        pageregex = re.compile('http\S?://' + App.get_running_app()
                               .root.baseurl + '.org/s/\S{10}/\d{0,10}-\d+')
        soup = BS(r)
        for a in soup.findAll(name="a", attrs={"href": pageregex}):
            pagelink = a["href"]
            pagenumber = a["href"].split("-")[-1]
            self.pagelinks[pagenumber] = pagelink
            db = App.get_running_app().db
            existpageurl = db.query(Pagelink).filter_by(
                pagelink=a["href"]).first()
            if existpageurl:
                pass
            else:
                pageurl = Pagelink(
                    galleryid=self.db_id,
                    pagelink=a["href"],
                    mainpage=req.url[:-2][-1:])
                db.add(pageurl)
                db.commit()
        self.gotpageresultcounter = req.url[:-2][-1:]

    def testmove(self, offset, min_move, direction):
        # Logger.info("Offset: {}".format(offset))
        if self.ids.gal_image.scale > 1:
            return
        if self.scrollstopper is False:
            if offset > 150:
                self.scrollstopper = True
                #self.ids.gallery_manager.transition.direction = "right"
                self.previous_image(self)
                Clock.schedule_once(self.togglestopper, 1)
            else:
                pass
            if offset < -140:
                self.scrollstopper = True
                #self.ids.gallery_manager.transition.direction = "left"
                self.next_image(self)
                Clock.schedule_once(self.togglestopper, 1)
            else:
                pass

    def togglestopper(self, *args):
        self.scrollstopper = False

    def next_image(self, dt):
        db = App.get_running_app().db
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).order_by(Pagelink.mainpage).all()

        #self.ids.gallery_manager.transition.direction = "left"
        for page in pagelinks:
            if page.current == 1:
                page_number = page.pagelink.split("-")[-1]
                print("PAGE_NUM: {}".format(page_number))
                newpageindex = int(self.current_page) + 1
                pages = []
                for pagenum in self.pagelinks.keys():
                    pages.append(int(pagenum))
                maxpage = max(pages)
                minpage = min(pages)
                print("MAX PAGES: {}".format(maxpage))
                print("MIN PAGES: {}".format(minpage))
                if newpageindex == maxpage +1:
                    print(maxpage)
                    self.current_page = minpage
                    newpageindex = self.current_page
                    Snackbar(text="End of Gallery").show()
                else:
                    print("Test newpageindex: {}".format(newpageindex))
                    self.current_page = newpageindex
                try:
                    print("NEWPAGEINDEX: {}".format(newpageindex))
                    newpage = pagelinks[newpageindex - 1]
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    break
                except:
                    # Create a end of gallery popup
                    Snackbar(text="End of Gallery").show()
                    self.current_page = minpage
                    newpage = pagelinks[0]
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    break

    def previous_image(self, instance):
        db = App.get_running_app().db
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).order_by(Pagelink.mainpage).all()

        #self.ids.gallery_manager.transition.direction = "right"
        for page in pagelinks:
            if page.current == 1:
                page_number = page.pagelink.split("-")[-1]
                newpageindex = int(self.current_page) - 1
                pages = []
                for pagenum in self.pagelinks.keys():
                    pages.append(int(pagenum))
                maxpages = max(pages)
                minpages = min(pages)
                if newpageindex == 0:
                    newpageindex = maxpages
                self.current_page = newpageindex
                try:
                    print(len(pagelinks))
                    newpage = pagelinks[newpageindex - 1]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                except Exception as e:
                    # Create start of gallery popup
                    print(e)
                    newpage = pagelinks[len(pagelinks)-1]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)

    def construct_image(self, pagelink):
        src = self.grab_image(pagelink)
        self.temppagelink = pagelink

    temp_gallery_images = ListProperty([])
    def push_image(self, src):
        new_gal_img = {}
        new_gal_img["scale"] = 1
        new_gal_img["pos"] = self.pos
        new_gal_img["source"] = src
        #new_gal_img["width"] = self.ids.container_layout.width
        #new_gal_img["height"] = self.ids.container_layout.height
        self.gallery_images.append(new_gal_img)
        if self.current_page < self.pagecount:
            Clock.schedule_once(self.next_image, .1)
        else:
            Logger.info(self.gallery_images)

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

        soup = BS(r)

        srctag = soup.findAll(name="img")

        for each in srctag:
            if re.match(ipmatch, each['src']):
                src = each['src']

        self.push_image(src)
