
import unittest
from unittest.mock import patch

from nba_data import NBADataError
from nba_integration import GUNXNBAIntegration


class TestGUNXNBAIntegration(unittest.TestCase):

    def setUp(self):
        self.home_stats = {
            "team_name": "Boston Celtics",
            "ppg": 118.5,
            "opp_ppg": 109.2,
            "pace": 98.5,
            "win_pct": 0.70,
            "season": "2026-27",
            "games_played": 10,
        }

        self.away_stats = {
            "team_name": "Los Angeles Lakers",
            "ppg": 115.2,
            "opp_ppg": 112.4,
            "pace": 99.1,
            "win_pct": 0.60,
            "season": "2026-27",
            "games_played": 10,
        }

    @patch("nba_integration.NBAAnalysisEngine")
    @patch("nba_integration.NBADataProvider")
    def test_successful_match_analysis(
        self,
        mock_provider,
        mock_engine
    ):
        provider_instance = mock_provider.return_value
        engine_instance = mock_engine.return_value

        provider_instance.get_matchup_stats.return_value = (
            self.home_stats,
            self.away_stats
        )

        engine_instance.analyze_game.return_value = {
            "predicted_winner": "Boston Celtics",
            "home_win_probability": 0.65,
            "away_win_probability": 0.35,
            "status": "ESTIMATE",
        }

        integration = GUNXNBAIntegration()

        result = integration.analyze_match(
            "Boston Celtics",
            "Los Angeles Lakers"
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["data_source"], "NBA_STATS")
        self.assertEqual(result["data_status"], "SEASON_DATA")

        self.assertIn("home_team_stats", result)
        self.assertIn("away_team_stats", result)

        self.assertEqual(
            result["home_team_stats"]["team_name"],
            "Boston Celtics"
        )

        self.assertEqual(
            result["away_team_stats"]["team_name"],
            "Los Angeles Lakers"
        )

        self.assertEqual(
            result["games_played"]["home"],
            10
        )

        self.assertEqual(
            result["games_played"]["away"],
            10
        )

        provider_instance.get_matchup_stats.assert_called_once()

        engine_instance.analyze_game.assert_called_once()

    @patch("nba_integration.NBADataProvider")
    def test_missing_team_name(self, mock_provider):
        integration = GUNXNBAIntegration()

        result = integration.analyze_match(
            "",
            "Los Angeles Lakers"
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["data_status"], "UNAVAILABLE")

        mock_provider.return_value.get_matchup_stats.assert_not_called()

    @patch("nba_integration.NBADataProvider")
    def test_same_team_rejected(self, mock_provider):
        integration = GUNXNBAIntegration()

        result = integration.analyze_match(
            "Boston Celtics",
            "boston celtics"
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertIn("cannot be the same", result["message"])

        mock_provider.return_value.get_matchup_stats.assert_not_called()

    @patch("nba_integration.NBAAnalysisEngine")
    @patch("nba_integration.NBADataProvider")
    def test_data_provider_error(
        self,
        mock_provider,
        mock_engine
    ):
        mock_provider.return_value.get_matchup_stats.side_effect = (
            NBADataError("NBA data unavailable")
        )

        integration = GUNXNBAIntegration()

        result = integration.analyze_match(
            "Boston Celtics",
            "Los Angeles Lakers"
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["data_status"], "UNAVAILABLE")
        self.assertIn("NBA data unavailable", result["message"])

    @patch("nba_integration.NBAAnalysisEngine")
    @patch("nba_integration.NBADataProvider")
    def test_invalid_data_error(
        self,
        mock_provider,
        mock_engine
    ):
        mock_provider.return_value.get_matchup_stats.side_effect = (
            KeyError("team_name")
        )

        integration = GUNXNBAIntegration()

        result = integration.analyze_match(
            "Boston Celtics",
            "Los Angeles Lakers"
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["data_status"], "INVALID_DATA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
