RECOMMENDED SYSTEM: A1 — DUAL-SCREEN PI KIOSK
EMO Oregon Day Center Client Management System
February 3, 2026

────────────────────────────────────────────────────────────────────

DEPLOYMENT DIAGRAM

Front desk, viewed from above:


            CLIENT SIDE OF DESK
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

          ┌───────────────┐
          │ ┌───────────┐ │
          │ │  CHECK IN  │ │
          │ │           │ │
          │ │  *tap*    │ │  7" touchscreen
          │ │           │ │  in metal stand
          │ │  [ID] [GO]│ │  (faces client)
          │ └───────────┘ │
          │  KKSB stand   │
          └───────┬───────┘
                  │ DSI ribbon cable
    ══════════════╪═══════════════════════════  ← desk surface
                  │
          ┌───────┴───────┐
          │               │
          │  Raspberry    │     USB ──── ⬡ USB flash drive
          │  Pi 5         │               (backup/export)
          │               │
          │  (under desk  │     USB ──── ⌨ keyboard
          │   or behind   │               (from Free Geek)
          │   monitor)    │
          │               │     USB ──── 🖱 mouse (optional)
          └───────┬───────┘               (from Free Geek)
                  │ micro-HDMI
                  │
          ┌───────┴──────────────────┐
          │ ┌──────────────────────┐ │
          │ │  ADMIN / REPORTS     │ │
          │ │                      │ │
          │ │  [Clients] [Reports] │ │  15.6" touchscreen
          │ │  [Users]   [Export]  │ │  (faces staff)
          │ │                      │ │
          │ │  Client list.......  │ │
          │ │  Daily count: 47     │ │
          │ └──────────────────────┘ │
          │  Volcora monitor stand   │
          └──────────────────────────┘

    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
            STAFF SIDE OF DESK


Side view:

    client                              staff
    facing →                          ← facing

    ┌─────┐                     ┌────────────┐
    │     │                     │            │
    │ 7"  │    ┌─────┐         │   15.6"    │
    │     │    │ Pi  │         │            │
    └──┬──┘    └──┬──┘         └─────┬──────┘
    ───┴──────────┴──────────────────┴─────────  desk
       ↑          ↑                  ↑
     KKSB      under desk         Volcora
     stand     (velcro/mount)     built-in stand


Cable diagram:

    ┌──────────────────────────────────────────────┐
    │                                              │
    │  Raspberry Pi 5 (2 GB)                       │
    │                                              │
    │  DSI ──────────── 7" Touch Display 2         │
    │  HDMI 0 ───────── Volcora 15.6" monitor      │
    │  USB-A ─────────── USB flash drive (backup)  │
    │  USB-A ─────────── keyboard                  │
    │  USB-C ─────────── 27W power supply ── wall  │
    │                                              │
    │  Volcora monitor ── 12V power supply ── wall │
    │  Volcora monitor ── USB cable ── Pi USB-A    │
    │                     (for touch input)        │
    │                                              │
    └──────────────────────────────────────────────┘

    Total wall outlets needed: 2 (Pi power supply + monitor)
    Surge protector recommended for both.

────────────────────────────────────────────────────────────────────

BILL OF MATERIALS — WITH PURCHASE LINKS

── COMPUTE ────────────────────────────────────────────────────

  Raspberry Pi 5 (2 GB RAM)                         $65.00
  https://www.adafruit.com/product/6007
  In stock (limit 2 per customer)

  Official Raspberry Pi 32 GB microSD (A2-class)    $13.69
  https://www.adafruit.com/product/6010
  In stock. Blank; flash with Raspberry Pi Imager.

  Official Raspberry Pi 27W Power Supply (USB-C)    $14.04
  https://www.adafruit.com/product/5814
  In stock. 5.1V / 5A. Required for Pi 5.

── CLIENT DISPLAY (7" TOUCHSCREEN) ────────────────────────────

  Raspberry Pi Touch Display 2                     $154.20
  7" 720x1280 IPS, anti-glare, capacitive touch
  https://www.adafruit.com/product/6079
  In stock (52 units). Connects via DSI ribbon cable
  (included). Production guaranteed through Jan 2030.

  KKSB Metal Display Stand                          $33.99
  Aluminum + powder-coated steel, 360-degree ball joint
  https://www.amazon.com/dp/B07Y8WLB7H
  In stock. Buy from Amazon US (avoids import tariffs
  vs. ordering from kksb-cases.com in EU).
  Also available direct:
  https://kksb-cases.com/products/kksb-display-stand-for-raspberry-pi-touch-display-2-with-case-for-raspberry-pi-5

── STAFF DISPLAY (15.6" TOUCHSCREEN) ──────────────────────────

  Volcora 15.6" Touchscreen Monitor                $215.95
  1366x768, 10-point capacitive touch, HDMI + VGA
  https://volcora.com/products/15-6-touchscreen-monitor
  In stock. Also available on Amazon:
  https://www.amazon.com/dp/B0DLNJSKCJ
  Includes built-in stand and 12V power adapter.
  Weighs 11 lbs — stationary desk monitor.
  Touch requires USB cable from monitor to Pi.

  Official Raspberry Pi Micro-HDMI to HDMI Cable    $11.81
  1 meter, overmolded connectors
  https://www.adafruit.com/product/4302
  In stock. Connects Pi 5 to Volcora HDMI input.

── PERIPHERALS ────────────────────────────────────────────────

  USB Keyboard                                       $0.00
  Source: Free Geek Portland
  https://www.freegeek.org/shop
  3731 SE Division St, Portland, OR 97202
  Any standard USB keyboard works. Compact preferred
  to save desk space. Free Geek sells tested, cleaned
  peripherals for $2-5, or they may donate for a
  nonprofit project.

  USB Mouse (optional)                               $0.00
  Source: Free Geek Portland
  Staff screen is a touchscreen, so a mouse is optional
  but may be more comfortable for extended admin work.

── BACKUP & STORAGE ───────────────────────────────────────────

  Samsung FIT Plus 128 GB USB 3.1 Flash Drive (x3) ~$60.00
  Tiny form factor, 400 MB/s read, durable
  https://www.bhphotovideo.com/c/product/1417043-REG/
  In stock at B&H Photo ($19.99 each).
  Currently out of stock on Amazon. Monitor for restock:
  https://www.amazon.com/dp/B07D7PDLXC
  Amazon historical price: $13-17 each.

  Alternative if Samsung unavailable:
  SanDisk Ultra Fit 128 GB USB 3.1 (~$14/each)
  https://www.amazon.com/dp/B07855LJ99

  Allocation:
    Drive A — weekly rotation (in kiosk)
    Drive B — weekly rotation (in secure storage)
    Drive C — annual archive (in fireproof safe)

── POWER PROTECTION ───────────────────────────────────────────

  Surge Protector (6-outlet, 790J, 6ft cord)         $9.88
  https://www.amazon.com/dp/B00TP1C51M
  In stock. Covers both the Pi power supply and the
  Volcora monitor power adapter.

────────────────────────────────────────────────────────────────────

COST SUMMARY

  Component                               Cost
  ──────────────────────────────────────────────
  Raspberry Pi 5 (2 GB)                  $65.00
  microSD Card 32 GB                     $13.69
  Pi 27W Power Supply                    $14.04
  Pi Touch Display 2 (7")              $154.20
  KKSB Metal Stand                       $33.99
  Volcora 15.6" Monitor                $215.95
  Micro-HDMI to HDMI Cable              $11.81
  Keyboard (Free Geek)                    $0.00
  Mouse (Free Geek, optional)             $0.00
  USB Flash Drives x3 (B&H)             $59.97
  Surge Protector                         $9.88
  ──────────────────────────────────────────────
  HARDWARE TOTAL                       $578.53

  Development (Statement of Work)    $5,000.00
  ──────────────────────────────────────────────
  PROJECT TOTAL                      $5,578.53

────────────────────────────────────────────────────────────────────

WHAT IT LOOKS LIKE IN USE

  Opening:

    Staff arrives, flips the surge protector on.
    Both screens light up within 30 seconds.
    Client screen shows the check-in interface.
    Staff screen shows the admin login.

  Client checks in:

    Client walks up to the 7" screen.
    Enters their client code or name.
    Taps "Check In."
    Selects services (meal, shower, etc.).
    Done. Walks away.

  Staff registers a new client:

    Staff sees a new face, turns to the 15.6" screen.
    Logs in (if not already), taps "New Client."
    Types name, DOB, assigns a client code.
    Hands the client a card with their code.
    Client uses the code to check in on the 7" screen.

  End of day:

    Staff inserts USB drive into the Pi.
    On the 15.6" screen: Reports > Export.
    Selects report type, enters password.
    Taps "Export to USB." Green checkmark.
    Removes USB drive, stores in locked drawer.
    Flips the surge protector off. Done.

  Weekly:

    Staff swaps USB Drive A and Drive B.
    The drive that was in storage goes into the kiosk.
    The drive that was in the kiosk goes into storage.

  If the kiosk breaks:

    Staff takes the USB drive from secure storage.
    Plugs it into any Windows PC.
    Runs the recovery tool from the USB drive.
    Enters the decryption password.
    All data exports to Excel files on the PC.
    Operations continue on paper until a replacement
    Pi + SD card is prepared.

────────────────────────────────────────────────────────────────────

WHAT TO ORDER AND WHERE

  ┌──────────────────────────────────────────────────────┐
  │  ORDER FROM ADAFRUIT (one cart)                      │
  │  https://www.adafruit.com                            │
  │                                                      │
  │  qty  product #   item                       price   │
  │  1    6007        Raspberry Pi 5 (2GB)       $65.00  │
  │  1    6010        microSD Card 32GB          $13.69  │
  │  1    5814        27W USB-C Power Supply     $14.04  │
  │  1    6079        Touch Display 2 (7")      $154.20  │
  │  1    4302        Micro-HDMI to HDMI cable   $11.81  │
  │                                     ─────────────── │
  │                            Adafruit subtotal $258.74 │
  │                                     + shipping       │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │  ORDER FROM AMAZON (one cart)                        │
  │  https://www.amazon.com                              │
  │                                                      │
  │  qty  ASIN          item                     price   │
  │  1    B07Y8WLB7H    KKSB Metal Stand         $33.99  │
  │  1    B00TP1C51M    Surge Protector            $9.88  │
  │                                     ─────────────── │
  │                             Amazon subtotal   $43.87 │
  │                                     + tax            │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │  ORDER FROM VOLCORA                                  │
  │  https://volcora.com                                 │
  │                                                      │
  │  qty  item                               price       │
  │  1    15.6" Touchscreen Monitor          $215.95     │
  │                                     + shipping/tax   │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │  ORDER FROM B&H PHOTO                                │
  │  https://www.bhphotovideo.com                        │
  │                                                      │
  │  qty  item                               price       │
  │  3    Samsung FIT Plus 128GB USB 3.1     $19.99 ea   │
  │                                     ─────────────── │
  │                            B&H subtotal   $59.97     │
  │                                     + tax            │
  │                                                      │
  │  (If restocked on Amazon, buy there instead —        │
  │   typically $13-17/each, saving ~$10-20 total)       │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │  PICK UP FROM FREE GEEK                              │
  │  3731 SE Division St, Portland, OR 97202             │
  │  https://www.freegeek.org/shop                       │
  │                                                      │
  │  1    USB keyboard (compact preferred)       ~$0-5   │
  │  1    USB mouse (optional)                   ~$0-5   │
  └──────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────

NOTES

  - The Pi 5 has a purchase limit of 2 per customer at
    Adafruit. This is not an issue for a single-kiosk
    build, but relevant if ordering spares or a second
    unit for Topology 2.

  - The KKSB stand houses both the Pi 5 and the 7"
    Touch Display 2 in a single integrated enclosure.
    The Pi mounts inside the back of the stand. No
    separate Pi case is needed.

  - The Volcora monitor requires TWO connections to
    the Pi: HDMI (for video) and USB (for touch input).
    Both cables are included with the monitor.

  - The 7" Touch Display 2 connects via DSI ribbon
    cable (included with the display), not HDMI. This
    leaves both HDMI ports on the Pi 5 available. One
    is used for the Volcora; the other is a spare.

  - Total wall outlets needed: 2 (Pi power supply +
    Volcora 12V adapter). Both plug into the surge
    protector. The 7" display is powered through the
    DSI connection from the Pi — no separate power.

────────────────────────────────────────────────────────────────────
