from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.properties import BooleanProperty
from kivy.clock import Clock

from BeautifulSoup import BeautifulSoup as BS

# Self made components
from components import GalleryCarousel, GalleryImage, GalleryContainerLayout
from components import GalleryImageScreen, GalleryNavButton

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
    title = gallery_name
    scrollstopper = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        # list of previous screens

    def on_enter(self):
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
        gallerypages = float(self.pagecount) / float(40)
        pageregex = re.compile('http://' + App.get_running_app().root.baseurl +
                               '.org/s/\S{10}/\d{6}-\d+')

        if gallerypages.is_integer():
            pass
        else:
            gallerypages += 1

        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        for i in range(int(gallerypages)):
            galleryrequest = requests.get(
                "http://" + App.get_running_app().root.baseurl +
                ".org/g/{}/{}/?p={}\
                                          "
                .format(self.gallery_id, self.gallery_token, i),
                headers=headers,
                cookies=cookies)

            soup = BS(galleryrequest.text)

            for a in soup.findAll(name="a", attrs={"href": pageregex}):
                self.pagelinks.append(a["href"])
                existpageurl = db.query(Pagelink).filter_by(
                    pagelink=a["href"]).first()
                if existpageurl:
                    pass
                else:
                    pageurl = Pagelink(galleryid=self.db_id,
                                       pagelink=a["href"])
                    db.add(pageurl)
                    db.commit()

        # pagetimer = 0
        # for page in self.pagelinks:
        #   Clock.schedule_once(partial(self.grab_image, page), 2*pagetimer)
        #    pagetimer += 1

        self.next_page = 1

        currentexist = db.query(Pagelink).filter_by(galleryid=self.db_id,
                                                    current=1).first()
        if currentexist:
            first_screen = self.construct_image(currentexist.pagelink)
            self.ids.gallery_manager.switch_to(first_screen)
        else:
            first_screen = self.construct_image(self.pagelinks[0])
            self.ids.gallery_manager.switch_to(first_screen)
            # consider adding this in its own thread
            firstimage = db.query(Pagelink).filter_by(
                pagelink=self.pagelinks[0]).first()
            firstimage.current = 1
            db.commit()

    def testmove(self, offset, min_move, direction):
        print "Did it"
        print offset
        print min_move
        print direction
        print self.scrollstopper
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
        print "Toggled scrollstopper"
        self.scrollstopper = False

    def next_image(self, instance):
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).all()

        print self.scrollstopper
        self.ids.gallery_manager.transition.direction = "left"
        for page in pagelinks:
            if page.current == 1:
                newpageindex = pagelinks.index(page) + 1
                try:
                    newpage = pagelinks[newpageindex]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    self.ids.gallery_manager.switch_to(newscreen)
                    break
                except:
                    # Create a end of gallery popup
                    pass

    def previous_image(self, instance):
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).all()

        self.ids.gallery_manager.transition.direction = "right"
        print self.scrollstopper
        for page in pagelinks:
            if page.current == 1:
                newpageindex = pagelinks.index(page) - 1
                try:
                    newpage = pagelinks[newpageindex]
                    newpage.current = 1
                    page.current = 0
                    db.commit()
                    newscreen = self.construct_image(newpage.pagelink)
                    self.ids.gallery_manager.switch_to(newscreen)
                    break
                except:
                    # Create start of gallery popup
                    pass

    def construct_image(self, pagelink):
        src = self.grab_image(pagelink)
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
        galleryscreen = GalleryImageScreen(id=pagelink)
        galleryscreen.add_widget(gallerycontainer)

        return galleryscreen

    def grab_image(self, i):
        headers = {'User-agent': 'Mozilla/5.0'}
        cookies = App.get_running_app().root.cookies
        pagerequest = requests.get(url=i, headers=headers, cookies=cookies)

        soup = BS(pagerequest.text)

        srctag = soup.findAll(name="img", attrs={"id": "img"})
        for each in srctag:
            src = each["src"]

        return src
