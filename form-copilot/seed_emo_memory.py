#!/usr/bin/env python3
"""
Seed the memory layer with notes from the Feb 19 2026 site visit
and meeting with Miss Cobine at the EMO Oregon Day Center.

Run once from the form-copilot directory:
    python3 seed_emo_memory.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for memory import
sys.path.insert(0, str(Path(__file__).parent))
from memory import Memory

MEMORY_PATH = ".memory"

def load_config():
    with open("questions_config.json") as f:
        return json.load(f)

def seed():
    config = load_config()
    mem = Memory(MEMORY_PATH, prefix="emo")

    # Build question lookup by ID
    questions = {q["id"]: q for q in config["questions"]}

    # --- Site visit observations and meeting notes ---
    # Organized by question ID with answers/context from the visit.

    notes = {
        # Q1: Typical day at the center
        "1": {
            "status": "in_progress",
            "answer": (
                "The center has a front entrance with a kiosk area and a back door with a clipboard. "
                "Clients sign in at the front entrance. Staff sit in a separate office room within the shelter. "
                "The current kiosk is turned off. There is a paper clipboard for sign-in at both entrances. "
                "Brochures about additional services and events are on the table near the kiosk. "
                "Miss Cobine wants the brochure information displayed on a screen mounted on the wall "
                "to free up table space."
            ),
            "context": "Need to confirm: hours of operation, who greets clients, peak times.",
        },

        # Q2: Current sign-in process
        "2": {
            "status": "in_progress",
            "answer": (
                "Current sign-in: paper clipboard at the front entrance. The existing kiosk hardware "
                "(has keyboard and mouse) is turned off and not in use. When the kiosk was active, "
                "clients identified themselves from a scrolling list of first name and last initial. "
                "This is the UX pattern to carry forward."
            ),
            "context": (
                "Key UX constraint: some clients cannot read or write. The system must support "
                "BOTH keyboard filtering (type letters of last name to narrow the list) AND "
                "scrolling through the full list of names to select. We may iterate on this UX."
            ),
        },

        # Q3: New client registration
        "3": {
            "status": "closed",
            "answer": (
                "New clients are directed to the staff office. First day is free — a one-day guest pass. "
                "When the client decides to come back for a second day, their record is entered into the system. "
                "This is a deliberate workflow: a guest pass before signing up."
            ),
            "context": (
                "This is an intentional low-barrier-to-entry design, not a gap. The kiosk should handle "
                "'not found' gracefully — direct client to staff office for first visit. Registration "
                "happens in the staff office, not at the kiosk."
            ),
        },

        # Q4: Services offered
        "4": {
            "status": "in_progress",
            "answer": (
                "Services include showers and laundry (time-slotted). Other services mentioned via "
                "brochures on the table. Full service list still needed. "
                "Nice-to-have: client picks an available time for shower or laundry at check-in. "
                "This goes into a schedule and notifies staff."
            ),
            "context": (
                "Have printout sheets (examples of sign-up sheets for services) from the visit. "
                "Need to photograph/digitize these. Shower and laundry scheduling is a Phase 2 "
                "nice-to-have — build check-in first, then add scheduling."
            ),
        },

        # Q18: Physical layout
        "18": {
            "status": "in_progress",
            "answer": (
                "The center has:\n"
                "- A front entrance with the current (inactive) kiosk and sign-in table\n"
                "- A back door with a clipboard for sign-in\n"
                "- A separate staff office room (not in line of sight of check-in)\n"
                "- The staff office has 4 desks\n"
                "- Miss Cobine has a desktop at her desk plus a laptop\n"
                "- All other staff have laptops which they take home with them\n"
                "- The kiosk table currently has brochures about services and events\n"
                "- Kitchen area had WiFi coverage issues, recently mitigated with additional AP"
            ),
            "context": (
                "Staff office is SEPARATE from the check-in area — this is Topology 2. "
                "The kiosk must operate independently. Staff access to the system is from their office."
            ),
        },

        # Q19: Topology
        "19": {
            "status": "closed",
            "answer": (
                "Topology 2: Staff admin is in a separate room from client check-in. "
                "The staff office has 4 desks and is not in the same room as the front entrance kiosk."
            ),
            "context": (
                "This means: standalone kiosk at front entrance, staff access via their office computers "
                "(laptops/desktop). Requires either network connectivity between kiosk and staff machines, "
                "or the staff interface runs on the same machine and they remote in / use a web interface."
            ),
        },

        # Q21: Internet
        "21": {
            "status": "in_progress",
            "answer": (
                "Wireless internet is provided to clients. Comcast business router is visible in the office. "
                "Bundles of Cat 5 cabling go in various directions from the office. "
                "The kitchen had WiFi coverage issues — a recent addition was an additional WiFi access point. "
                "Internet is available for the kiosk if needed."
            ),
            "context": (
                "WiFi is available and functional. The kiosk could use the network for staff notifications "
                "and real-time data access from the staff office. This opens up a web-based architecture "
                "where the kiosk runs a local web app and staff access it over the LAN."
            ),
        },

        # Q23: Single vs dual screen
        "23": {
            "status": "in_progress",
            "answer": (
                "Wall-mounted touchscreen for client check-in. Staff access from their office "
                "(separate room). Not a dual-screen-at-one-desk scenario. "
                "When asked about preference, the room chose touchscreen over mouse/keyboard."
            ),
            "context": (
                "Miss Cobine asked the room: mouse or touchscreen? Only reply was touchscreen. "
                "This is a single client-facing touchscreen on the wall, with staff accessing "
                "the system from their own devices in the office."
            ),
        },

        # Q29: Client check-in flow
        "29": {
            "status": "in_progress",
            "answer": (
                "Client identifies from a scrolling list of first name and last initial. "
                "This was the previous kiosk workflow and should carry forward. "
                "Must also support typing letters of a last name to filter down the list, "
                "because some clients cannot read or write and need to scroll visually. "
                "Both input methods required: type-to-filter AND scroll-to-select."
            ),
            "context": (
                "Critical accessibility requirement: some clients cannot read or write. "
                "The scrolling list with first name + last initial is a proven UX for this population. "
                "Type-to-filter is an enhancement for literate clients, not a replacement for scrolling."
            ),
        },

        # Q30: Self-registration
        "30": {
            "status": "closed",
            "answer": (
                "Clients do NOT self-register. New clients are directed to the staff office. "
                "First day is free (guest pass). Registration enters the system on second visit. "
                "If someone isn't in the system, the kiosk should say: please see staff."
            ),
            "context": (
                "Guest pass / free first day is a deliberate low-barrier design. "
                "Registration requires staff involvement — collected in the office, not at the kiosk."
            ),
        },

        # Q41: Wall-mounted display
        "41": {
            "status": "in_progress",
            "answer": (
                "Miss Cobine wants the screen mounted on the wall to free up table space. "
                "This replaces the current table-based kiosk setup. Touchscreen confirmed as preferred input."
            ),
            "context": (
                "Wall mount changes hardware calculus: need VESA-compatible touchscreen + hidden mini PC, "
                "or a wall-mountable AIO. Consider ergonomics: height for standing clients, "
                "angle for touch interaction. ADA accessibility if required."
            ),
        },

        # Q42: Information radiator
        "42": {
            "status": "in_progress",
            "answer": (
                "Miss Cobine wants the kiosk screen to display events, calendar, schedule, "
                "and brochure content when not in use for check-in. Currently this information "
                "is on paper brochures on the table. Digital display would free up table space "
                "and keep information current."
            ),
            "context": (
                "This is an idle-mode / screensaver feature. Needs a staff-friendly way to update "
                "content (events, calendar, announcements). Could be as simple as a folder of images "
                "or a lightweight CMS. The screen cycles through content until a client taps to check in."
            ),
        },

        # Q43: Shower and laundry scheduling
        "43": {
            "status": "in_progress",
            "answer": (
                "Nice-to-have: clients pick an available time slot for showers or laundry at check-in. "
                "The booking goes into a schedule and notifies staff. Have printout sheets showing "
                "current paper-based sign-up process."
            ),
            "context": (
                "Nice-to-have, not MVP. Build check-in and information radiator first. "
                "Scheduling adds: time slot config, availability display, booking logic, "
                "staff notifications. Good Phase 2 feature."
            ),
        },

        # Q6: Staff
        "6": {
            "status": "in_progress",
            "answer": (
                "Staff office has 4 desks. Miss Cobine has a desktop and a laptop. "
                "All other staff have laptops which they take home. "
                "Miss Cobine is the primary contact and decision maker."
            ),
            "context": (
                "Prior IT person was let go — concerns were speed of work and reluctance to multitask. "
                "Tasks included laptop setup, printer/fax, and software development. "
                "The expectation is efficient use of time — e.g., start another task while waiting "
                "for a laptop to download updates."
            ),
        },

        # Q38: Primary contact
        "38": {
            "status": "closed",
            "answer": "Miss Cobine is the primary point of contact at EMO.",
            "context": "Met at the shelter location on Feb 19, 2026. She led the meeting and made decisions.",
        },
    }

    # Create a parent task for the whole discovery
    parent = mem.tasks.create(
        title="Phase 1 Discovery — EMO Day Center Kiosk",
        description=(
            "Complete all discovery questions for the EMO Oregon Day Center kiosk project. "
            "Site visit conducted Feb 19, 2026 at the Chautauqua location with Miss Cobine."
        ),
        status="in_progress",
        labels=["phase1", "discovery"],
    )

    created = 0
    answered = 0

    for q in config["questions"]:
        qid = q["id"]
        note = notes.get(qid)

        if note:
            status = note["status"]
            desc = f"Question: {q['question_text']}\n\nAnswer: {note['answer']}"
            if note.get("context"):
                desc += f"\n\nContext notes: {note['context']}"
        else:
            status = "open"
            desc = f"Question: {q['question_text']}"
            if q.get("helper_text"):
                desc += f"\n\nHelper: {q['helper_text']}"

        labels = [f"q{qid}", f"section:{q['section_id']}", f"priority:{q.get('priority', 2)}"]
        if note:
            labels.append("has_notes")
            answered += 1

        task = mem.tasks.create(
            title=f"Q{qid}: {q['question_text'][:80]}",
            description=desc,
            status=status,
            parent_id=parent.id,
            labels=labels,
            metadata={
                "question_id": qid,
                "section_id": q["section_id"],
                "priority": q.get("priority", 2),
                "question_type": q.get("question_type", "long_text"),
            },
        )
        created += 1

    # Record key decisions from the meeting
    d1 = mem.decisions.begin(
        "Input method for client check-in kiosk",
        task_id=parent.id,
    )
    mem.decisions.hypothesize(d1.id, "Keyboard and mouse", rationale="Current inactive kiosk had this setup")
    mem.decisions.hypothesize(d1.id, "Touchscreen", rationale="Preferred by clients when asked at meeting")
    mem.decisions.decide(d1.id, "h2", rationale="Miss Cobine asked the room. Only reply was touchscreen.")

    d2 = mem.decisions.begin(
        "Kiosk form factor and placement",
        task_id=parent.id,
    )
    mem.decisions.hypothesize(d2.id, "Table-based kiosk", rationale="Current setup, takes up table space")
    mem.decisions.hypothesize(d2.id, "Wall-mounted touchscreen", rationale="Frees table space, requested by Miss Cobine")
    mem.decisions.decide(d2.id, "h2", rationale="Miss Cobine wants screen on wall to free table space for other uses.")

    d3 = mem.decisions.begin(
        "New client registration workflow",
        task_id=parent.id,
    )
    mem.decisions.hypothesize(d3.id, "Self-registration at kiosk", rationale="Reduces staff workload")
    mem.decisions.hypothesize(d3.id, "Staff-only registration in office after guest pass day", rationale="Current deliberate workflow — low barrier to entry")
    mem.decisions.decide(d3.id, "h2", rationale="Existing workflow is intentional: free first day, staff registers on second visit.")

    d4 = mem.decisions.begin(
        "Deployment topology: staff access to kiosk data",
        task_id=parent.id,
    )
    mem.decisions.hypothesize(d4.id, "Topology 1: Side-by-side screens at one desk", rationale="Simpler, one machine")
    mem.decisions.hypothesize(d4.id, "Topology 2: Separate rooms, networked", rationale="Matches physical layout — staff office is separate from check-in")
    mem.decisions.decide(d4.id, "h2", rationale="Staff sit in a separate office room. Kiosk is at front entrance. Physical separation confirmed at site visit.")

    mem.close()

    print(f"Memory seeded at {MEMORY_PATH}/")
    print(f"  Parent task: {parent.id}")
    print(f"  Questions created: {created}")
    print(f"  With meeting notes: {answered}")
    print(f"  Decisions recorded: 4")
    print(f"\nReady for 'Queen's Garden' workflow in Claude Code.")


if __name__ == "__main__":
    seed()
