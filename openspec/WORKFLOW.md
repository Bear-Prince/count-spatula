# OpenSpec workflow recipes

Practical, use-case-driven notes for working with OpenSpec in this repository. The upstream documentation explains
why OpenSpec exists but is thin on "what do I actually do when X happens", so this file grinds out the common
situations - especially the awkward ones, like correcting work that turned out wrong.

## Mental model

OpenSpec has two layers, and keeping them straight resolves most confusion.

- `openspec/specs/` is the **living truth**: what the system does right now. One folder per capability, each with a
  `spec.md` of requirements and scenarios. You never edit these by hand.
- `openspec/changes/<name>/` is a **proposal to change that truth**. It is disposable and ephemeral.

The unit you iterate on is the **change**, not the spec. The spec is permanent and continuously evolving; a change
is one increment against it. The closest analogy is Git:

```text
  specs/   = the working tree's current, authoritative state
  change   = a commit proposing an edit
  archive  = applying that commit to the spec

  spec ──change──► archive ──► spec' ──change──► archive ──► spec'' ──► ...
                     │                             │
                     └─ you never reopen a commit; you add another one
```

You do not reopen an archived change for the same reason you do not amend a commit that already shipped. You raise a
new change. Archiving is one-way and terminal.

## What a delta is

A **delta** is the structured, machine-readable diff a change makes to the specs. It lives in the change at
`changes/<name>/specs/<capability>/spec.md` and uses one of four operations as a heading:

- `## ADDED Requirements` - new requirements.
- `## MODIFIED Requirements` - changed behaviour. You must paste the **entire** updated requirement, not just the
  edited line, so the merge is unambiguous.
- `## REMOVED Requirements` - deprecated behaviour. Requires a **Reason** and a **Migration** note.
- `## RENAMED Requirements` - name changes only, using `FROM:` / `TO:`.

Every requirement needs at least one `#### Scenario:` block. When a change is archived, OpenSpec applies its deltas
to `openspec/specs/` - that is how a proposal's spec edits become the new living truth.

The `proposal.md` narrative is **not** a delta. Editing the proposal is refining a draft; a delta is a concrete edit
to the published spec. Nothing is locked until archive.

## The core idea: iterate by streaming changes

There is no "reopen", "amend", or "issue" object. Every correction, fix, or follow-up is simply **another change**
against the current spec. The spec accumulates; the changes come and go.

## Recipes

| Situation | What to do |
| --- | --- |
| Found a bug in shipped behaviour ("raise an issue") | Raise a new change with a `MODIFIED` delta (fix the requirement) or an `ADDED` delta (add a regression guarantee). |
| Built something complete but conceptually wrong, not yet archived | Abandon the change (delete `changes/<name>/`), do not merge the branch, and carry the learning forward into the superseding change's proposal. |
| Shipped something, then realised it was wrong | Raise a new change with a `REMOVED` or `MODIFIED` delta. The original stays in `archive/` as honest history. |
| Learned something mid-flight that changes scope | Edit the in-flight change's artifacts directly. Nothing is locked before archive. |
| Want to note work you have not designed yet | Keep a proposal-only change as a backlog stub. Accept that it will not pass strict validation until it has deltas. |

## Fixing a bug in shipped behaviour

This is the answer to "where does raise-an-issue go". A bug fix is a new change, not a reopen. Its delta is usually
a `MODIFIED` requirement (the behaviour was specified, and the spec was right but the code was wrong, or the spec
itself was wrong) or an `ADDED` requirement (you are adding a guarantee, such as a regression scenario). Implement,
then archive so the delta folds into the living spec.

## Abandoning a change that turned out wrong (pre-archive)

If a change is implemented and even passing tests but the concept is wrong, do not ship it just because it is
"complete". Delete the change directory, leave the branch unmerged, and **transcribe the rationale forward** into the
proposal of whatever supersedes it (a `## Background` or "Supersedes" section). You do not lose the learning, because
you wrote it down; the abandoned branch also remains in Git history if you need it.

## Walking back behaviour already shipped (post-archive)

Deprecation is first-class in the delta vocabulary. Raise a new change whose delta `## REMOVED Requirements` names
the requirement to retire, with a **Reason** and a **Migration**. The corrective change's tasks remove or rework the
code. The original change is untouched in `archive/`; the history honestly shows "we did this, then we knew better".

## Changing scope mid-flight

Before archive, an in-flight change is fully editable - rewrite the proposal, adjust the design, rework the deltas.
The only friction is renaming a change for clarity (see conventions below).

## Keeping a backlog item

A "tracked problem I have not designed yet" can only be a proposal-only change. That is fine, but be aware
`openspec validate` will report it as invalid ("no deltas found") until you write its specs. Use `openspec status`
to see real progress (for example, `1/4 artifacts`); `validate` measures completeness, not intent.

## Conventions for this repo

- **Supersede in prose.** OpenSpec does not model relationships between changes, so when change B replaces change A,
  say so explicitly in B's proposal and mark A as superseded.
- **Transcribe learnings forward.** When you abandon or supersede, copy the "why" into the replacement. The tool will
  not preserve it for you.
- **Keep changes small.** Small changes are cheap to abandon, which is what makes course-correction painless.
- **Generate the UAT models before archiving.** Geometry output can't be fully judged by the test suite, so each
  change's verification/UAT task group must regenerate the affected bins (the `UAT.md` cases) to `build/` for
  slicer review. Order this step *before* the archive step (and before any push/PR), so the bins are eyeballed
  while the change is still active. If the change affects geometry or the example model set, also regenerate the
  README renders (`uv run python render_models.py`) and eyeball them in the same UAT step, since committed images
  go stale silently otherwise.
- **Renaming a change is manual.** The change name, its directory, and the branch are coupled only by convention.
  To rename: `git mv openspec/changes/<old> openspec/changes/<new>`, update any cross-references inside the
  artifacts, and rename the branch to match. There is no CLI command for this.

## Known rough edges (as of writing)

These are limitations of the tooling, not of your understanding. Worth knowing so they do not surprise you.

- **No issue, draft, or spike primitive.** `openspec new` only creates a `change`. Backlog items are proposal-only
  changes that fail strict validation.
- **Archive is one-way.** There is no reopen or un-archive. Even a one-line correction is a whole new change.
- **No modeled change-to-change relationships.** Supersedes, replaces, and depends-on are prose, not data. You
  cannot query "what replaced X".
- **Name coupling is manual.** Change directory, branch name, and cross-references drift unless you keep them aligned
  by hand.
- **Validation is binary.** A change is either complete or not; there is no "intentionally a stub" state that
  suppresses the delta requirement.
