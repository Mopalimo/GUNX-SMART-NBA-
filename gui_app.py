
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
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import get_color_from_hex
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout

from nba_integration import GUNXNBAIntegration
from daily_picks import DailyPicksService


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
        with self.canvas.after:
            Color(*get_color_from_hex("#176BCE"))
            self.edge = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(14)),
                width=1.15
            )
            Color(*get_color_from_hex("#B98722"))
            self.gold_edge = Line(
                rounded_rectangle=(self.x + dp(2), self.y + dp(2),
                                   max(0, self.width - dp(4)),
                                   max(0, self.height - dp(4)), dp(12)),
                width=0.55
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.edge.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(14)
        )
        self.gold_edge.rounded_rectangle = (
            self.x + dp(2), self.y + dp(2),
            max(0, self.width - dp(4)),
            max(0, self.height - dp(4)), dp(12)
        )


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
        self.daily_picks_service = DailyPicksService(
            data_provider=self.nba_integration.data_provider,
            engine=self.nba_integration.engine
        )
        self.daily_picks_running = False
        self.daily_scan_started = False
        self.analysis_running = False

        Window.clearcolor = get_color_from_hex(BG)

        # Main screen manager
        self.app_manager = ScreenManager(
            transition=SlideTransition(duration=0.22, direction="left")
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
        Clock.schedule_once(self._start_daily_scan, 3.4)

        return self.app_manager

    def _show_dashboard(self, dt):
        self.app_manager.current = "dashboard"

    def _start_daily_scan(self, dt):
        if not self.daily_scan_started:
            self.daily_scan_started = True
            self.run_daily_picks()

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------


    def build_header(self):

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
            padding=[dp(10), dp(7)],
            spacing=dp(10)
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
            size=(dp(76), dp(76)),
            allow_stretch=True,
            keep_ratio=True
        )
        header.add_widget(logo)

        brand = BoxLayout(orientation="vertical", spacing=dp(1))
        brand.add_widget(self.label("GUNX SMART NBA", 21, GOLD, True, 35))
        brand.add_widget(self.label("ANALYZE  |  PREDICT  |  WIN", 11, WHITE, True, 24))
        brand.add_widget(self.label("NBA INTELLIGENCE CENTER", 10, MUTED, True, 21))
        header.add_widget(brand)

        self.root_layout.add_widget(header)


    def build_navigation(self):
        # Persistent bottom navigation: each destination opens its own screen.
        nav = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(58), spacing=dp(3), padding=[dp(2), dp(3)])
        with nav.canvas.before:
            Color(*get_color_from_hex("#09152A"))
            nav.bg = RoundedRectangle(pos=nav.pos, size=nav.size, radius=[dp(12)])
        nav.bind(pos=lambda obj, value: setattr(obj.bg, "pos", value),
                 size=lambda obj, value: setattr(obj.bg, "size", value))
        items = [
            ("⌂", "HOME", "home"), ("🏆", "DAILY", "daily"),
            ("🧠", "AI", "analysis"), ("⚖", "ODDS", "odds"),
            ("📊", "STATS", "performance"), ("🔴", "LIVE", "live"),
        ]
        for symbol, title, page in items:
            btn = Button(text=symbol + "\n" + title, font_size=sp(10),
                         bold=True,
                         color=get_color_from_hex(GOLD if page == "home" else WHITE),
                         background_normal="", background_down="",
                         background_color=get_color_from_hex("#142B50"),
                         size_hint_x=1)
            btn.bind(on_release=lambda instance, p=page: self.open_page(p))
            nav.add_widget(btn)
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
    def page_banner(self, content, eyebrow, title, subtitle):
        banner = GunxCard()
        banner.orientation = "horizontal"
        banner.size_hint_y = None
        banner.height = dp(126)
        banner.padding = [dp(8), dp(7)]
        banner.spacing = dp(9)
        logo = Image(source="gunx_logo.png", size_hint=(None, 1),
                     width=dp(105), allow_stretch=True, keep_ratio=True)
        banner.add_widget(logo)
        words = BoxLayout(orientation="vertical", spacing=dp(1))
        words.add_widget(self.label(eyebrow, 10, BLUE, True, 22))
        words.add_widget(self.label(title, 19, GOLD, True, 38))
        words.add_widget(self.label(subtitle, 10, WHITE, False, 42))
        banner.add_widget(words)
        content.add_widget(banner)
        return banner

    # HOME PAGE
    # -------------------------------------------------


    def home_page(self):

        scroll, content = self.make_page()

        # Hero display: official GUNX logo, gold title and today's date.
        hero = GunxCard()
        hero.orientation = "horizontal"
        hero.size_hint_y = None
        hero.height = dp(142)
        hero.padding = [dp(10), dp(9)]
        hero.spacing = dp(10)

        hero_logo = Image(
            source="gunx_logo.png",
            size_hint=(None, 1),
            width=dp(112),
            allow_stretch=True,
            keep_ratio=True
        )
        hero.add_widget(hero_logo)

        hero_text = BoxLayout(orientation="vertical", spacing=dp(2))
        hero_text.add_widget(self.label(
            "NBA DAILY", 14, WHITE, True, 27
        ))
        hero_text.add_widget(self.label(
            "TOP 10 PICKS", 23, GOLD, True, 40
        ))
        hero_text.add_widget(self.label(
            "SMART ANALYSIS. HIGHER CHANCES.", 10, MUTED, True, 25
        ))
        hero_text.add_widget(self.label(
            datetime.now().strftime("%a, %d %b %Y"),
            11, WHITE, True, 25
        ))
        hero.add_widget(hero_text)
        content.add_widget(hero)

        wide = Window.width >= dp(650)

        # Main dashboard panels. Two columns on tablet/wide displays,
        # a single readable column on narrow phones.
        primary = GridLayout(
            cols=2 if wide else 1,
            size_hint_y=None,
            spacing=dp(9),
            row_default_height=dp(280),
            row_force_default=False
        )
        primary.bind(minimum_height=primary.setter("height"))

        picks = GunxCard()
        picks.add_widget(self.label(
            "🎯  TOP 10 PICKS TODAY", 17, GOLD, True, 38
        ))
        columns = GridLayout(
            cols=4, size_hint_y=None, height=dp(32), spacing=dp(3)
        )
        for title in ("#", "MATCH", "MARKET", "CONF."):
            columns.add_widget(self.label(title, 10, BLUE, True, 28))
        picks.add_widget(columns)
        picks.add_widget(self.label(
            "No verified NBA fixtures or market odds loaded yet.",
            12, MUTED, False, 58
        ))
        picks.add_widget(self.label(
            "Verified picks will appear here when the data feed is available.",
            11, GREEN, True, 52
        ))
        primary.add_widget(picks)

        analysis = GunxCard()
        analysis.add_widget(self.label(
            "🧠  AI ANALYSIS", 17, GOLD, True, 38
        ))
        analysis.add_widget(self.label(
            "Team form  •  Pace  •  Points for/against",
            12, WHITE, False, 42
        ))
        analysis.add_widget(self.label(
            "Win probability and projected points appear after verified team statistics are received.",
            12, MUTED, False, 86
        ))
        analyze = GunxButton(
            text="SEE FULL ANALYSIS",
            size_hint_y=None, height=dp(44)
        )
        analyze.bind(on_release=lambda instance: self.open_page("analysis"))
        analysis.add_widget(analyze)
        primary.add_widget(analysis)

        content.add_widget(primary)

        secondary = GridLayout(
            cols=2 if wide else 1,
            size_hint_y=None,
            spacing=dp(9)
        )
        secondary.bind(minimum_height=secondary.setter("height"))

        live = GunxCard()
        live.add_widget(self.label(
            "🔴  LIVE NBA SCORES", 16, GOLD, True, 38
        ))
        live.add_widget(self.label(
            "Live scoreboard feed is not connected yet. Scores will show here once a verified live source is connected.",
            12, MUTED, False, 76
        ))
        live_btn = GunxButton(
            text="VIEW ALL LIVE SCORES",
            size_hint_y=None, height=dp(42)
        )
        live_btn.bind(on_release=lambda instance: self.open_page("live"))
        live.add_widget(live_btn)
        secondary.add_widget(live)

        odds = GunxCard()
        odds.add_widget(self.label(
            "⚖  ODDS CENTER", 16, GOLD, True, 38
        ))
        odds.add_widget(self.label(
            "Over / Under  •  Moneyline  •  Spread",
            12, WHITE, True, 35
        ))
        odds.add_widget(self.label(
            "Verified bookmaker odds are not loaded. No sample prices are displayed.",
            12, MUTED, False, 60
        ))
        odds_btn = GunxButton(
            text="VIEW MORE ODDS",
            size_hint_y=None, height=dp(42)
        )
        odds_btn.bind(on_release=lambda instance: self.open_page("odds"))
        odds.add_widget(odds_btn)
        secondary.add_widget(odds)

        content.add_widget(secondary)

        performance = GunxCard()
        performance.orientation = "horizontal"
        performance.size_hint_y = None
        performance.height = dp(82)
        performance.add_widget(self.label(
            "🏆  PERFORMANCE", 15, GOLD, True, 55
        ))
        for value, caption in (
            ("0", "PICKS"),
            ("—", "SUCCESS"),
            ("—", "ROI")
        ):
            stat = BoxLayout(orientation="vertical", spacing=dp(1))
            stat.add_widget(self.label(value, 18, GREEN, True, 34))
            stat.add_widget(self.label(caption, 9, MUTED, True, 25))
            performance.add_widget(stat)
        content.add_widget(performance)

        content.add_widget(self.label(
            "DATA INTEGRITY: VERIFIED DATA ONLY — NO FABRICATED ODDS OR SCORES",
            10, GREEN, True, 38
        ))

        return scroll

    def daily_page(self):

        scroll, content = self.make_page()
        self.page_banner(content, "GUNX SMART NBA / MATCH CENTER", "DAILY TOP PICKS",
                         "AI-ranked fixtures • team form • model probability")
        content.add_widget(self.label(
            "NBA DAILY TOP 5 PICKS", 22, GOLD, True, 48
        ))
        content.add_widget(self.label(
            "AUTOMATIC FIXTURE SCAN + TEAM STATISTICS ANALYSIS",
            12, MUTED, True, 35
        ))
        self.daily_status = self.label(
            "STATUS: READY — TAP TO SCAN TODAY'S NBA GAMES",
            12, GREEN, True, 45
        )
        content.add_widget(self.daily_status)

        self.daily_refresh_btn = GunxButton(
            text="SCAN TODAY'S NBA GAMES",
            size_hint_y=None, height=dp(52)
        )
        self.daily_refresh_btn.bind(
            on_release=lambda instance: self.run_daily_picks()
        )
        content.add_widget(self.daily_refresh_btn)

        self.daily_results_box = GunxCard()
        self.daily_results_box.add_widget(self.label(
            "YOUR TOP 5 WILL APPEAR HERE", 15, GOLD, True, 38
        ))
        self.daily_results_box.add_widget(self.label(
            "GUNX scans today's fixture list, retrieves NBA team-season "
            "statistics and ranks available moneyline predictions.",
            12, MUTED, False, 75
        ))
        content.add_widget(self.daily_results_box)
        content.add_widget(self.label(
            "MODEL FAIR ODDS ARE CALCULATED FROM GUNX PROBABILITIES; "
            "THEY ARE NOT LIVE BETPAWA ODDS. Injuries and confirmed "
            "lineups are not included yet.",
            11, MUTED, False, 85
        ))
        return scroll

    def run_daily_picks(self):

        if self.daily_picks_running:
            return
        self.daily_picks_running = True
        self.daily_scan_started = True
        self.daily_refresh_btn.disabled = True
        self.daily_refresh_btn.text = "SCANNING NBA FIXTURES..."
        self.daily_status.text = (
            "STATUS: FETCHING TODAY'S FIXTURES AND TEAM STATS..."
        )
        self.daily_status.color = get_color_from_hex(GOLD)
        Thread(target=self._daily_picks_worker, daemon=True).start()

    def _daily_picks_worker(self):

        try:
            result = self.daily_picks_service.build_daily_top_five()
        except Exception as exc:
            result = {"status": "ERROR", "message": str(exc), "picks": []}
        Clock.schedule_once(
            lambda dt: self._display_daily_picks(result), 0
        )

    def _display_daily_picks(self, result):

        self.daily_picks_running = False
        self.daily_refresh_btn.disabled = False
        self.daily_refresh_btn.text = "REFRESH DAILY TOP 5"
        self.daily_results_box.clear_widgets()
        status = result.get("status", "ERROR")
        picks = result.get("picks", [])

        if status == "SUCCESS" and picks:
            self.daily_status.text = (
                "STATUS: COMPLETE — "
                + str(result.get("games_analyzed", 0))
                + " GAMES ANALYZED"
            )
            self.daily_status.color = get_color_from_hex(GREEN)
            self.daily_results_box.add_widget(self.label(
                "🏆  GUNX TOP " + str(len(picks)) + " PICKS",
                16, GOLD, True, 40
            ))
            for index, pick in enumerate(picks, 1):
                self.daily_results_box.add_widget(self.label(
                    str(index) + ". " + pick["match"],
                    13, WHITE, True, 30
                ))
                self.daily_results_box.add_widget(self.label(
                    pick["selection"] + "  |  "
                    + str(pick["model_probability"])
                    + "% model probability",
                    12, GREEN, True, 28
                ))
                self.daily_results_box.add_widget(self.label(
                    "MODEL FAIR ODDS: " + str(pick["model_fair_odds"])
                    + "  |  Projected total: "
                    + str(pick["projected_total"]),
                    11, MUTED, False, 27
                ))
        else:
            self.daily_status.text = (
                "STATUS: " + str(status) + " — "
                + str(result.get("message", "No verified picks available."))
            )
            self.daily_status.color = get_color_from_hex(RED)
            self.daily_results_box.add_widget(self.label(
                "NO VERIFIED PICKS AVAILABLE", 15, GOLD, True, 42
            ))
            self.daily_results_box.add_widget(self.label(
                str(result.get(
                    "message",
                    "Fixtures or team statistics could not be retrieved."
                )),
                12, MUTED, False, 75
            ))

    def analysis_page(self):

        scroll, content = self.make_page()
        self.page_banner(content, "GUNX INTELLIGENCE LAB", "AI ANALYSIS",
                         "Team form • pace • scoring • win probability")

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
        self.page_banner(content, "MARKET BREAKDOWN", "ODDS CENTER",
                         "Totals • team totals • spread • moneyline")

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
        self.page_banner(content, "TRACK RECORD", "PERFORMANCE",
                         "Measure predictions using settled results only")

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
        self.page_banner(content, "NBA GAME CENTER", "LIVE SCORES",
                         "Live scoreboard connection status")

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
