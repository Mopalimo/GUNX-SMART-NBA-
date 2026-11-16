
import math


class NBAAnalysisEngine:
    """
    GUNX SMART NBA analysis engine.
    Uses supplied team statistics; does not invent missing data.
    """

    REQUIRED_STATS = (
        "ppg",
        "opp_ppg",
        "pace",
        "win_pct",
    )

    def _validate_team(self, team):
        if not isinstance(team, dict):
            raise ValueError("Team statistics must be a dictionary.")

        missing = [
            key for key in self.REQUIRED_STATS
            if key not in team
        ]

        if missing:
            raise ValueError(
                "Missing team statistics: " + ", ".join(missing)
            )

        for key in self.REQUIRED_STATS:
            value = float(team[key])

            if not math.isfinite(value):
                raise ValueError("Invalid statistic: " + key)

        if float(team["pace"]) <= 0:
            raise ValueError("Pace must be greater than zero.")

        if not 0 <= float(team["win_pct"]) <= 1:
            raise ValueError("win_pct must be between 0 and 1.")

    def analyze_game(self, home_team, away_team,
                     home_stats, away_stats):

        self._validate_team(home_stats)
        self._validate_team(away_stats)

        home_ppg = float(home_stats["ppg"])
        away_ppg = float(away_stats["ppg"])

        home_def = float(home_stats["opp_ppg"])
        away_def = float(away_stats["opp_ppg"])

        home_pace = float(home_stats["pace"])
        away_pace = float(away_stats["pace"])

        average_pace = (home_pace + away_pace) / 2

        # Estimate points using offense, opponent defense and pace.
        home_expected = (
            (home_ppg + away_def) / 2
        ) * (average_pace / 100)

        away_expected = (
            (away_ppg + home_def) / 2
        ) * (average_pace / 100)

        # Small home-court adjustment.
        home_expected += 2.0

        projected_total = home_expected + away_expected
        projected_margin = home_expected - away_expected

        # Approximate win probability.
        home_probability = 1 / (
            1 + math.exp(-projected_margin / 12)
        )

        away_probability = 1 - home_probability

        winner = (
            home_team
            if home_probability >= 0.5
            else away_team
        )

        confidence = max(
            home_probability,
            away_probability
        ) * 100

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_projected_points": round(home_expected, 1),
            "away_projected_points": round(away_expected, 1),
            "projected_total": round(projected_total, 1),
            "projected_margin": round(projected_margin, 1),
            "predicted_winner": winner,
            "home_win_probability": round(
                home_probability * 100, 1
            ),
            "away_win_probability": round(
                away_probability * 100, 1
            ),
            "model_confidence": round(confidence, 1),
            "status": "ESTIMATE",
          }
                       
