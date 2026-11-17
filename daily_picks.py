import json
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from nba_data import NBADataProvider, NBADataError
from nba_engine import NBAAnalysisEngine


class DailyPicksService:
    """
    Builds a daily NBA shortlist from ESPN's public scoreboard and
    NBA team-season statistics. Fair odds are model-implied, not bookmaker odds.
    """

    SCOREBOARD_URL = (
        "https://site.api.espn.com/apis/site/v2/sports/"
        "basketball/nba/scoreboard"
    )

    def __init__(self, data_provider=None, engine=None, timeout=20):
        self.data_provider = data_provider or NBADataProvider(timeout=timeout)
        self.engine = engine or NBAAnalysisEngine()
        self.timeout = timeout

    def _get_scoreboard(self, game_date=None):
        if game_date is None:
            game_date = datetime.now(ZoneInfo("Africa/Dar_es_Salaam")).date()
        date_text = game_date.strftime("%Y%m%d")
        url = self.SCOREBOARD_URL + "?" + urllib.parse.urlencode({
            "dates": date_text,
            "limit": 100,
        })
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "GUNX-SMART-NBA/1.0"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise NBADataError("NBA fixture feed unavailable: " + str(exc))

        events = payload.get("events", [])
        games = []
        for event in events:
            competitions = event.get("competitions") or []
            if not competitions:
                continue
            competitors = competitions[0].get("competitors") or []
            home = next(
                (item for item in competitors if item.get("homeAway") == "home"),
                None
            )
            away = next(
                (item for item in competitors if item.get("homeAway") == "away"),
                None
            )
            if not home or not away:
                continue
            home_name = (home.get("team") or {}).get("displayName")
            away_name = (away.get("team") or {}).get("displayName")
            if home_name and away_name:
                games.append({
                    "event_id": event.get("id"),
                    "start_time": event.get("date"),
                    "home_team": home_name,
                    "away_team": away_name,
                    "status": (event.get("status") or {}).get("type", {}).get("name"),
                })
        return games

    @staticmethod
    def _fair_decimal_odds(probability):
        if probability <= 0:
            return None
        return round(1.0 / probability, 2)

    def build_daily_top_five(self, game_date=None):
        games = self._get_scoreboard(game_date)
        if not games:
            return {
                "status": "NO_GAMES",
                "date": str(game_date or datetime.now(
                    ZoneInfo("Africa/Dar_es_Salaam")
                ).date()),
                "source": "ESPN_SCOREBOARD + NBA_STATS",
                "picks": [],
                "message": "No NBA fixtures found for this date.",
            }

        all_stats = self.data_provider.get_all_team_stats()
        analyzed = []
        errors = []

        for game in games:
            home_key = game["home_team"].strip().lower()
            away_key = game["away_team"].strip().lower()
            home = all_stats.get(home_key)
            away = all_stats.get(away_key)
            if not home or not away:
                errors.append(
                    game["home_team"] + " vs " + game["away_team"]
                    + ": team stats not available"
                )
                continue
            try:
                result = self.engine.analyze_game(
                    home["team_name"],
                    away["team_name"],
                    home,
                    away
                )
                if result.get("predicted_winner") == home["team_name"]:
                    probability = result["home_win_probability"] / 100.0
                    selection = home["team_name"] + " WIN"
                else:
                    probability = result["away_win_probability"] / 100.0
                    selection = away["team_name"] + " WIN"

                analyzed.append({
                    "event_id": game.get("event_id"),
                    "start_time": game.get("start_time"),
                    "match": game["away_team"] + " @ " + game["home_team"],
                    "selection": selection,
                    "market": "MONEYLINE",
                    "model_probability": round(probability * 100, 1),
                    "model_fair_odds": self._fair_decimal_odds(probability),
                    "projected_total": result["projected_total"],
                    "projected_score": (
                        str(result["home_projected_points"]) + " - "
                        + str(result["away_projected_points"])
                    ),
                    "data_status": "SEASON_STATS",
                    "note": (
                        "Model-implied fair odds; not live bookmaker odds. "
                        "Injuries and confirmed lineups are not included."
                    ),
                })
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(game["home_team"] + " vs " + game["away_team"]
                              + ": " + str(exc))

        analyzed.sort(
            key=lambda item: item["model_probability"],
            reverse=True
        )
        picks = analyzed[:5]

        return {
            "status": "SUCCESS" if picks else "NO_VERIFIED_PICKS",
            "date": str(game_date or datetime.now(
                ZoneInfo("Africa/Dar_es_Salaam")
            ).date()),
            "source": "ESPN_SCOREBOARD + NBA_STATS",
            "fixtures_found": len(games),
            "games_analyzed": len(analyzed),
            "picks": picks,
            "errors": errors,
            "message": (
                "Top picks ranked by model probability. "
                "No bookmaker prices or totals lines are supplied."
            ),
        }
