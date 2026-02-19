WINDOWS PLATFORM OPTIONS
EMO Oregon Day Center Kiosk
February 19, 2026

────────────────────────────────────────────────────────────────────

CONTEXT

Hardware discussion scoped to a Windows PC with touchscreen.
Two software paths available on this platform.

────────────────────────────────────────────────────────────────────

PATH 1: NATIVE WINDOWS — C# / WPF or WinUI 3

  Stack:
    Language:       C# (.NET 8+)
    UI Framework:   WPF (proven) or WinUI 3 (modern)
    Database:       SQLite + Microsoft.Data.Sqlite
    Encryption:     SQLCipher via SQLitePCLRaw.bundle_sqlcipher
                    (NuGet package, AES-256 at rest)
    Packaging:      MSIX or standalone .exe
    Kiosk lockdown: Windows Assigned Access (single-app kiosk mode)
                    Built into Windows 10/11 Pro

  What this looks like:
    - Native desktop app, no browser involved
    - Touch-optimized WPF/WinUI controls
    - Runs at startup in kiosk mode via Assigned Access
    - Single .exe install, no dependencies to manage
    - USB export writes CSV/Excel directly to drive
    - Windows Task Scheduler handles automated backups

  Advantages:
    - Native OS integration (kiosk mode, file system, USB)
    - No browser layer, no web server, no localhost
    - .NET ecosystem is well-supported, long-lived
    - Assigned Access is a mature, Microsoft-supported
      kiosk lockdown — no custom compositor needed
    - Easier for a future developer to maintain on Windows
    - Windows Defender + BitLocker available out of the box
    - Can use BitLocker for full disk encryption in addition
      to SQLCipher for database encryption

  Considerations:
    - Different language from original SOW (C# vs Python)
    - Dual-screen: WPF/WinUI can open windows on specific
      monitors — client window on screen 1 (kiosk mode),
      staff window on screen 2 (or same screen, PIN-switched)
    - Assigned Access locks to one app; dual-screen with
      two distinct modes requires either one app managing
      both windows, or a second user session on screen 2
    - Not directly portable to Pi if they ever want that

  Kiosk lockdown detail:
    Windows Assigned Access (Settings > Accounts > Kiosk):
    - Create a dedicated kiosk user account
    - Assign the app as the single allowed application
    - On boot, auto-logs into kiosk user, launches app
    - No taskbar, no desktop, no alt-tab, no escape
    - Staff access: switch user (Ctrl+Alt+Del) to a
      staff account, or app has internal PIN-based
      mode switch
    - Available on Windows 10/11 Pro (not Home)

────────────────────────────────────────────────────────────────────

PATH 2: WSL2 + PYTHON/FLASK (LINUX-ON-WINDOWS)

  Stack:
    Runtime:        WSL2 (Windows Subsystem for Linux)
    OS inside WSL:  Ubuntu 24.04 LTS
    Language:       Python 3.12+
    Web framework:  Flask
    Database:       SQLite + SQLCipher (AES-256)
    UI:             Chromium/Edge in kiosk mode (--kiosk flag)
                    pointed at localhost
    Kiosk lockdown: Windows Assigned Access (Edge in kiosk mode)
                    or Shell Launcher v2

  What this looks like:
    - Flask app runs inside WSL2 on localhost
    - Edge or Chromium opens fullscreen to http://localhost:5000
    - Identical application code to the original Pi SOW
    - WSL2 starts automatically on boot via Task Scheduler
    - USB access from WSL2 via /mnt/d/ (Windows drives)

  Advantages:
    - Same Python/Flask codebase as original SOW
    - Portable: same code runs on Pi if they ever want that
    - Flask + HTML/JS UI is easier to iterate on than WPF
    - Web-based UI is inherently touch-friendly
    - Familiar stack if Aaron is stronger in Python than C#

  Considerations:
    - Extra layer: Windows → WSL2 → Ubuntu → Flask → Browser
    - WSL2 occasionally needs updates or restarts
    - USB drive access from WSL2 works but has friction
      (Windows auto-mounts, WSL2 accesses via /mnt/)
    - Assigned Access works with Edge in kiosk mode, but
      the Flask server must start before Edge opens — need
      a startup script that sequences WSL2 → Flask → Edge
    - If WSL2 crashes or fails to start, kiosk shows
      "cannot connect" — need a watchdog/retry
    - Not a standard deployment pattern; a future maintainer
      needs to understand both Windows and WSL2

  Startup sequence:
    1. Windows boots, auto-logs into kiosk user
    2. Task Scheduler runs: wsl -d Ubuntu -- flask run
    3. Wait for Flask to bind to localhost:5000
    4. Assigned Access launches Edge in kiosk mode
       pointing to http://localhost:5000
    5. Edge shows the check-in screen

  USB export from WSL2:
    - Windows mounts USB as D:\ (or E:\, etc.)
    - WSL2 sees it at /mnt/d/
    - Flask app writes exports to /mnt/d/exports/
    - Works, but auto-detection of USB insertion requires
      a polling script or Windows-side helper

────────────────────────────────────────────────────────────────────

HEAD-TO-HEAD COMPARISON

                          C# Native         WSL2 + Python
  ──────────────────────────────────────────────────────────
  Language                C# (.NET 8)       Python 3.12
  UI                      WPF / WinUI 3     HTML/JS (Flask)
  Database                SQLCipher          SQLCipher
  Encryption at rest      SQLCipher +        SQLCipher +
                          BitLocker          BitLocker
  Kiosk mode              Assigned Access    Assigned Access
                          (native app)       (Edge + Flask)
  Layers                  Windows → App      Windows → WSL2
                                             → Flask → Edge
  Startup reliability     High (native)      Medium (sequenced)
  USB handling            Native Win32 API   /mnt/ from WSL2
  Dual-screen             Multi-window app   Two browser windows
  Portability to Pi       No                 Yes (same code)
  Future maintainer       C#/.NET devs       Python devs
  Dev effort              Comparable         Comparable
  Offline operation       Native             Native
  OS requirement          Win 10/11 Pro      Win 10/11 Pro

────────────────────────────────────────────────────────────────────

RECOMMENDATION

  For a Windows-only deployment: PATH 1 (C# Native)

  Rationale:
    - Fewer moving parts. No WSL2 layer to manage.
    - Assigned Access + native app is the intended kiosk
      pattern on Windows. Microsoft built it for this.
    - USB, file system, startup, and shutdown are all
      first-class Windows operations — no translation layer.
    - A day shelter kiosk needs to be dead reliable on boot.
      One app starting is more reliable than sequencing
      WSL2 → Flask → Browser.
    - BitLocker + SQLCipher gives defense-in-depth encryption.
    - If the machine dies, replace it, install the app,
      restore from USB backup. No WSL2 setup needed.

  When to choose PATH 2 (WSL2 + Python):
    - If the same codebase MUST run on both Windows and Pi
    - If the developer is significantly more productive in
      Python than C# (enough to offset the operational cost
      of the WSL2 layer)
    - If rapid UI iteration matters more than deployment
      simplicity (HTML/CSS is faster to tweak than WPF XAML)

────────────────────────────────────────────────────────────────────

HARDWARE: WINDOWS TOUCHSCREEN OPTIONS

  All options: Windows 11 Pro required (for Assigned Access).
  Touch required. Dual-screen optional (USB-C/HDMI out).

────────────────────────────────────────────────────

  TIER 1: ALL-IN-ONE TOUCHSCREEN PC (~$400-700)

    Examples:
    - HP ProOne 440 G9 (21.5" or 23.8" touch AIO)
    - Lenovo ThinkCentre M90a (23.8" touch AIO)
    - Dell OptiPlex 7410 AIO (23.8" touch)

    What you get:
    - Single unit: PC + display + touch integrated
    - Business-class, 3-year warranty typical
    - Multiple USB ports for backup drives
    - HDMI/DP out for second display
    - VESA mountable
    - Pro SKUs ship with Windows 11 Pro

    Dual-screen: plug a second touchscreen monitor into
    HDMI/DP out. Client checks in on the AIO, staff uses
    the second display (or vice versa).

────────────────────────────────────────────────────

  TIER 2: WINDOWS TABLET + STAND (~$300-600)

    Examples:
    - Microsoft Surface Go 4 (10.5", $450-600)
    - Lenovo Tab Plus / IdeaPad Duet (budget)
    - HP Elite x2 G4 (refurbished, ~$300)

    What you get:
    - Compact, portable, built-in battery (UPS for free)
    - Touchscreen is the primary interface
    - USB-C for external display and USB drives
    - Need a locking kiosk stand ($80-150)

    Considerations:
    - Smaller screen (10-13") — fine for check-in,
      tight for staff admin with tables
    - Windows 11 Pro required — verify before purchasing
      (many consumer tablets ship with Home or S Mode)
    - Less durable than an AIO in a commercial setting

────────────────────────────────────────────────────

  TIER 3: MINI PC + TOUCHSCREEN MONITOR (~$350-600)

    Examples:
    - Intel NUC or Beelink Mini PC ($150-250)
      + Elo 15.6" touchscreen monitor ($610)
      + or Volcora 15.6" touchscreen ($216)

    What you get:
    - Separates compute from display (like the Pi approach)
    - Mini PC is powerful, replaceable, cheap
    - Touch monitor can be commercial-grade (Elo)
    - Easy to add a second monitor

    Considerations:
    - Two components to manage (PC + monitor)
    - Requires Windows 11 Pro license ($140 retail,
      or included with OEM mini PC)

────────────────────────────────────────────────────

HARDWARE RECOMMENDATION FOR DISCUSSION

  For a day center front desk:

  PRIMARY: All-in-One touchscreen (Tier 1)        ~$400-700
    - One unit, one power cable, one warranty
    - Business-class, built for institutional use
    - HDMI out for a second display if needed later
    - HP ProOne or Lenovo ThinkCentre are the safe picks

  Add for dual-screen:
    Second touchscreen (Volcora 15.6")               ~$216
    ──────────────────────────────────────────────────
    Total hardware                               ~$600-900

  BUDGET: Refurbished AIO + Volcora               ~$350-500
  PREMIUM: New AIO + Elo 15.6" staff display      ~$900-1,300

────────────────────────────────────────────────────────────────────

SOW IMPACT

  If Windows + C# is selected:
    - SOW language changes from Python/Flask to C#/.NET
    - All features remain the same
    - Kiosk lockdown changes from Cage Wayland to
      Windows Assigned Access
    - Encrypted backup approach unchanged (SQLCipher)
    - BitLocker adds full-disk encryption (free with Pro)
    - Development cost: $5,000 (unchanged)
    - "Read-only root filesystem" replaced by
      "Assigned Access + Windows write filter" (UWF)
      which provides equivalent tamper resistance

  If Windows + WSL2/Python is selected:
    - SOW language stays Python/Flask
    - Adds WSL2 deployment and startup scripting
    - Otherwise same as above

────────────────────────────────────────────────────────────────────
