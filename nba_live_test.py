
from nba_data import NBADataProvider, NBADataError


def run_live_test():

    print("=" * 50)
    print("       GUNX NBA LIVE DATA TEST")
    print("=" * 50)

    provider = NBADataProvider(
        timeout=45,
        retries=1
    )

    season = provider.current_season()

    print("\nNBA SEASON:", season)
    print("Connecting to NBA Stats API...")

    try:
        print("\nTEST 1: BASE STATISTICS")

        base_data = provider._request_stats(
            season,
            "Base"
        )

        print("Base rows received:", len(base_data))

        if not base_data:
            raise NBADataError("Base data is empty.")

        print("\nTEST 2: ADVANCED STATISTICS")

        advanced_data = provider._request_stats(
            season,
            "Advanced"
        )

        print(
            "Advanced rows received:",
            len(advanced_data)
        )

        if not advanced_data:
            raise NBADataError(
                "Advanced data is empty."
            )

        print("\nTEST 3: TEAM DATA VALIDATION")

        teams = provider.get_all_team_stats(
            season,
            force_refresh=True
        )

        print("Valid teams:", len(teams))

        if len(teams) < 20:
            raise NBADataError(
                "Fewer than 20 NBA teams received."
            )

        print("\nSAMPLE TEAM:")

        sample = next(iter(teams.values()))

        print("Team:", sample["team_name"])
        print("PPG:", sample["ppg"])
        print("Pace:", sample["pace"])
        print("Offensive Rating:", sample["off_rating"])
        print("Defensive Rating:", sample["def_rating"])
        print("Net Rating:", sample["net_rating"])

        print("\nNBA LIVE DATA TEST PASSED")

    except Exception as exc:

        print("\nNBA LIVE DATA TEST FAILED")
        print("Error type:", type(exc).__name__)
        print("Reason:", str(exc))

        raise SystemExit(1)


if __name__ == "__main__":
    run_live_test()
