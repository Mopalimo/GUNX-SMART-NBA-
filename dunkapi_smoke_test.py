"""Small CI smoke test for the DunkAPI repository secret.

This runs in GitHub Actions only. It never prints or embeds the API key.
"""
import os
import sys

try:
    from dunkapi import Client
except ImportError as exc:
    print("DUNKAPI SDK IMPORT FAILED:", exc)
    sys.exit(1)

if not os.environ.get("DUNKAPI_API_KEY"):
    print("DUNKAPI_API_KEY is not available to this workflow.")
    sys.exit(2)

try:
    client = Client()
    result = client.get_team_stats(season=2026, league="nba")
    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        result = result["data"]
    teams = result.get("teams", []) if isinstance(result, dict) else []
    if not teams:
        print("DunkAPI responded, but no team statistics were returned.")
        sys.exit(3)

    first = teams[0]
    print("DunkAPI authentication: OK")
    print("NBA team statistics: OK")
    print("Teams returned:", len(teams))
    print("Sample team:", first.get("display_name", first.get("abbrev", "available")))
    print("Season:", result.get("season", 2026))
    print("API key value: [not displayed]")
except Exception as exc:
    print("DunkAPI request failed:", type(exc).__name__, str(exc))
    sys.exit(4)
