"""Collect Steam reviews for the most-played games reported by SteamSpy."""

import argparse
import csv
import time
from typing import Any

import requests


STEAMSPY_URL = "https://steamspy.com/api.php"
STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{app_id}"
REVIEW_FIELDS = (
  "app_id",
  "recommendationid",
  "language",
  "review",
  "voted_up",
  "votes_up",
  "votes_funny",
  "weighted_vote_score",
  "comment_count",
  "steam_purchase",
  "received_for_free",
  "written_during_early_access",
  "timestamp_created",
)


def get_appids(session: requests.Session, game_count: int) -> list[str]:
  """Return app IDs for the games with the most players in the last two weeks."""
  response = session.get(
    STEAMSPY_URL,
    params={"request": "top100in2weeks"},
    timeout=30,
  )
  response.raise_for_status()
  games = response.json()
  return list(games)[:game_count]


def get_reviews(
  session: requests.Session,
  app_id: str,
  review_limit: int,
  page_size: int = 100,
) -> list[dict[str, Any]]:
  """Fetch up to review_limit reviews for one app using Steam's cursor pagination."""
  reviews: list[dict[str, Any]] = []
  cursor = "*"

  while len(reviews) < review_limit:
    response = session.get(
      STEAM_REVIEWS_URL.format(app_id=app_id),
      params={
        "json": 1,
        "language": "all",
        "num_per_page": min(page_size, review_limit - len(reviews)),
        "filter": "all",
        "cursor": cursor,
      },
      timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    page = payload.get("reviews", [])

    for review in page:
      reviews.append(
        {field: review.get(field) for field in REVIEW_FIELDS if field != "app_id"}
        | {"app_id": app_id}
      )

    next_cursor = payload.get("cursor")
    if not page or not next_cursor or next_cursor == cursor:
      break
    cursor = next_cursor

  return reviews[:review_limit]


def scrape_reviews(
  game_count: int,
  reviews_per_game: int,
  output_path: str,
  delay_seconds: float,
) -> int:
  """Scrape reviews and return the number of rows written."""
  session = requests.Session()
  session.headers.update({"User-Agent": "steam-sentiment-analysis/1.0"})
  app_ids = get_appids(session, game_count)
  rows: list[dict[str, Any]] = []

  for index, app_id in enumerate(app_ids, start=1):
    print(f"Fetching game {index}/{len(app_ids)} (app {app_id})...")
    rows.extend(get_reviews(session, app_id, reviews_per_game))
    if index < len(app_ids):
      time.sleep(delay_seconds)

  with open(output_path, "w", newline="", encoding="utf-8") as output_file:
    writer = csv.DictWriter(output_file, fieldnames=REVIEW_FIELDS)
    writer.writeheader()
    writer.writerows(rows)

  return len(rows)


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--games", type=int, default=10, help="Number of popular games to scrape")
  parser.add_argument("--reviews-per-game", type=int, default=100, help="Maximum reviews per game")
  parser.add_argument("--output", default="steam_reviews.csv", help="CSV output path")
  parser.add_argument("--delay", type=float, default=1.0, help="Seconds between games")
  args = parser.parse_args()

  if args.games < 1 or args.reviews_per_game < 1 or args.delay < 0:
    parser.error("games and reviews-per-game must be positive; delay cannot be negative")

  row_count = scrape_reviews(args.games, args.reviews_per_game, args.output, args.delay)
  print(f"Wrote {row_count} reviews to {args.output}")


if __name__ == "__main__":
  main()