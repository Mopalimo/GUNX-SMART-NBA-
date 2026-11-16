
from nba_integration import GUNXNBAIntegration


def print_line():
    print("=" * 50)


def run_test():

    print_line()
    print("       GUNX SMART NBA - SYSTEM TEST")
    print_line()

    gunx = GUNXNBAIntegration()

    home = "Boston Celtics"
    away = "Los Angeles Lakers"

    print("\nMATCH:", home, "vs", away)
    print("\nFetching NBA season statistics...")

    result = gunx.analyze_match(
        home,
        away
    )

    # Check for errors.
    if result.get("status") != "SUCCESS":

        print("\nTEST FAILED")
        print("Reason:", result.get("message"))

        return False

    home_stats = result["home_team_stats"]
    away_stats = result["away_team_stats"]

    print("\nNBA DATA RECEIVED SUCCESSFULLY")

    print("\nDATA INFORMATION")
    print("-" * 40)

    print("Data Source:", result.get("data_source"))
    print("Data Status:", result.get("data_status"))
    print("Season:", result.get("season"))

    print("\nHOME TEAM")
    print("-" * 40)

    print("Team:", result["home_team"])
    print("PPG:", home_stats.get("ppg"))
    print("Opponent PPG:", home_stats.get("opp_ppg"))
    print("Pace:", home_stats.get("pace"))
    print("Win Percentage:", home_stats.get("win_pct"))
    print("Offensive Rating:", home_stats.get("off_rating"))
    print("Defensive Rating:", home_stats.get("def_rating"))
    print("Net Rating:", home_stats.get("net_rating"))
    print("Games Played:", home_stats.get("games_played"))

    print("\nAWAY TEAM")
    print("-" * 40)

    print("Team:", result["away_team"])
    print("PPG:", away_stats.get("ppg"))
    print("Opponent PPG:", away_stats.get("opp_ppg"))
    print("Pace:", away_stats.get("pace"))
    print("Win Percentage:", away_stats.get("win_pct"))
    print("Offensive Rating:", away_stats.get("off_rating"))
    print("Defensive Rating:", away_stats.get("def_rating"))
    print("Net Rating:", away_stats.get("net_rating"))
    print("Games Played:", away_stats.get("games_played"))

    print("\nGUNX ADVANCED ANALYSIS")
    print("-" * 40)

    print(
        "Rating Source:",
        result.get("rating_source")
    )

    print(
        "Projected Score:",
        result["home_projected_points"],
        "-",
        result["away_projected_points"]
    )

    print(
        "Projected Total:",
        result["projected_total"]
    )

    print(
        "Projected Margin:",
        result["projected_margin"]
    )

    print(
        "Predicted Winner:",
        result["predicted_winner"]
    )

    print(
        "Home Win Probability:",
        result["home_win_probability"], "%"
    )

    print(
        "Away Win Probability:",
        result["away_win_probability"], "%"
    )

    print(
        "Model Confidence:",
        result["model_confidence"], "%"
    )

    print("\nVALIDATION")

    required_fields = [
        "home_projected_points",
        "away_projected_points",
        "projected_total",
        "predicted_winner",
        "home_win_probability",
        "away_win_probability",
        "rating_source",
    ]

    missing = [
        field
        for field in required_fields
        if field not in result
    ]

    if missing:
        print("MISSING FIELDS:", missing)
        print("\nTEST FAILED")
        return False

    probability_sum = (
        result["home_win_probability"]
        + result["away_win_probability"]
    )

    if abs(probability_sum - 100) > 0.2:
        print("Probability validation failed.")
        print("Probability sum:", probability_sum)
        return False

    print("Required fields: PASS")
    print("Probability validation: PASS")

    if (
        home_stats.get("net_rating") is not None
        and away_stats.get("net_rating") is not None
    ):
        print("Net Rating validation: PASS")
    else:
        print("Net Rating validation: NOT AVAILABLE")

    print_line()
    print("       GUNX SYSTEM TEST PASSED")
    print_line()

    return True


if __name__ == "__main__":
    success = run_test()

    if not success:
        raise SystemExit(1)
    
