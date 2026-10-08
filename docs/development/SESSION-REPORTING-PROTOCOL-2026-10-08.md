# SESSION START / STOP / DAILY REPORTING PROTOCOL

Date: 2026-10-08

Status: ACTIVE / OWNER-MANDATED / MANDATORY FOR EVERY WORK CONVERSATION

## Owner decision

Every work conversation for this repository must use a durable opening/closing
reporting cycle.

The OWNER signals the phase explicitly:

- `RAPORT START` -> execute the opening report before substantive work.
- `RAPORT STOP` -> execute the closing report before ending or handing off work.

The reporting system is repository governance. It is not optional chat etiquette
and must not depend on one workstation or one conversation's memory.

GitHub is the durable shared handoff source.

## Goals

The reporting cycle must make it possible for another conversation or instance
to determine from GitHub alone:

- where work started,
- what repository state was used,
- what the authorized scope was,
- what was changed,
- what tests actually ran,
- what was committed and pushed,
- what external writes occurred or did not occur,
- what long-running operations must be preserved,
- what remains unresolved,
- what exact next step should be taken.

## Durable report locations

Use role-based labels only. Do not persist workstation-identifying details.

Session reports:

```text
docs/reports/sessions/YYYY-MM-DD/YYYYMMDD-HHMM-ROLE.md
```

Role examples:

```text
COSMIC
OFFICE
DELL
WORK
```

Daily report:

```text
docs/reports/daily/YYYY-MM-DD.md
```

A session file contains both START and STOP sections. The START section is
created and delivered to GitHub at `RAPORT START`. The same session file is
completed at `RAPORT STOP`.

The daily report is cumulative for the calendar day and is updated at every
STOP from the durable session reports for that day. If more than one session or
instance is active, refresh remote state before updating the daily report and
never blindly overwrite another session's report.

## RAPORT START — mandatory content

Before substantive work, record:

1. date/time and role label,
2. active branch,
3. local HEAD and remote branch HEAD,
4. clean/dirty working-tree state and intended local changes,
5. OWNER-authorized task/scope for this conversation,
6. mandatory project/governance documents actually read,
7. relevant current checkpoint / roadmap / work order when the repository uses them,
8. active long-running processes or protected work that must not be disturbed,
9. local/runtime data boundary for the session,
10. external/provider-write authority: NO/YES and exact scope,
11. local working-artifact location policy,
12. known blockers/open decisions,
13. planned next steps.

A START report must distinguish facts actually verified from assumptions.

After creating the START report:

- stage only the report file explicitly,
- run `git diff --check`,
- commit it,
- push the authorized branch,
- verify local and remote SHA.

The conversation must not claim the START report is durable until push and
remote verification succeeded.

## RAPORT STOP — mandatory content

Before ending or handing off the conversation, update the same session report
with:

1. end date/time and role,
2. work actually completed,
3. files changed,
4. architectural/product decisions made by OWNER,
5. tests/acceptance actually run and their results,
6. commits created,
7. push status with verified local and remote SHA,
8. local/runtime data reads and writes actually performed,
9. provider/API/external writes actually performed,
10. local artifacts created and their role-relative/home-relative locations,
11. active long-running operations intentionally left running,
12. blockers/unresolved questions,
13. exact next safe step,
14. final working-tree status.

Never report a test, push, acceptance, external write or data write as completed
unless it actually happened.

After completing STOP:

- update the daily report,
- stage only the intended report files,
- run `git diff --check`,
- commit,
- push,
- verify local and remote SHA.

The conversation is not considered durably closed until the STOP report and
daily report are on GitHub, unless a blocker makes delivery impossible. If
delivery is blocked, report the blocker explicitly and leave exact recovery
steps.

## DAILY REPORT — mandatory content

`docs/reports/daily/YYYY-MM-DD.md` is the cross-session summary for the day.

It must contain:

- date,
- sessions/roles opened and closed,
- branch/HEAD progression,
- work completed,
- tests and acceptance run,
- commits delivered,
- local/runtime data writes,
- provider/external writes,
- long-running operations still active,
- unresolved blockers and decisions,
- exact next work to resume.

The daily report is a summary/index, not a replacement for individual session
reports.

If a session has START but no STOP, mark it OPEN / INCOMPLETE rather than
inventing a closure.

## Privacy and repository hygiene

Reports must follow repository privacy and data-minimization rules.

Do not persist:

- hostname/machine name,
- local username,
- personal email,
- serial/MAC/IP/machine IDs,
- secrets/tokens,
- provider account identifiers,
- private customer identifiers,
- absolute home paths containing a username.

Use role labels such as COSMIC / OFFICE / DELL / WORK and home-relative paths
such as `~/...`.

Runtime databases, credentials, tokens, raw user data and temporary audits do
not become source code merely because a report refers to them.

## Multi-instance safety

Before START and before STOP delivery:

1. inspect current branch state,
2. fetch/refresh the remote branch,
3. do not destroy local work,
4. reconcile remote report changes before writing a shared daily report,
5. never use reset/clean/force-push to make reporting convenient.

If another instance advanced the branch, integrate safely according to the
repository's Git governance. Do not overwrite its report.

## Relationship to checkpoints and project documentation

START/STOP reports do not replace architecture documents, checkpoints, roadmaps
or task documents.

A durable architectural/product decision still belongs in the appropriate
project document.

Session reports answer: "what happened in this work conversation?"

Checkpoints answer: "what project state is accepted/important?"

## Short form

```text
OWNER: RAPORT START
    -> verify repository/GitHub state
    -> create START session report
    -> commit + push + verify
    -> work

OWNER: RAPORT STOP
    -> verify actual work/results
    -> complete STOP session report
    -> update DAILY report
    -> commit + push + verify
    -> handoff/close
```

No work conversation for this repository may silently omit an OWNER-requested
START or STOP report.
