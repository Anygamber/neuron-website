# PROJECT ARCHITECTURE & AGENT HANDOFF: NeurON Clinic Website

> **CONFIDENTIAL & INTERNAL HANDOFF DOCUMENT**  
> *Audited from live workspace (not the draft template myths).*  
> *Target: migrate + continue on new workstation `C:\Users\anyga\Projects\presentation\Website neuron`.*  
> *Purpose: full context restore for Cursor / Claude / GPT agents.*

**Audit date:** 2026-04-09 (source machine: `C:\Users\user\Projects\presentation\Website neuron`)  
**Git:** none (no `.git` — copy the whole folder; do not assume remotes)  
**Production site:** https://neuronmedical.uz/

---

## 1. EXECUTIVE SUMMARY & TECH STACK

| Layer | Reality (correct this if older notes say otherwise) |
|--------|------------------------------------------------------|
| **Project** | NeurON Medical Centre — clinic marketing site + booking/callback + live chat → Telegram |
| **Frontend** | Mostly **single-file** `index.html` (~220KB): custom CSS (cyberpunk / neon cyan), vanilla JS, **no Tailwind build**. GSAP 3.12.2 + ScrollTrigger via **cdnjs**. Lucide icons CDN. |
| **i18n** | Client-side `i18n.js` (`window.NeuronI18n`) + extras `i18n-pages.js` / `i18n-prices.js` → `window.NEURON_I18N_EXTRA`. Languages: **`uz` (default)** and `ru`. Storage key `localStorage.neuron_lang`; also `?lang=`. |
| **Backend** | Python FastAPI **0.115.x**, SQLAlchemy 2 + **SQLite** (`server/data/neuron.db`). Factory: `server/app/factory.py` → `create_app()`. |
| **Hosting** | cPanel **Phusion Passenger** → `passenger_wsgi.py` wraps ASGI with **a2wsgi**. Local: `uvicorn` via `server/main.py` (`app` object). |
| **Bot** | Separate package `bot/` — aiogram Telegram bot `@uzneuron_bot` (booking / staff / chat). Own `bot/.env`. |
| **Analytics** | Secret unlisted dashboard path + token query param (see §6). Hits: `POST /api/v1/analytics/hit`. |
| **GSAP skills** | Mirrored under `.cursor/skills/gsap-*` and `.agents/skills/gsap-*` (official gsap-skills set). `package.json` only pins `gsap` for local reference; **runtime uses CDN**. |
| **CRM folder** | `crm/` exists but is **empty** — ignore. |

**Do not trust older drafts that claim:** Tailwind-as-primary CSS, root `.env`, `assets/istockphoto-…` as doctor avatar, or `main.py` at project root as Passenger entry.

---

## 2. DIRECTORY STRUCTURE & FILE MAP

Target workspace after migration:

```text
Website neuron/
├── passenger_wsgi.py          # cPanel WSGI entry (ASGI→WSGI via a2wsgi)
├── requirements.txt           # Passenger/root deps (mirrors server pins)
├── index.html                 # Main site UI + preloader + services + doctors + forms
├── i18n.js                    # Core RU/UZ dictionary + NeuronI18n API
├── i18n-pages.js              # Extra page strings → NEURON_I18N_EXTRA
├── i18n-prices.js             # Price-list i18n extras
├── price-data.js / .json      # Price catalogue data
├── NeurON (guidebook).html    # Secondary static page
├── images/
│   ├── clinic/                # Clinic photos
│   ├── doctors/
│   │   └── placeholder.jpg    # Unified doctor avatar (ALL cards)
│   └── patterns/              # Background patterns
├── NeurON.png / NeurON-light.png / NeurON-icon-circle.png  # Brand assets
├── package.json               # gsap npm pin (optional; site uses CDN)
├── .cursor/skills/gsap-*/     # Agent GSAP skills (use these for animation work)
├── .agents/skills/gsap-*/     # Duplicate skill set
├── server/
│   ├── .env                   # SECRETS — copy manually; never commit
│   ├── .env.example           # Template for new machine
│   ├── requirements.txt
│   ├── main.py                # ASGI `app = create_app()` for uvicorn / panels
│   ├── data/neuron.db         # SQLite (auto-created)
│   └── app/
│       ├── factory.py         # Routes + StaticFiles mount of PROJECT_ROOT
│       ├── config.py          # load_env, get_config, pathlib roots
│       ├── database.py        # Engine / SessionLocal / init_db
│       ├── telegram.py        # Send booking/callback messages
│       ├── models/            # analytics, chat, staff
│       ├── schemas*.py
│       └── services_*.py
└── bot/                       # Telegram bot (aiogram) — separate process
    ├── main.py
    ├── .env / .env.example
    └── handlers/ services/ …
```

**Path resolution (already portable):**  
`server/app/config.py` sets `SERVER_DIR = Path(__file__).resolve().parents[1]`, `PROJECT_ROOT = SERVER_DIR.parent`, `ENV_PATH = SERVER_DIR / ".env"`, `DATA_DIR = SERVER_DIR / "data"`.  
**Forbidden:** hardcoding `C:\Users\user\...` or `C:\Users\anyga\...` in app code.

---

## 3. CORE ARCHITECTURAL MODULES & STATE

### A. Frontend & GSAP

- **Preloader** (`#site-preloader` in `index.html`): cyberpunk sequence — brain logo → glitch → white typography curtain (“NeurON”) → curtain retract → brain flies into header logo. Numeric stats strip was **removed**.
- Timing: `SLOW = 1.3` (≈30% slower), plus `HOLD_EXTRA`; comment in code: “30% slower + ~2s longer overall feel”. Helper `dur(t) => t * SLOW`.
- GPU: `force3D: true`, `will-change`, `pinGpu()` / `translate3d`-style promotion to avoid sub-pixel shimmer.
- **Every full page load** shows the intro (session skip was removed by product decision).
- CSS hides preloader until GSAP owns it (avoids FOUC / flash).
- **Scroll:** GSAP ScrollTrigger fades / reveals on sections; hero logo float animation.
- **Design:** dark cyberpunk, cyan accents (`--paradiso` etc.), clinic photo + pattern backgrounds — **custom CSS in `<style>`, not Tailwind**.

### B. Multi-Language (RU / UZ Latin)

- Default language: **`uz`**.
- Engine: `NeuronI18n` applies `[data-i18n="…"]` keys from `DICT.ru` / `DICT.uz`, then merges `NEURON_I18N_EXTRA` from page/price scripts (`mergeExtra()`).
- **Doctor names must live in `i18n.js` DICT** (and may also appear in extras). Keys-only-in-`i18n-pages.js` previously failed to switch — keep names in core DICT.

| i18n key | RU | UZ (Latin) |
|----------|----|------------|
| `doc.burnashev.name` | Бурнашев Марсель Ильдарович | Burnashev Marsel Ildaovich |
| `doc.kim.name` | Ким Андрей Афонасьевич | Kim Andrey Afonasevich |
| `doc.alimov.name` | Алимов Ижод Рустамович | Alimov Ijod Rustamovich |
| `doc.hamrokulov.name` | Хамрокулов Бекзод Баходирович | Xamrokulov Bekzod Baxodirovich |
| `doc.allarov.name` | Аллаяров Улугбек Джураевич | Allayarov Ulugbek Juraevich |
| `doc.abdujapparov.name` | Абдужаппаров Сулаймон Бахриддинович | Abdujapparov Salaymon Baxriddinovich |
| `doc.muslimov.name` | Муслимов Улугбек Якубджанович | Muslimov Ulugbek Yakubjanovich |

Avatar for all: `images/doctors/placeholder.jpg` (root also has `istockphoto-1225961106-612x612.jpg` as source stock — **not** wired in HTML).

### C. Medical services (on main page)

1. **Female check-up** — `svc.checkF.*` — **2 600 000** UZS / so‘m  
2. **Male check-up** — `svc.checkM.*` — **2 900 000** UZS / so‘m  
3. **Pain Center** — `svc.pain.*` — RU «Центр боли» / UZ «Og‘riq markazi …»; COSMAN G4, blocks/RFA; full RU+UZ copy in `i18n.js`

Price list data: `price-data.js` + `i18n-prices.js` (dark price UI was a prior UX pass).

### D. Backend API surface (`server/app/factory.py`)

| Method | Path | Role |
|--------|------|------|
| POST | `/api/request-callback` | Callback request → Telegram |
| POST | `/api/submit-booking` | Booking → Telegram |
| POST | `/api/v1/analytics/hit` | Visit beacon from frontend |
| GET | `/api/v1/analytics/stats` | Stats (token-gated) |
| GET | `/analytics-x7k9m2p4q8w1n5v3` | Secret HTML dashboard |
| GET | `/health` | Healthcheck |
| POST/GET | `/api/v1/staff/*` | Staff register/list (bearer) |
| POST/GET | `/api/v1/chat/*` | Site chat ↔ managers |

Static: FastAPI serves `/` with OG injection (`lang` query, default **uz**), then mounts `StaticFiles(PROJECT_ROOT, html=True)`.

### E. Telegram bot (`bot/`)

- Run alongside API: `cd bot && python main.py` (expects API on `:8000` per comments).
- Handlers: booking, chat, staff registration.
- Config via `bot/.env` (separate from `server/.env`).

---

## 4. ENVIRONMENT & PATH STANDARDS (MIGRATION)

### Secrets to copy (do not invent; copy from old machine)

1. `server/.env` → same path on new laptop (see `server/.env.example`).
2. `bot/.env` → same.
3. Optional: `server/data/neuron.db` if you need existing analytics/chat history.

Key vars (`server/.env.example`):

- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `API_BEARER_TOKEN`
- `ANALYTICS_SECRET_TOKEN` → dashboard: `/analytics-x7k9m2p4q8w1n5v3/?t=TOKEN`
- `HOST` / `PORT` (default `127.0.0.1:8000`)
- `DATABASE_URL` optional; default `sqlite:///…/server/data/neuron.db`
- Clinic identity: `CLINIC_*`

### Setup on `anyga` machine

```powershell
cd "C:\Users\anyga\Projects\presentation\Website neuron"
python -m venv server\.venv
.\server\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r bot\requirements.txt
# ensure server\.env and bot\.env exist (copied)
cd server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Passenger (production): Application root = **project root** (where `passenger_wsgi.py` lives); startup file = `passenger_wsgi.py` (not an absolute path).

### User-global Cursor paths (update after migrate)

Old profile `C:\Users\user\…` → new `C:\Users\anyga\…`:

- Completion sound: `C:\Users\anyga\Downloads\cdb314abdd20b72.mp3` (or keep Downloads path if file moved)
- Notify script: `C:\Users\anyga\Desktop\Custom\notify_done.py`
- Global rules under `C:\Users\anyga\.cursor\rules\`

Project-local GSAP skills under `.cursor/skills/` travel with the folder — no path rewrite needed.

---

## 5. KNOWN PITFALLS (DO NOT REINTRODUCE)

1. **Circular import:** `server/main.py` must import `create_app` from `app.factory`, **not** `app.main`.
2. **Passenger:** needs `a2wsgi`; `sys.path` must put `server/` first so `import app` = `server/app`.
3. **Empty env from hosting panel:** `config.load_env` force-overwrites critical keys from file when panel injects empty `TELEGRAM_*`.
4. **Doctor names:** keep in `i18n.js` DICT for both langs.
5. **No Tailwind toolchain** — edit CSS in `index.html` (or extracted sheets if you split later).
6. **No git** today — initialize only if the user asks.
7. Preloader: respect `prefers-reduced-motion`; keep GPU pinning on transform paths.

---

## 6. SECRET ANALYTICS

- Path constant: `ANALYTICS_DASHBOARD_PATH = "/analytics-x7k9m2p4q8w1n5v3"`
- Auth: query `?t=` must match `ANALYTICS_SECRET_TOKEN`
- Table: `page_visits` (`server/app/models/analytics.py`)
- Frontend beacon near end of `index.html` → `POST /api/v1/analytics/hit`

Treat path + token as semi-secret (obscurity + token).

---

## 7. PROMPT FOR NEW AI AGENT / WORKSTATION INITIALIZATION

Copy-paste into the first Cursor chat on the new laptop:

```text
[SYSTEM CONTEXT RESTORATION & AGENT HANDOFF]
You are Lead Full-Stack & Animation Architect for the NeurON clinic site.
Read neuron_architecture_handoff.md in the workspace root first. Prefer that file over any older Tailwind/assets myths.

Stack (actual):
- Frontend: index.html + custom CSS + vanilla JS + GSAP/ScrollTrigger CDN + Lucide; i18n via i18n.js + NEURON_I18N_EXTRA (i18n-pages.js, i18n-prices.js). Default lang uz.
- Backend: FastAPI create_app in server/app/factory.py; SQLite; passenger_wsgi.py + a2wsgi on cPanel; server/main.py for uvicorn.
- Bot: bot/ (aiogram), separate .env.
- GSAP skills: .cursor/skills/gsap-* (and .agents/skills/gsap-*).

Current product state:
1. PRELOADER: cyberpunk brain → white text curtain → fly to header; SLOW=1.3 (~30% slower); force3D/will-change; no numeric counters; runs every load.
2. SERVICES: Female check-up 2.6M UZS, Male 2.9M UZS, Pain Center (Центр боли / Og'riq markazi) fully RU+UZ in i18n.js.
3. DOCTORS: 7 cards, bilingual names via data-i18n doc.*.name; avatar images/doctors/placeholder.jpg.
4. PATHS: pathlib from __file__; secrets only in server/.env and bot/.env. Machine user is anyga — never hardcode old C:\Users\user paths.
5. No git repo unless user requests init.

Acknowledge, verify server/.env exists and uvicorn health, then await instructions (features / SEO / SMM / deploy).
```

---

## 8. QUICK VERIFY CHECKLIST (new agent)

- [ ] Workspace root contains `index.html`, `passenger_wsgi.py`, `server/app/factory.py`, `neuron_architecture_handoff.md`
- [ ] `server/.env` present; `GET http://127.0.0.1:8000/health` OK
- [ ] Lang toggle switches doctor names and Pain Center / check-up copy
- [ ] Preloader plays without white flash; brain lands on header logo
- [ ] `.cursor/skills/gsap-core/SKILL.md` readable
- [ ] Notify sound path updated for `anyga` if using global completion hooks

---

*End of handoff. Source of truth = this file + the repository tree; discard conflicting draft trees that put Tailwind/`assets/`/root `.env` at the center.*
