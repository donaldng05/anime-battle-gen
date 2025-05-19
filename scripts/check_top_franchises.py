# scripts/check_top_franchises.py

import requests

ANILIST_API = "https://graphql.anilist.co"

# GraphQL query to fetch Top N by popularity
QUERY = '''
query ($type: MediaType, $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: $type, sort: POPULARITY_DESC) {
      title { romaji }
      popularity
    }
  }
}
'''

def fetch_top(media_type: str, per_page: int = 50):
    variables = {"type": media_type, "page": 1, "perPage": per_page}
    resp = requests.post(ANILIST_API, json={"query": QUERY, "variables": variables})
    resp.raise_for_status()
    data = resp.json()["data"]["Page"]["media"]
    return [m["title"]["romaji"] for m in data]

def annotate_picks(top_list, picks):
    """
    Return a dict mapping each pick → list of (rank, exact title)
    where the pick appears as a substring (case-insensitive).
    """
    picks_lc = [p.lower() for p in picks]
    found = {p: [] for p in picks}
    for idx, title in enumerate(top_list, start=1):
        t_lc = title.lower()
        for p, plc in zip(picks, picks_lc):
            if plc in t_lc:
                found[p].append((idx, title))
    return found

if __name__ == "__main__":
    # 1) Your target franchises
    picks = ["One Piece", "Dragon Ball", "Naruto", "Jujutsu Kaisen"]

    # 2) Fetch live Top 50 lists
    top_anime = fetch_top("ANIME", per_page=50)
    top_manga = fetch_top("MANGA", per_page=50)

    # 3) Annotate where our picks appear
    anime_hits = annotate_picks(top_anime, picks)
    manga_hits = annotate_picks(top_manga, picks)

    # 4) Print Top 50 Anime
    print("Top 50 Anime by Popularity:")
    for i, title in enumerate(top_anime, 1):
        mark = "✅" if any(title == hit[1] for hits in anime_hits.values() for hit in hits) else ""
        print(f"{i:2d}. {title} {mark}")

    # 5) Print Top 50 Manga
    print("\nTop 50 Manga by Popularity:")
    for i, title in enumerate(top_manga, 1):
        mark = "✅" if any(title == hit[1] for hits in manga_hits.values() for hit in hits) else ""
        print(f"{i:2d}. {title} {mark}")

    # 6) Summary
    print("\nSummary:")
    for p in picks:
        a = anime_hits[p]
        m = manga_hits[p]
        if a:
            ranks = ", ".join(f"{r} (‘{t}’)" for r, t in a)
            print(f"• {p} in Anime @ ranks: {ranks}")
        else:
            print(f"• {p} not in Top 50 Anime")
        if m:
            ranks = ", ".join(f"{r} (‘{t}’)" for r, t in m)
            print(f"  {p} in Manga @ ranks: {ranks}")
        else:
            print(f"  {p} not in Top 50 Manga")
