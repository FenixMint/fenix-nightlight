# AGENTS.md — Fenix Night Light execution guardrails

## Mandatory repository bootstrap

Before substantive work:

1. Read this `AGENTS.md`.
2. Read `README.md`.
3. Read the project documentation relevant to the requested task.
4. Inspect the active branch, current HEAD, recent commits and working-tree state.
5. Do not reconstruct current project state from chat memory when the repository
   contains newer durable information.

## Mandatory session reporting

Every work conversation for this repository must follow:

`docs/development/SESSION-REPORTING-PROTOCOL-2026-10-08.md`

The OWNER signals the phase explicitly:

- `RAPORT START` -> create the durable opening report before substantive work,
  commit it, push the authorized branch and verify local/remote SHA.
- `RAPORT STOP` -> complete the session report, update the daily report,
  commit, push and verify before handoff/closure.

No conversation may silently omit an OWNER-requested START or STOP report.

Session reports are durable GitHub handoff state. They do not replace project
architecture, checkpoints, roadmaps or task documents.

## Privacy and data minimization

Do not persist workstation-identifying, person-identifying, secret or private
runtime details in tracked reports or documentation unless an existing
technical contract strictly requires them.

Do not record hostnames, local usernames, personal email addresses, secrets,
tokens, account identifiers, serial/MAC/IP/machine IDs, or absolute home paths
that reveal a local account name.

Prefer role labels such as COSMIC / OFFICE / DELL / WORK and paths such as
`~/...`.

## Git safety

Do not use `git add .`. Stage intended files explicitly.

Run `git diff --check` before commit.

Do not use reset, clean, force-push or destructive history changes without
explicit OWNER approval.

Do not claim a push succeeded until local and remote SHA are verified.

## Status discipline

Do not claim work, tests, acceptance, external writes or delivery happened
unless they actually happened.

OWNER decisions must be recorded durably when losing them would force a later
conversation to rediscover or guess them.
