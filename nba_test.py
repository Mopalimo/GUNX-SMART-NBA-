
from nba_engine import NBAAnalysisEngine


def run_test():

    print("=" * 50)
    print("       GUNX SMART NBA - ENGINE TEST")
    print("=" * 50)

    engine = NBAAnalysisEngine()

    home = "Boston Celtics"
    away = "Los Angeles Lakers"

    home_stats = {
        "ppg": 118.5,
        "opp_ppg": 108.2,
        "pace": 98.5,
        "win_pct": 0.72,
        "off_rating": 120.5,
        "def_rating": 108.5,
        "net_rating": 12.0,
    }

    away_stats = {
        "ppg": 114.2,
        "opp_ppg": 112.8,
        "pace": 100.2,
        "win_pct": 0.61,
        "off_rating": 116.0,
        "def_rating": 112.0,
        "net_rating": 4.0,
    }

    print("\nAnalyzing:", home, "vs", away)

    result = engine.analyze_game(
        home,
        away,
        home_stats,
        away_stats
    )

    required = [
        "home_projected_points",
        "away_projected_points",
        "projected_total",
        "projected_margin",
        "predicted_winner",
        "home_win_probability",
        "away_win_probability",
        "model_confidence",
        "rating_source",
    ]

    missing = [
        key for key in required
        if key not in result
    ]

    if missing:
        raise AssertionError(
            "Missing fields: " + str(missing)
        )

    probability_sum = (
        result["home_win_probability"]
        + result["away_win_probability"]
    )

    if abs(probability_sum - 100) > 0.2:
        raise AssertionError(
            "Invalid win probabilities."
        )

    if abs(
        result["projected_total"]
        - (
            result["home_projected_points"]
            + result["away_projected_points"]
        )
    ) > 0.2:
        raise AssertionError(
            "Projected total calculation failed."
        )

    print("\nPROJECTED SCORE")
    print(
        result["home_team"],
        result["home_projected_points"],
        "-",
        result["away_projected_points"],
        result["away_team"]
    )

    print("\nPROJECTED TOTAL:", result["projected_total"])
    print("PREDICTED WINNER:", result["predicted_winner"])

    print(
        "HOME WIN PROBABILITY:",
        result["home_win_probability"], "%"
    )

    print(
        "AWAY WIN PROBABILITY:",
        result["away_win_probability"], "%"
    )

    print("RATING SOURCE:", result["rating_source"])

    print("\nVALIDATION: PASSED")

    print("=" * 50)
    print("       GUNX ENGINE TEST PASSED")
    print("=" * 50)


if __name__ == "__main__":
    run_test()
