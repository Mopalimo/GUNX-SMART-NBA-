from nba_integration import GUNXNBAIntegration


def run_test():

    print("=" * 45)
    print("       GUNX SMART NBA - SYSTEM TEST")
    print("=" * 45)

    gunx = GUNXNBAIntegration()

    home = "Boston Celtics"
    away = "Los Angeles Lakers"

    print("\nFetching NBA team statistics...")
    print(f"Match: {home} vs {away}")

    result = gunx.analyze_match(
        home,
        away
    )

    if result.get("status") == "ERROR":
        print("\nTEST FAILED")
        print("Reason:", result.get("message"))
        return

    print("\nNBA DATA RECEIVED SUCCESSFULLY")

    print("\nHOME TEAM:")
    print(result["home_team"])

    print("PPG:", result["home_team_stats"]["ppg"])
    print("PACE:", result["home_team_stats"]["pace"])
    print("WIN %:", result["home_team_stats"]["win_pct"])

    print("\nAWAY TEAM:")
    print(result["away_team"])

    print("PPG:", result["away_team_stats"]["ppg"])
    print("PACE:", result["away_team_stats"]["pace"])
    print("WIN %:", result["away_team_stats"]["win_pct"])

    print("\nGUNX PREDICTION")
    print("-" * 35)

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

    print("\nGUNX TEST COMPLETED")


if __name__ == "__main__":
    run_test()
  
