FONTS[1]["fn_regular"] = "fonts/NotoSansCJK-Regular.ttc"
FONTS[1]["fn_bold"] = "fonts/NotoSansCJK-Regular.ttc"
FONTS[1]["fn_italic"] = "fonts/NotoSansCJK-Regular.ttc"
FONTS[1]["fn_bolditalic"] = "fonts/NotoSansCJK-Regular.ttc"
for font in FONTS:
    LabelBase.register(**font)

class SadpandaRoot(BoxLayout):

    cookies = StringProperty()
    username = StringProperty("")
    password = StringProperty("")
    baseurl = StringProperty("g.e-hentai")
    edgemove = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SadpandaRoot, self).__init__(**kwargs)
        # list of previous screens
        self.screen_list = []
        #self.pusher = Pusher("")
    #        self.pusher.connect()
    #       self.pusher.bind_channel_simple("1111")
    #      self.sel = SubscriptionEventListener()
    #     self.pusher.bind_event("send", self.sel)

    def on_touch_down(self, touch):
        if touch.x < dp(30):
            self.edgemove = True
        else:
            self.edgemove = False
        super(SadpandaRoot, self).on_touch_down(touch)


    def on_touch_move(self, touch):
        if touch.x < dp(30):
            pass
        else:
            if self.edgemove:
                self.edgemove = False
                self.onBackBtn()
            else:
                pass
        super(SadpandaRoot, self).on_touch_move(touch)


    def default_settings(self):
        db = App.get_running_app().db
        if db.query(Settings).first() != None:
            pass
        else:
            db.add(Settings(logging=0))
            db.commit()

    def login_exhentai(self, username, password):
        db = App.get_running_app().db
        self.username = username.text
        self.password = password.text

        payload = {
            "UserName": username.text,
            "PassWord": password.text,
            "returntype": "8",
            "CookieDate": "1",
            "b": "d",
            "bt": "pone"
        }
        headers = {'User-Agent': 'Mozilla/5.0',
                   "Content-type": "application/x-www-form-urlencoded"}

        params = urllib.urlencode(payload)

        req = UrlRequest(
            "https://forums.e-hentai.org/index.php?act=Login&CODE=01",
            on_success=self.login_attempt,
            on_failure=self.login_failure,
            on_error=self.login_error,
            req_body=params,
            req_headers=headers)

    def login_failure(self, req, r):
        print "failure"
        print req.resp_headers
        print req
        print r

    def login_error(self, req, error):
        print "error"
        print req.resp_headers
        print req
        print error

    def login_attempt(self, req, r):
        db = App.get_running_app().db
        finalcookies = ""
        if "ipb_pass_hash" in req.resp_headers["set-cookie"]:
            cookies = req.resp_headers["set-cookie"].split(";")
            for cookie in cookies:
                print cookie
                if "ipb" in cookie:
                    splitcookie = cookie.split(",")
                    try:
                        finalcookies += splitcookie[1] + ";"
                    except:
                        finalcookies += splitcookie[0] + ";"

            print finalcookies
            self.cookies = finalcookies[:-1]
            cookies = User(cookies=str(self.cookies))
            db.add(cookies)
            db.commit()
            self.baseurl = "exhentai"
            self.goto_front()
        else:
            captchapopup = CaptchaPopup()
            captchapopup.bind(on_dismiss=self.login_captcha)
            captchapopup.open()

    def log_out(self):
        try:
            db = App.get_running_app().db
            user = db.query(User).first()
            db.delete(user)
            db.commit()
        except:
            pass
        self.baseurl = "g.e-hentai"
        self.next_screen("start_screen")

    def login_captcha(self, instance):
        if instance.action == "try_again":
            pass
        else:
            self.baseurl = "g.e-hentai"
            self.goto_front()

    def next_screen(self, neoscreen):

        db = App.get_running_app().db
        self.screen_list.append(self.ids.sadpanda_screen_manager.current)

        if self.ids.sadpanda_screen_manager.current == neoscreen:
            cur_screen = self.ids.sadpanda_screen_manager.get_screen(neoscreen)
            cur_screen.new_search()
            search = db.query(Search).order_by(Search.id.desc()).first()
            newsearch = search.searchterm
            cur_screen.searchword = newsearch
        else:
            self.ids.sadpanda_screen_manager.current = neoscreen

    def goto_front(self):
        if not self.ids.sadpanda_screen_manager.has_screen("front_screen"):
            from screens.frontscreen import FrontScreen
            self.ids.sadpanda_screen_manager.add_widget(
                FrontScreen(name="front_screen"))
        blanksearch = Search(searchterm=" ")
        db = App.get_running_app().db
        db.add(blanksearch)
        db.commit()
        self.next_screen("front_screen")

    def start_search(self, instance):
        db = App.get_running_app().db
        front_screen = self.ids.sadpanda_screen_manager.get_screen(
            "front_screen")
        searchword = front_screen.searchword
        search = db.query(Search).order_by(Search.id.desc()).first()
        if search:
            newsearch = search.searchterm
        else:
            newsearch = " "
        if newsearch == searchword:
            pass
        else:
            self.next_screen("front_screen")

    def search_popup(self):
        spopup = SearchPopup()
        spopup.bind(on_dismiss=self.start_search)
        spopup.open()

    def onBackBtn(self):
        # check if there are screens we can go back to
        if self.screen_list:
            currentscreen = self.screen_list.pop()
            self.ids.sadpanda_screen_manager.current = currentscreen
            # Prevents closing of app
            return True
        # no more screens to go back to, close app
        return False

    def show_filters(self):
        fpop = FilterPopup()
        fpop.bind(on_dismiss=self.set_filters)
        fpop.open()

    def set_filters(self, instance):
        db = App.get_running_app().db
        filters = {
            "doujinshi": 0,
            "manga": 0,
            "artistcg": 0,
            "gamecg": 0,
            "western": 0,
            "nonh": 0,
            "imageset": 0,
            "cosplay": 0,
            "asianporn": 0,
            "misc": 0
        }
        if instance.ids.doujinshi.active == True:
            filters["doujinshi"] = 1
        if instance.ids.manga.active == True:
            filters["manga"] = 1
        if instance.ids.artistcg.active == True:
            filters["artistcg"] = 1
        if instance.ids.gamecg.active == True:
            filters["gamecg"] = 1
        if instance.ids.western.active == True:
            filters["western"] = 1
        if instance.ids.nonh.active == True:
            filters["nonh"] = 1
        if instance.ids.imageset.active == True:
            filters["imageset"] = 1
        if instance.ids.cosplay.active == True:
            filters["cosplay"] = 1
        if instance.ids.asianporn.active == True:
            filters["asianporn"] = 1
        if instance.ids.misc.active == True:
            filters["misc"] = 1

        newfilter = Filters(
            doujinshi=filters["doujinshi"],
            manga=filters["manga"],
            artistcg=filters["artistcg"],
            gamecg=filters["gamecg"],
            western=filters["western"],
            nonh=filters["nonh"],
            imageset=filters["imageset"],
            cosplay=filters["cosplay"],
            asianporn=filters["asianporn"],
            misc=filters["misc"])
        db.add(newfilter)
        db.commit()


class SadpandaApp(App):

    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def __init__(self, **kwargs):
        super(SadpandaApp, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.onBackBtn)
        Window.softinput_mode = "below_target"
        data_dir = getattr(self, "user_data_dir")
        self.data_dir = data_dir
        #defaultdir = Config.getdefault("kivy", "log_dir", data_dir)
        #if defaultdir == data_dir:
        #    pass
        #else:
        #    Config.set("kivy", "log_dir", data_dir)
        #    Config.set("kivy", "log_enable", 1)
        #    Config.set("kivy", "log_level", "debug")
        #    Config.write()
        self.db = check_database(data_dir)
        migrationjsonstore = JsonStore("migrate.json")
        migration = migrationjsonstore.get("migrate")
        if migration["migration"] == "true":
            os.remove(data_dir + "/database.db")
            self.db = check_database(data_dir)
            migrationjsonstore.put("migrate", migration="false")
        else:
            pass
        # Makes sure only non-h is the default.
        existfilters = self.db.query(Filters).order_by(Filters.id.desc(
        )).first()
        if existfilters:
            pass
        else:
            clearstart = Filters(
                nonh=1,
                doujinshi=0,
                manga=0,
                artistcg=0,
                gamecg=0,
                western=0,
                imageset=0,
                cosplay=0,
                asianporn=0,
                misc=0)
            self.db.add(clearstart)
            self.db.commit()
        clearsearch = Search(searchterm=" ")
        self.db.add(clearsearch)
        self.db.commit()

    def onBackBtn(self, window, key, *args):
        # user presses back button
        if key == 27:
            return self.root.onBackBtn()

    def on_pause(self):
        return True


    def build(self):
        #print FONTS[0]
        self.nav_drawer = SadpandaNavdrawer()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Grey"
        self.theme_cls.primary_hue = "900"

        return SadpandaRoot()


if __name__ == "__main__":
    SadpandaApp().run()
