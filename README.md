# CAMPUSCART

## Overview

CampusCart is a CLI solution for campus vendors to streamline stock tracking, cart totals and receipt generation.

## Problem Statement

- **Manual Inventory problems:**
  Campus vendors use paper logs to track inventory. This leads to frequent stockouts, lost sales, and untracked waist during busy class breaks.
- **Slow Checkout Lines:**
  Calculating totals and tax manually during rush hours creates long queues. Students leave without purchasing due to wait times.

- **Lack of Sales Analytics:**
  Vendors cannot easily identify their best-selling items or daily revenue.

- **Receipt Tracking Friction:**
  Students lose paper receipts easily. Vendors have no digital archive to verify past transactions for returns or disputes.

## Target Audience

- **Student Entrepreneurs:**
  Campus residents running dorm-based snack shops, clothing thrifts, or printing services.

- **On-Campus Kiosk Operators:**
  Small-scale external vendors managing coffee carts, juice bars, or stationary stands.

- **Club and Society Treasurers:**
  Student leaders managing merchandise sales, ticket distributions, and bake sales for campus events.

## Key Value Proposition

CampusCart is a lightweight, fast CLI tool that removes checkout friction for campus vendors. It turns complex stock tracking and receipt generation into simple, keyboard-driven commands, allowing vendors to serve students faster without expensive POS hardware.

## ASCII CLI MOCKUP

```
  ╔══════════════════════════════════════════════════════════════╗
  ║                     C A M P U S C A R T                        ║
  ║              Campus Vendor Stock & Sales CLI                   ║
  ╚══════════════════════════════════════════════════════════════╝

  $ campuscart

  ┌─ Main Menu ─────────────────────────────────────────────────┐
  │                                                                │
  │   [1] Inventory      Manage & track stock                    │
  │   [2] New Sale        Start a checkout / cart                │
  │   [3] Receipts        View / search past transactions        │
  │   [4] Analytics       Best sellers & daily revenue            │
  │   [5] Settings        Vendor profile, tax rate, etc.          │
  │   [0] Exit                                                     │
  │                                                                │
  └────────────────────────────────────────────────────────────┘
  > _


  ──────────────────────────────────────────────────────────────
  $ campuscart inventory list
  ──────────────────────────────────────────────────────────────
  SKU     ITEM                QTY   LOW STOCK   PRICE
  ------------------------------------------------------------
  001     Instant Noodles      42       -        ₦350
  002     Bottled Water        6      ⚠ YES       ₦150
  003     Notebook (A5)        18       -        ₦500
  004     Phone Charger Cable  3      ⚠ YES       ₦1,200

  4 items | 2 low stock warnings
  [a]dd  [e]dit  [d]elete  [r]estock  [q]uit
  > _


  ──────────────────────────────────────────────────────────────
  $ campuscart sale new
  ──────────────────────────────────────────────────────────────
  NEW CART                                    Vendor: Ada's Snacks

  Scan/enter SKU or search item name:
  > 001

  ┌────────────────────────────────────────────┐
  │ 1x  Instant Noodles          ₦350           │
  │ 2x  Bottled Water            ₦300           │
  ├────────────────────────────────────────────┤
  │ Subtotal                     ₦650           │
  │ Tax (7.5%)                   ₦48.75         │
  │ TOTAL                        ₦698.75        │
  └────────────────────────────────────────────┘

  [c]heckout  [+]add item  [-]remove  [x]cancel
  > c

  ✔ Payment received — Cash
  ✔ Receipt #R-0231 generated
  ✔ Stock updated automatically


  ──────────────────────────────────────────────────────────────
  $ campuscart analytics today
  ──────────────────────────────────────────────────────────────
  DAILY SUMMARY — Fri, Aug 21

  Revenue:        ₦18,450
  Transactions:   27
  Avg. Sale:      ₦683

  Top Sellers:
    1. Bottled Water     ▓▓▓▓▓▓▓▓▓▓▓▓ 34 sold
    2. Instant Noodles   ▓▓▓▓▓▓▓▓     22 sold
    3. Notebook (A5)     ▓▓▓         9 sold

  ⚠ 2 items below low-stock threshold — run `inventory list`
```

## Proposed Menu Navigation

```
┌──────────────────────────────────────────────────────────────┐
│                         MAIN MENU                              │
│                                                                  │
│   campuscart> _                                                │
│                                                                  │
│   ╔══════════════════════════════════════════╗                │
│   ║   C A M P U S C A R T   v1.0              ║                │
│   ║   Campus Vendor Stock & Sales CLI          ║                │
│   ╚══════════════════════════════════════════╝                │
│                                                                  │
│   [1] Inventory                                                │
│   [2] New Sale                                                 │
│   [3] Receipts                                                 │
│   [4] Analytics                                                │
│   [5] Settings                                                 │
│   [0] Exit                                                     │
│                                                                  │
│   Select option: _                                             │
└───────────────┬──────────────────────────────────────────────┘
                │
   ┌────────────┼────────────┬────────────┬────────────┐
   │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌─────────┐
│  [1]   │ │  [2]    │ │  [3]     │ │  [4]      │ │  [5]    │
│INVENTORY│ │NEW SALE │ │RECEIPTS  │ │ANALYTICS  │ │SETTINGS │
└───┬────┘ └────┬────┘ └────┬─────┘ └─────┬─────┘ └────┬────┘
    │           │            │             │            │
    ▼           ▼            ▼             ▼            ▼

┌─────────────────────────┐   ┌─────────────────────────┐
│ INVENTORY SUB-MENU       │   │ NEW SALE SUB-MENU        │
│                           │   │                           │
│ [a] Add item              │   │ [s] Search / scan item    │
│ [e] Edit item              │   │ [+] Add to cart            │
│ [d] Delete item             │   │ [-] Remove from cart         │
│ [r] Restock item              │   │ [v] View cart                 │
│ [l] List all / filter          │   │ [c] Checkout                    │
│ [b] Back to Main Menu             │   │ [x] Cancel sale                    │
│                                         │   │ [b] Back to Main Menu                 │
│ Select option: _                          │   │                                         │
└─────────────────────────┘   │ Select option: _                          │
                               └─────────────────────────┘

┌─────────────────────────┐   ┌─────────────────────────┐
│ RECEIPTS SUB-MENU         │   │ ANALYTICS SUB-MENU        │
│                           │   │                           │
│ [v] View all receipts      │   │ [t] Today's summary        │
│ [f] Filter by date          │   │ [w] Weekly summary          │
│ [s] Search by ID / item      │   │ [m] Monthly summary          │
│ [p] Print / export            │   │ [b] Best sellers                │
│ [b] Back to Main Menu           │   │ [r] Revenue trend                 │
│                                    │   │ [b] Back to Main Menu               │
│ Select option: _                    │   │                                       │
└─────────────────────────┘   │ Select option: _                        │
                               └─────────────────────────┘

┌─────────────────────────┐
│ SETTINGS SUB-MENU         │
│                           │
│ [p] Vendor profile          │
│ [t] Tax rate                  │
│ [c] Currency                    │
│ [b] Back to Main Menu             │
│                                     │
│ Select option: _                     │
└─────────────────────────┘
```
