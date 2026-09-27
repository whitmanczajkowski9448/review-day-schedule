from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "students.json"
APP_TITLE = "Senior CERT / PSAT Review Day | Student Schedule Lookup"


st.set_page_config(
    page_title=APP_TITLE,
    layout="centered",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    :root {
        color-scheme: dark;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #080808 !important;
        color: #f5f5f5 !important;
    }

    [data-testid="stHeader"] {
        background: rgba(8, 8, 8, 0.92) !important;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 950px;
        padding-top: 2.1rem;
        padding-bottom: 3.5rem;
    }

    .hero {
        background: linear-gradient(145deg, #090909 0%, #151515 100%);
        color: #ffffff;
        border: 1px solid #3a3012;
        border-top: 4px solid #d4af37;
        border-radius: 18px;
        padding: 1.55rem 1.65rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 32px rgba(0, 0, 0, .32);
    }

    .hero-kicker {
        color: #e6c85c;
        font-weight: 800;
        letter-spacing: .10em;
        text-transform: uppercase;
        font-size: .78rem;
        margin-bottom: .45rem;
    }

    .hero-title {
        color: #ffffff;
        font-size: 1.95rem;
        font-weight: 850;
        line-height: 1.12;
        margin: 0;
    }

    .hero-subtitle {
        margin-top: .65rem;
        color: #cfcfcf;
        font-size: .98rem;
        line-height: 1.45;
    }

    .search-heading {
        color: #f2d36b;
        font-size: 1rem;
        font-weight: 800;
        margin: .2rem 0 .35rem 0;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label {
        color: #f2d36b !important;
        font-weight: 750 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: #111111 !important;
        border-color: #4b401b !important;
        color: #ffffff !important;
    }

    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within {
        border-color: #d4af37 !important;
        box-shadow: 0 0 0 1px #d4af37 !important;
    }

    .student-card {
        background: #101010;
        border: 1px solid #2b2b2b;
        border-radius: 16px;
        padding: 1.2rem 1.25rem;
        margin: 1.15rem 0 1rem 0;
        box-shadow: 0 8px 24px rgba(0,0,0,.24);
    }

    .student-name {
        font-size: 1.58rem;
        font-weight: 850;
        color: #ffffff;
        margin-bottom: .55rem;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .75rem;
        margin-top: .9rem;
    }

    .summary-item {
        background: #171717;
        border: 1px solid #292929;
        border-radius: 12px;
        padding: .8rem .9rem;
        min-height: 78px;
    }

    .summary-item.lunch-highlight {
        border: 1px solid #8f7621;
        background: linear-gradient(145deg, #17150d 0%, #1d190b 100%);
    }

    .summary-label {
        color: #a7a7a7;
        font-size: .75rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: .06em;
        margin-bottom: .26rem;
    }

    .summary-item.lunch-highlight .summary-label,
    .summary-item.lunch-highlight .summary-value {
        color: #f2d36b;
    }

    .summary-value {
        color: #ffffff;
        font-weight: 760;
        font-size: .98rem;
        line-height: 1.3;
    }

    .rotation-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .65rem;
        margin: .65rem 0 1rem 0;
    }

    .rotation-card {
        background: #111111;
        border: 1px solid #2d2d2d;
        border-bottom: 3px solid #8e751f;
        border-radius: 12px;
        padding: .75rem .85rem;
    }

    .rotation-label {
        color: #a7a7a7;
        text-transform: uppercase;
        letter-spacing: .05em;
        font-size: .72rem;
        font-weight: 800;
        margin-bottom: .24rem;
    }

    .rotation-value {
        color: #ffffff;
        font-weight: 760;
        line-height: 1.25;
    }

    .schedule-row {
        display: grid;
        grid-template-columns: 130px 1.2fr 1fr;
        gap: 1rem;
        background: #101010;
        border: 1px solid #292929;
        border-left: 5px solid #d4af37;
        border-radius: 13px;
        padding: .92rem 1rem;
        margin: .56rem 0;
        box-shadow: 0 4px 14px rgba(0,0,0,.15);
    }

    .schedule-time {
        font-weight: 850;
        color: #f2d36b;
    }

    .schedule-activity {
        font-weight: 760;
        color: #ffffff;
    }

    .schedule-location {
        color: #d7d7d7;
        font-weight: 650;
    }

    .schedule-detail {
        grid-column: 2 / 4;
        color: #a9a9a9;
        font-size: .9rem;
        margin-top: -.42rem;
        line-height: 1.35;
    }

    .section-title {
        font-size: 1.28rem;
        font-weight: 850;
        margin: 1.25rem 0 .4rem 0;
        color: #f2d36b;
    }

    .small-note {
        color: #a9a9a9;
        font-size: .88rem;
        margin-top: .65rem;
        line-height: 1.4;
    }

    .pill {
        display: inline-block;
        background: #241f0d;
        color: #f2d36b;
        border: 1px solid #64551d;
        border-radius: 999px;
        padding: .3rem .65rem;
        font-size: .8rem;
        font-weight: 800;
        margin-right: .35rem;
    }

    div[data-testid="stAlert"] {
        background: #151515 !important;
        color: #f5f5f5 !important;
        border-color: #4a401c !important;
    }

    @media (max-width: 700px) {
        .summary-grid,
        .rotation-grid {
            grid-template-columns: 1fr;
        }
        .schedule-row {
            grid-template-columns: 1fr;
            gap: .28rem;
        }
        .schedule-detail {
            grid-column: 1;
            margin-top: .18rem;
        }
        .hero-title {
            font-size: 1.55rem;
        }
        .block-container {
            padding-top: 1.25rem;
        }
    }
</style>
"""

st.html(CUSTOM_CSS)


@st.cache_data
def load_data() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("’", "'")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def ordinal_grade(grade: int) -> str:
    suffix = "th"
    if grade % 100 not in (11, 12, 13):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(grade % 10, "th")
    return f"{grade}{suffix} Grade"


def room_location(assignment: dict | None) -> str:
    if not assignment:
        return "See staff"
    teacher = str(assignment.get("teacher") or "").strip()
    room = str(assignment.get("room") or "").strip()
    if teacher and room:
        return f"{teacher} — Room {room}"
    if teacher:
        return teacher
    if room:
        return f"Room {room}"
    return "See staff"


def rotation(student: dict, index: int) -> dict:
    rotations = student.get("rotations") or []
    if 0 <= index < len(rotations):
        return rotations[index]
    return {}


def lunch_code(student: dict) -> str:
    raw = str(student.get("lunch") or "").strip().upper()
    if raw in {"A", "B", "C", "D"}:
        return raw

    grade = int(student["grade"])
    if grade in (6, 7):
        return "A"
    if grade in (8, 9):
        return "B"
    return ""


def lunch_time(code: str) -> str:
    return {
        "A": "11:25–11:55",
        "B": "11:55–12:25",
        "C": "12:40–1:10",
        "D": "1:10–1:40",
    }.get(code, "See staff")


def lunch_text(student: dict) -> str:
    code = lunch_code(student)
    if not code:
        return "See roster / staff"
    return f"{code} Lunch — {lunch_time(code)}"


def starting_location(student: dict) -> str:
    grade = int(student["grade"])
    if grade == 12:
        return room_location({"teacher": student.get("home_teacher"), "room": student.get("home_room")})
    return room_location(rotation(student, 0))


def stable_room(student: dict) -> str:
    grade = int(student["grade"])
    if grade == 12:
        return room_location({"teacher": student.get("home_teacher"), "room": student.get("home_room")})
    if grade in (9, 10, 11):
        return room_location(rotation(student, 2))
    return "Rotates each block"


def schedule_item(time: str, activity: str, location: str, detail: str = "") -> dict:
    return {"time": time, "activity": activity, "location": location, "detail": detail}


def build_schedule(student: dict) -> tuple[list[dict], list[str]]:
    grade = int(student["grade"])
    lunch = lunch_code(student)
    notes: list[str] = []

    if grade == 12:
        home = room_location({"teacher": student.get("home_teacher"), "room": student.get("home_room")})
        cert_activity = "ACT CERT"
        cert_detail = "Stay with your assigned teacher/group."
        if student.get("special_cert"):
            cert_activity = "See staff for your morning plan"
            cert_detail = (
                "Your roster entry is marked. The day instructions say marked students with a 36 do not complete CERT "
                "but should attend the thesis/class meeting later in the day."
            )
            notes.append("Because your roster name is marked, check with staff about your morning assignment before CERT begins.")

        items = [
            schedule_item("8:00–8:05", "Announcements", home),
            schedule_item("8:05–8:35", "ACT pre-administration", home, "If this runs past 8:35, finish it before moving on."),
            schedule_item("8:35–8:40", "Stretch / bathroom break", "Annex", "Stay in the annex."),
            schedule_item("8:45–12:30", cert_activity, home, cert_detail),
        ]

        if lunch == "C":
            items += [
                schedule_item("12:40–1:10", "C Lunch", "Lunch area"),
                schedule_item("1:10–1:40", "Directed Studies", home, "App video is shown during directed studies."),
            ]
        elif lunch == "D":
            items += [
                schedule_item("12:40–1:10", "Directed Studies", home, "App video is shown during directed studies."),
                schedule_item("1:10–1:40", "D Lunch", "Lunch area"),
            ]
        else:
            items.append(schedule_item("12:40–1:40", "Lunch / Directed Studies", home, "Check your roster lunch assignment with staff."))

        items.append(schedule_item("1:45–3:00", "Thesis Chapter 2, class meeting, and updates", "Auditorium"))
        return items, notes

    if grade == 11:
        r1, r2, r3 = rotation(student, 0), rotation(student, 1), rotation(student, 2)
        items = [
            schedule_item("8:00–8:05", "Announcements", room_location(r1)),
            schedule_item("8:05–9:20", "Rotation 1 — Bluebook setup / PSAT pre-registration", room_location(r1)),
            schedule_item("9:25–10:40", "Rotation 2 — ELA", room_location(r2)),
            schedule_item("10:45–12:00", "Rotation 3 — Math", room_location(r3), "Stay with this rotation for the rest of the day."),
            schedule_item("12:00–12:40", "Junior class meeting / rigor updates", "Auditorium"),
        ]

        if lunch == "C":
            items += [
                schedule_item("12:40–1:10", "C Lunch", "Lunch area"),
                schedule_item("1:10–1:40", "Return to Rotation 3 group", room_location(r3)),
            ]
        elif lunch == "D":
            items += [
                schedule_item("12:40–1:10", "Stay with Rotation 3 group", room_location(r3)),
                schedule_item("1:10–1:40", "D Lunch", "Lunch area"),
            ]
        else:
            items.append(schedule_item("12:40–1:40", "Lunch / Rotation 3", room_location(r3), "Check your roster lunch assignment with staff."))

        items.append(schedule_item("1:45–3:00", "App video, Khan Academy setup, directed studies, and practice", room_location(r3)))
        return items, notes

    if grade == 10:
        r1, r2, r3 = rotation(student, 0), rotation(student, 1), rotation(student, 2)
        items = [
            schedule_item("8:00–8:05", "Announcements", room_location(r1)),
            schedule_item("8:05–9:20", "Rotation 1 — Math", room_location(r1)),
            schedule_item("9:25–10:40", "Rotation 2 — Bluebook setup / PSAT pre-registration", room_location(r2)),
            schedule_item("10:45–12:00", "Rotation 3 — ELA", room_location(r3), "Stay with this rotation for the rest of the day."),
            schedule_item("12:00–12:40", "App video", room_location(r3)),
        ]

        if lunch == "C":
            items += [
                schedule_item("12:40–1:10", "C Lunch", "Lunch area"),
                schedule_item("1:10–1:40", "Return to Rotation 3 group", room_location(r3)),
            ]
        elif lunch == "D":
            items += [
                schedule_item("12:40–1:10", "Stay with Rotation 3 group", room_location(r3)),
                schedule_item("1:10–1:40", "D Lunch", "Lunch area"),
            ]
        else:
            items.append(schedule_item("12:40–1:40", "Lunch / Rotation 3", room_location(r3), "Check your roster lunch assignment with staff."))

        items += [
            schedule_item("1:45–2:15", "Khan Academy setup and practice", room_location(r3)),
            schedule_item("2:20–2:25", "Go to the gym", "Gym"),
            schedule_item("2:25–2:45", "Class meeting — rigor updates and questions", "Gym"),
            schedule_item("2:50–3:00", "Return to class", room_location(r3)),
        ]
        return items, notes

    if grade == 9:
        r1, r2, r3 = rotation(student, 0), rotation(student, 1), rotation(student, 2)
        lunch_label = f"{lunch} Lunch" if lunch else "Lunch"
        lunch_when = lunch_time(lunch) if lunch else "11:55–12:25"
        items = [
            schedule_item("8:00–8:05", "Announcements", room_location(r1)),
            schedule_item("8:05–9:20", "Rotation 1 — ELA", room_location(r1)),
            schedule_item("9:25–10:40", "Rotation 2 — Math", room_location(r2)),
            schedule_item("10:45–11:55", "Rotation 3 — Bluebook setup / PSAT pre-registration", room_location(r3), "Stay with this group for the rest of the day."),
            schedule_item(lunch_when, lunch_label, "Lunch area"),
            schedule_item("12:25–1:25", "App video", room_location(r3)),
            schedule_item("1:30–1:35", "Go to the gym", "Gym"),
            schedule_item("1:40–2:00", "Class meeting — rigor updates and questions", "Gym"),
            schedule_item("2:05–2:10", "Return to class", room_location(r3)),
            schedule_item("2:10–3:00", "Khan Academy setup and practice", room_location(r3)),
        ]
        return items, notes

    if grade in (6, 7, 8):
        rotations = student.get("rotations") or []
        block_times = [
            "8:00–8:50",
            "8:55–9:40",
            "9:45–10:30",
            "10:35–11:20",
            "12:30–1:15",
            "1:20–2:05",
        ]
        items = []
        for i, time in enumerate(block_times[:4]):
            items.append(schedule_item(time, f"Block {i + 1}", room_location(rotations[i] if i < len(rotations) else {})))

        block4_location = room_location(rotations[3] if len(rotations) > 3 else {})
        items.append(
            schedule_item(
                "11:20–12:25",
                "Lunch / app video",
                block4_location,
                f"Stay with your Block 4 rotation. Your lunch is {lunch_text(student)}; when you are not at lunch, follow the class activity.",
            )
        )

        for i, time in enumerate(block_times[4:], start=4):
            items.append(schedule_item(time, f"Block {i + 1}", room_location(rotations[i] if i < len(rotations) else {})))

        field = {6: "annex field", 7: "small soccer field", 8: "large soccer field"}[grade]
        notes.append(f"If weather permits, middle-school movement time is on the {field}.")
        return items, notes

    return [], notes


def result_label(student: dict) -> str:
    return f"{student['display_name']} — {ordinal_grade(int(student['grade']))}"


def render_rotations(student: dict) -> None:
    grade = int(student["grade"])
    if grade not in (9, 10, 11):
        return

    cards = []
    for i in range(3):
        assignment = rotation(student, i)
        cards.append(
            f"""
            <div class="rotation-card">
                <div class="rotation-label">Rotation {i + 1}</div>
                <div class="rotation-value">{html.escape(room_location(assignment))}</div>
            </div>
            """
        )

    st.html('<div class="section-title">Your rotation rooms</div>')
    st.html(f'<div class="rotation-grid">{"".join(cards)}</div>')


def render_student(student: dict) -> None:
    grade = int(student["grade"])
    group_html = ""
    if grade <= 8:
        group_html = f'<span class="pill">Group {html.escape(str(student.get("group", "")))}</span>'

    st.html(
        f"""
        <div class="student-card">
            <div class="student-name">{html.escape(student['display_name'])}</div>
            <span class="pill">{html.escape(ordinal_grade(grade))}</span>
            {group_html}
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-label">Start Here</div>
                    <div class="summary-value">{html.escape(starting_location(student))}</div>
                </div>
                <div class="summary-item lunch-highlight">
                    <div class="summary-label">Your Lunch</div>
                    <div class="summary-value">{html.escape(lunch_text(student))}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Later-Day Base</div>
                    <div class="summary-value">{html.escape(stable_room(student))}</div>
                </div>
            </div>
        </div>
        """
    )

    render_rotations(student)

    schedule, notes = build_schedule(student)
    st.html('<div class="section-title">Your schedule</div>')
    for item in schedule:
        detail = ""
        if item.get("detail"):
            detail = f'<div class="schedule-detail">{html.escape(item["detail"])}</div>'
        st.html(
            f"""
            <div class="schedule-row">
                <div class="schedule-time">{html.escape(item['time'])}</div>
                <div class="schedule-activity">{html.escape(item['activity'])}</div>
                <div class="schedule-location">{html.escape(item['location'])}</div>
                {detail}
            </div>
            """
        )

    for note in notes:
        st.info(note)


def optional_access_gate() -> None:
    try:
        required_code = str(st.secrets.get("ACCESS_CODE", "")).strip()
    except Exception:
        required_code = ""

    if not required_code:
        return
    if st.session_state.get("authorized"):
        return

    st.markdown("### Enter the school access code")
    entered = st.text_input("Access code", type="password", label_visibility="collapsed")
    if st.button("Continue", use_container_width=True):
        if entered == required_code:
            st.session_state["authorized"] = True
            st.rerun()
        else:
            st.error("That access code is not correct.")
    st.stop()


def main() -> None:
    data = load_data()
    students = data["students"]
    event = data.get("event", {})

    st.html(
        f"""
        <div class="hero">
            <div class="hero-kicker">{html.escape(event.get('date', 'September 28, 2026'))}</div>
            <div class="hero-title">{html.escape(APP_TITLE)}</div>
            <div class="hero-subtitle">Start typing your name below. Matching names will filter as you type. Select your name to see your teacher, room number, lunch, and full schedule for the day.</div>
        </div>
        """
    )

    optional_access_gate()

    lookup = {student["id"]: student for student in students}
    sorted_ids = sorted(
        lookup,
        key=lambda sid: (normalize_text(lookup[sid]["display_name"]), int(lookup[sid]["grade"])),
    )

    st.html('<div class="search-heading">Search for your name</div>')
    selected_id = st.selectbox(
        "Student name",
        options=sorted_ids,
        index=None,
        format_func=lambda sid: result_label(lookup[sid]),
        placeholder="Start typing your first or last name…",
        label_visibility="collapsed",
        key="student_lookup",
    )
    st.html('<div class="small-note">Click the box and type. The list will immediately narrow to matching names.</div>')

    if selected_id is None:
        return

    render_student(lookup[selected_id])
    st.html(
        '<div class="small-note">Schedule data is loaded specifically for Review Day on September 28, 2026. If a staff member gives you a different direction, follow the staff direction.</div>'
    )


if __name__ == "__main__":
    main()
