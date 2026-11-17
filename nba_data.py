import json
import socket
import ssl
import certifi
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
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "Connection": "keep-alive",
        "Host": "stats.nba.com",
    }

    def __init__(self, timeout=60, retries=4):
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
                print(
                    f"[NBA DATA] {measure_type} request "
                    f"{attempt + 1}/{self.retries}"
                )

                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout,
                    context=ssl.create_default_context(cafile=certifi.where())
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

                if exc.code not in (403, 408, 429, 500, 502, 503, 504):
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

            except NBADataError:
                raise

            except Exception as exc:
                last_error = exc

            if attempt < self.retries - 1:

                delay = min(5 * (2 ** attempt), 30)

                print(
                    f"[NBA DATA] Request failed: {last_error}"
                )

                print(
                    f"[NBA DATA] Retrying in {delay} seconds..."
                )

                time.sleep(delay)

        raise NBADataError(
            f"NBA {measure_type} request failed after "
            f"{self.retries} attempts: {last_error}"
        )

    def _espn_json(self, url):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.HEADERS["User-Agent"],
                "Accept": "application/json",
                "Referer": "https://www.espn.com/",
            },
        )
        with urllib.request.urlopen(
            request,
            timeout=min(self.timeout, 20),
            context=ssl.create_default_context(cafile=certifi.where()),
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    def _get_espn_team_stats(self, season):
        """
        Fallback data source when stats.nba.com blocks mobile requests.
        Computes points for/against and win rate from completed ESPN
        season game logs. Pace is explicitly a neutral estimate because
        the schedule feed does not supply possessions.
        """
        season_year = int(str(season).split("-")[0])
        teams_url = (
            "https://site.api.espn.com/apis/site/v2/sports/"
            "basketball/nba/teams?limit=100"
        )
        payload = self._espn_json(teams_url)
        teams = (
            payload.get("sports", [{}])[0]
            .get("leagues", [{}])[0]
            .get("teams", [])
        )
        if not teams:
            raise NBADataError("ESPN team directory returned no teams.")

        output = {}
        for item in teams:
            team_info = item.get("team", item)
            team_id = team_info.get("id")
            display_name = team_info.get("displayName") or team_info.get("name")
            abbreviation = team_info.get("abbreviation")
            if not team_id or not display_name:
                continue

            schedule_url = (
                "https://site.api.espn.com/apis/site/v2/sports/"
                f"basketball/nba/teams/{team_id}/schedule?season={season_year}"
            )
            schedule = self._espn_json(schedule_url)
            events = schedule.get("events", [])
            points_for = []
            points_against = []
            wins = 0
            played = 0

            for event in events:
                status = event.get("competitions", [{}])[0].get(
                    "status", {}
                ).get("type", {})
                if not status.get("completed"):
                    continue
                competition = event.get("competitions", [{}])[0]
                competitors = competition.get("competitors", [])
                if len(competitors) < 2:
                    continue

                own = next(
                    (c for c in competitors
                     if str(c.get("team", {}).get("id")) == str(team_id)),
                    None
                )
                opponent = next(
                    (c for c in competitors
                     if str(c.get("team", {}).get("id")) != str(team_id)),
                    None
                )
                if own is None or opponent is None:
                    continue
                try:
                    own_score = float(own.get("score"))
                    opponent_score = float(opponent.get("score"))
                except (TypeError, ValueError):
                    continue

                points_for.append(own_score)
                points_against.append(opponent_score)
                played += 1
                if own.get("winner") is True or own_score > opponent_score:
                    wins += 1

            if not played:
                continue

            ppg = sum(points_for) / played
            opp_ppg = sum(points_against) / played
            win_pct = wins / played
            output[display_name.lower()] = {
                "team_id": team_id,
                "team_name": display_name,
                "ppg": ppg,
                "opp_ppg": opp_ppg,
                "pace": 100.0,
                "win_pct": win_pct,
                "games_played": played,
                "season": season,
                "data_status": "ESPN_GAME_LOG_ESTIMATE",
                "data_source": "ESPN completed game logs",
                "pace_status": "NEUTRAL_ESTIMATE_NOT_LIVE_DATA",
            }

        if not output:
            raise NBADataError(
                "ESPN schedules returned no completed games for "
                + str(season)
                + ". The season may not have started or the feed is unavailable."
            )
        return output

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

        # Prefer ESPN game logs because stats.nba.com can reject
        # requests from Android/mobile networks. Use NBA Stats as backup.
        try:
            teams = self._get_espn_team_stats(season)
            with self._lock:
                self._cache[cache_key] = teams
            return teams
        except Exception as espn_error:
            print("[NBA DATA] ESPN fallback unavailable:", espn_error)

        base_data = self._request_stats(season, "Base")
        advanced_data = self._request_stats(season, "Advanced")

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
        
