In this project, we scrape reviews and player counts for a sample of games from Steam in order to find which game genres are most popular player count wise as well as which genres get the most community support.

The main problem we want to tackle with this project is finding an optimal way to weight sarcasm/troll reviews in the overall analysis.

## Collect reviews

Install the dependencies, then run:

```powershell
python scraper.py --games 10 --reviews-per-game 100 --output steam_reviews.csv
```

The scraper gets the most-played games from SteamSpy, fetches reviews from Steam's public review endpoint, and writes the results to CSV. Use a smaller run while developing:

```powershell
python scraper.py --games 1 --reviews-per-game 10 --delay 0
```
