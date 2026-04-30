"""
Genera CSVs con datos sinteticos coherentes para bulk ingestion.
~800 participantes, 120 equipos, 5 hackathones, 40 mentores.
"""
import csv
import random
from pathlib import Path
from faker import Faker
from datetime import date, timedelta

fake = Faker()
random.seed(42)
Faker.seed(42)

DATA_DIR = Path("/data")
DATA_DIR.mkdir(exist_ok=True)

N_HACKATHONS = 5
N_TRACKS_EACH = 4
N_PARTICIPANTS = 800
N_TEAMS = 120
N_MENTORS = 40
N_JUDGES = 20

SKILLS_POOL = [
    "Python", "React", "ML", "Blockchain", "iOS", "Android",
    "Go", "Rust", "Data Engineering", "UX Design", "DevOps",
    "NLP", "Computer Vision", "Finance", "HealthTech"
]

TRACK_NAMES = [
    "Artificial Intelligence", "Web3 & Blockchain", "Sustainability Tech",
    "HealthTech", "FinTech", "EdTech", "SpaceTech", "Cybersecurity"
]

STATUS_FLOW = ["Idea", "Approved", "In Development", "Delivered", "Evaluated"]


def pg_array(lst):
    items = ",".join(f'"{i}"' for i in lst)
    return "{" + items + "}"


hackathons = []
for i in range(1, N_HACKATHONS + 1):
    start = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2024, 6, 1))
    end = start + timedelta(days=random.randint(2, 5))
    hackathons.append({
        "id": i,
        "name": f"HackMX {fake.city()} {2020 + i}",
        "edition": random.randint(1, 5),
        "start_date": start,
        "end_date": end,
        "location": fake.city(),
        "max_team_size": random.choice([4, 5, 6]),
    })
with open(DATA_DIR / "hackathons.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=hackathons[0].keys())
    w.writeheader()
    w.writerows(hackathons)

tracks, track_id = [], 1
for h in hackathons:
    for name in random.sample(TRACK_NAMES, N_TRACKS_EACH):
        tracks.append({
            "id": track_id,
            "hackathon_id": h["id"],
            "name": name,
            "description": fake.sentence(nb_words=10),
        })
        track_id += 1
with open(DATA_DIR / "tracks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=tracks[0].keys())
    w.writeheader()
    w.writerows(tracks)

participants = []
for i in range(1, N_PARTICIPANTS + 1):
    h = random.choice(hackathons)
    participants.append({
        "id": i,
        "hackathon_id": h["id"],
        "full_name": fake.name(),
        "email": fake.unique.email(),
        "skills": pg_array(random.sample(SKILLS_POOL, random.randint(2, 5))),
        "university": fake.company() + " University",
        "country": fake.country(),
        "registered_at": fake.date_time_between(
            start_date=h["start_date"] - timedelta(days=30),
            end_date=h["start_date"],
        ),
    })
with open(DATA_DIR / "participants.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=participants[0].keys())
    w.writeheader()
    w.writerows(participants)

teams = []
for i in range(1, N_TEAMS + 1):
    h = random.choice(hackathons)
    t = random.choice([t for t in tracks if t["hackathon_id"] == h["id"]])
    teams.append({
        "id": i,
        "hackathon_id": h["id"],
        "track_id": t["id"],
        "name": f"Team {fake.unique.word().capitalize()} {i}",
    })
with open(DATA_DIR / "teams.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=teams[0].keys())
    w.writeheader()
    w.writerows(teams)

team_participant, seen = [], set()
for team in teams:
    h = next(h for h in hackathons if h["id"] == team["hackathon_id"])
    pool = [p for p in participants if p["hackathon_id"] == h["id"]]
    if not pool:
        continue
    size = random.randint(2, h["max_team_size"] - 1)
    for idx, p in enumerate(random.sample(pool, min(size, len(pool)))):
        key = (team["id"], p["id"])
        if key in seen:
            continue
        seen.add(key)
        team_participant.append({
            "team_id": team["id"],
            "participant_id": p["id"],
            "role": "Lead" if idx == 0 else "Member",
        })
with open(DATA_DIR / "team_participants.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=team_participant[0].keys())
    w.writeheader()
    w.writerows(team_participant)

mentors = []
for i in range(1, N_MENTORS + 1):
    mentors.append({
        "id": i,
        "full_name": fake.name(),
        "email": fake.unique.email(),
        "expertise": pg_array(random.sample(SKILLS_POOL, random.randint(1, 4))),
        "company": fake.company(),
        "max_teams": random.randint(2, 5),
    })
with open(DATA_DIR / "mentors.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=mentors[0].keys())
    w.writeheader()
    w.writerows(mentors)

team_mentor, seen_tm = [], set()
mentor_counts = {m["id"]: 0 for m in mentors}
for team in teams:
    for m in random.sample(mentors, random.randint(1, 2)):
        if mentor_counts[m["id"]] >= m["max_teams"]:
            continue
        key = (team["id"], m["id"])
        if key in seen_tm:
            continue
        seen_tm.add(key)
        team_mentor.append({"team_id": team["id"], "mentor_id": m["id"]})
        mentor_counts[m["id"]] += 1
with open(DATA_DIR / "team_mentors.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=team_mentor[0].keys())
    w.writeheader()
    w.writerows(team_mentor)

projects = []
for i, team in enumerate(teams, 1):
    status = random.choices(STATUS_FLOW, weights=[5, 10, 20, 40, 25], k=1)[0]
    projects.append({
        "id": i,
        "team_id": team["id"],
        "title": fake.catch_phrase(),
        "description": fake.paragraph(nb_sentences=3),
        "repo_url": f"https://github.com/{fake.user_name()}/{fake.slug()}",
        "current_status": status,
    })
with open(DATA_DIR / "projects.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=projects[0].keys())
    w.writeheader()
    w.writerows(projects)

status_history, hist_id = [], 1
for proj in projects:
    target_idx = STATUS_FLOW.index(proj["current_status"])
    current_dt = fake.date_time_between(start_date="-2y", end_date="-1y")
    for status in STATUS_FLOW[: target_idx + 1]:
        status_history.append({
            "id": hist_id,
            "project_id": proj["id"],
            "status": status,
            "changed_at": current_dt,
            "changed_by": "system",
            "notes": "",
        })
        hist_id += 1
        current_dt = fake.date_time_between(
            start_date=current_dt,
            end_date=current_dt + timedelta(days=random.randint(3, 21)),
        )
with open(DATA_DIR / "project_status_history.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=status_history[0].keys())
    w.writeheader()
    w.writerows(status_history)

judges = []
for i in range(1, N_JUDGES + 1):
    judges.append({
        "id": i,
        "full_name": fake.name(),
        "email": fake.unique.email(),
        "expertise": pg_array(random.sample(SKILLS_POOL, random.randint(1, 3))),
    })
with open(DATA_DIR / "judges.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=judges[0].keys())
    w.writeheader()
    w.writerows(judges)

evaluations, eval_id = [], 1
for proj in [p for p in projects if p["current_status"] in ("Delivered", "Evaluated")]:
    seen_eval = set()
    for j in random.sample(judges, random.randint(1, 3)):
        key = (proj["id"], j["id"])
        if key in seen_eval:
            continue
        seen_eval.add(key)
        evaluations.append({
            "id": eval_id,
            "project_id": proj["id"],
            "judge_id": j["id"],
            "score": round(random.uniform(50, 100), 2),
            "feedback": fake.sentence(nb_words=12),
        })
        eval_id += 1
with open(DATA_DIR / "evaluations.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=evaluations[0].keys())
    w.writeheader()
    w.writerows(evaluations)

print(
    f"Data generated: {len(hackathons)} hackathons | {len(tracks)} tracks | "
    f"{len(participants)} participants | {len(teams)} teams | "
    f"{len(projects)} projects | {len(evaluations)} evaluations | "
    f"{len(status_history)} history records"
)
