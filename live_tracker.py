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
FIXTURES_URL = "https://v3.football.api-sports.io/fixtures"
TEAMS_URL = "https://v3.football.api-sports.io/teams"
HEADERS = {"x-apisports-key": API_KEY}

# چرخه اصلی: 15:00 تا 02:00 به وقت ایران = 11:30 تا 22:30 UTC
MAIN_WINDOW_START_MIN = 11 * 60 + 30
MAIN_WINDOW_END_MIN = 22 * 60 + 30

# تایید پایان بازی: 14:30 تا 22:30 UTC، هر 60 دقیقه
FULLTIME_WINDOW_START_MIN = 14 * 60 + 30
FULLTIME_WINDOW_END_MIN = 22 * 60 + 30
FULLTIME_CHECK_INTERVAL_MIN = 60

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

GOAL_LABELS = {
    "Normal Goal": "گل",
    "Penalty": "گل (پنالتی)",
    "Own Goal": "گل به خودی",
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


def get_fixture_state(state, fixture_id, home, away, league_name):
    key = str(fixture_id)
    if key not in state:
        state[key] = {
            "last_message_id": None,
            "kickoff_posted": False,
            "fulltime_posted": False,
            "posted_events": [],
            "events_detail": [],
            "home": home,
            "away": away,
            "league_name": league_name,
        }
    return state[key]


def match_label(home, away, league_name, home_goals, away_goals, home_flag="", away_flag=""):
    hg = home_goals if home_goals is not None else 0
    ag = away_goals if away_goals is not None else 0
    home_display = f"{home_flag} {home}".strip()
    away_display = f"{away_flag} {away}".strip()
    return f"⚽ {home_display} {hg} - {ag} {away_display}\n🏆 {league_name}\n\n{CHANNEL_TAG}"


def extract_events(item):
    """رویدادهای مهم یک فیکسچر را استخراج می‌کند."""
    results = []
    for ev in item.get("events", []):
        ev_type = ev.get("type")
        ev_detail = ev.get("detail", "")
        minute = ev.get("time", {}).get("elapsed")
        extra = ev.get("time", {}).get("extra")
        player = ev.get("player", {}).get("name", "")
        team_name = ev.get("team", {}).get("name", "")

        if ev_type == "Goal" and ev_detail in ("Normal Goal", "Penalty", "Own Goal", "Missed Penalty"):
            pass
        elif ev_type == "Card" and ev_detail in ("Red Card", "Second Yellow card"):
            pass
        elif ev_type == "Var":
            pass
        else:
            continue

        key = f"{ev_type}-{ev_detail}-{minute}-{extra}-{player}-{team_name}"
        results.append({
            "key": key,
            "type": ev_type,
            "detail": ev_detail,
            "minute": minute,
            "extra": extra,
            "player": player,
            "team": team_name,
        })
    return results


def event_live_text(ev, label):
    minute_str = f"{ev['minute']}'" + (f"+{ev['extra']}" if ev['extra'] else "")
    if ev["type"] == "Goal" and ev["detail"] == "Missed Penalty":
        return f"❌ پنالتی از دست رفته ({minute_str})\n{ev['team']} - {ev['player']}\n\n{label}"
    if ev["type"] == "Goal":
        tag = " (پنالتی)" if ev["detail"] == "Penalty" else (" (به خودی)" if ev["detail"] == "Own Goal" else "")
        return f"⚽ گل{tag}! ({minute_str})\n{ev['team']} - {ev['player']}\n\n{label}"
    if ev["type"] == "Card":
        return f"🟥 اخراج ({minute_str})\n{ev['team']} - {ev['player']}\n\n{label}"
    if ev["type"] == "Var":
        return f"📺 تصمیم VAR ({minute_str})\n{ev['detail']}\n\n{label}"
    return None


def build_fulltime_summary(fstate, home_goals, away_goals, home_flag, away_flag):
    home = fstate["home"]
    away = fstate["away"]
    hg = home_goals if home_goals is not None else 0
    ag = away_goals if away_goals is not None else 0

    lines = [f"🏁 نتیجه نهایی\n{home_flag} {home} {hg} - {ag} {away} {away_flag}".strip(), ""]

    sorted_events = sorted(
        fstate["events_detail"],
        key=lambda e: (e["minute"] or 0, e["extra"] or 0),
    )

    for ev in sorted_events:
        minute_str = f"{ev['minute']}'" + (f"+{ev['extra']}" if ev["extra"] else "")
        if ev["type"] == "Goal" and ev["detail"] == "Missed Penalty":
            lines.append(f"❌ پنالتی از دست رفته {ev['team']} دقیقه {minute_str} {ev['player']}")
        elif ev["type"] == "Goal":
            label = GOAL_LABELS.get(ev["detail"], "گل")
            lines.append(f"⚽ {label} {ev['team']} دقیقه {minute_str} {ev['player']}")
        elif ev["type"] == "Card":
            lines.append(f"🟥 کارت قرمز {ev['team']} دقیقه {minute_str} {ev['player']}")
        elif ev["type"] == "Var":
            lines.append(f"📺 تصمیم VAR دقیقه {minute_str}: {ev['detail']}")

    lines.append("")
    lines.append(CHANNEL_TAG)
    return "\n".join(lines)


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


def process_live_item(item, state, league_name, league_id, team_cache):
    fixture_id = item["fixture"]["id"]
    status_short = item["fixture"]["status"]["short"]
    home = item["teams"]["home"]["name"]
    away = item["teams"]["away"]["name"]
    home_id = item["teams"]["home"]["id"]
    away_id = item["teams"]["away"]["id"]
    home_goals = item["goals"]["home"]
    away_goals = item["goals"]["away"]

    home_flag = get_team_flag(home_id, team_cache) if league_id in CONTINENTAL_LEAGUES else ""
    away_flag = get_team_flag(away_id, team_cache) if league_id in CONTINENTAL_LEAGUES else ""

    fstate = get_fixture_state(state, fixture_id, home, away, league_name)

    if status_short in ("1H", "LIVE") and not fstate["kickoff_posted"]:
        text = f"🟢 شروع بازی\n{match_label(home, away, league_name, 0, 0, home_flag, away_flag)}"
        msg_id = send_telegram(text)
        fstate["last_message_id"] = msg_id
        fstate["kickoff_posted"] = True

    for ev in extract_events(item):
        if ev["key"] in fstate["posted_events"]:
            continue
        label = match_label(home, away, league_name, home_goals, away_goals, home_flag, away_flag)
        text = event_live_text(ev, label)
        if text:
            msg_id = send_telegram(text, reply_to=fstate["last_message_id"])
            fstate["last_message_id"] = msg_id
        fstate["posted_events"].append(ev["key"])
        fstate["events_detail"].append(ev)

    if status_short in ("FT", "AET", "PEN") and not fstate["fulltime_posted"]:
        text = build_fulltime_summary(fstate, home_goals, away_goals, home_flag, away_flag)
        msg_id = send_telegram(text, reply_to=fstate["last_message_id"])
        fstate["last_message_id"] = msg_id
        fstate["fulltime_posted"] = True


def reconcile_fixture(fixture_data, state, team_cache):
    """برای بازی‌هایی که در تایید دسته‌ای بررسی می‌شوند: رویدادهای جامانده را ثبت (بدون پست جدا) و در صورت پایان، خلاصه نهایی را پست می‌کند."""
    fixture_id = fixture_data["fixture"]["id"]
    key = str(fixture_id)
    if key not in state:
        return True  # اطلاعاتی نداریم، از صف حذفش می‌کنیم

    fstate = state[key]
    status_short = fixture_data["fixture"]["status"]["short"]
    home_goals = fixture_data["goals"]["home"]
    away_goals = fixture_data["goals"]["away"]

    # رویدادهای جامانده را بدون پست جداگانه ثبت می‌کنیم (در خلاصه نهایی می‌آیند)
    for ev in extract_events(fixture_data):
        if ev["key"] not in fstate["posted_events"]:
            fstate["posted_events"].append(ev["key"])
            fstate["events_detail"].append(ev)

    if status_short in ("FT", "AET", "PEN") and not fstate["fulltime_posted"]:
        league_id = fixture_data.get("league", {}).get("id")
        home_id = fixture_data["teams"]["home"]["id"]
        away_id = fixture_data["teams"]["away"]["id"]
        home_flag = get_team_flag(home_id, team_cache) if league_id in CONTINENTAL_LEAGUES else ""
        away_flag = get_team_flag(away_id, team_cache) if league_id in CONTINENTAL_LEAGUES else ""

        text = build_fulltime_summary(fstate, home_goals, away_goals, home_flag, away_flag)
        msg_id = send_telegram(text, reply_to=fstate["last_message_id"])
        fstate["last_message_id"] = msg_id
        fstate["fulltime_posted"] = True
        return True  # از صف حذف شود

    if status_short in ("NS", "CANC", "PST", "ABD"):
        return True  # وضعیت غیرمنتظره؛ از صف حذف می‌کنیم تا گیر نکند

    return False  # هنوز جریان دارد یا وضعیت نامشخص؛ در صف بماند


def run_fulltime_check(state, pending_ids, team_cache):
    if not pending_ids:
        return
    chunk = pending_ids[:20]
    ids_param = "-".join(str(i) for i in chunk)
    try:
        resp = requests.get(FIXTURES_URL, headers=HEADERS, params={"ids": ids_param}, timeout=30)
        resp.raise_for_status()
        results = resp.json().get("response", [])
    except Exception as e:
        print(f"خطا در تایید دسته‌ای پایان بازی: {e}")
        return

    resolved_ids = set()
    for fixture_data in results:
        fid = fixture_data["fixture"]["id"]
        try:
            done = reconcile_fixture(fixture_data, state, team_cache)
            if done:
                resolved_ids.add(fid)
        except Exception as e:
            print(f"خطا در بررسی نهایی بازی {fid}: {e}")

    # بازی‌هایی که اصلاً در جواب نیامدند هم از صف خارج می‌کنیم (جلوگیری از گیر کردن ابدی)
    returned_ids = {f["fixture"]["id"] for f in results}
    for fid in chunk:
        if fid not in returned_ids:
            resolved_ids.add(fid)

    pending_ids[:] = [i for i in pending_ids if i not in resolved_ids]


def main():
    now_utc = datetime.now(timezone.utc)
    minutes_now = now_utc.hour * 60 + now_utc.minute

    if not (MAIN_WINDOW_START_MIN <= minutes_now <= MAIN_WINDOW_END_MIN):
        print("خارج از بازه فعال اصلی؛ درخواستی ارسال نشد.")
        return

    state = load_json(STATE_FILE, {})
    team_cache = load_json(TEAM_COUNTRY_CACHE_FILE, {})
    meta = load_json("meta_live.json", {"pending_fulltime_ids": [], "last_fulltime_check_min": -9999})

    resp = requests.get(LIVE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("response", [])

    live_by_id = {}
    processed_count = 0

    for item in data:
        relevant, league_name, league_id = is_relevant(item)
        if not relevant:
            continue
        fixture_id = item["fixture"]["id"]
        live_by_id[fixture_id] = True
        try:
            process_live_item(item, state, league_name, league_id, team_cache)
            processed_count += 1
        except Exception as e:
            print(f"خطا در پردازش بازی {fixture_id}: {e}")

    # بازی‌هایی که شروع شده‌اند ولی پایانشان پست نشده و دیگر زنده نیستند را به صف اضافه می‌کنیم
    pending = set(meta["pending_fulltime_ids"])
    for key, fstate in state.items():
        fixture_id = int(key)
        if fstate.get("kickoff_posted") and not fstate.get("fulltime_posted") and fixture_id not in live_by_id:
            pending.add(fixture_id)
    meta["pending_fulltime_ids"] = list(pending)

    # اجرای تایید دسته‌ای فقط در بازه و فاصله مجاز
    in_fulltime_window = FULLTIME_WINDOW_START_MIN <= minutes_now <= FULLTIME_WINDOW_END_MIN
    enough_time_passed = (minutes_now - meta["last_fulltime_check_min"]) >= FULLTIME_CHECK_INTERVAL_MIN

    if in_fulltime_window and enough_time_passed and meta["pending_fulltime_ids"]:
        pending_list = meta["pending_fulltime_ids"]
        run_fulltime_check(state, pending_list, team_cache)
        meta["pending_fulltime_ids"] = pending_list
        meta["last_fulltime_check_min"] = minutes_now

    save_json(STATE_FILE, state)
    save_json(TEAM_COUNTRY_CACHE_FILE, team_cache)
    save_json("meta_live.json", meta)
    print(f"بازی‌های زنده پردازش‌شده: {processed_count} | در صف تایید پایان: {len(meta['pending_fulltime_ids'])}")


if __name__ == "__main__":
    main()
