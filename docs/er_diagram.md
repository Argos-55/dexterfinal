```mermaid
erDiagram
    HACKATHON ||--o{ TRACK : "has"
    HACKATHON ||--o{ PARTICIPANT : "registers"
    HACKATHON ||--o{ TEAM : "hosts"
    TRACK ||--o{ TEAM : "categorizes"
    TEAM ||--o{ TEAM_PARTICIPANT : "has"
    PARTICIPANT ||--o{ TEAM_PARTICIPANT : "joins"
    TEAM ||--o{ TEAM_MENTOR : "assigned"
    MENTOR ||--o{ TEAM_MENTOR : "mentors"
    TEAM ||--|| PROJECT : "owns"
    PROJECT ||--o{ PROJECT_STATUS_HISTORY : "tracks"
    PROJECT ||--o{ EVALUATION : "receives"
    JUDGE ||--o{ EVALUATION : "submits"

    HACKATHON { int id PK; varchar name; date start_date; date end_date; int max_team_size }
    TRACK { int id PK; int hackathon_id FK; varchar name }
    PARTICIPANT { int id PK; int hackathon_id FK; varchar email; text[] skills }
    TEAM { int id PK; int hackathon_id FK; int track_id FK; varchar name }
    TEAM_PARTICIPANT { int team_id PK_FK; int participant_id PK_FK; varchar role }
    MENTOR { int id PK; varchar email; int max_teams }
    TEAM_MENTOR { int team_id PK_FK; int mentor_id PK_FK }
    PROJECT { int id PK; int team_id FK; project_status current_status }
    PROJECT_STATUS_HISTORY { int id PK; int project_id FK; project_status status; timestamptz changed_at }
    JUDGE { int id PK; varchar email }
    EVALUATION { int id PK; int project_id FK; int judge_id FK; numeric score }
```
