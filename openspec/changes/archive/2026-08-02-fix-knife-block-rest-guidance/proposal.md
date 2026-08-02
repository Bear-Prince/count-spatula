## Why

The `knife-blade-block` spec describes how the block supports a knife, and it describes it wrongly.
The error was found by physical UAT: the first printed block worked, but not for the reason the spec
gives.

Two related claims are false:

1. That `deck_height_mm` is a matching interface for a user-supplied blank, so a blank of that height
   "keeps the knives resting level". A blade seats **below** the block's top face, by 5.14 mm for a
   3 mm spine down to 8.57 mm for a 2 mm one. A blank at the block's own height would therefore sit
   proud of where the blade sits and take the knife's weight before the blade reached its slot,
   lifting it back out. Nothing goes under the handles at all.
2. That the block "locates the blades laterally while the knives rest along their length". The knives
   do not rest along their length. The slot grips the blade along the full length of the block and the
   knife cantilevers, counterbalanced by the run of blade projecting past the far end.

The second claim also obscures the real reason a knife may need help: a blade that tapers to a point
drops away from the slot as it narrows, so only a short run of it is gripped. Combined with a heavy
handle on the lever arm, that is what tips a knife - not handle weight alone. Straight, even-depth
blades are held along the whole length and sit steady, which is why most of a set needs nothing.

Anyone reading the spec or the README today would build the wrong thing.

## What Changes

- Correct the two requirements that misdescribe how a knife is supported, and rename the scenario that
  asserts the false blank-matching interface.
- Correct the same claim in `README.md` and in the `deck_height_mm` docstring.
- `deck_height_mm` keeps its name and its arithmetic. It is a correct value for the block's top face;
  only its documented *purpose* was wrong.

## Capabilities

### Modified Capabilities

- `knife-blade-block`: two requirements change. "Knife blade block holds knives by the blade" is
  corrected to describe a cantilever rather than knives resting along their length. "Generate only the
  block; compose handle zones with blanks" drops the blank-matching interface, and its scenario "Deck
  height is exposed for blank matching" is replaced by one that states what the value actually is.

## Impact

- **No code or geometry change.** `deck_height_mm` returns the right number and its test asserts the
  right thing; both stand.
- **`tests/test_knife_block.py`** - one `@pytest.mark.scenario` marker renamed to follow the scenario,
  as the traceability guard requires. The assertion is unchanged.
- **`README.md`**, **`knife_block.py`** docstring - prose only.
- No change to models, so no regeneration and nothing to re-upload.
