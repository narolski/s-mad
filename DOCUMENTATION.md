# Documentation standard for every experiment

Author's instruction, 11 Nov 2026: no research may exist only in an agent's memory. If the agent
stops this minute, a reader with no context must be able to understand what was done, check every
number, and continue the work.

## Where

`experiments/<folder of the experiment>/README.md`, beside `prereg.md` and `result.md`.
`result.md` stays the short verdict; the README is the full record. Code lives in `src/<ID>/`, large
outputs under `/mnt/t7/smad_next/<ID>/`.

## Sections

Keep this order. Write "none" rather than dropping a section.

1. **Question and current answer.** Plain words, three to eight sentences, with the date and the
   status (running, finished, blocked on what).
2. **Timeline.** Dated steps in the order they happened: what was done, why, the command, what came
   out. Every amendment to the registration with its reason.
3. **Data.** Every input and every set produced: absolute path, number of items, how it was built
   (script and command), hash of lists and tars, where copies are (DGX, T7 drive, Athena, WCSS,
   rented machine). Which items were dropped and why.
4. **Code.** Every script in `src/<ID>/`: one line on its job, the run order, the arguments used.
   Environment: Python and package versions, model weights with source and hash. Seeds.
5. **Results.** Every number anyone might quote, with its interval, the number of items behind it and
   the file it comes from. Full tables, not only the headline.
6. **Checks.** How the code was verified (gates, equivalence checks, reproductions of published
   numbers) and, separately, what was not verified.
7. **Dead ends and failures.** Everything tried that did not work, bugs found and how they were
   fixed, failed or killed runs, statements that were withdrawn, each with its evidence. This is the
   part that is lost first, so it is the most important one.
8. **Observations and ideas.** Things noticed along the way that lie outside the question, with
   enough detail to follow up.
9. **Open items and next steps.**
10. **Handover state.** Running processes (host, process or job number, log path, expected end),
    queued tasks, files in progress, what to do if each fails. Compute spent (GPU-hours, USD).
11. **Reproduce from scratch.** The commands in order.

## Rules

- Write the README now for the work done so far, then keep it current: at every milestone, before
  every long wait, and at least once per hour of work. Add dated lines; do not rewrite history.
- Plain language. Experiments by plain name with the ID in brackets. Acronyms explained at first use.
  Absolute paths.
- Nothing that matters stays in `/tmp`, `/dev/shm`, a scratchpad or a chat message. Scripts go to
  `src/<ID>/`, outputs to `/mnt/t7/smad_next/<ID>/`, small tables (under 2 MB) to the experiment
  folder.
- What a helper agent (Sonnet, Haiku) did and found is recorded by the owner who started it.
- No secrets (keys, passwords, tokens) and no content of sealed sets.
- The lead commits and pushes. An owner says "README updated" with the path in its report.
