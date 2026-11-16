
import json
import socket
import time
import urllib.parse
import urllib.request
import urllib.error

from datetime import datetime
from threading import Lock


class NBADataError(Exception):
    """Raised when NBA data cannot be retrieved or validated."""


class NBADataProvider:

    BASE_URL = "https://stats.nba.com/stats/leaguedashteamstats"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "Connection": "keep-alive",
    }

    def __init__(self, timeout=35, retries=3):
        self.timeout = timeout
        self.retries = retries
        self._cache = {}
        self._lock = Lock()

    @staticmethod
    def current_season():
        now = datetime.now()

        if now.month >= 10:
            start = now.year
        else:
            start = now.year - 1

        return f"{start}-{str(start + 1)[-2:]}"

    def _request_stats(self, season, measure_type):

        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": measure_type,
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Regular Season",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
        }

        query = urllib.parse.urlencode(params)
        url = self.BASE_URL + "?" + query

        last_error = None

        for attempt in range(self.retries):

            request = urllib.request.Request(
                url,
                headers=self.HEADERS
            )

            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout
                ) as response:

                    raw = response.read().decode("utf-8")

                payload = json.loads(raw)

                result_sets = payload.get("resultSets")

                if not result_sets:
                    raise NBADataError(
                        "NBA returned no statistics."
                    )

                dataset = result_sets[0]

                headers = dataset.get("headers", [])
                rows = dataset.get("rowSet", [])

                if not headers or not rows:
                    raise NBADataError(
                        "NBA statistics are empty."
                    )

                return [
                    dict(zip(headers, row))
                    for row in rows
                ]

            except urllib.error.HTTPError as exc:

                last_error = exc

                if exc.code not in (429, 500, 502, 503, 504):
                    raise NBADataError(
                        f"NBA {measure_type} HTTP error: "
                        f"{exc.code} {exc.reason}"
                    )

            except (
                urllib.error.URLError,
                TimeoutError,
                socket.timeout,
                json.JSONDecodeError,
            ) as exc:

                last_error = exc

            if attempt < self.retries - 1:
                time.sleep(2 ** (attempt + 1))

        raise NBADataError(
            f"NBA {measure_type} request failed after "
            f"{self.retries} attempts: {last_error}"
        )

    def get_all_team_stats(
        self,
        season=None,
        force_refresh=False
    ):

        season = season or self.current_season()
        cache_key = season

        with self._lock:
            if not force_refresh and cache_key in self._cache:
                return self._cache[cache_key]

        base_data = self._request_stats(
            season,
            "Base"
        )

        advanced_data = self._request_stats(
            season,
            "Advanced"
        )

        advanced_lookup = {
            row["TEAM_ID"]: row
            for row in advanced_data
        }

        teams = {}

        for row in base_data:

            team_id = row.get("TEAM_ID")
            advanced = advanced_lookup.get(team_id)

            if not advanced:
                continue

            try:
                ppg = float(row["PTS"])
                plus_minus = float(row["PLUS_MINUS"])
                win_pct = float(row["W_PCT"])
                pace = float(advanced["PACE"])

                off_rating = float(advanced["OFF_RATING"])
                def_rating = float(advanced["DEF_RATING"])

                if pace <= 0:
                    continue

                if not 0 <= win_pct <= 1:
                    continue

                team = {
                    "team_id": team_id,
                    "team_name": row["TEAM_NAME"],
                    "ppg": ppg,
                    "opp_ppg": ppg - plus_minus,
                    "pace": pace,
                    "win_pct": win_pct,
                    "off_rating": off_rating,
                    "def_rating": def_rating,
                    "net_rating": off_rating - def_rating,
                    "games_played": int(row["GP"]),
                    "season": season,
                    "data_status": "SEASON_DATA",
                }

                teams[row["TEAM_NAME"].lower()] = team

            except (KeyError, TypeError, ValueError):
                continue

        if not teams:
            raise NBADataError(
                "No valid NBA team statistics were found."
            )

        with self._lock:
            self._cache[cache_key] = teams

        return teams

    def get_team_stats(self, team_name, season=None):

        if not team_name:
            raise NBADataError("Team name is required.")

        teams = self.get_all_team_stats(season)

        search_name = team_name.strip().lower()

        if search_name in teams:
            return dict(teams[search_name])

        matches = [
            team for name, team in teams.items()
            if search_name in name
        ]

        if len(matches) == 1:
            return dict(matches[0])

        if len(matches) > 1:
            raise NBADataError(
                f"Ambiguous team name: {team_name}"
            )

        raise NBADataError(
            f"Team not found: {team_name}"
        )

    def get_matchup_stats(
        self,
        home_team,
        away_team,
        season=None
    ):

        home_stats = self.get_team_stats(
            home_team,
            season
        )

        away_stats = self.get_team_stats(
            away_team,
            season
        )

        return home_stats, away_stats
        
