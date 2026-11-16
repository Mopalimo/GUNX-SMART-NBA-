
from nba_data import NBADataProvider, NBADataError
from nba_engine import NBAAnalysisEngine


class GUNXNBAIntegration:
    """
    Connects NBA statistics provider to GUNX analysis engine.
    """

    def __init__(self):
        self.data_provider = NBADataProvider()
        self.engine = NBAAnalysisEngine()

    def analyze_match(
        self,
        home_team,
        away_team,
        season=None
    ):
        try:
            if not home_team or not away_team:
                raise NBADataError(
                    "Both home and away teams are required."
                )

            if (
                home_team.strip().lower()
                == away_team.strip().lower()
            ):
                raise NBADataError(
                    "Home and away teams cannot be the same."
                )

            home_stats, away_stats = (
                self.data_provider.get_matchup_stats(
                    home_team,
                    away_team,
                    season
                )
            )

            result = self.engine.analyze_game(
                home_stats["team_name"],
                away_stats["team_name"],
                home_stats,
                away_stats
            )

            result["home_team_stats"] = home_stats
            result["away_team_stats"] = away_stats

            result["data_source"] = "NBA_STATS"
            result["data_status"] = "SEASON_DATA"

            result["season"] = (
                home_stats.get("season")
            )

            result["games_played"] = {
                "home": home_stats.get("games_played"),
                "away": away_stats.get("games_played"),
            }

            result["status"] = "SUCCESS"

            return result

        except NBADataError as exc:
            return {
                "status": "ERROR",
                "message": str(exc),
                "data_source": "NBA_STATS",
                "data_status": "UNAVAILABLE",
            }

        except (TypeError, ValueError, KeyError) as exc:
            return {
                "status": "ERROR",
                "message": str(exc),
                "data_source": "GUNX",
                "data_status": "INVALID_DATA",
            }

        except Exception as exc:
            return {
                "status": "ERROR",
                "message": str(exc),
                "data_source": "GUNX",
                "data_status": "SYSTEM_ERROR",
            }
            
