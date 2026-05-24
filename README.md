# SmartSeat AI Pro 🎓🤖

SmartSeat AI Pro is an automated, enterprise-grade seating arrangement and allocation platform designed for colleges and universities. The application streamlines exam logistics by mapping college infrastructure, scheduling exam matrices, and optimizing student distributions using advanced interleaving (mixing) rules and gap-seating algorithms.

The system features an autonomous **Admin Control Center** for batch seat generation and data updates, alongside a fast, intuitive **Student Portal** where examinees can instantly find their classrooms and exact seats via registration lookup or QR codes.

---

## 🚀 Key Features

### 🛡️ Admin Portal
- **Robust Database Management (UPSERT Mode):** Direct Excel synchronizations for infrastructure templates and student records. Uses structural upserting instead of table truncation to preserve existing institutional history.
- **Batch Seating Engine:** Runs seat allocations for a single target date or multi-day exam windows sequentially through an automated master loop.
- **Advanced Interleaving:** Mixes seats by variable criteria combinations (e.g., interleaving by `Stream + Semester`, or `Section + Year`) to minimize academic malpractice.
- **Gap Seating Control:** Optional toggle to mandate an empty buffer position between occupied seats automatically.
- **Master Plan Analytics & Excel-Style Filters:** Live searchable registry to filter master plans by Name, Registration ID, or Subject Code before exporting documents.
- **Dynamic Sticker Printing:** Generates multi-column grid PDF seating cards with embedded custom QR codes (`STU_ID:`) for door frames or desk placements.

### 🔍 Student Portal
- **Instant Seating Directory:** Lightweight lookup interface requiring only a unique Registration/Roll ID.
- **Responsive Schedule Timelines:** Displays chronological exam listings displaying verified parameters: `DATE`, `SUBJECT`, `HALL NAME`, and `SEAT LABEL`.

---

## 🛠️ System Architecture & Stack

- **Frontend & Dashboard UI:** Streamlit (Python-native reactive state handling)
- **Core Seating Processor:** Pandas (Vectorized multi-key sorting, matching, and row-wise physical allocation matrices)
- **Primary Database Engine:** PostgreSQL (Relational management with concurrent connection pooling)
- **Document Generator:** FPDF (High-performance coordinate-mapped PDF rendering)
- **Cryptographic Routing:** Qrcode API (Generates localized target strings mapped to individual data nodes)

---

## 📂 Project Structure

```text
SmartSeat_Pro/
│
├── app.py                  # Streamlit Multi-Page UI, Routing, & Filter Views
├── engine.py               # Core Allocation Algorithms & Batch Loop Callbacks
├── database_manager.py     # PostgreSQL Connection Pooling & UPSERT Database Layer
├── .gitignore              # Safeguard tracking definitions (Ignores venv/, caches, temp files)
└── README.md               # System Documentation
