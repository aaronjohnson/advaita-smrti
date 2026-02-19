PHASE 1 DISCOVERY — MEETING GUIDE
EMO Oregon Day Center Kiosk
Chautauqua, February 19, 2026

────────────────────────────────────────────────────────────────────

PURPOSE

Finalize the Statement of Work. Walk out with enough to build.
Time budget: ~3 hours (4 hours billed including writeup).

────────────────────────────────────────────────────────────────────

SECTION 1: THE DAY CENTER TODAY
(Start here. Understand their world before proposing anything.)

  1.1  Walk me through a typical day at the center, open to close.
       - What time do doors open? Close?
       - What happens when someone walks in?
       - Who greets them? Is there a front desk?

  1.2  How do clients currently sign in?
       - Paper log? Excel? Nothing?
       - What information is captured at sign-in today?
       - Who handles it — the client or staff?

  1.3  How are new clients registered today?
       - What information do you collect on first visit?
       - Is there an intake form? Can I see a copy?
       - How long does registration take?

  1.4  What services does the center offer?
       - List them all (meals, showers, laundry, case mgmt,
         mail, phone, computer access, etc.)
       - Which services do you need to track per visit?
       - Are any services limited (e.g., one shower per day)?

  1.5  How many clients per day, roughly?
       - Average day?
       - Busiest day?
       - How many total unique clients over a year?

  1.6  Who are the staff members who will use this system?
       - How many staff? What roles?
       - Volunteers? Do they need access?
       - Who is the day-to-day system owner?

────────────────────────────────────────────────────────────────────

SECTION 2: DATA AND REPORTING
(What do they need to get OUT of the system?)

  2.1  What reports do you run today?
       - Daily counts? Monthly summaries?
       - Who reads these reports? (Board, funders, staff?)
       - What format? (Printed, emailed, uploaded somewhere?)

  2.2  What are your funding sources?
       - HUD homeless assistance grants? (triggers HMIS)
       - Ryan White HIV/AIDS Program? (triggers RSR)
       - SAMHSA? Other federal grants?
       - State or county contracts?
       - Private foundations?

  2.3  Do you currently report to HMIS?
       - Which regional CoC?
       - Which HMIS vendor? (Clarity, ServicePoint, other?)
       - Who does the HMIS data entry today?
       - How? (Direct entry into HMIS portal? CSV upload?)
       - How often? (Daily, weekly, monthly, quarterly?)

  2.4  Do you report Ryan White / RSR data?
       - Do you use CAREWare?
       - Who handles RSR reporting?

  2.5  What other reporting obligations exist?
       - Funder-specific reports?
       - Internal board reports?
       - County or state reporting?

  2.6  Is there existing data to migrate?
       - Excel spreadsheets? Access database?
       - How far back does it go?
       - How clean is it? (Duplicates, missing fields, etc.)
       - Can I get a copy (de-identified if needed) to assess?

────────────────────────────────────────────────────────────────────

SECTION 3: CLIENT DATA FIELDS
(What exactly goes into the system?)

  3.1  REGISTRATION FIELDS — what to collect on first visit:

       Start with the minimum. For each field, ask:
       "Do you need this? Is it required by a funder?"

       Demographics:
       [ ] First name
       [ ] Last name
       [ ] Preferred/chosen name
       [ ] Date of birth
       [ ] SSN (last 4? full? none?)
       [ ] Gender identity
       [ ] Race
       [ ] Ethnicity
       [ ] Veteran status
       [ ] Disabling condition (yes/no)
       [ ] Prior living situation

       Contact:
       [ ] Phone number
       [ ] Email
       [ ] Emergency contact

       Program-specific:
       [ ] HIV status — SEE 3.2
       [ ] Insurance status
       [ ] Income level
       [ ] Household composition
       [ ] Referral source

       Operational:
       [ ] Photo (for ID/recognition)?
       [ ] Client ID card issued?
       [ ] Notes/comments field?
       [ ] Case manager assignment?

  3.2  HIV STATUS — handle carefully.

       This is the most sensitive data question.

       "Does your grant reporting require you to track HIV
       status at the individual client level? Or does the
       center serve people who may be living with HIV without
       recording that specifically?"

       Options:
       a) Don't collect it (safest — nothing to protect)
       b) Collect as yes/no (minimal, for grant compliance)
       c) Collect with detail (diagnosis date, viral load, etc.)

       Recommendation: option (a) unless a funder explicitly
       requires it. Under ORS 433.045, HIV data has heightened
       confidentiality protections. Not collecting it is the
       strongest protection.

  3.3  CHECK-IN FIELDS — what to capture at each visit:

       [ ] Date and time (automatic)
       [ ] Services used (from service list)
       [ ] Check-out time (automatic at close? manual?)
       [ ] Notes (staff only?)
       [ ] Reason for visit?
       [ ] Referrals made?

────────────────────────────────────────────────────────────────────

SECTION 4: PHYSICAL SPACE AND WORKFLOW
(Determines hardware and deployment topology.)

  4.1  Describe the physical layout of the center.
       - Is there a front desk or reception area?
       - Where would clients check in?
       - Where do staff sit?
       - Is the check-in area in line of sight of staff?

  4.2  Is there a desk where both a client screen and a
       staff screen could sit side by side?
       (This is Topology 1 — recommended, simplest to build.)

  4.3  Or does the staff admin need to be in a separate
       room from where clients check in?
       (This is Topology 2 — requires two devices + network.)

  4.4  Power situation:
       - Are there outlets at the check-in location?
       - Is the power reliable? Surges? Outages?
       - Does the center have a UPS or surge protection?

  4.5  Internet:
       - Is there WiFi at the center?
       - The kiosk does NOT need internet for daily operation.
       - But: is occasional internet available for software
         updates? Or is the system truly air-gapped?

  4.6  Security of the device:
       - Is the check-in area supervised at all times?
       - Risk of theft or tampering?
       - Does the device need to be locked down / bolted?

────────────────────────────────────────────────────────────────────

SECTION 5: HARDWARE DECISION
(Windows PC — present options based on answers to Section 4.)

  Platform: Windows 11 Pro with touchscreen.
  Software: Native C# app (recommended) or Python via WSL2.
  Kiosk lockdown: Windows Assigned Access (built-in).

  Three hardware tiers:

  TIER 1: All-in-One Touchscreen PC             ~$400-700
    HP ProOne 440, Lenovo ThinkCentre M90a, Dell OptiPlex
    - Single unit: PC + display + touch
    - Business-class, 3-year warranty
    - HDMI out for second screen
    - The safe, boring, reliable choice

  TIER 2: Windows Tablet + Locking Stand         ~$300-600
    Surface Go 4, HP Elite x2
    - Compact, built-in battery (free UPS)
    - Need locking kiosk stand ($80-150)
    - Verify Windows 11 Pro (not Home/S Mode)

  TIER 3: Mini PC + Touchscreen Monitor          ~$350-600
    Beelink/NUC + Volcora or Elo monitor
    - Separates compute from display
    - Flexible, easy to swap components

  For dual-screen (client + staff), add:
    Second touchscreen (Volcora 15.6")              ~$216
    or commercial (Elo 15.6")                       ~$610

  Key questions:

  5.1  Single screen or dual screen?
       - Single: staff and clients share one screen,
         PIN switches between check-in and admin mode
       - Dual: client screen + staff screen at same desk
         (recommended if there's a front desk)

  5.2  All-in-one or separate components?
       - AIO is one unit, one warranty, one power cable
       - Mini PC + monitor is more flexible, replaceable

  5.3  New or refurbished?
       - Refurbished business AIO: ~$250-350
         (HP/Lenovo off-lease, 1-year warranty typical)
       - New: ~$400-700

  5.4  Do you want spare hardware on hand?
       - A second mini PC or spare AIO means same-day recovery
       - Without it, recovery depends on sourcing a replacement
       - USB backup drive + install media can restore the system
         onto ANY Windows 11 Pro PC

  TOTAL HARDWARE SCENARIOS:

    Budget:   Refurb AIO single-screen          ~$300-400
    Standard: New AIO + Volcora staff screen    ~$600-900
    Premium:  New AIO + Elo staff display       ~$900-1,300

  DECISION NEEDED: Confirm hardware path so ordering can begin.

────────────────────────────────────────────────────────────────────

SECTION 5B: SOFTWARE PATH
(Internal decision — may not need client input.)

  OPTION A: C# / .NET Native Windows App (RECOMMENDED)

    - Native Windows application, no browser
    - Assigned Access kiosk mode (Microsoft-supported)
    - SQLCipher (database encryption) + BitLocker (disk)
    - One app, starts on boot, no dependencies
    - USB export via native Windows file I/O
    - Future maintainer needs: C# / .NET skills

  OPTION B: Python / Flask via WSL2

    - Same codebase as original Pi-based SOW
    - Runs Flask in WSL2, displays in Edge kiosk mode
    - Boot sequence: Windows → WSL2 → Flask → Edge
    - USB access via /mnt/ (works, but indirect)
    - Portable to Pi/Linux if ever needed
    - Future maintainer needs: Python + WSL2 knowledge

  The client probably doesn't care about this distinction.
  It's an implementation detail. But if they ask:
    "Same features either way. I recommend the native
     Windows app — fewer moving parts, more reliable
     on startup, easier to maintain long-term."

  NOTE TO SELF: The W-2 vs 1099 question may affect this.
  If they want to own the codebase and have internal IT
  maintain it, C# on Windows is the more conventional
  enterprise choice. Python/Flask is the more portable,
  open-source-friendly choice.

────────────────────────────────────────────────────────────────────

SECTION 6: ACCESS CONTROL AND ROLES
(Who can do what in the system?)

  6.1  How many staff accounts are needed?

  6.2  What permission levels make sense?

       Proposed roles:
       - Admin: full access, user management, settings
       - Staff: register clients, view records, run reports
       - Kiosk: client-facing check-in only (no login)

       Are these sufficient? Do you need more granularity?

  6.3  How should the client check-in screen work?

       Options:
       a) Client enters a code (from an ID card you issue)
       b) Client types their name and selects from matches
       c) Client enters date of birth + last name
       d) Staff checks them in (not self-service)

       Which feels right for your population?

  6.4  Can clients self-register, or must staff do it?

  6.5  What should happen if someone isn't in the system?
       - "Not found — please see front desk"?
       - Allow self-registration on the kiosk?

────────────────────────────────────────────────────────────────────

SECTION 7: POLICY DECISIONS
(Confirm or adjust the defaults from the quote.)

  7.1  Data retention: 10-year unified policy?
       (Satisfies Oregon medical, HIPAA, HMIS, federal grants.)
       Confirm or adjust.

  7.2  Backup rotation: weekly swap (Drive A/B) + annual
       archive (Drive C)?
       Confirm or adjust.

  7.3  Open source or proprietary code?
       - Open source (MIT): reusable, no lock-in, community
       - Proprietary: EMO owns exclusively

       Recommendation is open source. Any concerns?

  7.4  Who holds the database decryption password?
       - Which staff member(s)?
       - Where is it stored? (Sealed envelope in a safe?)
       - Who is the backup if that person leaves?

  7.5  Data incident procedure:
       - Does EMO have an existing data breach policy?
       - If a USB drive is lost, who gets notified?

────────────────────────────────────────────────────────────────────

SECTION 8: TIMELINE AND LOGISTICS

  8.1  When do you want the system operational?
       - Is there a hard deadline (grant cycle, fiscal year)?
       - Or "as soon as practical"?

  8.2  Hardware ordering:
       - Does EMO purchase directly, or do I order and invoice?
       - Who approves the purchase?
       - Ship to the center or to me for setup?

  8.3  Development access:
       - Can I visit the center to see the space?
       - Who is my primary point of contact at EMO?
       - Best way to reach them for questions during build?

  8.4  Training:
       - How many staff need training?
       - On-site training at deployment?
       - Written guide sufficient for ongoing reference?

  8.5  Testing:
       - Can I deploy a test version at the center before
         going live?
       - Is there a quiet period to do a soft launch?

────────────────────────────────────────────────────────────────────

MEETING CLOSE

  Recap decisions made:
  [ ] Services list confirmed
  [ ] Data fields confirmed
  [ ] Funding sources / reporting requirements confirmed
  [ ] HIV status collection approach confirmed
  [ ] Hardware path selected
  [ ] Deployment topology confirmed
  [ ] Check-in flow confirmed (self-service vs staff-assisted)
  [ ] Open source vs proprietary confirmed
  [ ] Timeline confirmed
  [ ] Existing data migration scope assessed
  [ ] Primary contact at EMO identified

  Action items coming out of the meeting:
  [ ] Finalize SOW based on today's decisions
  [ ] Order hardware
  [ ] Get copy of existing data for migration assessment
  [ ] Get copy of current intake form (if one exists)
  [ ] Schedule site visit
  [ ] Begin development

────────────────────────────────────────────────────────────────────

NOTES DURING MEETING

  (Space for recording answers — fill in during conversation)










────────────────────────────────────────────────────────────────────
