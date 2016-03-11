from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.storage.jsonstore import JsonStore

from os.path import join

from models import User, db

import json
import ast


class StartScreen(Screen):

    global data_dir

    def on_enter(self):

        Clock.schedule_once(self.check_cookies)

    def check_cookies(self, *args):
        data_dir_store = JsonStore("user_data_dir.json")
        data_dir = data_dir_store["data_dir"]["data_dir"]

        user = db.query(User).first()
        if user:
            cookies = ast.literal_eval(user.cookies)
            print cookies, "cookies here"
            print type(cookies)
            App.get_running_app().root.cookies = cookies
            App.get_running_app().root.baseurl = "exhentai"
            App.get_running_app().root.next_screen("front_screen")
        else:
            pass
