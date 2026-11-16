
import math


class NBAAnalysisEngine:
    """
    GUNX SMART NBA Analysis Engine.

    Uses team season statistics and advanced ratings.
    Does not invent missing statistics.
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
                "Missing statistics: "
                + ", ".join(missing)
            )

        for key in self.REQUIRED_STATS:

            try:
                value = float(team[key])
            except (TypeError, ValueError):
                raise ValueError(
                    "Invalid statistic: " + key
                )

            if not math.isfinite(value):
                raise ValueError(
                    "Non-finite statistic: " + key
                )

        if float(team["ppg"]) < 0:
            raise ValueError("PPG cannot be negative.")

        if float(team["opp_ppg"]) < 0:
            raise ValueError(
                "Opponent PPG cannot be negative."
            )

        if float(team["pace"]) <= 0:
            raise ValueError(
                "Pace must be greater than zero."
            )

        if not 0 <= float(team["win_pct"]) <= 1:
            raise ValueError(
                "win_pct must be between 0 and 1."
            )

    @staticmethod
    def _optional_number(team, key):

        value = team.get(key)

        if value is None:
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None

        return number

    def _calculate_team_rating(self, team):

        off_rating = self._optional_number(
            team,
            "off_rating"
        )

        def_rating = self._optional_number(
            team,
            "def_rating"
        )

        net_rating = self._optional_number(
            team,
            "net_rating"
        )

        if net_rating is None:
            if (
                off_rating is not None
                and def_rating is not None
            ):
                net_rating = off_rating - def_rating

        return {
            "off_rating": off_rating,
            "def_rating": def_rating,
            "net_rating": net_rating,
        }

    def analyze_game(
        self,
        home_team,
        away_team,
        home_stats,
        away_stats
    ):

        self._validate_team(home_stats)
        self._validate_team(away_stats)

        if not home_team or not away_team:
            raise ValueError(
                "Both team names are required."
            )

        if (
            str(home_team).strip().lower()
            == str(away_team).strip().lower()
        ):
            raise ValueError(
                "Home and away teams cannot be the same."
            )

        home_ppg = float(home_stats["ppg"])
        away_ppg = float(away_stats["ppg"])

        home_def = float(home_stats["opp_ppg"])
        away_def = float(away_stats["opp_ppg"])

        home_pace = float(home_stats["pace"])
        away_pace = float(away_stats["pace"])

        average_pace = (
            home_pace + away_pace
        ) / 2

        # Basic points projection.
        home_basic = (
            (home_ppg + away_def) / 2
        ) * (average_pace / 100)

        away_basic = (
            (away_ppg + home_def) / 2
        ) * (average_pace / 100)

        home_rating = self._calculate_team_rating(
            home_stats
        )

        away_rating = self._calculate_team_rating(
            away_stats
        )

        home_off = home_rating["off_rating"]
        away_off = away_rating["off_rating"]

        home_def_rating = home_rating["def_rating"]
        away_def_rating = away_rating["def_rating"]

        advanced_available = all(
            value is not None
            for value in (
                home_off,
                away_off,
                home_def_rating,
                away_def_rating,
            )
        )

        if advanced_available:

            # Advanced rating based projection.
            home_advanced = (
                home_off + away_def_rating
            ) / 2

            away_advanced = (
                away_off + home_def_rating
            ) / 2

            home_expected = (
                home_basic * 0.35
                + home_advanced
                * (average_pace / 100) * 0.65
            )

            away_expected = (
                away_basic * 0.35
                + away_advanced
                * (average_pace / 100) * 0.65
            )

            rating_source = "ADVANCED_RATINGS"

        else:

            home_expected = home_basic
            away_expected = away_basic

            rating_source = "BASIC_STATS"

        # Home court advantage.
        home_expected += 2.0

        # Small adjustment using net rating difference.
        home_net = home_rating["net_rating"]
        away_net = away_rating["net_rating"]

        if (
            home_net is not None
            and away_net is not None
        ):

            net_difference = (
                home_net - away_net
            )

            adjustment = max(
                -5.0,
                min(5.0, net_difference * 0.05)
            )

            home_expected += adjustment
            away_expected -= adjustment

        # Prevent impossible negative score projections.
        home_expected = max(0.0, home_expected)
        away_expected = max(0.0, away_expected)

        projected_total = (
            home_expected + away_expected
        )

        projected_margin = (
            home_expected - away_expected
        )

        # Win probability estimate.
        exponent = max(
            -20,
            min(20, -projected_margin / 12)
        )

        home_probability = 1 / (
            1 + math.exp(exponent)
        )

        away_probability = (
            1 - home_probability
        )

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
                confidence, 1
            ),

            "rating_source": rating_source,

            "status": "ESTIMATE",
        }
