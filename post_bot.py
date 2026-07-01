"""
Social Auto Poster
-------------------
Roz chalta hai (GitHub Actions cron ke zariye), schedule.json mein se
aaj ka post nikalta hai, AI se image + caption generate karta hai,
aur Facebook Page + Instagram Business account par post kar deta hai.

Agar schedule khatam ho jaye (koi naya month na diya jaye), to yeh
automatically WAPAS SHURU se (day 1) cycle kar deta hai -- isliye
posting kabhi nahi rukti.
"""

import json
import os
import sys
import urllib.parse
from datetime import date, datetime

import requests

# ---------- CONFIG (GitHub Secrets se aate hain) ----------
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # optional

GRAPH_API_VERSION = "v19.0"
SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), "schedule.json")


def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_todays_post(schedule):
    """Start_date se leke aaj tak kitne din guzray hain wo nikal ke,
    schedule ki list mein se uss din ka post cycle karke wapis deta hai."""
    start = datetime.strptime(schedule["start_date"], "%Y-%m-%d").date()
    today = date.today()
    days_passed = (today - start).days

    posts = schedule["posts"]
    if not posts:
        raise ValueError("schedule.json mein koi post nahi mila.")

    # Loop / cycle logic -- jitne bhi din guzray hon, posts ki length se
    # mod le kar hamesha ek valid index milta hai (schedule khud ba khud
    # repeat hoti rehti hai)
    index = days_passed % len(posts)
    return posts[index]


def generate_caption(topic, fallback_caption):
    if fallback_caption:
        return fallback_caption

    if not ANTHROPIC_API_KEY:
        # AI key nahi di gayi to simple caption bana dete hain
        return f"{topic} #motivation #dailypost"

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Instagram/Facebook ke liye is topic par ek "
                        f"chota, engaging caption likhein (2-3 lines, "
                        f"emojis + relevant hashtags ke sath): {topic}"
                    ),
                }
            ],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"].strip()


def generate_image_url(image_prompt):
    """Pollinations.ai (free, no API key) se image URL banata hai."""
    encoded_prompt = urllib.parse.quote(image_prompt)
    # width/height aur seed add karte hain taake image consistent size ki ho
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    return url


def post_to_facebook(image_url, caption):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{FB_PAGE_ID}/photos"
    resp = requests.post(
        url,
        data={
            "url": image_url,
            "caption": caption,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        },
        timeout=60,
    )
    print("Facebook response:", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()


def post_to_instagram(image_url, caption):
    base = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}"

    # Step 1: media container banana
    create_resp = requests.post(
        f"{base}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=60,
    )
    print("IG create response:", create_resp.status_code, create_resp.text)
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    # Step 2: publish karna
    publish_resp = requests.post(
        f"{base}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=60,
    )
    print("IG publish response:", publish_resp.status_code, publish_resp.text)
    publish_resp.raise_for_status()
    return publish_resp.json()


def main():
    missing = [
        name
        for name, val in [
            ("FB_PAGE_ID", FB_PAGE_ID),
            ("FB_PAGE_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN),
            ("IG_USER_ID", IG_USER_ID),
        ]
        if not val
    ]
    if missing:
        print(f"ERROR: Ye secrets set nahi hain: {', '.join(missing)}")
        sys.exit(1)

    schedule = load_schedule()
    post = get_todays_post(schedule)

    print(f"Aaj ka post (day {post['day']}): {post['topic']}")

    caption = generate_caption(post["topic"], post.get("caption", ""))
    image_url = generate_image_url(post["image_prompt"])

    print("Generated caption:", caption)
    print("Generated image URL:", image_url)

    fb_result = post_to_facebook(image_url, caption)
    ig_result = post_to_instagram(image_url, caption)

    print("Done! FB post id:", fb_result.get("id"))
    print("Done! IG post id:", ig_result.get("id"))


if __name__ == "__main__":
    main()
