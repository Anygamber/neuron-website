# PROJECT ARCHITECTURE & AGENT HANDOFF: NeurON Clinic Website

> **CONFIDENTIAL & INTERNAL HANDOFF DOCUMENT**
> *Target System: FastAPI Backend, Passenger WSGI, Single-File/Modular Frontend (HTML/Tailwind/GSAP), SQLite/JSON Storage.*
> *Purpose: Seamless context restoration for AI coding agents (Cursor / Claude / GPT) on a new workstation environment.*

---

## 1. EXECUTIVE SUMMARY & TECH STACK
- **Project Name**: NeurON Medical Centre Website (`Website neuron`)
- **Core Objective**: High-end cyberpunk-inspired medical web portal with multi-language support (RU/UZ), dynamic preloaders, interactive medical services (Female/Male Check-ups, Pain Center / Og'riq markazi), and staff directory.
- **Backend Stack**: Python 3.x, FastAPI, Uvicorn (local development), Passenger WSGI (cPanel/Production deployment config).
- **Frontend Stack**: Native HTML5, Tailwind CSS, Vanilla JavaScript, **GSAP (GreenSock) + Official Cursor/Animation Skills integration**.
- **Data Layer**: SQLite / local JSON / static assets.

---

## 2. DIRECTORY STRUCTURE & FILE MAP
Ensure the workspace root (`C:\Users\anyga\Projects\presentation\Website neuron`) contains the following structural baseline:

```text
Website neuron/
├── .env                              # Global environment variables & secrets
├── requirements.txt                  # Python dependencies (FastAPI, uvicorn, etc.)
├── main.py (or app.py)               # FastAPI entry point / WSGI hook
├── index.html                        # Main frontend interface (Single-file architecture per page rules)
├── passenger_wsgi.py                 # cPanel deployment bridge
├── assets/                           # Images, fonts, icons
│   ├── istockphoto-1225961106-612x612.jpg  # Unified doctor placeholder avatar
│   └── logo/                         # Brain logo elements
├── server/                           # Backend routing, database, and logic
│   ├── .env                          # Server-specific tokens/configs
│   ├── database.py                   # SQLite connection and session management
│   └── models.py                     # Pydantic schemas & DB models
└── .cursor/                          # AI Agent behavioral rules & GSAP skills
    ├── skills/                       # Official gsap-skills repository data
    └── rules/                        # Custom project coding constraints
```

---

## 3. CORE ARCHITECTURAL MODULES & STATE

### A. Frontend & Animation Engine (GSAP)
- **Preloader**: 
  - Features a high-performance brain animation scaling into a white text rollout, smooth collapse, and transition into the header logo.
  - Optimized for a 2-second extended timeline, 30% slower smooth fluidity, with `will-change: transform`, `force3D: true`, and `translate3d(0,0,0)` to eliminate sub-pixel jitter/micro-stuttering.
- **Design Language**: Cyberpunk 2077 aesthetic (dark mode, neon cyan highlights, clean glassmorphism cards, scanline micro-effects).

### B. Multi-Language System (RU / UZ)
- **Localization Engine**: Dynamic client-side/server-side dictionary switching for Russian (`ru`) and Uzbek Latin (`uz`).
- **Doctors Directory (Bilingual Mapping)**:
  1. Бурнашев Марсель Ильдарович $\leftrightarrow$ `Burnashev Marsel Ildaovich`
  2. Ким Андрей Афонасьевич $\leftrightarrow$ `Kim Andrey Afonasevich`
  3. Алимов Ижод Рустамович $\leftrightarrow$ `Alimov Ijod Rustamovich`
  4. Хамрокулов Бекзод Баходирович $\leftrightarrow$ `Xamrokulov Bekzod Baxodirovich`
  5. Аллаяров Улугбек Джураевич $\leftrightarrow$ `Allayarov Ulugbek Juraevich`
  6. Абдужаппаров Сулаймон Бахриддинович $\leftrightarrow$ `Abdujapparov Salaymon Baxriddinovich`
  7. Муслимов Улугбек Якубджанович $\leftrightarrow$ `Muslimov Ulugbek Yakubjanovich`

### C. Core Medical Services Offerings
1. **Female Check-up**: *2,600,000 UZS* / *Ayollar uchun check-up "Salomatlik va go'zallik uyg'unligi"*
2. **Male Check-up**: *2,900,000 UZS* / *Erkaklar uchun check-up "Salomatlik va uzoq umr ko'rish kaliti"*
3. **Pain Center (Центр боли / Og'riq markazi)**:
   - Primary care for acute and chronic pain management (migraines, spinal disorders, joint pain, neuralgias, minimally invasive blocks). Fully localized in RU and UZ.

---

## 4. ENVIRONMENT & PATH STANDARDS (CRITICAL FOR MIGRATION)
- **Path Portability Rule**: Hardcoded absolute paths (e.g., `C:\Users\user\...`) are **forbidden**. All file access must utilize Python's `pathlib.Path(__file__).resolve().parent` or dynamic `Path.home()` lookups.
- **Dependencies Setup**:
  ```bash
  cd "C:\Users\anyga\Projects\presentation\Website neuron"
  pip install -r requirements.txt
  ```

---

## 5. PROMPT FOR NEW AI AGENT / WORKSTATION INITIALIZATION
Copy and paste the prompt block below into your new Cursor session to instantly brief the AI agent on the complete project context:

```text
[SYSTEM CONTEXT RESTORATION & AGENT HANDOFF]
You are operating as the Lead Full-Stack & Animation Architect for the "NeurON" clinic web application. 
Read the local project architecture document ("neuron_architecture_handoff.md") in the workspace root to understand our complete technology stack (FastAPI, SQLite, Passenger WSGI, Tailwind, and GSAP with official gsap-skills).

Current Project State & Constraints:
1. PRELOADER: Uses an optimized 2-second extended timeline, 30% slowed fluidity, hardware acceleration (will-change, force3D, translate3d) to eradicate sub-pixel stuttering. Numeric counters are removed; only the brain logo and typography remain.
2. SERVICES: Main services include Female Check-up (2.6M UZS), Male Check-up (2.9M UZS), and the newly integrated "Pain Center" (Og'riq markazi / Pain Management), fully localized for RU and UZ (Latin).
3. MEDICAL STAFF: 7 doctors mapped with bilingual names (RU / UZ Latin) using a unified placeholder asset ("assets/istockphoto-1225961106-612x612.jpg").
4. PATH SAFETY: All script/file references use relative paths or pathlib to ensure cross-machine compatibility between user profiles.

Acknowledge this context, verify environment integrity, and await further instructions for feature expansion, SEO implementation, or SMM management integration.
```