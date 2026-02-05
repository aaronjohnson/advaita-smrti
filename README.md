# Day Shelter Kiosk

A secure, offline check-in kiosk system for day shelters and service centers.

**Status:** Pre-development (proposal phase)
**Client:** EMO Oregon HIV Day Center (via Express Employment)
**Consultant:** Aaron Johnson

---

## What This Is

This repository contains two things:

1. **A consulting engagement** — proposal documents, hardware specifications, and project planning for EMO Oregon's day center check-in system

2. **A repeatable template** — patterns, research, and documentation that can be adapted for similar nonprofit kiosk projects

The system being designed is a self-contained, offline kiosk for client check-in at a day shelter serving individuals who may be experiencing homelessness or living with HIV. It prioritizes data privacy (HIPAA-adjacent), local data residency (no cloud), and operational simplicity.

---

## The System

### Core Requirements

- **Offline-first**: No internet required for daily operation
- **Encrypted at rest**: SQLite + SQLCipher (AES-256)
- **On-premises data**: All client data stays on the physical device
- **Touch-optimized**: Self-service check-in for clients
- **Dual-screen**: Client-facing kiosk + staff-facing admin
- **HMIS-compatible**: CSV export matching HUD data standards (if needed)
- **Tamper-resistant**: Read-only root filesystem, automatic recovery

### Proposed Architecture

```
┌─────────────────┐       ┌──────────────────────┐
│  CLIENT SCREEN  │       │  STAFF SCREEN        │
│  7" touch       │       │  10-15" touch        │
│                 │       │                      │
│  Check in/out   │       │  Register clients    │
│  Select services│       │  Run reports         │
│                 │       │  Export to USB       │
└────────┬────────┘       └──────────┬───────────┘
         │                          │
         └──────────┬───────────────┘
                    │
           ┌────────┴────────┐
           │  Raspberry Pi   │
           │  or Commercial  │
           │  Linux Device   │
           │                 │
           │  Flask + SQLite │
           │  Cage Wayland   │
           └─────────────────┘
```

### Hardware Options Under Consideration

| Option | Hardware Cost | Durability |
|--------|---------------|------------|
| Elo I-Series (commercial all-in-one) | ~$1,200 | Commercial-grade |
| CM5 + Waveshare kiosk + Elo staff | ~$1,015 | Semi-industrial |
| CM5 + Waveshare + Volcora | ~$680 | Mixed |
| Pi 5 + KKSB + Volcora | ~$605 | Consumer-premium |

Development cost is $5,000 regardless of hardware path.

---

## Repository Contents

### Client-Facing Documents

| File | Description |
|------|-------------|
| `EMO_Oregon_Statement_of_Work-1.docx` | Original SOW (draft, Jan 2026) |
| `EMO_Oregon_Budget_Addendum-1.docx` | Budget breakdown |
| `EMO_Oregon_Hardware_and_Services_Quote.md` | Hardware quote v3 with deployment topology |
| `Recommended_System_A1.md` | Detailed BOM with purchase URLs and diagrams |
| `Daily_Data_Procedure.md` | Staff one-pager for daily operations |
| `Meeting_Notes_Hardware_Options.md` | Discussion document for hardware decisions |

### Internal Notes

| File | Description |
|------|-------------|
| `Notes_Secure_Storage_and_Boot_Architecture.md` | Two-database design, hardware-encrypted USB options |
| `Notes_Consulting_Engagement_Patterns.md` | Personal reflection on consulting boundaries |
| `links.txt` | Raw hardware links (initial research) |

---

## Learnings So Far

### On the Technical Side

1. **Offline kiosk architecture is well-solved.** Cage (Wayland compositor) + Chromium + Flask is a clean stack. The Pi ecosystem has mature kiosk tooling.

2. **The boot/encryption tradeoff is real.** Unattended boot vs. encrypted database requires either stored keys (less secure) or a two-tier database design (operational data auto-unlocks, sensitive data requires staff auth).

3. **Hardware-encrypted USB drives exist and are reasonably priced.** Apricorn Aegis, Kingston IronKey, iStorage datAshur — $65-75 for FIPS-certified, PIN-pad drives. This shifts encryption responsibility from software to hardware.

4. **HMIS compatibility is a CSV export problem, not an integration problem.** The HUD CSV spec is well-documented. Real-time API integration with regional HMIS vendors is out of scope and unnecessary.

5. **Data retention requirements overlap.** Oregon medical records (10 years) is the longest; satisfying it automatically covers HIPAA (6 years), HMIS (7 years), and federal grants (3 years).

### On the Consulting Side

1. **The blueprint is the deliverable, not the sales pitch.** Detailed specs, hardware research, architecture design — this is paid work, not proposal work.

2. **Paid discovery should be the entry point.** 2-4 hours of billable research before writing a detailed proposal filters tire-kickers and values the work appropriately.

3. **Time-box proposals.** Maximum 2 hours of free work. Beyond that, it's Phase 1 (paid).

4. **Intermediaries have their own incentives.** A staffing company referring work wants to close deals and look good. They won't protect consultant boundaries — that's the consultant's job.

5. **Structures protect against over-delivery.** Written scope, time limits, contracts before work. These aren't adversarial; they enable generosity within boundaries.

---

## Repeatable Template

This engagement is being documented as a template for similar projects:

**Target use cases:**
- Nonprofit service centers needing client check-in
- Day shelters, food banks, community health centers
- Organizations with data residency requirements (no cloud)
- HMIS-participating homeless service providers

**What's reusable:**
- Hardware research and BOM patterns
- Deployment topology options
- Data retention policy framework
- HMIS CSV export approach
- Boot/encryption architecture
- Staff procedure documentation style
- Proposal and quote document structure

**What's client-specific:**
- Exact data fields collected
- Services tracked at check-in
- Branding and UI customization
- Funding source requirements (HMIS, RSR, etc.)

If this project proceeds and the code is open-sourced (recommended), the software itself becomes the most reusable asset.

---

## Project Status

- [x] Initial proposal and SOW
- [x] Hardware research and options
- [x] Deployment topology design
- [x] Data retention and compliance research
- [x] Meeting preparation documents
- [ ] Client approval and contract signing
- [ ] Hardware procurement
- [ ] Phase 1: Discovery
- [ ] Phase 2: Development
- [ ] Phase 3: Testing and documentation
- [ ] Phase 4: Deployment and training

---

## License

Code (when written): MIT License (pending client approval of open source approach)

Documentation in this repo: Private consulting materials, not for distribution.

---

## Contact

Aaron Johnson
Independent Technical Consultant
Portland, Oregon
