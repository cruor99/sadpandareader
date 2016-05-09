from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, NumericProperty

from os.path import join
from functools import partial
from collections import deque

from BeautifulSoup import BeautifulSoup as BS

# Self made components
from components import GalleryScatter, GalleryImage, GalleryContainerLayout
from components import GalleryImageScreen, GalleryNavButton

import requests
import re

from models import db, Gallery, Pagelink

gesture_strings = {
    'leftright':
    "eNq1l81y2yAURve8SLyph8v9gxdwt53JA3ScRON40toaW2mbty9c5NiaaSplgReS/QEHwcFIWu1f9r/e1rvuPLyeOvd1PPferZ56cPd3h+3P7s71IX/NJ3Tn+7vzcDq+dOf8k9zqR89u9U/IvVVzvRSU5vb9cX8YSrNYmqUPmn0rtVwP9QrKJbzlJhDc5otf+wCCJMAY8xFDuZw/pRitmDnGRAG9SsrH6M4P2//3QtYLu92HHewu7OAJg3ELnefZNnDQBWySoOQttsJ5djR2asEONvMBFrAxcgS9TLfOz0kIxsYmbHMZlrjMS2OyTmgebjKDtoGbzXBj04cbZQikeuWDUtD47jPMG0UzitCMb1YRm/HNLHIzvslFbcY3v7jQr+fPrh8yvwTN+OaXsBnf/NISvwUvlK6FPL/Jk+klbYU3u5Qa4dnkMrTCm1vGRXhAJLjuerIAb2qZW+FNLWsrvKnlUW2m50Y3jwAQrvAAHlF47DrvD7NwMbECbeCmVXAJnKKmeLnPKsyzzanwEnbUwOky4zy/FYgJFW3CNpuyxCYG1gDwPuPzcDWbusQmCkH8zJOkmkxdIpN8EPrU5qtmU5fYJALwrJdCsDtfeSF4PHXd4f3xXqU83+c/3moDIGvvNsycT0Ov0W1LGCdhsjDAbRh9DXkSQg3TJAwW4tiR1BAtpDAJqYZxErKFPK0pNeR1uv1oqaG1htYaI2sM6/DET8I6PAm3YarDE5qEdXgik7AOTyYdpTy8OvXP3X73PORJT+Q2pYuc/d4/Dc8l4txizIbjj+60PTyWd7kkthuWeFwS3/vT8en10ThaOEIsghHztPqU75znh/VfvUm0YA==",
    'rightleft':
    "eNq1mNFu2zgQRd/1I/FLDQ6HM0P+gPu6QD5gkU2ExGg3EWx32/79UjNOI2IzJbFAxAc7o6Mr6t6RKGd3/HL85+f+cT5fvp3m6fP1cwnT7mGB6fbm+e7v+WZaYv1aP3A6396cL6eXL/O5/pmm3deFpt27IreKTQuvUlKPX16Oz5f1sLweVpzD/lipaQGbwTqFn/UQiNPhU9iHiCm/DgoR8jqhHyuA0yHsict2pOn8193vT5P0NDQ9/uYMj1dx3G4R++J66SBv4oEwvI5YAuIv8SR5M4Spr55VvQypx+3ALF31qP5H+CD1qOo4oo5bYzLnvrhmGmlIvN1Cv2Oihhrlg9Q11DgUamxaJiN31VFDRfggdQ0Vh0JtOiZBPbSrrqniNdUqDnEzvcxv0oE3g6DfjaiRonSlobGEZMATzRNLX5q2I/Rv/6RZJugrN9IJ+02YNMiEXenQ9gj0782kKaZ+im2IhXlg2hpj6scY2ucVQV9aY0y9GD/pns1AGuhs0iQJBsTflqZ19O0mTZJwQLpRpty3mzRKor42BNyO1L8jSaMkGdDGsh3cX5VJs6SBLEFoM5j782aNkgeijE2fQOnPmzVLHni8/j95jZNpTL5txDLgjCbKMibfNiMMzF5D5dJ/j6v7sHEnDqwQorkKjMm3Ldm/S0WTFRxTb5ty4EYVTVZoSD61z69VfH3lvz/N8/OvF/i68NU3eJFpd0iB92E6cEj147JInu7WYmqKxYq4LeZgRbAi1YZ422AFYAWqfy4QDWAXQAPQBZIBwQVIgVxcgA3wJykGiAtkA65Xwf8FigFpX7Zbep8u4ZV25IrZmtEFzNYcXcBszeACZmsOLmC2SnEBs1WyC5itIi5gtoprazFbhTwAglkpOGQ8BHjFXUFzVqJPmLUCPmHeSvAJM5eLT5i7nH3C7GXxCfOX2SfMYPYNBjOYk0+Yp4zNrjp/B48+Tu/g5jZH794EMLcZfOLqdvAJc5uKT5jblH3C3CbZPkHrsm7V5gkM0VwlaqvmJKW2aoYRtlXzhWJbNS8I2mq9flsjnubj49NF/1dTDY/tRUD9dVWZ78eHy5MiMh10hrV4efk6n+6e72fdkfU3y1q/rmZ/LqeXh2/3plxWZanrVlXMTAVjgHUF3P8LKvejwQ==",
}

from kivy.gesture import GestureDatabase, Gesture

gestures = GestureDatabase()

for name, gesture_string in gesture_strings.items():
    print name, gesture_string
    gesture = gestures.str_to_gesture(gesture_string)
    print gesture
    gesture.name = name
    gestures.add_gesture(gesture)


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

    def __init__(self, **kwargs):
        super(GalleryScreen, self).__init__(**kwargs)
        # list of previous screens
        for name in gesture_strings:
            self.register_event_type('on_{}'.format(name))

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

    def on_leftright(self):
        print "did it"
        self.next_image(self)

    def on_rightleft(self):
        self.previous_image(self)

    def on_touch_down(self, touch):
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GalleryScreen, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        try:
            touch.ud['gesture_path'].append((touch.x, touch.y))
        except:
            pass
        super(GalleryScreen, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'gesture_path' in touch.ud:
            gesture = Gesture()
            gesture.add_stroke(touch.ud['gesture_path'])
            gesture.normalize()
            match = gestures.find(gesture, minscore=0.6666660)
            if match:
                if match[1].name == "leftright":
                    self.next_image(self)
                if match[1].name == "rightleft":
                    self.previous_image(self)
                print("{} happened".format(match[1].name))
        super(GalleryScreen, self).on_touch_up(touch)

    def next_image(self, instance):
        pagelinks = db.query(Pagelink).filter_by(galleryid=self.db_id).all()

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
        imageroot = GalleryScatter()
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
