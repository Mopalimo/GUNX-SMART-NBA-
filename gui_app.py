
from datetime import datetime
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout

from nba_integration import GUNXNBAIntegration


BG = "#070D1B"
PANEL = "#101C33"
BLUE = "#087DFF"
GOLD = "#F5B900"
WHITE = "#FFFFFF"
MUTED = "#A9B8D0"
GREEN = "#19D66B"
RED = "#FF5555"


class GunxCard(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = dp(14)
        self.spacing = dp(9)

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

    # -------------------------------------------------
    # MAIN BUILD + SPLASH SCREEN
    # -------------------------------------------------

    def build(self):

        self.title = "GUNX SMART NBA"
        self.icon = "gunx_logo.png"

        self.nba_integration = GUNXNBAIntegration()
        self.analysis_running = False

        Window.clearcolor = get_color_from_hex(BG)

        # Main screen manager
        self.app_manager = ScreenManager(
            transition=NoTransition()
        )

        # SPLASH SCREEN
        splash = Screen(name="splash")

        splash_layout = AnchorLayout(
            anchor_x="center",
            anchor_y="center"
        )

        splash_logo = Image(
            source="gunx_logo.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.94, 0.94)
        )

        splash_layout.add_widget(splash_logo)
        splash.add_widget(splash_layout)

        self.app_manager.add_widget(splash)

        # DASHBOARD SCREEN
        dashboard = Screen(name="dashboard")

        self.root_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            padding=[dp(8), dp(8), dp(8), dp(6)]
        )

        self.build_header()

        self.manager = ScreenManager(
            transition=NoTransition()
        )

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

        self.build_navigation()

        dashboard.add_widget(self.root_layout)
        self.app_manager.add_widget(dashboard)

        # Show dashboard after 3 seconds
        Clock.schedule_once(self._show_dashboard, 3)

        return self.app_manager

    def _show_dashboard(self, dt):
        self.app_manager.current = "dashboard"

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------

    def build_header(self):

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(155),
            padding=[dp(13), dp(8)],
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

        logo = Image(
            source="gunx_logo.png",
            size_hint=(None, None),
            size=(dp(75), dp(75)),
            allow_stretch=True,
            keep_ratio=True
        )

        header.add_widget(logo)

        header.add_widget(self.label(
            "GUNX SMART NBA",
            25, GOLD, True, 40
        ))

        header.add_widget(self.label(
            "ANALYZE  |  PREDICT  |  WIN",
            12, WHITE, True, 23
        ))

        header.add_widget(self.label(
            "NBA INTELLIGENCE CENTER",
            11, MUTED, True, 22
        ))

        self.root_layout.add_widget(header)

    # -------------------------------------------------
    # NAVIGATION
    # -------------------------------------------------

    def build_navigation(self):

        nav = ScrollView(
            size_hint_y=None,
            height=dp(49),
            do_scroll_y=False,
            bar_width=dp(2)
        )

        row = BoxLayout(
            size_hint_x=None,
            spacing=dp(5)
        )

        row.bind(minimum_width=row.setter("width"))

        items = [
            ("HOME", "home"),
            ("DAILY PICKS", "daily"),
            ("AI ANALYSIS", "analysis"),
            ("ODDS", "odds"),
            ("PERFORMANCE", "performance"),
            ("LIVE", "live"),
            ("HISTORY", "history"),
            ("ABOUT", "about"),
        ]

        for title, page in items:

            btn = GunxButton(
                text=title,
                size_hint_x=None,
                width=dp(112),
                font_size=sp(11),
                background_color=get_color_from_hex("#142B50")
            )

            btn.bind(
                on_release=lambda instance, p=page:
                self.open_page(p)
            )

            row.add_widget(btn)

        nav.add_widget(row)
        self.root_layout.add_widget(nav)

    def open_page(self, page):
        self.manager.current = page

    # -------------------------------------------------
    # GENERAL UI
    # -------------------------------------------------

    def label(
        self,
        text,
        size=14,
        color=WHITE,
        bold=False,
        height=40
    ):

        lbl = Label(
            text=str(text),
            font_size=sp(size),
            color=get_color_from_hex(color),
            bold=bold,
            halign="left",
            valign="middle",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(height)
        )

        lbl.bind(
            width=lambda instance, value:
            setattr(
                instance,
                "text_size",
                (max(0, value - dp(4)), None)
            )
        )

        return lbl

    def make_page(self):

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["bars", "content"]
        )

        content = BoxLayout(
            orientation="vertical",
            padding=[dp(5), dp(8)],
            spacing=dp(11),
            size_hint_y=None
        )

        content.bind(
            minimum_height=content.setter("height")
        )

        scroll.add_widget(content)

        return scroll, content

    def add_card(self, parent, title, description):

        card = GunxCard()

        card.add_widget(self.label(
            title, 16, GOLD, True, 36
        ))

        card.add_widget(self.label(
            description, 13, MUTED, False, 58
        ))

        parent.add_widget(card)

        return card

    # -------------------------------------------------
    # HOME PAGE
    # -------------------------------------------------

    def home_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "WELCOME TO GUNX SMART NBA",
            19, GOLD, True, 45
        ))

        content.add_widget(self.label(
            datetime.now().strftime("%A, %d %B %Y"),
            12, MUTED, False, 28
        ))

        self.add_card(
            content,
            "DAILY TOP 10 PICKS",
            "Your strongest verified NBA predictions will appear here."
        )

        self.add_card(
            content,
            "AI ANALYSIS",
            "Team form, offensive rating, defensive rating and pace."
        )

        self.add_card(
            content,
            "ODDS CENTER",
            "Over/Under, match totals, probability and fair odds."
        )

        self.add_card(
            content,
            "LIVE NBA SCORES",
            "Live scores require a verified live game data source."
        )

        self.add_card(
            content,
            "PERFORMANCE",
            "Track wins, losses, ROI and prediction accuracy."
        )

        content.add_widget(self.label(
            "DATA STATUS: NBA SEASON INTEGRATION READY",
            12, GREEN, True, 45
        ))

        return scroll

    # -------------------------------------------------
    # DAILY PICKS PAGE
    # -------------------------------------------------

    def daily_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "DAILY TOP 10 PICKS",
            21, GOLD, True, 48
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
            12, GREEN, True, 48
        ))

        return scroll

    # -------------------------------------------------
    # NBA AI ANALYSIS PAGE
    # -------------------------------------------------

    def analysis_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "GUNX AI ANALYSIS",
            22, GOLD, True, 48
        ))

        content.add_widget(self.label(
            "NBA SEASON STATISTICS ANALYSIS",
            13, MUTED, True, 35
        ))

        content.add_widget(self.label(
            "Enter the two NBA team names. GUNX will retrieve "
            "their season statistics.",
            13, WHITE, False, 58
        ))

        self.analysis_inputs = {}

        fields = [
            ("home_name", "HOME TEAM", "Boston Celtics"),
            ("away_name", "AWAY TEAM", "New York Knicks"),
        ]

        for key, title, hint in fields:

            content.add_widget(self.label(
                title, 12, GOLD, True, 30
            ))

            field = TextInput(
                hint_text=hint,
                multiline=False,
                size_hint_y=None,
                height=dp(49),
                font_size=sp(15),
                foreground_color=get_color_from_hex(WHITE),
                background_color=get_color_from_hex(PANEL),
                cursor_color=get_color_from_hex(GOLD),
                padding=[dp(11), dp(12)]
            )

            self.analysis_inputs[key] = field
            content.add_widget(field)

        self.analyze_btn = GunxButton(
            text="RUN GUNX NBA ANALYSIS",
            size_hint_y=None,
            height=dp(53)
        )

        self.analyze_btn.bind(
            on_release=lambda instance:
            self.run_nba_analysis()
        )

        content.add_widget(self.analyze_btn)

        self.analysis_status = self.label(
            "STATUS: READY",
            12, GREEN, True, 38
        )

        content.add_widget(self.analysis_status)

        self.analysis_output = self.label(
            "NBA ANALYSIS RESULTS WILL APPEAR HERE",
            13, WHITE, True, 300
        )

        self.analysis_output.valign = "top"
        content.add_widget(self.analysis_output)

        return scroll

    # -------------------------------------------------
    # RUN NBA INTEGRATION
    # -------------------------------------------------

    def run_nba_analysis(self):

        if self.analysis_running:
            return

        home_name = self.analysis_inputs["home_name"].text.strip()
        away_name = self.analysis_inputs["away_name"].text.strip()

        if not home_name or not away_name:

            self.analysis_status.text = "STATUS: INPUT ERROR"

            self.analysis_output.text = (
                "Please enter both home and away teams."
            )

            return

        if home_name.lower() == away_name.lower():

            self.analysis_status.text = "STATUS: INPUT ERROR"

            self.analysis_output.text = (
                "Home and away teams cannot be the same."
            )

            return

        self.analysis_running = True

        self.analyze_btn.disabled = True
        self.analyze_btn.text = "ANALYZING NBA DATA..."

        self.analysis_status.text = (
            "STATUS: CONNECTING TO NBA DATA PROVIDER..."
        )

        self.analysis_status.color = get_color_from_hex(GOLD)

        self.analysis_output.text = (
            "GUNX is retrieving NBA season statistics.\n\n"
            "Please wait..."
        )

        Thread(
            target=self._nba_analysis_worker,
            args=(home_name, away_name),
            daemon=True
        ).start()

    def _nba_analysis_worker(self, home_name, away_name):

        try:

            result = self.nba_integration.analyze_match(
                home_name,
                away_name
            )

            Clock.schedule_once(
                lambda dt: self._display_nba_result(result),
                0
            )

        except Exception as exc:

            error_result = {
                "status": "ERROR",
                "message": str(exc),
                "data_status": "SYSTEM_ERROR"
            }

            Clock.schedule_once(
                lambda dt: self._display_nba_result(error_result),
                0
            )

    # -------------------------------------------------
    # DISPLAY NBA RESULTS
    # -------------------------------------------------

    def _display_nba_result(self, result):

        self.analysis_running = False

        self.analyze_btn.disabled = False
        self.analyze_btn.text = "RUN GUNX NBA ANALYSIS"

        if result.get("status") != "SUCCESS":

            self.analysis_status.text = "STATUS: NBA DATA ERROR"
            self.analysis_status.color = get_color_from_hex(RED)

            self.analysis_output.text = (
                "ANALYSIS UNAVAILABLE\n\n"
                + str(result.get(
                    "message",
                    "Unknown NBA integration error."
                ))
                + "\n\nPlease check your team names "
                "and internet connection."
            )

            return

        home_stats = result.get("home_team_stats", {})
        away_stats = result.get("away_team_stats", {})

        home_team = result.get(
            "home_team",
            home_stats.get("team_name", "HOME TEAM")
        )

        away_team = result.get(
            "away_team",
            away_stats.get("team_name", "AWAY TEAM")
        )

        home_points = result.get("home_projected_points", "N/A")
        away_points = result.get("away_projected_points", "N/A")

        home_probability = result.get("home_win_probability", "N/A")
        away_probability = result.get("away_win_probability", "N/A")

        total = result.get("projected_total", "N/A")
        winner = result.get("predicted_winner", "N/A")
        season = result.get("season", "N/A")
        games = result.get("games_played", {})

        self.analysis_status.text = (
            "STATUS: SUCCESS - NBA SEASON DATA"
        )

        self.analysis_status.color = get_color_from_hex(GREEN)

        self.analysis_output.text = (
            "GUNX SMART NBA RESULTS\n\n"

            f"HOME: {home_team}\n"
            f"PROJECTED POINTS: {home_points}\n"
            f"WIN PROBABILITY: {home_probability}%\n"
            f"GAMES PLAYED: {games.get('home', 'N/A')}\n\n"

            f"AWAY: {away_team}\n"
            f"PROJECTED POINTS: {away_points}\n"
            f"WIN PROBABILITY: {away_probability}%\n"
            f"GAMES PLAYED: {games.get('away', 'N/A')}\n\n"

            f"PROJECTED TOTAL: {total}\n"
            f"PREDICTED WINNER: {winner}\n\n"

            f"NBA SEASON: {season}\n"
            f"DATA SOURCE: {result.get('data_source', 'N/A')}\n"
            f"DATA STATUS: {result.get('data_status', 'N/A')}\n\n"

            "MODEL STATUS: ESTIMATE\n"
            "NOT A GUARANTEED RESULT"
        )

    # -------------------------------------------------
    # ODDS PAGE
    # -------------------------------------------------

    def odds_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "ODDS CENTER",
            22, GOLD, True, 48
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

    # -------------------------------------------------
    # PERFORMANCE PAGE
    # -------------------------------------------------

    def performance_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "PERFORMANCE CENTER",
            22, GOLD, True, 48
        ))

        stats = [
            "Total predictions: 0",
            "Wins: 0",
            "Losses: 0",
            "Accuracy: Not available",
            "ROI: Not available",
        ]

        for item in stats:
            self.add_card(
                content,
                item,
                "Verified results only"
            )

        return scroll

    # -------------------------------------------------
    # LIVE PAGE
    # -------------------------------------------------

    def live_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "LIVE NBA SCORES",
            22, GOLD, True, 48
        ))

        self.add_card(
            content,
            "LIVE SCORES NOT CONNECTED",
            "Season statistics are available through NBA integration. "
            "Live game scores require a separate live scoreboard source."
        )

        return scroll

    # -------------------------------------------------
    # HISTORY PAGE
    # -------------------------------------------------

    def history_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "PICK HISTORY",
            22, GOLD, True, 48
        ))

        self.add_card(
            content,
            "NO HISTORY YET",
            "Settled predictions will be recorded here."
        )

        return scroll

    # -------------------------------------------------
    # ABOUT PAGE
    # -------------------------------------------------

    def about_page(self):

        scroll, content = self.make_page()

        content.add_widget(self.label(
            "ABOUT GUNX SMART NBA",
            21, GOLD, True, 48
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

        return scroll


if __name__ == "__main__":
    GunxSmartNBAApp().run()
