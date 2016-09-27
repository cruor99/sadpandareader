from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.properties import BooleanProperty
from kivy.clock import Clock
import urllib
from kivy.network.urlrequest import UrlRequest
import kivymd.snackbar as Snackbar
from kivy.lang import Builder

Builder.load_file("kv/galleryscreen.kv")

from BeautifulSoup import BeautifulSoup as BS

# Self made components
from components.images import GalleryCarousel, GalleryImage, GalleryContainerLayout, GalleryImageScreen
from components.buttons import GalleryNavButton

import re

from models import Gallery, Pagelink


class GalleryScreen(Screen):

    db_id = NumericProperty(0)
    gallery_id = StringProperty("")
    gallery_token = StringProperty("")
    pagelinks = ListProperty([])
    pagecount = NumericProperty(0)
    gallery_name = StringProperty("")
    nextpage = NumericProperty(0)
    current_page = NumericProperty()
    title = gallery_name
    scrollstopper = BooleanProperty(False)
    galleryscreen = ObjectProperty()

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        # list of previous screens
        print "initiated"
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

        galleryrequest.wait()

        currentexist = db.query(Pagelink).filter_by(
            galleryid=self.db_id, current=1).first()
        if currentexist:
            for page in self.pagelinks:
                if page == currentexist.pagelink:
                    self.current_page = self.pagelinks.index(page)
            self.construct_image(currentexist.pagelink)
        else:
            spliturl = self.pagelinks[0].split("-")
            print spliturl
            if App.get_running_app().root.baseurl == "g.e-hentai":
                pageurl = "".join(spliturl[0]) + "-" + spliturl[1] + "-" + "1"
            else:
                pass

            self.construct_image(self.pagelinks[0])
            firstimage = db.query(Pagelink).filter_by(
                pagelink=self.pagelinks[0]).first()
            firstimage.current = 1
            db.commit()

    def got_result(self, req, r):

        pageregex = re.compile('http\S{0,1}?://' + App.get_running_app()
                               .root.baseurl + '.org/s/\S{10}/\d{6}-\d+')
        soup = BS(r)
        for a in soup.findAll(name="a", attrs={"href": pageregex}):
            self.pagelinks.append(a["href"])
            db = App.get_running_app().db
            existpageurl = db.query(Pagelink).filter_by(
                pagelink=a["href"]).first()
            if existpageurl:
                pass
            else:
                pageurl = Pagelink(galleryid=self.db_id, pagelink=a["href"])
                db.add(pageurl)
                db.commit()

    def testmove(self, offset, min_move, direction):
        if self.scrollstopper is False:
            if offset > 1:
                self.scrollstopper = True
                self.ids.gallery_manager.transition.direction = "right"
                self.previous_image(self)
                Clock.schedule_once(self.togglestopper, 1)
            else:
                pass
            if offset < -1:
                self.scrollstopper = True
                self.ids.gallery_manager.transition.direction = "left"
                self.next_image(self)
                Clock.schedule_once(self.togglestopper, 1)
            else:
                pass

    def togglestopper(self, *args):
        self.scrollstopper = False

    def next_image(self, instance):
        db = App.get_running_app().db
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).all()

        self.ids.gallery_manager.transition.direction = "left"
        for page in pagelinks:
            if page.current == 1:
                newpageindex = pagelinks.index(page) + 1
                if newpageindex == len(pagelinks):
                    self.current_page = 0
                else:
                    self.current_page = newpageindex
                try:
                    newpage = pagelinks[newpageindex]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    break
                except:
                    # Create a end of gallery popup
                    Snackbar.make("End of Gallery")
                    newpage = pagelinks[0]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    break

    def previous_image(self, instance):
        db = App.get_running_app().db
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).all()

        self.ids.gallery_manager.transition.direction = "right"
        for page in pagelinks:
            if page.current == 1:
                newpageindex = pagelinks.index(page) - 1
                if newpageindex == -1:
                    newpageindex = len(pagelinks) - 1
                self.current_page = newpageindex
                try:
                    newpage = pagelinks[newpageindex]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                except:
                    # Create start of gallery popup
                    pass

    def construct_image(self, pagelink):
        src = self.grab_image(pagelink)
        self.temppagelink = pagelink

    def push_image(self, src):
        image = GalleryImage(source=src, allow_stretch=True)
        imageroot = GalleryCarousel()
        gallerycontainer = GalleryContainerLayout()
        imageroot.add_widget(image)
        forwardsbutton = GalleryNavButton(pos_hint={"x": 0.8})
        forwardsbutton.bind(on_release=self.next_image)
        backwardsbutton = GalleryNavButton(pos_hint={"x": 0.01})
        backwardsbutton.bind(on_release=self.previous_image)
        gallerycontainer.add_widget(imageroot)
        gallerycontainer.add_widget(backwardsbutton)
        gallerycontainer.add_widget(forwardsbutton)
        galleryscreen = GalleryImageScreen(id=self.temppagelink)
        galleryscreen.add_widget(gallerycontainer)

        self.galleryscreen = galleryscreen

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
