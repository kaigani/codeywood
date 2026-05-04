# The Prestige-Literary Centroid — Antiviral Brief

*Portable brief for any Claude Code writing session. Standalone — no project context required to use. Can be pasted into a fresh session as preamble or referenced via path.*

*Source research: Codeywood writers-room, pitch-round, snowflake, and Stray Signal v3 graduations (2026-04 through 2026-05). Existing tooling: `skills/writer/ANTIVIRAL_PROMPT.md` (40+ item blocklist, validated −64 on Snowflake 2126). This brief extends the existing tooling to address a failure mode the blocklist alone does not catch.*

---

## The Failure Mode

Claude has a strong centroid attractor for **prestige-literary protagonists** — characters whose job lets them *observe, record, decode, archive, restore, translate, or forecast* without acting. The model defaults to this archetype because its training data is over-weighted toward NYT-bestseller / MFA / awards-bait fiction where these protagonists dominate, and because they are HHH-safe (they don't act, so they don't break things).

**The named offenders:** archivist, librarian, cartographer, linguist, translator, decoder, watchmaker, conservator, restorer, curator, lighthouse keeper, radio operator, signal analyst, forensic scientist, medical examiner, court stenographer, transcriptionist, probate specialist, hospice worker, oncology nurse, end-of-life specialist, weather forecaster, demographer, compliance officer, records clerk, power-readings analyst.

**What unites them:** access to past-tense material (records, artifacts, texts, languages, signals) without present-tense agency. They produce contemplative interiority, deferred plot, and a melancholy that the model has internalized as "good writing." The centroid is sticky because the prose it produces *reads* well at the sentence level — sad, careful, observant — and the model is rewarded for that on first read.

---

## What the Existing Antiviral Catches (And What It Misses)

`skills/writer/ANTIVIRAL_PROMPT.md` BANNED CONCEPTS #1 already prohibits:

> *A protagonist whose job title is officer, analyst, auditor, compliance, mediator, archivist, facilitator, or counselor.*

This works for the **direct hit** — the model proposes "Mira, an archivist," the antiviral kicks in, the pitch is rewritten. Validated on Snowflake 2126 (cohort mean 102.8 → 39.0).

**What it misses: centroid migration to surrounding characters.** When the protagonist's job is forced kinetic by the blocklist, the centroid does not disappear — it migrates to the supporting cast. The protagonist becomes a courier, but the protagonist's *uncle* is a power-readings analyst. The antagonist becomes embodied, but she's a *Senior Cartographer* and her superior is the *Director of the Records and Cartography Bureau*. The love interest is a *translator*. The wise elder is a *linguist*. The whole world becomes Archivist Family with one non-archivist at the center.

This is **centroid laundering**. The antiviral catches the protagonist, the world remains prestige-coded, and the show is still doing the same thing under a different protagonist's name.

The other miss: **occupation-as-mechanism drift inside lore.** When the head writer drafts world history (Lore Forge, etc.), the antagonist's project is "the Reorganisation" — a regime that *renames things on maps* and *destroys records*. The conflict is still being conducted in the prestige register — it's just been promoted to historical scale. The kids are not fighting a mob, they're fighting a *cartographer*.

---

## Detection Heuristics

Apply these *to the whole cast and the central conflict*, not just the protagonist.

1. **The Job Census.** List every named character's job. If more than 30% of named characters have prestige-centroid occupations (records, mapping, language, signals, archives, restoration, decoding, forecasting), the centroid has migrated and the antiviral has been laundered.

2. **The Action Test.** Can each named character's job be the source of present-tense pressure on a body, or does it merely give them access to past-tense material? "Watches signals come in" fails. "Drives the truck that delivers the signal-jamming equipment" passes.

3. **The Body Test.** Does each named character have a body the show stages, or are they a voice / a desk / an interior register? Bodies that sweat, lift, run, sleep badly, get hurt, eat — pass. Bodies that "are precise" or "carry quiet authority" — fail.

4. **The Conflict-Register Test.** What is the central conflict's *register*? If the antagonist's project can be summarized as *renaming, redrawing, recording, redacting, destroying records, rewriting history* — the conflict has been promoted to the prestige register. The show may still be good, but it is not escaping the centroid; it has just laundered the centroid into world-historical material.

5. **The Replacement Heuristic.** Pick any named prestige-coded character and ask: what if their job required them to act, fail, get hurt, get fired? If the role *cannot* survive that pressure, the role is the centroid wearing a name.

---

## The Three-Level Fix

The antiviral only works if it's applied at every level the centroid migrates through. Currently `ANTIVIRAL_PROMPT.md` is appended at pitch-round and writers-room v3.2 Story Lock prompts. That covers the protagonist. It does not cover the world-building or the lore.

**Level 1 — Pitch / Brief:** existing antiviral works. Keep it.

**Level 2 — Story Lock (writers-room v3.2 antiviral + v3.6 Structural Stakes Checklist):** the Structural Stakes Checklist Lane B forces the embodied antagonist to be named with a concrete grievance — but does not currently constrain *occupation*. Add to Lane B: **"What is the antagonist's job, and does it pass the Action Test? If the antagonist's project is conducted through records / maps / archives / language, document a deliberate-YES choice with the show's compensating physical-action discipline."**

**Level 3 — Lore Forge (writers-room v3.5 Phase 3.5):** the lore document is currently unconstrained on occupational distribution. Add the **Job Census** as a required check before lore is locked: list every named character's occupation, count the prestige-centroid percentage, document any choice above 30% as deliberate.

**Level 4 — Surrounding-Cast Audit:** at Phase 4 review, run the Job Census across the full Character Shadows table. The AAA delivers a flag if the count is above 30%. This is the laundry-detection step — it catches centroid migration that the per-character checklists miss because they evaluate characters in isolation.

---

## The Blue-Collar Pivot

When a character's role fails any of the four tests, swap toward roles with bodies and present-tense pressure:

- **Movers:** courier, longshoreman, transit driver, EMT, delivery, evacuation crew, freight handler
- **Builders:** plumber, electrician, mason, scaffolder, demolition, scrap salvage, pipe-fitter
- **Feeders:** line cook, bartender, butcher, fishmonger, baker on night shift, school cafeteria
- **Carers (with hands):** daycare worker, dog walker, nurse on night ward (not "hospice specialist"), hairdresser, masseur
- **Watchers (with consequence):** night-shift security, parking enforcement, ferry deckhand, harbor pilot
- **Makers (with risk):** welder, glassblower, roofer, tree surgeon, fishing-boat crew

The rule is not "no white-collar characters." The rule is: **a character's job must be able to break under them within the show's runtime.** A roof can collapse on a roofer. A truck can blow a tire on a courier. A dough can burn on a baker. A record cannot break on an archivist — and that is why archivists are the centroid.

---

## Worked Example: Stray Signal v3.2 (the centroid migration case)

After the v3.2 lock, the writers-room Story Lock and SEASON_LORE.md contain:
- **Antagonist:** Howard Cavendish, Director of the Records and Cartography Bureau
- **Antagonist's instrument:** Beryl Heath, Senior Cartographer
- **Antagonist's deputy:** Orville Plinth, junior cartographer
- **Protagonist's uncle:** Llewelyn Pryce, Corporation power-readings analyst
- **Wise-elder figure:** Heledd Vaughn, Hen Iaith matriarch fluent in the suppressed language
- **Antagonist's project:** PHASE IV — the *redevelopment* (i.e., redrawing) of the Seam, run by *Records and Cartography*, signed by *signature*, executed under *displacement orders*

The protagonist (Six, a 12-year-old creche kid who sorts trinks by feel) is kinetic, embarrassing, embodied — the antiviral worked at the protagonist level. But the cast and conflict around him have laundered the centroid into world-historical material. The show is, structurally, *Cartographer vs. Power-Readings Analyst, with a translation matriarch and a 12-year-old as witness.* The kid has a body. Almost nobody else does.

This is not necessarily fatal — Stray Signal can still work because (a) the kids' POV is genuinely physical, (b) the v3.2 lock added a named-figure consequence beat that puts a body in The Seam at risk, (c) the senior-superior pattern preserves the no-theatre rule deliberately. But the show is operating *adjacent to* the centroid, not free of it. A subsequent project starting from a similar brief should not assume the antiviral will catch this — it didn't.

---

## How to Apply This Brief in a New Session

Paste the following two lines into the new session's preamble (or open the brief as a file the session can read):

> *Apply the prestige-literary centroid antiviral throughout this work. Source: `references/centroid_antiviral_brief.md`. Run the Job Census, the Action Test, and the Conflict-Register Test on every named character at every structural lock point. Treat centroid migration to surrounding cast as a first-class antiviral concern, not just protagonist drift. Existing tooling at `skills/writer/ANTIVIRAL_PROMPT.md` covers the protagonist level; this brief covers the world level.*

If the session is doing pitch-round work: cite the brief as the cast / world layer of the existing antiviral.
If the session is doing writers-room work: cite the brief as a Lane B extension of the v3.6 Structural Stakes Checklist and as a required check before SEASON_LORE.md is locked.
If the session is doing solo drafting (no room): run the four tests manually on the cast list at first lock and again before each draft of new material.

---

## Origin and Validation

Discovered as a craft observation by the user during Stray Signal v3.2 review (2026-05-04): the project's villain-vacuum and war-stakes problems had been solved at v3.2, but the solution itself (Howard Cavendish + records destruction) reproduced the prestige centroid at world-historical scale. The existing antiviral had laundered into the cast and conflict register without being detected.

This brief is the response. It is unvalidated as a tool — it has not yet been tested on a fresh project. It should be run alongside the existing antiviral on the next greenfield writers-room project and the centroid distribution measured against the unmodified-antiviral baseline. Until then, treat as a hypothesis with strong worked evidence (Stray Signal v3.2) and weak general evidence.
