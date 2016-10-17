from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty
from kivy.lang import Builder

from models import Settings

Builder.load_file("kv/settingsscreen.kv")


class SettingsScreen(Screen):
    title = StringProperty("Settings")
    settingvals = DictProperty({})

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.settingvals["logging"] = 0

    def on_enter(self):
        #self.db_settings()
        # Set slider values to values from database
        if self.settingvals['logging'] == 1:
            self.ids.logging.active = True

    def db_settings(self):
        db = App.get_running_app().db
        settings = db.query(Settings).first()

        self.settingvals['logging'] = settings.logging
