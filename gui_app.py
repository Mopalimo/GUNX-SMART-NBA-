
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex


BG = "#070D1B"
PANEL = "#101C33"
BLUE = "#087DFF"
GOLD = "#F5B900"
WHITE = "#FFFFFF"
MUTED = "#A9B8D0"
GREEN = "#19D66B"



class GunxCard(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(13)
        self.spacing = dp(8)

        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(*get_color_from_hex(PANEL))
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class GunxButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = get_color_from_hex(BLUE)
        self.color = get_color_from_hex(WHITE)
        self.bold = True
        self.font_size = sp(13)


class GunxSmartNBAApp(App):

    def build(self):
        self.title = "GUNX SMART NBA"

        Window.clearcolor = get_color_from_hex(BG)

        self.root_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(8)
        )

        self.build_header()
        self.build_navigation()

        self.manager = ScreenManager()

        pages = [
            ("home", self.home_page),
            ("daily", self.daily_page),
            ("analysis", self.analysis_page),
            ("odds", self.odds_page),
            ("performance", self.performance_page),
            ("live", self.live_page),
            ("history", self.history_page),
            ("about", self.about_page),
        ]

        for name, function in pages:
            screen = Screen(name=name)
            screen.add_widget(function())
            self.manager.add_widget(screen)

        self.root_layout.add_widget(self.manager)
        self.build_bottom_navigation()

        return self.root_layout

    def label(self, text, size=14, color=WHITE,
              bold=False, height=None):
        return Label(
            text=str(text),
            font_size=sp(size),
            color=get_color_from_hex(color),
            bold=bold,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(height or 34),
            text_size=(None, None)
        )

    def build_header(self):
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            padding=[dp(12), dp(7)],
            spacing=dp(3)
        )

        with header.canvas.before:
            Color(*get_color_from_hex("#0B1934"))
            header.bg = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[dp(15)]
            )

        header.bind(
            pos=lambda obj, value: setattr(obj.bg, "pos", value),
            size=lambda obj, value: setattr(obj.bg, "size", value)
        )

        header.add_widget(self.label(
            "👑 GUNX SMART NBA",
            25, GOLD, True, 40
        ))

        header.add_widget(self.label(
            "ANALYZE  •  PREDICT  •  WIN",
            12, WHITE, True, 23
        ))

        header.add_widget(self.label(
            "🏀 NBA INTELLIGENCE CENTER",
            11, MUTED, True, 22
        ))

        self.root_layout.add_widget(header)

    def build_navigation(self):
        nav = ScrollView(
            size_hint_y=None,
            height=dp(48),
            do_scroll_y=False
        )

        row = BoxLayout(
            size_hint_x=None,
            spacing=dp(5)
        )
        row.bind(minimum_width=row.setter("width"))

        items = [
            ("HOME", "home"),
            ("DAILY 10", "daily"),
            ("AI ANALYSIS", "analysis"),
            ("ODDS", "odds"),
            ("PERFORMANCE", "performance"),
        ]

        for title, page in items:
            btn = GunxButton(
                text=title,
                size_hint_x=None,
                width=dp(112),
                background_color=get_color_from_hex("#142B50")
            )
            btn.bind(
                on_release=lambda instance, p=page:
                self.open_page(p)
            )
            row.add_widget(btn)

        nav.add_widget(row)
        self.root_layout.add_widget(nav)

    def build_bottom_navigation(self):
        nav = BoxLayout(
            size_hint_y=None,
            height=dp(54),
            spacing=dp(4)
        )

        items = [
            ("⌂ HOME", "home"),
            ("▥ LIVE", "live"),
            ("★ PICKS", "daily"),
            ("◷ HISTORY", "history"),
            ("ⓘ ABOUT", "about"),
        ]

        for title, page in items:
            btn = Button(
                text=title,
                font_size=sp(10),
                bold=True,
                background_normal="",
                background_color=get_color_from_hex("#14233D"),
                color=get_color_from_hex(WHITE)
            )
            btn.bind(
                on_release=lambda instance, p=page:
                self.open_page(p)
            )
            nav.add_widget(btn)

        self.root_layout.add_widget(nav)

    def open_page(self, page):
        self.manager.current = page

    def make_page(self):
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3)
        )

        content = BoxLayout(
            orientation="vertical",
            padding=dp(5),
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        scroll.add_widget(content)
        return scroll, content

    def add_card(self, parent, title, description):
        card = GunxCard()
        card.add_widget(self.label(
            title, 17, GOLD, True, 35
        ))
        card.add_widget(self.label(
            description, 13, MUTED, False, 45
        ))
        parent.add_widget(card)
        return card

    def home_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "WELCOME TO GUNX SMART NBA",
            18, GOLD, True, 42
        ))

        content.add_widget(self.label(
            datetime.now().strftime("%A, %d %B %Y"),
            12, MUTED, False, 25
        ))

        self.add_card(
            content,
            "🏆 DAILY TOP 10",
            "Your strongest verified NBA predictions will appear here."
        )

        self.add_card(
            content,
            "🧠 AI ANALYSIS",
            "Team form • Offensive rating • Defensive rating • Pace"
        )

        self.add_card(
            content,
            "📊 ODDS CENTER",
            "Over/Under • Match totals • Probability • Fair odds"
        )

        self.add_card(
            content,
            "🔴 LIVE NBA SCORES",
            "Live scores will appear when a verified data source is connected."
        )

        self.add_card(
            content,
            "📈 PERFORMANCE",
            "Track wins, losses, ROI and prediction accuracy."
        )

        content.add_widget(self.label(
            "DATA STATUS: WAITING FOR NBA DATA",
            12, GREEN, True, 35
        ))

        return scroll

    def daily_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "🔥 DAILY 10 PICKS",
            21, GOLD, True, 45
        ))

        content.add_widget(self.label(
            "NBA BEST PREDICTIONS",
            13, MUTED, True, 30
        ))

        self.add_card(
            content,
            "NO VERIFIED PICKS YET",
            "The prediction engine will publish picks after receiving "
            "valid NBA fixtures, statistics and market data."
        )

        content.add_widget(self.label(
            "We will not invent matches, odds or confidence scores.",
            12, GREEN, True, 45
        ))

        return scroll

    def analysis_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "🧠 AI ANALYSIS",
            22, GOLD, True, 45
        ))

        sections = [
            ("TEAM FORM", "Last 5 and last 10 games"),
            ("OFFENSIVE RATING", "Points produced per 100 possessions"),
            ("DEFENSIVE RATING", "Points conceded per 100 possessions"),
            ("PACE", "Estimated possessions per game"),
            ("HOME / AWAY", "Performance differences"),
            ("HEAD TO HEAD", "Previous meetings"),
            ("PLAYER AVAILABILITY", "Injuries and player status"),
            ("EXPECTED TOTAL", "Projected combined match points"),
        ]

        for title, description in sections:
            self.add_card(content, title, description)

        return scroll

    def odds_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "📊 ODDS CENTER",
            22, GOLD, True, 45
        ))

        markets = [
            ("GAME TOTAL", "Over / Under total points"),
            ("TEAM TOTAL", "Home and away team points"),
            ("FIRST HALF", "First half total points"),
            ("QUARTER TOTAL", "Quarter points"),
            ("SPREAD", "Point spread analysis"),
            ("MONEYLINE", "Match winner probability"),
        ]

        for title, description in markets:
            self.add_card(content, title, description)

        return scroll

    def performance_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "📈 PERFORMANCE CENTER",
            22, GOLD, True, 45
        ))

        stats = [
            "Total predictions: 0",
            "Wins: 0",
            "Losses: 0",
            "Accuracy: Not available",
            "ROI: Not available",
        ]

        for item in stats:
            self.add_card(content, item, "Verified results only")

        return scroll

    def live_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "🔴 LIVE NBA SCORES",
            22, GOLD, True, 45
        ))

        self.add_card(
            content,
            "LIVE DATA NOT CONNECTED",
            "Live game information will appear after a data provider "
            "is configured."
        )

        return scroll

    def history_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "◷ PICK HISTORY",
            22, GOLD, True, 45
        ))

        self.add_card(
            content,
            "NO HISTORY YET",
            "Settled predictions will be recorded here."
        )

        return scroll

    def about_page(self):
        scroll, content = self.make_page()

        content.add_widget(self.label(
            "👑 ABOUT GUNX SMART NBA",
            21, GOLD, True, 45
        ))

        self.add_card(
            content,
            "OUR MISSION",
            "Build an intelligent NBA analysis platform powered by "
            "statistics, probability and disciplined predictions."
        )

        self.add_card(
            content,
            "OUR PRINCIPLE",
            "Accuracy before quantity. Evidence before predictions."
        )

        content.add_widget(self.label(
            "GUNX SMART NBA © 2026",
            13, GOLD, True, 35
        ))

        return scroll


if __name__ == "__main__":
    GunxSmartNBAApp().run()
