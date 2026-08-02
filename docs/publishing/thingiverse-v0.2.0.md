# Thingiverse listing — v0.2.0 update (knife blade block)

Paste-ready copy for adding the knife blade block to the existing Thingiverse listing (not a new
Thing — the same one the v0.1.0 set went up on). Everything between the `---` rules in each section
below is intended to be pasted as-is. UAT (first physical print) passed — ready to publish.

## Listing metadata

- **Title:** unchanged — the block is a natural extension of the existing "drawer bins" listing, not
  a separate thing.
- **License (Thingiverse dropdown):** unchanged — Creative Commons - Attribution - Share Alike.
- **Tags to add:** `knife_block`, `knife_storage`, `knife_rack`
- **Images to add:** the render below, plus (once printed) a photo of two knives loaded
  head-to-toe in the block — that's the shot that actually explains it at a glance.

## Description — new section to append

Add this as a new subsection, right after "### The bins":

---

### Knife blade block

A different way to store kitchen knives: instead of a knife-block-in-a-drawer that holds knives by
the handle (wasting most of a drawer's depth on blade you can't use for anything else), this holds
them by the *blade*. Knives lie flat, edge-down, alternating head-to-toe so each one's handle lands
at the opposite end from its neighbour's — that's what lets them sit closer together than their
handles alone would allow. Every blade passes through the same small block, each in its own
self-centring tapered slot that grips spines from 2–3 mm without rattling and keeps the cutting edge
floating clear of the plastic.

**The block is the only part you need.** It drops into a standard Gridfinity baseplate like any
other bin, and it does all the holding on its own: each slot grips its blade along the full length of
the block, so the knife is carried by the blade alone. The handle hangs clear at one end, and the run
of blade projecting from the other end counterbalances it. Nothing sits under the handles.

Sized by default for seven similarly-lengthed kitchen knives (handles up to 26 mm wide, 2–3 mm
spines) on a 3×2 Gridfinity footprint (125.5 × 83.5 mm) — it prints flat in one piece, no splitting
needed. If your knives differ, the generator's `--knife-count`, `--handle-width-mm`, and
`--handle-gap-mm` flags retune the whole layout.

**Blades that taper to a point may need a hand.** A straight blade of even depth — a bread knife, a
flat carving knife — is gripped along the block's whole length and sits rock steady. A blade that
tapers towards its tip only engages the slot over a short run, because it drops away from the grip as
it narrows. With less of the blade held and a heavy handle out on one end, the knife can tip. The fix
is a small riser under that handle. The right height depends on the individual knife, so shim the
handle with folded card until it sits still, measure, and print to suit. Two of mine wanted 40 mm:

```text
uv run python main.py --grid-x 1 --grid-y 2 --height-mm 40 --no-cutouts
```

Same generator, no new geometry — which is rather the point of a parametric tool.

---

### Version — replace with

---

This is a **0.2.0 beta** — adds the knife blade block above to the original four-bin set. Feedback
on fit (especially whether the slot grips your own knives without rattling) is very welcome.
Generated files (STL and 3MF) are also attached to the
[GitHub release](https://github.com/Bear-Prince/count-spatula/releases).

---

## Instructions (steps) — new step to append

Add this as **Step 5**, after the existing four:

---

### Step 5 — Add a knife blade block

Measured my own kitchen knives (handle width, blade spine thickness) and prototyped a tapered
self-centring slot in a notebook before writing any real geometry — the same "prove it in isolation
first" approach that had already paid off for the cutout profile. The result holds knives by the
blade instead of the handle, so a full set fits in far less drawer depth than a traditional block.

---

## Files to upload

From the GitHub Release (or `build/release/` locally):

| File | Model |
| --- | --- |
| `knife_block_7knives_3x2.stl` / `.3mf` | Knife blade block, 7 lanes, 3×2 Gridfinity |

## Print settings (Thingiverse fields)

Same as the existing set — no supports, no raft, 0.2 mm layers, PLA or PETG. The block is small and
prints flat in one piece.

## GitHub release notes (v0.2.0)

---

Adds the knife blade block: a Gridfinity module that stores kitchen knives by their blades instead
of their handles, alternating head-to-toe through a single block of tapered self-centring slots
(STL + 3MF attached). Drops into a standard baseplate and carries each knife by the blade alone, so
the block is the only part needed. Default sized for seven similarly-lengthed knives (2–3 mm spines,
handles up to 26 mm); override with `--knife-count`, `--handle-width-mm`, `--handle-gap-mm` for a
different set.

Models are CC BY-SA 4.0; the generator code is Apache 2.0. See `CREDITS.md` for lineage.

---
