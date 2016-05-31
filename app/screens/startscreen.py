from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.storage.jsonstore import JsonStore

from os.path import join

from models import User, db

import json
import ast


class StartScreen(Screen):


    def on_enter(self):

        Clock.schedule_once(self.check_cookies)

    def check_cookies(self, *args):
        user = db.query(User).first()
        if user:
            cookies = ast.literal_eval(user.cookies)
            App.get_running_app().root.cookies = cookies
            App.get_running_app().root.baseurl = "exhentai"
            App.get_running_app().root.next_screen("front_screen")
        else:
            pass
