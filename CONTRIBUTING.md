# Contributing

How work flows through this repository: the relationship between work sessions, OpenSpec changes, Git branches, and
pull requests. For the OpenSpec-internal mechanics — deltas, archiving, abandoning or superseding a change — see
[openspec/WORKFLOW.md](openspec/WORKFLOW.md).

## The four moving parts

| Concept | What it is | Lives until | Rough cardinality |
| --- | --- | --- | --- |
| Work session | A single working sitting (for example, one Claude chat). Where thinking and edits happen. | You stop working | Many-to-many with changes |
| OpenSpec change | One unit of spec evolution under `openspec/changes/<name>/`. | It is archived | One change is about one branch |
| Git branch | One line of development. | It is merged or deleted | One branch is one PR |
| Pull request | One reviewable unit landing on `main`. | It is merged | Usually one per change |

The trap is assuming all four line up one-to-one. Three of them nearly do — but the **session does not**.

## The session is a workspace, not a unit of work

A session is where work happens, not a thing that ships. Do not try to make session boundaries match change
boundaries. In practice:

- One session may touch several changes (explore one, fix another, write a doc).
- One change may span several sessions (you pause and resume days later).
- Planning may happen in one session and implementation in another.

The durable units are the change, the branch, and the PR. The session is disposable scaffolding around them.

## The default flow

For most work, the simple model is correct: **one change, one branch, several commits, one PR at the end.**

1. Create or pick the OpenSpec change under `openspec/changes/<name>/`.
2. Branch named after it: `feature/<name>`, `fix/<name>`, `docs/<name>`, and so on.
3. Commit as you go — proposal, design, and specs first, then implementation, ticking `tasks.md`.
4. Run UAT — build the real artifact and confirm behaviour.
5. Archive the change as the final step so the spec deltas fold into `openspec/specs/` on the same branch.
6. Open one PR. Review, then merge to `main`.

One change in, one PR out. This is the common case and the right default.

## The exception: a proposal-only PR

Sometimes a single change is best landed in **two** PRs — a planning PR first, then an implementation PR later:

- The planning PR contains only `proposal.md` (and maybe `design.md`). There is no code, so there is nothing to
  UAT; reviewers assess the *plan*, not behaviour.
- The implementation PR, later and usually on a fresh branch, contains the specs, tasks, code, and the archive.

Reach for the split when:

- The change is large or architectural and you want the design reviewed before sinking time into building it.
- You want concurrent contributors to see the plan on `main` now, so their work can account for it.
- You are capturing a backlog item you do not intend to build yet. A proposal-only change will fail
  `openspec validate` with "no deltas found" — that is expected; see [openspec/WORKFLOW.md](openspec/WORKFLOW.md).

If none of those apply, prefer the single all-in-one PR.

## UAT and archiving

- **UAT belongs to implementation PRs.** A proposal-only PR has no behaviour to test.
- **Archive on the implementation branch**, as the last step before or within the implementation PR, so that `main`
  always has `openspec/specs/` in sync with the code that satisfies it.

## Worked example

A single session might produce all of this:

```text
session (one chat)
├── change: add-foo       → branch feature/add-foo     → PR (plan + build + archive)
├── change: fix-bar       → branch fix/bar             → PR (build + archive)
└── doc: workflow notes   → branch docs/workflow-notes → PR (docs only)
```

Three changes, three branches, three PRs, one session. Conversely, `add-foo` might have been *proposed* in an
earlier session and only *implemented* in this one. The session is just where the keystrokes happened.

## Conventions

- Branch names: `feature/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>`, `chore/<slug>`.
- Keep each PR to one coherent change; do not bundle unrelated changes.
- Open a PR when branch work is complete; do not merge without review.
- Any PR containing AI-generated code must disclose the coding agent and model used.
