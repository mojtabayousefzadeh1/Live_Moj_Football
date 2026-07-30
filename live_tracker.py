import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ["API_FOOTBALL_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

STATE_FILE = "state_live.json"
TEAM_COUNTRY_CACHE_FILE = "team_country_cache.json"
LIVE_URL = "https://v3.football.api-sports.io/fixtures?live=all"
TEAMS_URL = "https://v3.football.api-sports.io/teams"
HEADERS = {"x-apisports-key": API_KEY}

WINDOW_START_UTC_MIN = 10 * 60 + 30
WINDOW_END_UTC_MIN = 22 * 60 + 30

CHANNEL_TAG = "@moj_football"

CONTINENTAL_LEAGUES = {2, 3, 848, 17, 18}

LEAGUES = {
    696: "🇬🇧 پریمیرلیگ انگلیس",
    45: "🇬🇧 جام حذفی انگلیس (FA Cup)",
    48: "🇬🇧 جام اتحادیه انگلیس (EFL Cup)",
    528: "🇬🇧 کامیونیتی شیلد انگلیس",
    140: "🇪🇸 لالیگا اسپانیا",
    143: "🇪🇸 کوپا دل‌ری",
    556: "🇪🇸 سوپرکاپ اسپانیا",
    61: "🇫🇷 لیگ ۱ فرانسه",
    66: "🇫🇷 کوپ دو فرانس",
    135: "🇮🇹 سری‌آ ایتالیا",
    137: "🇮🇹 کوپا ایتالیا",
    78: "🇩🇪 بوندسلیگا آلمان",
    715: "🇩🇪 یوپوکال آلمان (DFB Pokal)",
    290: "🇮🇷 لیگ برتر ایران",
    291: "🇮🇷 لیگ دسته اول ایران (آزادگان)",
    495: "🇮🇷 جام حذفی ایران",
    905: "🇮🇷 سوپرکاپ ایران",
    2: "لیگ قهرمانان اروپا",
    3: "لیگ اروپا",
    848: "لیگ کنفرانس اروپا",
    17: "لیگ قهرمانان آسیا (نخبگان)",
    18: "لیگ قهرمانان آسیا ۲",
    1: "🌐 جام جهانی",
    15: "🌐 جام باشگاه‌های جهان",
    4: "🌐 یورو",
    7: "🌐 جام ملت‌های آسیا",
    9: "🌐 کوپا آمه‌ریکا",
    6: "🌐 جام ملت‌های آفریقا",
    5: "🌐 لیگ ملت‌های اروپا",
    30: "🌐 انتخابی جام جهانی - آسیا",
    31: "🌐 انتخابی جام جهانی - کونکاکاف",
    29: "🌐 انتخابی جام جهانی - آفریقا",
    32: "🌐 انتخابی جام جهانی - اروپا",
    34: "🌐 انتخابی جام جهانی - آمریکای جنوبی",
}

SPECIAL_TEAMS = {
    10: "تیم ملی انگلیس",
    33: "منچستریونایتد",
    40: "لیورپول",
    42: "آرسنال",
    50: "منچسترسیتی",
    2: "تیم ملی فرانسه",
    85: "پاریس سن‌ژرمن",
    25: "تیم ملی آلمان",
    157: "بایرن مونیخ",
    9: "تیم ملی اسپانیا",
    529: "بارسلونا",
    541: "رئال مادرید",
    22: "تیم ملی ایران",
    2733: "استقلال",
    2742: "پرسپولیس",
    7500: "داماش گیلان",
    2710: "سپیدرود رشت",
    2939: "النصر",
    2932: "الهلال",
    9568: "اینترمیامی",
    6: "تیم ملی برزیل",
    26: "تیم ملی آرژانتین",
    27: "تیم ملی پرتغال",
    497: "آ‌اس‌رم",
    505: "اینترمیلان",
    489: "آث‌میلان",
    496: "یوونتوس",
    266: "چلسی",
}

COUNTRY_FLAGS = {
    "England": "🇬🇧", "Spain": "🇪🇸", "France": "🇫🇷", "Italy": "🇮🇹",
    "Germany": "🇩🇪", "Portugal": "🇵🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
    "Iran": "🇮🇷", "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "UAE": "🇦🇪",
    "Japan": "🇯🇵", "South Korea": "🇰🇷", "Australia": "🇦🇺", "China PR": "🇨🇳",
    "Uzbekistan": "🇺🇿", "Iraq": "🇮🇶", "Jordan": "🇯🇴", "Kuwait": "🇰🇼",
    "Turkey": "🇹🇷", "Greece": "🇬🇷", "Scotland": "🇬🇧", "Austria": "🇦🇹",
    "Switzerland": "🇨🇭", "Croatia": "🇭🇷", "Serbia": "🇷🇸", "Ukraine": "🇺🇦",
    "Poland": "🇵🇱", "Czech-Republic": "🇨🇿", "Denmark": "🇩🇰", "Sweden": "🇸🇪",
    "Norway": "🇳🇴", "Brazil": "🇧🇷", "Argentina": "🇦🇷", "Egypt": "🇪🇬",
    "Morocco": "🇲🇦", "Tunisia": "🇹🇳", "Algeria": "🇩🇿", "USA": "🇺🇸",
    "Mexico": "🇲🇽", "Russia": "🇷🇺", "Azerbaijan": "🇦🇿", "Israel": "🇮🇱",
}


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_team_flag(team_id, cache):
    key = str(team_id)
    if key in cache:
        country = cache[key]
    else:
        country = ""
        try:
            resp = requests.get(TEAMS_URL, headers=HEADERS, params={"id": team_id}, timeout=30)
            resp.raise_for_status()
            data = resp.json().get("response", [])
            if data:
                country = data[0]["team"].get("country", "") or ""
        except Exception as e:
            print(f"خطا در گرفتن کشور تیم {team_id}: {e}")
        cache[key] = country

    return COUNTRY_FLAGS.get(country, "")


def send_telegram(text, reply_to=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["result"]["message_id"]


def get_fixture_state(state, fixture_id):
    key = str(fixture_id)
    if key not in state:
        state[key] = {
            "last_message_id": None,
            "kickoff_posted": False,
            "fulltime_posted": False,
            "posted_events": [],
        }
    return state[key]


def match_label(home, away, league_name, home_goals, away_goals, home_flag="", away_flag=""):
    hg = home_goals if home_goals is not None else 0
    ag = away_goals if away_goals is not None else 0
    home_display = f"{home_flag} {home}".strip()
    away_display = f"{away_flag} {away}".strip()
    return f"⚽ {home_display} {hg} - {ag} {away_display}\n🏆 {league_name}\n\n{CHANNEL_TAG}"


def process_fixture(item, state, league_name, league_id, team_cache):
    fixture_id = item["fixture"]["id"]
    status_short = item["fixture"]["status"]["short"]
    home = item["teams"]["home"]["name"]
    away = item["teams"]["away"]["name"]
    home_id = item["teams"]["home"]["id"]
    away_id = item["teams"]["away"]["id"]
    home_goals = item["goals"]["home"]
    away_goals = item["goals"]["away"]

    home_flag = ""
    away_flag = ""
    if league_id in CONTINENTAL_LEAGUES:
        home_flag = get_team_flag(home_id, team_cache)
        away_flag = get_team_flag(away_id, team_cache)

    fstate = get_fixture_state(state, fixture_id)

    if status_short in ("1H", "LIVE") and not fstate["kickoff_posted"]:
        text = f"🟢 شروع بازی\n{match_label(home, away, league_name, 0, 0, home_flag, away_flag)}"
        msg_id = send_telegram(text)
        fstate["last_message_id"] = msg_id
        fstate["kickoff_posted"] = True

    for ev in item.get("events", []):
        ev_type = ev.get("type")
        ev_detail = ev.get("detail", "")
        minute = ev.get("time", {}).get("elapsed")
        extra = ev.get("time", {}).get("extra")
        player = ev.get("player", {}).get("name", "")
        team_name = ev.get("team", {}).get("name", "")

        ev_key = f"{ev_type}-{ev_detail}-{minute}-{extra}-{player}-{team_name}"
        if ev_key in fstate["posted_events"]:
            continue

        minute_str = f"{minute}'" + (f"+{extra}" if extra else "")
        text = None
        label = match_label(home, away, league_name, home_goals, away_goals, home_flag, away_flag)

        if ev_type == "Goal" and ev_detail == "Missed Penalty":
            text = f"❌ پنالتی از دست رفته ({minute_str})\n{team_name} - {player}\n\n{label}"
        elif ev_type == "Goal":
            text = f"⚽ گل! ({minute_str})\n{team_name} - {player}\n\n{label}"
        elif ev_type == "Card" and ev_detail in ("Red Card", "Second Yellow card"):
            text = f"🟥 اخراج ({minute_str})\n{team_name} - {player}\n\n{label}"
        elif ev_type == "Var":
            text = f"📺 تصمیم VAR ({minute_str})\n{ev_detail}\n\n{label}"

        if text:
            msg_id = send_telegram(text, reply_to=fstate["last_message_id"])
            fstate["last_message_id"] = msg_id
            fstate["posted_events"].append(ev_key)

    if status_short in ("FT", "AET", "PEN") and not fstate["fulltime_posted"]:
        text = f"🏁 پایان بازی\n{match_label(home, away, league_name, home_goals, away_goals, home_flag, away_flag)}"
        msg_id = send_telegram(text, reply_to=fstate["last_message_id"])
        fstate["last_message_id"] = msg_id
        fstate["fulltime_posted"] = True


def is_relevant(item):
    league_id = item.get("league", {}).get("id")
    home_id = item.get("teams", {}).get("home", {}).get("id")
    away_id = item.get("teams", {}).get("away", {}).get("id")

    if league_id in LEAGUES:
        return True, LEAGUES[league_id], league_id
    if home_id in SPECIAL_TEAMS or away_id in SPECIAL_TEAMS:
        api_league_name = item.get("league", {}).get("name", "بازی دوستانه/سایر")
        return True, api_league_name, league_id
    return False, None, None


def main():
    now_utc = datetime.now(timezone.utc)
    minutes_now = now_utc.hour * 60 + now_utc.minute

    if not (WINDOW_START_UTC_MIN <= minutes_now <= WINDOW_END_UTC_MIN):
        print("خارج از بازه فعال (۱۴:۰۰ تا ۰۲:۰۰ به وقت ایران)؛ درخواستی ارسال نشد.")
        return

    resp = requests.get(LIVE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("response", [])

    state = load_json(STATE_FILE, {})
    team_cache = load_json(TEAM_COUNTRY_CACHE_FILE, {})
    processed_count = 0

    for item in data:
        relevant, league_name, league_id = is_relevant(item)
        if not relevant:
            continue
        try:
            process_fixture(item, state, league_name, league_id, team_cache)
            processed_count += 1
        except Exception as e:
            fixture_id = item.get("fixture", {}).get("id", "?")
            print(f"خطا در پردازش بازی {fixture_id}: {e}")
            continue

    save_json(STATE_FILE, state)
    save_json(TEAM_COUNTRY_CACHE_FILE, team_cache)
    print(f"تعداد بازی‌های پردازش‌شده در این اجرا: {processed_count}")


if __name__ == "__main__":
    main()
