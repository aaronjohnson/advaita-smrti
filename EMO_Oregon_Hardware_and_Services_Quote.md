HARDWARE & ADDITIONAL SERVICES QUOTE
EMO Oregon Day Center Client Management System
February 3, 2026
DRAFT v3 - For Discussion

Prepared for: Clark D. Melillo
Prepared by: Aaron Johnson, Independent Technical Consultant

────────────────────────────────────────────────────────────────────

TABLE OF CONTENTS

1. Overview
2. Relationship to the Statement of Work
3. Deployment Topology
4. Hardware Options
5. Data Retrieval & Export
6. Data Retention Policy
7. HMIS & Ryan White Compatibility
8. Ongoing Support
9. Open Source & Code Ownership
10. Summary
11. Next Steps

────────────────────────────────────────────────────────────────────

1. OVERVIEW

This document provides hardware pricing and additional service
quotes for the items identified as out-of-scope in the original
Statement of Work (January 22, 2026). Specifically:

  - Hardware procurement (kiosk device, displays, enclosure)
  - Data retrieval workflow (how EMO staff access and export
    check-in records, including HMIS-formatted reports)
  - Data retention and backup rotation policy
  - Ongoing support beyond initial deployment

All hardware options below are self-contained, offline-capable
systems that store data locally with encryption at rest. No
internet connection or cloud service is required for daily
operation.

────────────────────────────────────────────────────────────────────

2. RELATIONSHIP TO THE STATEMENT OF WORK

The original Statement of Work ($4,500 + $500 contingency =
$5,000) includes development of the complete application:

  - Check-In Interface (client-facing kiosk screen)
  - Administration Interface (client lookup, registration,
    service recording)
  - Reporting Module (export to CSV/Excel)
  - User Management (staff accounts, permissions)
  - Backup Automation (encrypted backup to USB)
  - Data Migration (from existing Excel records)
  - Documentation (privacy policy, security plan, user manual)

The admin interface, reporting module, and user management are
part of the same application as the check-in kiosk — not a
separate program. They are accessed through a staff login on
the same system.

HMIS-compatible CSV export and Ryan White RSR export are
included in this budget. The data model will be designed from
the start with HUD Universal Data Elements and RSR-relevant
fields in mind. Exporting data in the correct format is a
reporting function, not a separate feature. The specific fields
collected and export formats enabled will be confirmed during
the discovery session based on EMO Oregon's funding sources.

A standalone Windows data recovery tool is also included as a
standard deliverable (see Section 5).

The development cost is $5,000 flat. What this hardware quote
adds is the physical equipment, the deployment configuration,
backup/retention policy, and optional ongoing support.

────────────────────────────────────────────────────────────────────

3. DEPLOYMENT TOPOLOGY

The system has two user-facing modes: a client check-in screen
and a staff administration screen. How these are physically
deployed depends on the day center's space and workflow. Three
configurations are possible. The right choice depends on how
EMO Oregon operates today — this will be confirmed during the
discovery session.

────────────────────────────────────

TOPOLOGY 1: DUAL-SCREEN, SINGLE DESK (RECOMMENDED)

One device drives two screens at the same desk. The client
screen faces outward toward clients. The staff screen faces
the staff member behind the desk.

  ┌─────────────────┐       ┌──────────────────────┐
  │  CLIENT SCREEN  │       │  STAFF SCREEN        │
  │  7" touch       │       │  10-15" touch        │
  │  (faces client) │       │  (faces staff)       │
  │                 │       │                      │
  │  Check in/out   │       │  Register new clients│
  │  Select services│       │  Look up records     │
  │                 │       │  Run reports         │
  │  Locked down.   │       │  Export to USB       │
  │  No escape.     │       │  Manage staff users  │
  └────────┬────────┘       └──────────┬───────────┘
           │  HDMI / DSI               │  HDMI / DSI
           └───────────┬───────────────┘
                       │
              ┌────────┴────────┐
              │  Raspberry Pi 5 │
              │  (single device)│
              │  SQLCipher DB   │
              │  USB backup     │
              └─────────────────┘

Advantages:
  - Single device, single database, no networking required
  - Staff can register a new client immediately as they
    walk in, then the client checks in on the other screen
  - Lowest hardware cost (one Pi, two screens)
  - All data and logging in one place
  - Staff screen can be larger for tables and reports
  - Mirrors a typical front-desk workflow: sign-in sheet
    faces the visitor, staff paperwork faces the worker

Considerations:
  - Both screens must be at the same physical desk
  - The Pi 5 has two HDMI outputs and one DSI connector,
    so it can drive two displays natively
  - Staff screen should have a keyboard (USB) for data
    entry during client registration

This topology is recommended if EMO has a staffed front desk
or reception area where clients currently sign in on paper.
It reproduces the paper workflow digitally.

────────────────────────────────────

TOPOLOGY 2: TWO DEVICES, SAME BUILDING

Separate kiosk and staff station in different areas of the
building (e.g., kiosk in the lobby, staff station in a back
office). Connected by a direct ethernet cable or a small
dedicated WiFi access point (no internet).

  ┌─────────────────┐                ┌─────────────────┐
  │  CLIENT KIOSK   │   ethernet     │  STAFF STATION  │
  │  (lobby)        │ ─────────────> │  (back office)  │
  │  Pi + 7" screen │   or local     │  Pi + 15" screen│
  │                 │   WiFi         │  + keyboard     │
  └─────────────────┘                └─────────────────┘

Advantages:
  - Client kiosk can be in a public area; staff station
    in a private area (better for viewing sensitive data)
  - Kiosk operates independently if staff station is off

Considerations:
  - Requires two Pi devices (~$130 additional hardware)
  - Requires a network connection between them (ethernet
    cable or WiFi access point, ~$20-50)
  - Data synchronization adds development complexity
  - Network, even though local-only, increases the
    attack surface compared to a single device

────────────────────────────────────

TOPOLOGY 3: AIR-GAPPED (USB SNEAKERNET)

Kiosk operates completely standalone. Data is exported to
USB and physically carried to a separate computer (Windows
PC, staff Pi, or another location) for reporting.

  ┌─────────────────┐   USB drive   ┌─────────────────┐
  │  CLIENT KIOSK   │ ───────────>  │  ANY COMPUTER   │
  │  (day center)   │  physically   │  (office, other │
  │                 │  carried      │   location)     │
  └─────────────────┘               └─────────────────┘

Advantages:
  - Maximum physical security (true air gap)
  - Kiosk and reporting can be at different locations
  - No network of any kind

Considerations:
  - Staff cannot manage clients in real time at the kiosk
  - New client registration must happen at the kiosk
    itself (requires a staff PIN to access admin mode)
    or clients self-register
  - USB transfer adds a manual step to the daily workflow
  - If the admin system is a separate machine, it either
    runs the same Flask app (reading the USB database)
    or uses the Windows recovery tool (see Section 5)

────────────────────────────────────

TOPOLOGY RECOMMENDATION

Topology 1 (dual-screen, single desk) is recommended as the
starting point. It is the simplest to build, deploy, and
maintain. It puts the staff member right next to the client
interaction, which matches the typical day center front-desk
workflow. Reports and HMIS exports go to a USB drive that
staff can then open on any Windows PC with Excel.

If the discovery session reveals that the admin station needs
to be in a separate room or location, Topology 2 or 3 can be
accommodated. The software architecture supports all three
configurations.

────────────────────────────────────────────────────────────────────

4. HARDWARE OPTIONS

Prices are approximate, based on current availability as of
February 2026. Memory component prices are trending upward
due to industry-wide supply constraints. Ordering sooner may
avoid further increases.

────────────────────────────────────

PLATFORM CHOICE: LINUX vs. ANDROID

Two platform approaches are viable. The choice affects the
software development approach and should be decided before
development begins.

  LINUX (Raspberry Pi)

    OS: Raspberry Pi OS Lite (64-bit) with Cage Wayland
      compositor (purpose-built kiosk compositor)
    App: Python/Flask web app on localhost, displayed in
      fullscreen Chromium
    DB: SQLite + SQLCipher (AES-256 encryption at rest)
    Tamper resistance: Read-only root filesystem via
      overlay FS; reboots restore to known-good state
    Development: As described in the current Statement
      of Work (Python/Flask/HTML/JS). No changes needed.

  ANDROID (Tablet)

    OS: Android with Lock Task Mode (single-app kiosk)
    App: Native Android app built with Flutter (Dart) or
      Kotlin, with SQLite/SQLCipher local database
    DB: SQLite + SQLCipher, plus Android file-based
      encryption by default
    Tamper resistance: Android Lock Task Mode prevents
      exiting the app. Samsung Knox adds enterprise
      management on Samsung devices.
    Development: Requires revising the Statement of Work
      to reflect a Flutter or Kotlin codebase instead of
      Python/Flask. Development effort is comparable, but
      the technology stack and required skillset differ.

────────────────────────────────────

OPTION A: RASPBERRY PI — DUAL SCREEN (TOPOLOGY 1)

One Raspberry Pi 5 driving two displays at the same desk.
Client screen (small, touch-only) and staff screen (larger,
with USB keyboard for data entry).

── A1: Pi + 7" Client + 15.6" Staff ──────────────────────

  Raspberry Pi 5 (2 GB)                          $65.00
  Pi Touch Display 2, 7" (client screen)         $154.20
    720x1280 IPS, anti-glare, capacitive touch
  KKSB Metal Display Stand (client screen)        $30.00
    Aluminum/steel, ball joint, professional
  Volcora 15.6" Touchscreen (staff screen)       $215.95
    1366x768, HDMI, capacitive touch
  Official Pi 27W Power Supply (USB-C)            $14.04
  Micro-HDMI to HDMI cable (staff screen)          $8.00
  microSD Card 32 GB (A2-class)                   $12.00
  USB keyboard (staff data entry)                 $15.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
    2 weekly rotation + 1 annual archive
  Surge Protector                                 $12.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $571.19

  Recommended configuration. Client gets a clean 7"
  touch kiosk in a metal stand. Staff gets a full 15.6"
  screen with keyboard for registration and reports.
  Both driven by a single Pi under the desk.

── A2: Pi + 7" Client + 7" Staff (Compact) ───────────────

  Raspberry Pi 5 (2 GB)                          $65.00
  Pi Touch Display 2, 7" (client screen)         $154.20
  KKSB Metal Display Stand (client screen)        $30.00
  Pi Foundation 7" Display (staff screen)         $79.95
    800x480, capacitive touch
  SmartiPi Touch 2 Stand (staff screen)           $39.99
  Official Pi 27W Power Supply (USB-C)            $14.04
  microSD Card 32 GB (A2-class)                   $12.00
  USB keyboard (staff data entry)                 $15.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  Surge Protector                                 $12.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $467.18

  Compact and lower cost. Both screens are 7". The staff
  screen (800x480) is adequate for check-in management
  but tight for detailed reports and tables. Reports
  are better viewed after exporting to a Windows PC.

────────────────────────────────────

OPTION B: RASPBERRY PI — SINGLE SCREEN (TOPOLOGY 3)

One Pi, one display. Admin functions accessed via a staff
PIN on the same screen, or via USB export to a Windows PC.

── B1: Pi + 7" Premium ───────────────────────────────────

  Raspberry Pi 5 (2 GB)                          $65.00
  Pi Touch Display 2, 7" (720x1280 IPS)         $154.20
  KKSB Metal Display Stand                        $30.00
  Official Pi 27W Power Supply (USB-C)            $14.04
  microSD Card 32 GB (A2-class)                   $12.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  Surge Protector                                 $12.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $332.24

── B2: Pi + 7" Budget ────────────────────────────────────

  Raspberry Pi 5 (2 GB)                          $65.00
  Pi Foundation 7" Touchscreen (800x480)          $79.95
  SmartiPi Touch 2 Stand (plastic)                $39.99
  Official Pi 27W Power Supply (USB-C)            $14.04
  microSD Card 32 GB (A2-class)                   $12.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  Surge Protector                                 $12.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $267.98

────────────────────────────────────

OPTION C: ANDROID TABLETS (TOPOLOGY 1 OR 3)

NOTE: Selecting Android changes the development approach.
The Statement of Work would need to be revised to reflect
a Flutter or Kotlin codebase. Development effort is
comparable. See Platform Choice section above.

── C1: Two Tablets, Dual-Screen Desk ─────────────────────

  Samsung Galaxy Tab A9 8.7" (client kiosk)      $139.00
    Android, Samsung Knox enterprise security
  Countertop kiosk stand, locking (client)       $100.00
  Samsung Galaxy Tab A9+ 11" (staff station)     $199.00
    Larger screen for admin/reports
  Countertop stand (staff)                        $80.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $563.00

  Clean form factor. Each tablet is self-contained with
  its own battery backup (survives brief power outages).
  Samsung Knox provides enterprise kiosk lockdown.
  Tablets sync over local WiFi (no internet needed) or
  share a database via USB-C connection.

── C2: Single Tablet ─────────────────────────────────────

  Samsung Galaxy Tab A9 (8.7")                   $139.00
  Countertop kiosk stand, locking                $100.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $284.00

  Single device. Staff access admin mode via PIN.

── C3: Budget Single Tablet ──────────────────────────────

  Walmart onn. 8" Tablet                          $79.00
  Countertop kiosk stand                          $80.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $204.00

  Lowest cost. No enterprise security features.
  No Samsung Knox. Limited manufacturer support
  and security update lifespan (2-3 years).

────────────────────────────────────

OPTION D: COMMERCIAL TOUCHSCREEN (ELO)

For high-traffic environments where hardware durability is
the priority. Pairs with a Raspberry Pi (Linux stack).

── D1: Elo 15.6" + Pi (Single Screen) ───────────────────

  Raspberry Pi 5 (2 GB)                          $65.00
  Elo 1502L 15.6" Touchscreen                   $610.00
    Commercial-grade, 3-year warranty, TouchPro
  Official Pi 27W Power Supply (USB-C)            $14.04
  Micro-HDMI to HDMI cable                         $8.00
  microSD Card 32 GB (A2-class)                   $12.00
  Standalone Pi 5 case                             $12.00
  USB Flash Drives 128 GB x3 (backup rotation)   $45.00
  Surge Protector                                 $12.00
  ─────────────────────────────────────────────────────
  SUBTOTAL                                       $778.04

  Only justified for heavy daily use, rough handling, or
  institutional environments requiring commercial-grade
  equipment. The Elo is an industry-standard POS monitor.

────────────────────────────────────────────────────────────────────

5. DATA RETRIEVAL & EXPORT

The system provides three ways for staff to access and export
data, plus a standalone recovery tool for disaster scenarios.

────────────────────────────────────

METHOD 1: STAFF ADMIN SCREEN (BUILT IN)

The administration interface is part of the application,
accessed via staff login on the staff screen (Topology 1)
or via a staff PIN on the kiosk itself (Topology 3). This
provides:

  - Client search and record lookup
  - New client registration
  - Daily/weekly/monthly check-in reports
  - Service utilization summaries
  - HMIS CSV export (if enabled)
  - Ryan White RSR export (if enabled)
  - User and staff account management
  - Audit log viewer

This is included in the Statement of Work.

────────────────────────────────────

METHOD 2: USB EXPORT (CSV / EXCEL)

From the admin screen, staff can export reports to the USB
flash drive as CSV or Excel files. These files are standard
spreadsheet files — not encrypted — intended to be opened
in Excel on any Windows PC.

  Step 1. Insert USB drive into the kiosk.
  Step 2. Go to Reports > Export.
  Step 3. Select report type and date range.
  Step 4. Enter staff password (authorizes and logs export).
  Step 5. Tap "Export to USB." Wait for confirmation.
  Step 6. Remove USB drive. Open files in Excel.

Available export formats:
  - Standard reports (daily counts, monthly summaries,
    client lists) as CSV or Excel
  - HMIS CSV files (Client.csv, Enrollment.csv, Exit.csv,
    Services.csv) conforming to the HUD HMIS CSV Format
    Specification, ready for upload to the regional HMIS
  - Ryan White RSR data export (if applicable)

IMPORTANT: Exported CSV/Excel files contain client
information in readable form. The USB drive should be
handled with the same care as paper client records and
stored securely when not in use.

────────────────────────────────────

METHOD 3: ENCRYPTED BACKUP (USB)

Separately from report exports, the system writes a full
encrypted database backup to the USB drive on a configurable
schedule (daily recommended) or on demand. This backup is an
AES-256 encrypted SQLCipher database file. It cannot be
opened in Excel or read without the system decryption
password.

The backup serves two purposes:
  - Disaster recovery (if the kiosk SD card fails, the
    backup can restore the full database to a new device)
  - Secure data transfer (if needed, the encrypted backup
    can be carried to another location and loaded into
    another instance of the application)

See Section 6 for the backup rotation schedule.

────────────────────────────────────

WINDOWS DATA RECOVERY TOOL (INCLUDED)

A standalone Windows application is provided as part of the
standard deliverables. This tool exists for one scenario:
the kiosk is unavailable (hardware failure, theft, fire)
and staff need to access data from the USB backup drives.

The recovery tool:
  1. Reads the encrypted SQLCipher database from a USB drive
  2. Prompts for the decryption password
  3. Exports all data to CSV/Excel files on the Windows PC

This is a small, self-contained program (no installation
required — runs directly from the USB drive or any folder).
It does not require the kiosk to be operational. Any Windows
PC with the recovery tool and the decryption password can
access the backup data.

The recovery tool is included on each USB backup drive
alongside the encrypted database, so that the drive itself
is a complete disaster recovery package: the data, the tool
to read it, and instructions. All that is needed is the
password, which should be stored separately in a secure
location (e.g., a sealed envelope in a safe).

This tool is included in the Statement of Work at no
additional cost.

────────────────────────────────────────────────────────────────────

6. DATA RETENTION POLICY

Multiple regulatory frameworks govern how long client data
must be retained. The applicable requirements depend on
EMO Oregon's funding sources and will be confirmed during
discovery.

APPLICABLE RETENTION REQUIREMENTS

  Regulation                   Retention Period
  ──────────────────────────────────────────────────────
  Oregon medical records       10 years from last contact
  (OAR 333-505-0050)

  HIPAA administrative         6 years from creation or
  records and audit logs       last in effect
  (45 CFR 164.530(j))

  HUD HMIS data                7 years from creation;
  (69 FR 45888)                then delete or de-identify

  Federal grant records        3 years after final
  (2 CFR 200.334)              expenditure report

  Oregon HIV confidentiality   No separate retention
  (ORS 433.045)                period; follows medical
                               records (10 years) with
                               heightened confidentiality

SIMPLIFIED POLICY (RECOMMENDED)

Rather than managing multiple overlapping timelines, a
single unified policy satisfies all requirements:

  Retain all client records for 10 years from the
  client's last date of service. After 10 years,
  securely delete.

This satisfies Oregon's 10-year medical records standard
(the longest applicable period), which automatically covers
HMIS (7 years), HIPAA administrative (6 years), and federal
grant (3 years) requirements.

Records subject to an active audit, legal hold, or open
complaint must be retained until the matter is resolved,
regardless of the 10-year timeline.

SECURE DISPOSAL

When records reach the end of their retention period:
  - Digital records: cryptographic erasure (re-encrypt
    the database with a new random key, then delete the
    key) or reformat the storage media
  - USB backup drives: reformat before reuse or disposal
  - Paper records (if any): cross-cut shredding

DATA MINIMIZATION

The system collects only data necessary for operations and
required reporting. The most effective protection for
sensitive information is not to collect it in the first
place. Specific fields collected will be determined during
discovery based on actual operational and reporting needs.

HIV status in particular warrants careful consideration
under ORS 433.045. If EMO Oregon serves individuals who
may have HIV without recording that status at the
individual level, there is no HIV data to protect. This
is the safest approach and is recommended unless grant
reporting specifically requires individual-level HIV
status tracking.

USB BACKUP ROTATION SCHEDULE

Three USB flash drives are included in the hardware BOM:

  DRIVE A and DRIVE B: Weekly rotation

    - Drive A is in the kiosk this week, receiving daily
      automated backups.
    - Drive B is in secure storage (locked drawer, safe).
    - At the end of each week, swap them. Drive B goes
      into the kiosk; Drive A goes into secure storage.
    - Each drive always contains: the encrypted database
      backup, the Windows recovery tool, and a printed
      instruction card.
    - If the kiosk is lost or destroyed, the drive in
      storage has data no more than one week old.

  DRIVE C: Annual archive

    - Once per year (e.g., January), create a fresh
      backup on Drive C. Label it with the year.
    - Store in a fireproof safe or offsite location.
    - Purchase a new Drive C each year (~$15).
    - Keep annual archive drives for 10 years per the
      retention policy, then securely erase.
    - Over the 10-year retention period, this amounts
      to 10 archive drives at a total cost of ~$150.

  Why not monthly?

    The weekly rotation drives already contain the
    complete database (all historical records, not just
    that week's data). A monthly archive adds point-in-
    time recovery ("what did the data look like on
    March 1st") but limited practical value for a day
    center. Annual archives are sufficient for long-term
    retention compliance, and weekly rotation provides
    adequate disaster recovery.

    Monthly rotation can be implemented if desired at
    minimal cost (~$180/year for 12 additional drives).

────────────────────────────────────────────────────────────────────

7. HMIS & RYAN WHITE COMPATIBILITY

Whether these features are needed depends on EMO Oregon's
funding sources. This will be confirmed during discovery.
Both are included in the development budget at no additional
cost, enabled or disabled based on what is needed.

────────────────────────────────────

HMIS (HOMELESS MANAGEMENT INFORMATION SYSTEM)

HMIS is a HUD-mandated data system for tracking services to
individuals experiencing homelessness. Each region's
Continuum of Care (CoC) operates a shared HMIS instance,
typically hosted by a vendor such as Bitfocus Clarity or
WellSky ServicePoint.

Projects receiving HUD homeless assistance funding must
participate in HMIS and collect Universal Data Elements.

What "HMIS compatible" means for this project:

  1. DATA COLLECTION: Check-in and registration screens
     capture HUD Universal Data Elements using the correct
     enumerated value codes from the HMIS Data Dictionary:

       - Name (first, middle, last)
       - Social Security Number (with data quality flag)
       - Date of Birth (with data quality flag)
       - Race and Ethnicity (HUD categories)
       - Veteran Status
       - Disabling Condition (yes/no)
       - Prior Living Situation

  2. CSV EXPORT: The reporting module generates CSV files
     conforming to the HUD HMIS CSV Format Specification:

       - Client.csv (demographics)
       - Enrollment.csv (project entry records)
       - Exit.csv (project exit records)
       - Services.csv (services at each visit)

     These files can be uploaded to the regional HMIS by
     the CoC's HMIS administrator using standard import
     tools provided by the HMIS vendor.

  3. NOT INCLUDED: Direct API integration with Bitfocus
     Clarity, WellSky, or other HMIS vendors. API access
     is vendor-specific, requires a relationship with the
     CoC's HMIS lead agency, and would be a separate
     engagement if needed in the future.

────────────────────────────────────

RYAN WHITE / RSR REPORTING

If EMO Oregon receives Ryan White HIV/AIDS Program funding,
a separate reporting obligation exists: the Ryan White
Services Report (RSR), managed by HRSA through its CAREWare
software.

RSR and HMIS are completely distinct systems with different
data elements and reporting pipelines. However, the
demographic fields overlap substantially. If the data model
is designed with both systems in mind (which it will be),
adding an RSR-compatible export is a reporting format
change, not a separate feature.

The kiosk will collect the common demographic fields once.
Staff export to HMIS format, RSR format, or both, depending
on what is needed.

────────────────────────────────────

DEVELOPMENT COST

Both HMIS and RSR export capabilities are included in the
$5,000 development budget. The data model is designed with
these reporting requirements in mind from the start. The
specific fields collected and export formats enabled are
configured during the discovery session based on EMO
Oregon's actual funding sources and reporting obligations.

If EMO Oregon is not HUD-funded and does not receive Ryan
White funding, these features are simply not enabled, and
the data model collects only what is needed for day center
operations — resulting in a simpler, leaner system.

────────────────────────────────────────────────────────────────────

8. ONGOING SUPPORT

The kiosk is designed to operate with minimal maintenance.
The read-only root filesystem resets to a known-good state
on every reboot. The encrypted database and automated
backups protect against data loss. If the hardware fails,
staff use the Windows recovery tool on the USB backup drive
to access data while a replacement is prepared.

This is an offline system with no network connectivity.
There is no remote access, remote monitoring, or remote
troubleshooting capability. Support is provided on-site or
by preparing updated SD card images for staff to swap in.

SUPPORT AVAILABILITY

  Rate: $75/hour, billed as used
  Response: Best effort, typically within 48 business hours
  No retainer or monthly commitment required

  Typical support scenarios:
    - Hardware replacement (SD card failure, screen damage):
      consultant prepares a new SD card image; staff swaps
      the card or the consultant visits on-site
    - Software updates: consultant prepares an updated SD
      card image; staff swaps it in on the next convenient
      day. The database is on the USB drive, not the SD
      card, so no data is lost during an update
    - Bug fixes or feature requests: quoted per request
    - Annual security review: if desired, the consultant
      reviews the system for known vulnerabilities in the
      software stack and prepares an updated image (~2-4
      hours, $150-$300 annually)

  If EMO Oregon wants a guaranteed response time (e.g.,
  next business day), a small annual retainer can be
  arranged. This would be discussed based on actual
  needs after the system has been in operation.

────────────────────────────────────────────────────────────────────

9. OPEN SOURCE & CODE OWNERSHIP

The question of code ownership and open-source licensing is
worth addressing up front, as it affects both EMO Oregon's
long-term flexibility and the consultant's ability to use
this work as a portfolio reference.

────────────────────────────────────

PROPOSED APPROACH: OPEN SOURCE WITH FULL OWNERSHIP

The recommended approach is to release the application code
under a permissive open-source license (such as the MIT
License or BSD 2-Clause License). Under this model:

  What EMO Oregon gets:

    - Full, unrestricted ownership of their data (always —
      this is non-negotiable regardless of licensing)
    - Full access to all source code
    - The right to use, modify, and distribute the software
      without restriction
    - No vendor lock-in: any developer can maintain, modify,
      or extend the system in the future
    - No licensing fees, now or ever
    - Community benefit: other shelters and day centers
      facing the same problem can adopt the system,
      which may lead to community-contributed improvements
      that benefit EMO Oregon at no cost

  What the consultant gets:

    - The ability to reference the project in a professional
      portfolio
    - The ability to offer the same system to other
      nonprofit organizations serving similar populations
    - Community visibility and contribution credit

  What open source does NOT do:

    - It does NOT expose EMO Oregon's data. The source code
      is the application logic (how the system works). Client
      data is never included in the code repository. Data
      stays on the kiosk, encrypted, under EMO's physical
      control.
    - It does NOT mean the system is less secure. Security
      through obscurity (hiding the code) is not a reliable
      security practice. The system's security relies on
      encryption (AES-256), access controls (passwords and
      roles), and audit logging — none of which depend on
      the code being secret.
    - It does NOT prevent EMO from making private
      modifications. EMO can fork the code at any time
      and keep changes private if desired.

────────────────────────────────────

ALTERNATIVE: PROPRIETARY / WORK-FOR-HIRE

If EMO Oregon prefers that the code remain private:

    - EMO Oregon owns the code exclusively
    - The consultant retains no rights to reuse or
      redistribute
    - Other organizations cannot benefit from the work
    - Future maintenance depends entirely on EMO's ability
      to hire a developer familiar with the stack

  This is a standard work-for-hire arrangement and is fully
  supported if preferred. There is no cost difference.

────────────────────────────────────

RECOMMENDATION

Open source under a permissive license (MIT or BSD) is
recommended. It protects EMO Oregon's interests (full access,
no lock-in, no fees) while allowing the work to benefit the
broader community of organizations serving similar
populations. A check-in kiosk for day shelters is a common
need; an open-source solution that others can adopt and
improve creates value beyond this single deployment.

This decision does not need to be made immediately. It can
be discussed during the discovery session and formalized
before the first code is written.

────────────────────────────────────────────────────────────────────

10. SUMMARY

HARDWARE COMPARISON

  Option                          Cost    Screens  Topology
  ──────────────────────────────────────────────────────────
  A1  Pi dual: 7" + 15.6"       $571    2        Same desk
  A2  Pi dual: 7" + 7"          $467    2        Same desk
  B1  Pi single: 7" premium     $332    1        Standalone
  B2  Pi single: 7" budget      $268    1        Standalone
  C1  Android dual: 8.7" + 11"  $563    2        Same desk
  C2  Android single: 8.7"      $284    1        Standalone
  C3  Android single: 8" budget $204    1        Standalone
  D1  Pi + Elo commercial 15.6" $778    1        Standalone

DEVELOPMENT COST

  Complete application development          $5,000
  (Statement of Work + contingency)
  Includes:
    - Check-in interface
    - Admin interface with reporting
    - HMIS CSV export
    - Ryan White RSR export
    - Encrypted backup system
    - Windows data recovery tool
    - Data migration from Excel
    - All documentation
    - Staff training

  No additional development costs anticipated.

TOTAL PROJECT COST SCENARIOS

  Scenario 1: RECOMMENDED (Dual-Screen Pi Kiosk)
    Development                              $5,000
    Hardware (A1: Pi + 7" + 15.6")             $571
    ──────────────────────────────────────────────
    Total                                    $5,571

  Scenario 2: COMPACT (Dual-Screen Pi, Both 7")
    Development                              $5,000
    Hardware (A2: Pi + 7" + 7")                $467
    ──────────────────────────────────────────────
    Total                                    $5,467

  Scenario 3: MINIMAL (Single-Screen Pi)
    Development                              $5,000
    Hardware (B1: Pi + 7" premium)             $332
    ──────────────────────────────────────────────
    Total                                    $5,332

  Scenario 4: ANDROID (Dual Tablet)
    Development                              $5,000
    Hardware (C1: Samsung dual tablets)        $563
    ──────────────────────────────────────────────
    Total                                    $5,563

  All scenarios represent a complete, working system
  including software, hardware, data migration, training,
  and documentation. Ongoing support is available at
  $75/hour as needed.

────────────────────────────────────────────────────────────────────

11. NEXT STEPS

  1. Review this quote alongside the original Statement
     of Work.

  2. Schedule discovery session with EMO Oregon stakeholders
     (tentatively this coming Monday). Key items to resolve:

     - Funding sources (HUD, Ryan White, other) to determine
       which data fields and export formats to enable
     - Current intake workflow (who registers new clients,
       where, and when)
     - Physical space and desk layout at the day center
       (determines deployment topology)
     - Platform preference (Linux Pi vs. Android tablet)
     - Services tracked at check-in
     - Staff roles and permission levels needed
     - Whether HIV status is tracked at the individual level
     - Open source vs. proprietary code preference
     - Data retention policy review and approval

  3. Approve hardware procurement so devices can be ordered
     and available for development and testing.

  4. Begin Phase 1 (Discovery & Requirements) per the
     Statement of Work timeline.

────────────────────────────────────────────────────────────────────

NOTES

  - All hardware prices are approximate and based on
    current availability as of February 2026. Memory
    component prices are trending upward due to industry-
    wide supply constraints. Ordering sooner may avoid
    further increases.

  - Hardware can be purchased directly by EMO Oregon from
    the listed retailers, or procured by the consultant
    and invoiced at cost (no markup).

  - All software deliverables include source code. EMO
    Oregon has full access to the code and complete
    ownership of their data. No recurring license fees
    under any scenario.

────────────────────────────────────────────────────────────────────

Prepared by:

_________________________________
Aaron Johnson
Independent Technical Consultant

Date: February 3, 2026

Document Control: Version 3.0 (DRAFT)
Supersedes: Version 2.0 (February 3, 2026)
