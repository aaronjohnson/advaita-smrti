HARDWARE OPTIONS DISCUSSION
EMO Oregon Day Center Kiosk Project
Meeting with Clark and Kylie
February 2026

────────────────────────────────────────────────────────────────────

CONTEXT

Feedback from Clark: budget is flexible for hardware. Priority is
durability and good value for a system that will run reliably for
5+ years with minimal maintenance.

This document presents three hardware paths at different price
points, from commercial all-in-one to Pi-based solutions. All
run the same application and meet the same functional requirements.

────────────────────────────────────────────────────────────────────

HARDWARE PATHS

────────────────────────────────────

PATH 1: COMMERCIAL ALL-IN-ONE (ELO I-SERIES)

A purpose-built commercial touchscreen computer — the same type
of hardware used in retail POS, hospital check-in kiosks, and
quick-service restaurants.

  Elo 10" I-Series for Linux                    ~$450-500
    - 10.1" 1280x800 capacitive touchscreen
    - Rockchip 6-core ARM processor
    - 4 GB RAM, 32 GB flash storage
    - Debian Linux (native, not Android)
    - WiFi, Ethernet, Bluetooth 5.0
    - 5 MP camera (optional use)
    - VESA 75/100 mounting
    - Designed for 24/7 commercial operation
    - Commercial warranty and support

  What you get:
    - Single integrated unit, no assembly
    - Built for retail/hospitality abuse
    - Replacement parts available for years
    - Elo is the industry standard (now part of Zebra)

  What changes:
    - Not a Raspberry Pi — runs ARM Debian Linux
    - Flask application runs identically (Python/Linux)
    - Minor deployment adaptation, no code changes

  Best for: Maximum durability, lowest long-term risk,
    "set it and forget it" deployment.

────────────────────────────────────

PATH 2: EMBEDDED PI (CM5 + WAVESHARE KIOSK)

A Raspberry Pi Compute Module 5 in an integrated aluminum
enclosure with touchscreen. This is the "embedded product"
form factor that commercial Pi-based products use.

  Raspberry Pi Compute Module 5                      $60
    - 4 GB RAM, 32 GB eMMC (no SD card)
    - Quad-core 2.4 GHz ARM Cortex-A76
    - WiFi + Bluetooth
    - Production guaranteed through 2036

  Waveshare CM4-DISP-BASE-7A-BOX                $170-200
    - 7" 800x480 capacitive touchscreen
    - Toughened glass
    - Aluminum enclosure
    - Wide voltage input: 7-36V DC
      (tolerates dirty/variable power)
    - M.2 slot for NVMe SSD (optional, more reliable)
    - Real-time clock with battery backup
    - Dual speakers
    - Full GPIO, USB, HDMI breakout

  27W USB-C Power Supply                             $15
  USB flash drives (3x, backup rotation)             $60
  Surge protector                                    $10
  ─────────────────────────────────────────────────────
  SUBTOTAL                                     ~$315-355

  What you get:
    - Same Pi software stack as current SOW
    - eMMC storage (more reliable than SD cards)
    - Aluminum enclosure, professional appearance
    - Wide voltage tolerance for power resilience
    - Compact integrated form factor

  What changes:
    - Uses Compute Module instead of Pi 5
    - Requires CM5 IO board or Waveshare carrier
    - Slightly different deployment procedure

  Best for: Pi flexibility with improved durability,
    good middle ground between consumer and commercial.

────────────────────────────────────

PATH 3: PREMIUM PI BUILD (KKSB ENCLOSURE)

The current recommended configuration with upgraded enclosure.
Standard Raspberry Pi 5 in a professional metal case.

  Raspberry Pi 5 (4 GB)                              $60
  Pi Touch Display 2 (7", 720x1280 IPS)             $154
  KKSB Panel Mount Case (aluminum/steel)          $60-75
  27W USB-C Power Supply                             $15
  microSD Card 32 GB (A2-class)                      $14
  USB flash drives (3x, backup rotation)             $60
  Surge protector                                    $10
  ─────────────────────────────────────────────────────
  SUBTOTAL                                     ~$375-390

  What you get:
    - Standard Pi 5, widely supported
    - Higher resolution display (720p vs 480p)
    - Professional metal enclosure
    - VESA mountable, Kensington lock slot
    - Easy to repair/replace components

  What changes:
    - Nothing from current SOW — this is the baseline

  Best for: Flexibility, repairability, lowest risk
    of vendor lock-in.

────────────────────────────────────────────────────────────────────

DUAL-SCREEN CONFIGURATIONS

The recommended deployment has two screens at the same desk:
a client-facing check-in screen and a larger staff-facing
admin screen. Here's how each path scales to dual-screen:

────────────────────────────────────

OPTION A: ELO + ELO (FULL COMMERCIAL)

  Client: Elo 10" I-Series Linux              ~$475
  Staff:  Elo 15" I-Series Linux              ~$650
  USB drives, surge protector, etc.            ~$75
  ─────────────────────────────────────────────────
  HARDWARE TOTAL                            ~$1,200

  Both units are commercial-grade. Staff unit has
  larger screen for reports and data entry. Both
  run Debian Linux — same Flask app on both, with
  different browser URLs (one for check-in, one
  for admin).

  Durability: Commercial-grade, 5+ year lifespan
  Appearance: Professional, retail-quality
  Maintenance: Lowest — commercial warranty/support

────────────────────────────────────

OPTION B: CM5 KIOSK + COMMERCIAL STAFF DISPLAY

  Client: CM5 + Waveshare integrated kiosk    ~$330
  Staff:  Elo 15.6" touchscreen monitor        $610
          (with separate Pi 5 or shared CM5)
  USB drives, cables, surge protector          ~$75
  ─────────────────────────────────────────────────
  HARDWARE TOTAL                            ~$1,015

  Client kiosk is the integrated Waveshare unit.
  Staff display is a commercial Elo monitor driven
  by either a shared compute unit or a second Pi.

  Durability: Mixed — semi-industrial client,
    commercial staff display
  Appearance: Professional
  Maintenance: Moderate

────────────────────────────────────

OPTION C: CM5 KIOSK + CONSUMER STAFF DISPLAY

  Client: CM5 + Waveshare integrated kiosk    ~$330
  Staff:  Volcora 15.6" touchscreen            $216
          (with Pi 5 or shared CM5)
  Pi 5 for staff display (if separate)          $60
  USB drives, cables, surge protector          ~$75
  ─────────────────────────────────────────────────
  HARDWARE TOTAL                              ~$680

  Same client kiosk, but staff display is the
  consumer-grade Volcora monitor. Good value,
  but not commercial-grade.

  Durability: Mixed — semi-industrial client,
    consumer staff display
  Appearance: Good
  Maintenance: Moderate

────────────────────────────────────

OPTION D: KKSB BUILD + VOLCORA (CURRENT QUOTE)

  Client: Pi 5 + Touch Display 2 + KKSB       ~$315
  Staff:  Volcora 15.6" + shared Pi             $216
  Keyboard (Free Geek)                           $0
  USB drives, cables, surge protector          ~$75
  ─────────────────────────────────────────────────
  HARDWARE TOTAL                              ~$605

  This is the A1 configuration from the current
  quote. Solid value, consumer-premium hardware.

  Durability: Consumer-premium
  Appearance: Good (KKSB metal stand)
  Maintenance: Easy — standard Pi components

────────────────────────────────────────────────────────────────────

COMPARISON SUMMARY

  Option                    Hardware    Durability       Notes
  ──────────────────────────────────────────────────────────────
  A  Elo + Elo              ~$1,200    Commercial       Best durability
  B  CM5 Kiosk + Elo Staff  ~$1,015    Mixed-high       Good balance
  C  CM5 Kiosk + Volcora      ~$680    Mixed-medium     Value option
  D  KKSB Pi + Volcora        ~$605    Consumer-premium Current quote

  Development cost is $5,000 for all options (unchanged).

  Total project cost:
    Option A: $5,000 + $1,200 = $6,200
    Option B: $5,000 + $1,015 = $6,015
    Option C: $5,000 +   $680 = $5,680
    Option D: $5,000 +   $605 = $5,605

────────────────────────────────────────────────────────────────────

RECOMMENDATION

For a day shelter front desk that needs to run reliably for
5+ years with minimal maintenance:

  PRIMARY: Option B (CM5 Kiosk + Elo Staff)     ~$6,015

    - Client kiosk is the Waveshare integrated unit:
      aluminum enclosure, toughened glass, wide voltage
      tolerance, embedded compute module with eMMC
      (no SD card failures)

    - Staff display is commercial Elo: built for retail,
      3-year warranty, parts available for years

    - Still runs the same Flask/Python application
      on Raspberry Pi compute — no software changes

  ALTERNATIVE: Option A (Full Elo)              ~$6,200

    - Both units are commercial-grade
    - Highest durability, lowest maintenance risk
    - Slightly higher cost, slightly less flexibility
    - Application runs on Debian Linux (minor adaptation)

  BUDGET-CONSCIOUS: Option C or D              ~$5,600-5,700

    - Solid value, good for 3-5 years
    - May need hardware refresh sooner than commercial
    - Easier to repair with off-the-shelf Pi parts

────────────────────────────────────────────────────────────────────

QUESTIONS FOR DISCUSSION

  1. What is the physical environment at the day center?
     - Is there a staffed front desk?
     - How much space is available?
     - Is there reliable, clean power?

  2. How rough is the expected use?
     - Will clients touch the screen gently or firmly?
     - Is there risk of spills, impacts, or tampering?

  3. What is the expected lifespan?
     - 3 years? 5 years? 7+ years?
     - Is there budget for hardware refresh in year 4-5?

  4. Is commercial warranty/support important?
     - Or is local repair capability sufficient?

  5. Platform preference?
     - Stay with Raspberry Pi (Paths 2, 3)?
     - Move to commercial Linux (Path 1)?

────────────────────────────────────────────────────────────────────

NEXT STEPS (PENDING DISCUSSION)

  1. Confirm hardware path based on budget and durability needs
  2. Order hardware for development and testing
  3. Begin Phase 1 (Discovery) per Statement of Work
  4. Finalize data model based on funding sources (HMIS, RSR)
  5. Confirm deployment topology (dual-screen same desk vs other)

────────────────────────────────────────────────────────────────────

REFERENCE LINKS

  Elo 10" I-Series Linux:
  https://www.elotouch.com/touchscreen-computers-10-inch-i-series-linux.html

  Elo 15" I-Series Linux:
  https://www.elotouch.com/touchscreen-computers-15-inch-i-series-linux.html

  Raspberry Pi Compute Module 5:
  https://www.raspberrypi.com/products/compute-module-5/

  Waveshare CM4-DISP-BASE-7A-BOX:
  https://www.waveshare.com/cm4-disp-base-7a-box.htm

  KKSB Cases:
  https://kksb-cases.com/

────────────────────────────────────────────────────────────────────
