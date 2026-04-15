# Implementation Instructions

Use this document as the operating guide for implementing the ShelfDB refactor plan.

## Source Of Truth

- strategy and target design: `worklog/plan.md`
- ordered implementation tasks: `worklog/action.md`
- running notes and progress log: `worklog/progress.md`

`worklog/plan.md` defines **what** we want.

`worklog/action.md` defines **how to execute it step by step**.

`worklog/progress.md` records **what actually happened** while implementing.

## Main Rule

Implement `worklog/plan.md` by following `worklog/action.md` in order.

If `worklog/action.md` needs to be adjusted for a safer or clearer implementation path, update it as needed, but keep it aligned with `worklog/plan.md`.

Do not skip ahead unless:

- the current task is blocked,
- the task list is clearly wrong,
- or a smaller safer step is needed to keep tests passing.

If the order changes, record the reason in `worklog/progress.md` and update `worklog/action.md`.

## Task Execution Workflow

For each task:

1. read the target intent in `worklog/plan.md`
2. find the next unfinished task in `worklog/action.md`
3. make only the smallest change needed for that task
4. preserve public imports and add compatibility wrappers when needed
5. run relevant tests/checks before declaring the task done
6. update `worklog/action.md`
7. update `worklog/progress.md`
8. report the result clearly

## Required Constraints

- keep the refactor incremental
- keep the repository in a test-passing state after each task
- prefer copy/re-export/shim first, then migrate imports, then clean up later
- avoid large rename-only changes that mix many concerns at once
- preserve public import paths unless an explicit decision is recorded

## How To Use `worklog/action.md`

- treat it as the implementation checklist
- keep tasks ordered
- mark progress as tasks start and finish
- if a task is too large, split it into smaller test-safe tasks
- if a new dependency between tasks is discovered, update the file

## How To Use `worklog/progress.md`

Use it as the current progress snapshot and working notebook, not as a long historical log. Keep entries focused on the current state, blockers, and next steps.

Use it as both:

- a progress log for the user
- a short working notebook for implementation notes

Each entry should include:

- task id and title
- status: `in_progress`, `done`, or `blocked`
- what changed
- tests/checks run and result
- compatibility notes
- risk, blocker, or next-step notes

It is okay to add short notes such as:

- observations about module boundaries
- why a compatibility shim was added
- why a task was split or reordered
- reminders for the next task

## Reporting Back

When reporting progress, put the most important information first:

1. whether tests passed
2. what changed
3. what compatibility layer was added or removed
4. any design decision that affects later tasks
5. any blocker, risk, or question that needs attention

## Decision Rules During Refactor

If unsure where code belongs, use `worklog/plan.md` package rules:

- shared wire contract -> `protocol/`
- client behavior -> `client/`
- server behavior -> `server/`
- core domain logic -> `shelf/`
- persistence/backend detail -> `shelf/storage/`
- truly generic helper -> `util/`

If one file mixes multiple roles, split it instead of forcing it into one place.

## Definition Of Done For Each Task

A task is done only when:

- the code change is complete
- tests/checks for that task pass
- `worklog/action.md` is updated
- `worklog/progress.md` is updated
- important notes are recorded for later steps

## Final Goal

Reach the target structure described in `worklog/plan.md` through a sequence of small, safe, test-passing tasks tracked in `worklog/action.md` and documented in `worklog/progress.md`.
