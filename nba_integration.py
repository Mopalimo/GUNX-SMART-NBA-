
from nba_data import NBADataProvider, NBADataError
from nba_engine import NBAAnalysisEngine


class GUNXNBAIntegration:

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
            result["data_status"] = "LIVE_DATA"

            return result

        except NBADataError as exc:
            return {
                "status": "ERROR",
                "message": str(exc),
                "data_source": "NBA_STATS"
            }

        except Exception as exc:
            return {
                "status": "ERROR",
                "message": str(exc),
                "data_source": "GUNX"
            }
          
