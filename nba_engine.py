
import math


class NBAAnalysisEngine:
    """
    GUNX SMART NBA Analysis Engine.
    Uses real supplied team statistics.
    Supports advanced ratings with safe fallbacks.
    """

    REQUIRED_STATS = (
        "ppg",
        "opp_ppg",
        "pace",
        "win_pct",
    )

    def _validate_team(self, team):
        if not isinstance(team, dict):
            raise ValueError(
                "Team statistics must be a dictionary."
            )

        missing = [
            key for key in self.REQUIRED_STATS
            if key not in team
        ]

        if missing:
            raise ValueError(
                "Missing statistics: " + ", ".join(missing)
            )

        for key in self.REQUIRED_STATS:
            value = float(team[key])

            if not math.isfinite(value):
                raise ValueError(
                    "Invalid statistic: " + key
                )

        if float(team["pace"]) <= 0:
            raise ValueError("Pace must be positive.")

        if not 0 <= float(team["win_pct"]) <= 1:
            raise ValueError(
                "win_pct must be between 0 and 1."
            )

    def _optional_number(self, team, key):
        value = team.get(key)

        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(value):
            return None

        return value

    def _team_strength(self, team):
        off = self._optional_number(
            team, "off_rating"
        )
        defense = self._optional_number(
            team, "def_rating"
        )
        net = self._optional_number(
            team, "net_rating"
        )

        if net is None and off is not None and defense is not None:
            net = off - defense

        if off is not None and defense is not None:
            return net, off, defense, "ADVANCED_RATINGS"

        return None, off, defense, "BASIC_STATS"

    def analyze_game(
        self,
        home_team,
        away_team,
        home_stats,
        away_stats
    ):
        self._validate_team(home_stats)
        self._validate_team(away_stats)

        home_ppg = float(home_stats["ppg"])
        away_ppg = float(away_stats["ppg"])

        home_opp = float(home_stats["opp_ppg"])
        away_opp = float(away_stats["opp_ppg"])

        home_pace = float(home_stats["pace"])
        away_pace = float(away_stats["pace"])

        average_pace = (
            home_pace + away_pace
        ) / 2

        # Basic offensive and defensive projection.
        home_basic = (
            (home_ppg + away_opp) / 2
        ) * (average_pace / 100)

        away_basic = (
            (away_ppg + home_opp) / 2
        ) * (average_pace / 100)

        home_net, home_off, home_def, home_source = (
            self._team_strength(home_stats)
        )

        away_net, away_off, away_def, away_source = (
            self._team_strength(away_stats)
        )

        home_expected = home_basic
        away_expected = away_basic

        # Advanced ratings improve the estimate when both
        # teams provide complete offensive and defensive ratings.
        if (
            home_off is not None
            and home_def is not None
            and away_off is not None
            and away_def is not None
        ):
            home_rating_points = (
                (home_off + away_def) / 2
            ) * (average_pace / 100)

            away_rating_points = (
                (away_off + home_def) / 2
            ) * (average_pace / 100)

            home_expected = (
                0.65 * home_rating_points
                + 0.35 * home_basic
            )

            away_expected = (
                0.65 * away_rating_points
                + 0.35 * away_basic
            )

        # Home-court adjustment.
        home_expected += 2.0

        projected_total = (
            home_expected + away_expected
        )

        projected_margin = (
            home_expected - away_expected
        )

        # Add a small net-rating adjustment when available.
        if home_net is not None and away_net is not None:
            net_difference = home_net - away_net

            projected_margin += (
                net_difference * 0.10
            )

            home_expected += (
                net_difference * 0.05
            )

            away_expected -= (
                net_difference * 0.05
            )

            projected_total = (
                home_expected + away_expected
            )

        # Win probability estimate, not calibrated certainty.
        home_probability = 1 / (
            1 + math.exp(
                -max(-50, min(50, projected_margin)) / 12
            )
        )

        away_probability = 1 - home_probability

        winner = (
            home_team
            if home_probability >= 0.5
            else away_team
        )

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_projected_points": round(
                home_expected, 1
            ),
            "away_projected_points": round(
                away_expected, 1
            ),
            "projected_total": round(
                projected_total, 1
            ),
            "projected_margin": round(
                projected_margin, 1
            ),
            "predicted_winner": winner,
            "home_win_probability": round(
                home_probability * 100, 1
            ),
            "away_win_probability": round(
                away_probability * 100, 1
            ),
            "model_confidence": round(
                max(home_probability, away_probability) * 100,
                1
            ),
            "rating_source": (
                "ADVANCED_RATINGS"
                if home_source == "ADVANCED_RATINGS"
                and away_source == "ADVANCED_RATINGS"
                else "BASIC_STATS"
            ),
            "status": "ESTIMATE",
        }
