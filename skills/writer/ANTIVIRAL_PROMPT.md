# Anti-Viral Prompt Extension

Append to any story-generation prompt in the writer pipeline (pitch-round, writers-room, snowflake, survival tests, visual pitch round).

## Why this exists

Claude/Sonnet's pre-training produces a structural bias toward institutional, procedural, prestige-somber storytelling — the four viruses catalogued in the Snowflake 2126 scorecard:

1. **Paperwork porn** — bureaucratic process as the dramatic engine
2. **Villain vacuum** — no named on-camera human antagonist
3. **Passive endings** — stories that end on filings, realizations, implications
4. **Interior action** — rooms, terminals, committees in place of bodies moving in space

Two treatments were tested. Swapping persona `influences:` from prestige references (Lumet, Gilroy, Pinter, le Carré) to action/physical references (Cuaron, Bigelow, Miller, Carpenter) moved scores −21 on average but left rigid-mechanism personas in Terminal band. Appending a negative blocklist — banned words plus banned structural patterns — moved scores −64 on average and cleared three of five Terminal-scoring personas into Mild/Clean.

Finding: **the virus lives in Sonnet's default vocabulary and structural habits, not in its influences.** The blocklist works because it removes the escape route back to institutional patterns, forcing a different dramatic structure to surface.

Validated 2026-04-18 on 5 Terminal personas (Roza Vidal, Sola Jin, Nils Halden, Luthor Reed, Ezra Bloom). Cohort means: 102.8 (Terminal) → 39.0 (Mild). Full test: `projects/260417-snowflake-2126/INFLUENCE_TEST/`.

---

## BANNED WORDS

Do not use these words in any story output. Find a different way or cut the concept entirely.

1. compliance
2. audit / auditor
3. ledger
4. tribunal
5. mandate
6. protocol
7. registry
8. bureau
9. filing / filed
10. memo
11. accord
12. charter
13. adjudicate
14. arbitrator
15. certification
16. oversight
17. directive
18. administrative
19. procedural
20. disclosure

## BANNED TONE WORDS

The prestige-somber register is sticky even after institutional vocabulary is gone. These register signals keep stories locked at B5 (Prestige-Somber Tone) even when every other virus signal has cleared. Cut them.

1. austere
2. measured
3. methodical
4. solemn
5. restrained (as tonal self-description)
6. melancholic
7. elegiac
8. contemplative
9. meditative
10. hushed
11. clinical
12. detached
13. spare (as tonal descriptor)
14. grave (as tonal descriptor)
15. "quiet competence" / "quiet authority" / "quiet dignity"

## BANNED CONCEPTS

These patterns are structural failures. If your story contains any of them, rewrite until it doesn't.

1. A protagonist whose job title is officer, analyst, auditor, compliance, mediator, archivist, facilitator, or counselor
2. An ending where the climactic action is submitting, filing, transmitting, or publishing a document
3. Drama conducted through meetings, hearings, committee sessions, or depositions
4. An antagonist that is "the system" without a named human who chose to do harm
5. Characters who process, review, or discover information while seated at a desk or terminal
6. A story set entirely inside one institutional building, station, or facility
7. A protagonist who investigates by reading files instead of going to a dangerous place
8. A "realization" ending where understanding replaces action
9. Professional competence as the protagonist's primary identity
10. A moral framework where all sides are equally valid and no one is clearly wrong
11. Institutional reform, policy change, or systemic correction as the climax
12. Characters introduced by institutional title before name, want, or body
13. Scenes where characters discuss what to do instead of doing it
14. A whistleblower who exposes through documents rather than confrontation
15. Clock pressure that is a paperwork deadline rather than physical danger to a body
16. All conflict resolved through speech acts — testimony, declaration, ruling, or verdict
17. Settings limited to offices, clinics, labs, tribunals, hearing rooms, or control rooms with no exterior action
18. "Protagonist discovers the system is flawed" as the central arc
19. An ending that is ambiguous, circular, continuation-based, or "the work goes on"
20. Grief, loss, or trauma processed through institutional frameworks instead of human contact, physical action, or direct confrontation

## BANNED TONE MOVES

Sentence-level register habits that reproduce prestige-somber tone even when the plot is physical. Remove them.

1. The single-line declarative ending that summarises the story's moral ("The rule holds. The consequence is irreversible. The world does not apologize.")
2. Fragment sentences deployed to signal gravity ("She knew. She had always known.")
3. Character introduced by adjective stack describing their inner register ("Measured. Illegible. Fluent in both registers.")
4. The final image held as atmosphere in place of action ("The camera does not show her hand on the screen.")
5. Weight-words sprinkled into every sentence ("the weight of," "the cost of," "what it took," "what remains")
6. Silence or stillness used as the climactic rhythm (a climax resolves through movement and decision, not a held beat)
7. Description of a character's precision, discipline, or control substituted for description of their want
8. Implication-endings that conclude on what the audience is meant to feel rather than what they are meant to see

---

## How to apply

- All four lists are hard constraints, not guidelines. The pitch, synopsis, or outline must be readable with zero matches.
- If a banned word or concept is genuinely load-bearing for the persona's mechanism (e.g., an absurdist comedy about a tribunal), name the mechanism explicitly and request override. Override must be documented, not silent.
- The blocklist is appended AFTER the persona lens and AFTER the brief. It is the last thing the model reads before writing.
- The blocklist does not override a persona's legitimate artistic commitments — a genuinely kinetic persona cannot be made more kinetic by removing words. It targets the drift that happens when a flexible persona is written by a model with a virus habit.

## Known limitations

- B5 (tone lock) is the stickiest virus signal. Even successful antiviral runs retained ~5/10 on B5 while moving all other signals to 1-3/10. The tone-word and tone-move lists above are the v2 addition aimed at this specific residue.
- Personas whose mechanism is itself institutional (arbitration, partition mediation, compliance) will lose the institutional frame under the blocklist. This is by design — the blocklist tests whether the underlying mechanism can produce physical-world drama. If it cannot, the persona's mechanism is diagnosed as virus-captured at the YAML level.
- The blocklist does NOT prevent a writer from telling a story about power, institutions, or systemic harm. It prevents the story from being TOLD through the grammar of institutions. A story about a water treaty can be a story about two people trying to kill each other over water — the treaty is backstory, the bodies are the story.
