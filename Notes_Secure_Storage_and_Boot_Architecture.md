DESIGN NOTES: SECURE STORAGE & BOOT ARCHITECTURE
EMO Oregon Day Center Client Management System
February 3, 2026
Internal working notes — not client-facing

────────────────────────────────────────────────────────────────────

HARDWARE-ENCRYPTED USB OPTION

If asked about physical security of the backup drives, the
following hardware-encrypted USB drives have physical PIN
pads and FIPS certification. The PIN is entered on the drive
itself — no software, no drivers, OS-independent. After 10
failed PIN attempts, the drive crypto-erases.

  Apricorn Aegis Secure Key 3NXC, 8 GB     ~$69
    FIPS 140-2 Level 3, IP68, USB-C
    https://www.amazon.com/dp/B08D2WLC7Z

  Kingston IronKey Keypad 200, 8 GB         ~$65
    FIPS 140-3 Level 3, USB-A or USB-C
    https://www.amazon.com/dp/B0CF9JDGMG

  iStorage datAshur PRO2, 8 GB              ~$70
    FIPS 140-2 Level 3, IP68, USB-A
    https://www.amazon.com/dp/B07VK7JTQT

Suggested allocation if using hardware-encrypted drives:
  2x Apricorn Aegis (~$138) — weekly rotation
  1x standard USB (~$17)    — annual archive (safe storage)
  1x thermal printer (~$25) — daily summary receipts
  Total: ~$180 (vs $45 for 3x standard drives)

The hardware encryption eliminates the need for SQLCipher
on the backup file — the drive itself handles encryption.
Backup can be a plain SQLite database on a physically
locked drive. Simpler software, FIPS-certified for audits.

────────────────────────────────────────────────────────────────────

THERMAL RECEIPT PRINTER

A 58mm USB thermal printer (~$20-30) can print daily
aggregate summaries with no PII. Zero digital attack
surface.

  Example output:
    EMO Oregon Day Center
    Tuesday, February 3, 2026
    ─────────────────────────
    Check-ins today:     47
    Meals served:        31
    Showers:              8
    Laundry:              4
    New registrations:    3
    ─────────────────────────
    Printed 5:02 PM

  Linux compatible via ESC/POS (python-escpos library).
  Paper rolls ~$0.50 each, last weeks.

────────────────────────────────────────────────────────────────────

CD-R FOR TAMPER-EVIDENT ARCHIVAL

Write-once optical media cannot be altered after burning.
More tamper-evident than USB for annual audit archives.

  USB DVD/CD burner: ~$20
  50x CD-R spindle:  ~$10
  50 MB database fits ~14x on a single CD-R

Practical for monthly or annual snapshots only. Not for
daily use. Receiving computer also needs an optical drive.

────────────────────────────────────────────────────────────────────

TWO-DATABASE BOOT ARCHITECTURE (TO REVISIT)

The kiosk needs to boot unattended (no staff password on
power-up) while keeping sensitive data locked until a staff
member authenticates. This suggests splitting the data:

  checkin.db (operational)
    Encrypted with a DEVICE KEY stored on the SD card.
    Opens automatically on boot.
    Contains only: client_code, first_name, last_initial,
      check-in/out timestamps, services selected.
    Enough for the client check-in screen to work with
    no staff involvement.

  admin.db (sensitive)
    Encrypted with a STAFF PASSWORD.
    Opens only when an admin logs in on the staff screen.
    Contains: full demographics, SSN, DOB, HMIS fields,
      audit log, staff accounts, system config.

  Boot sequence:
    Power on → Pi boots → Flask starts → reads device
    key from SD card → opens checkin.db → client screen
    ready. Staff screen shows login prompt. Staff enters
    password → admin.db opens → full admin access.

  Security posture:
    - Stolen USB drive: encrypted, no keys. Safe.
    - Stolen Pi + SD card: attacker gets client codes
      and first names only. No SSN, DOB, or HMIS data.
    - Stolen Pi + SD card + USB drive: same as above.
      admin.db requires the staff password.

  If using hardware-encrypted USB drives (Apricorn etc.),
  the backup of BOTH databases is on a PIN-locked drive.
  An attacker with the drive and no PIN gets nothing.

  Development tradeoff: two databases with foreign key
  references via client_code is more complex than one
  database, but the security posture is substantially
  stronger. Worth the added complexity.

  TO DO: finalize this architecture during development.
  Consider whether the device key should be derived from
  the Pi's hardware serial number (ties the database to
  a specific device) or a randomly generated key stored
  in a config file (more portable but must be backed up).

────────────────────────────────────────────────────────────────────
