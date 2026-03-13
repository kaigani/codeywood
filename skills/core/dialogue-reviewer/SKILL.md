# Dialogue Reviewer Skill

## Purpose

Review dialogue for the invisible qualities that separate functional speech from living conversation. Great dialogue doesn't just convey information — it reveals the soul of the character while keeping the reader hooked. This skill provides a structured audit against 12 principles of dialogue craft, producing a diagnostic report that tells the dialogue-doctor exactly where to focus.

This is a **read-only review** skill. It does not rewrite dialogue — it identifies what's working, what's failing, and why.

## Trigger

`SCRIPTS/SCRIPT_EP{{XX}}.md` exists (first draft complete, before dialogue-doctor pass).

## Pipeline Position

```
screenplay-writer → dialogue-reviewer → dialogue-doctor → story-critic → Gate 5
```

## Inputs Required

- `SCRIPTS/SCRIPT_EP{{XX}}.md` (the screenplay to review)
- `CHARACTER_SHEETS/*.md` (voice profiles, backgrounds, relationships)
- `CREATIVE_BRIEF.md` (tone, genre, world rules)
- `LOGLINE_LOCK.md` (thematic promises)

## Outputs Produced

- `STORY/DIALOGUE_REVIEW_EP{{XX}}.md` — structured audit report with per-scene scoring, flagged lines, and revision priorities

**This skill does NOT modify the script.** It produces a diagnostic that feeds into the dialogue-doctor.

---

## The 12 Principles of Dialogue Review

### Principle 1: Character Voice and Idiolect

**The standard**: Every character should sound like themselves — and only themselves. Education level, upbringing, age, regional dialect, professional vocabulary, and personal quirks should all shape word choice. If you swap the character names on the script, you should still be able to tell who is talking.

**What to look for**:
- Vocabulary level matches the character's background (a mechanic and a professor describe the same problem differently)
- Sentence structure reflects personality (a nervous character fragments; a controlling one speaks in complete, declarative sentences)
- Verbal tics, pet phrases, or habitual constructions that belong to this character alone
- Cultural or regional markers used consistently (not stereotypically)
- Technical jargon used correctly when the character would know it, absent when they wouldn't

**Red flags**:
- Two characters use the same phrasing in different scenes
- A character's vocabulary suddenly shifts without narrative reason
- All characters sound like the author — same rhythm, same wit level, same references
- A blue-collar character suddenly drops academic language (or vice versa) without the script acknowledging it

**The test**: Cover the character names. Read five random lines from each character. Can you identify the speaker from voice alone? If not, the idiolect needs work.

---

### Principle 2: Emotional Resonance

**The standard**: Dialogue should make the reader feel something specific — not just understand information. Whether it's a gut-wrenching confession, a quiet revelation, or a perfectly timed comeback, the words should land with impact. The reader should feel the temperature change in the room.

**What to look for**:
- Lines that create a physical response (tension, relief, laughter, discomfort)
- Emotional beats that arrive through the character's specific way of expressing feeling, not generic statements
- The gap between what a character says and what the audience feels (dramatic irony, understatement, misdirection)
- Moments where what's NOT said hits harder than what is

**Red flags**:
- Characters announce their emotions: "I'm so angry right now"
- Emotionally significant moments feel flat or clinical
- The dialogue tells us how to feel rather than making us feel it
- Key scenes read like report summaries rather than lived experience

**The test**: Read the scene's emotional climax aloud. Does your voice naturally shift? Does the line hit you in the chest or just in the head? If it only registers intellectually, it hasn't earned its emotional beat.

---

### Principle 3: Subtext vs. Text

**The standard**: People rarely say exactly what they mean. The most powerful dialogue operates on two levels simultaneously — the surface conversation and the real conversation happening underneath. Review every exchange for the gap between what is said and what is meant.

**What to look for**:
- Characters who talk about one thing while meaning another (arguing about dishes when they're really arguing about commitment)
- Deflection as character revelation (answering a different question than was asked)
- Silence and pauses that carry weight
- Physical contradictions (saying "I'm fine" while gripping the table)
- Subject changes that reveal more than direct answers would

**Red flags**:
- Characters state their feelings directly in emotional scenes
- Characters explain their motivations to each other
- The audience can only understand the scene at face value — no second layer exists
- Confrontation scenes where characters say exactly what they mean (real people almost never do this)

**The test**: For each exchange, ask two questions: (1) What is this character actually saying? (2) What do they really want? If the answers are identical, the subtext is missing.

---

### Principle 4: Directness and "The Point"

**The standard**: Dialogue isn't a transcript of real life — it's a curated version of it. Every line should earn its place. Characters shouldn't tread water with meaningless small talk, pleasantries, or circular conversation unless that awkwardness is itself the point (revealing discomfort, avoidance, or a character's social strategy).

**What to look for**:
- Lines that advance the scene's purpose (reveal character, escalate conflict, deliver information through friction)
- Entrances that skip the greeting and land mid-conversation
- Exits that cut before the expected goodbye
- Small talk that is actually subtext in disguise

**Red flags**:
- Scenes that take three exchanges to get to the point when one would do
- "Hello, how are you, fine thanks" openers that don't serve character
- Characters restating what was just said: "So what you're saying is..."
- Circular dialogue where the same point is made twice in different words
- Polite agreement that kills momentum

**The test**: For every line, ask: "What happens if I cut this?" If the scene still works, the line is filler.

---

### Principle 5: Pacing and Rhythm

**The standard**: Dialogue has musicality. Short, punchy sentences speed up a scene — useful for arguments, confrontation, or rising tension. Longer, flowing sentences slow it down — useful for intimacy, reflection, or dawning realization. The best scenes vary their rhythm like a piece of music, building toward crescendos and letting silence breathe.

**What to look for**:
- Rhythm shifts that match emotional gear changes (rapid-fire in arguments, lingering in vulnerability)
- Sentence length variation within a single character's speech
- The strategic use of single-word lines for impact ("No." / "Go." / "Stay.")
- Interruptions that feel natural, not scripted
- Pauses (indicated by em-dashes, ellipses, or beats) placed for maximum effect

**Red flags**:
- All lines are the same length throughout a scene
- An argument scene with long, articulate sentences (real arguments get clipped and messy)
- An intimate scene with short, staccato lines (intimacy usually sprawls)
- No variation in rhythm across the entire script
- Every character speaks in the same cadence regardless of emotional state

**The test**: Read the scene aloud and tap the rhythm on a table. Can you hear the tempo changes? If it's metronomic — same beat, same length, same pause — the pacing needs work.

---

### Principle 6: Information Dumping (Exposition)

**The standard**: The audience needs information, but dialogue should never feel like a Wikipedia article wearing a costume. Watch for "As you know, Bob" syndrome — characters telling each other things they both already know purely to inform the reader. Information should be revealed through conflict, necessity, or discovery — never through lecture.

**What to look for**:
- New information delivered because one character genuinely needs it from the other
- Exposition embedded in argument (characters reveal backstory while fighting about something else)
- Information withheld as power play (making someone ask, refusing to explain)
- World-building that comes through casual reference rather than explanation

**Red flags**:
- "As you know, we've been partners for three years..." (both characters know this)
- "Maid-and-butler" dialogue: two characters explaining the plot to each other
- A character recapping events the audience just witnessed
- Backstory delivered as monologue rather than emerging through present-tense conflict
- Technical explanations that no character in the room actually needs
- "Let me explain..." followed by a paragraph of world-building

**The test**: For every piece of information in the dialogue, ask: "Does the speaking character have a reason to say this *right now*, to *this person*?" If the only reason is "the audience needs to know," it's a dump.

---

### Principle 7: Action Beats vs. Speech Tags

**The standard**: How a line is delivered matters as much as what's said. Instead of relying on adverbs to do the emotional heavy lifting ("he said angrily"), use action beats — physical behavior that shows the emotion and grounds the reader in the scene. The body tells the truth even when the mouth lies.

**What to look for**:
- Physical behavior that reveals emotional state (drumming fingers, avoiding eye contact, pouring a drink they don't touch)
- Action beats that contradict the dialogue (saying "It's fine" while crushing a napkin)
- Environmental interaction that reflects inner state (straightening things when anxious, breaking things when angry)
- Specificity in physical detail (not "she fidgeted" but "she tore the label off the bottle in one long strip")

**Red flags**:
- Over-reliance on "said angrily," "whispered nervously," "shouted furiously" — adverbs doing the work the dialogue should do
- No physical grounding — dialogue floating in a void with no sense of bodies in space
- Generic stage directions: "She looked upset." (How? Show it.)
- Every beat is the same gesture (nodding, sighing, looking away)

**The test**: Remove all speech tags and adverbs. Can you still tell how the line is delivered from the action beat alone? If there's no action beat, can you infer delivery from the words themselves?

---

### Principle 8: Conflict and Stakes

**The standard**: Even in a friendly conversation, there is usually a push and pull. Each character should want something from the exchange — information, approval, control, comfort, escape. If everyone agrees immediately, the scene lacks tension. Conflict doesn't mean shouting — it means competing wants.

**What to look for**:
- Competing objectives in every scene (character A wants X, character B wants Y)
- Micro-conflicts within larger agreements (they agree on the goal but disagree on how)
- Escalation — the stakes of the conversation rising as it continues
- At least one character who doesn't get what they want
- The cost of winning (what does the "winner" of the exchange sacrifice?)

**Red flags**:
- Characters agree too quickly on important matters
- One character asks, the other answers, conversation over — no negotiation
- Scenes where both characters want the same thing and get it without resistance
- Friendly banter that has no underlying tension or purpose
- Exposition scenes disguised as "catching up" with no stakes

**The test**: For each scene, name what each character wants. If they want the same thing — or if one character wants nothing — the conflict is missing.

---

### Principle 9: Consistency of Tone

**The standard**: Dialogue must inhabit the world of the story. A hard-boiled noir detective shouldn't suddenly deploy Gen Z slang — unless there's a deliberate, plot-driven reason for the shift. Tonal breaks shatter the reader's immersion. The dialogue should feel like it belongs in this specific universe, this specific genre, this specific emotional register.

**What to look for**:
- Vocabulary and reference points that match the story's world and era
- Humor that fits the genre (dark comedy in noir, absurdist in satire, dry in drama)
- Formality levels appropriate to the setting and relationships
- Consistent register within a character's speech across scenes (unless a shift is narratively motivated)

**Red flags**:
- Modern slang in a period piece (or period language in a modern setting) without intent
- A character whose wit level changes based on what the scene needs rather than who they are
- Comedic beats in an otherwise serious scene that weren't earned
- Genre-inappropriate language (flowery prose in a thriller, clinical detachment in a romance)
- The author's contemporary voice bleeding through a character who shouldn't have it

**The test**: Does this line sound like it belongs in this movie, or does it sound like it wandered in from a different script?

---

### Principle 10: Realism and "The Ear Test"

**The standard**: Read every line out loud. If you trip over the words, stumble on a phrase, or find yourself rephrasing mid-sentence, a reader will too — and a voice actor will struggle with it. Dialogue should be "heightened reality": it sounds natural and speakable, but without the "ums," "ahs," false starts, and repetitive filler of actual conversation. It's real speech with the boring parts cut out.

**What to look for**:
- Lines that flow naturally when spoken aloud
- Contractions used where a real person would use them ("don't" not "do not" — unless the character is formal)
- Sentence structures that match how people actually construct thoughts (not essay-like compound sentences)
- Breath points — natural places to pause within longer lines

**Red flags**:
- Tongue-twisters or consonant clusters that are hard to say
- Lines that are grammatically perfect but sound robotic when spoken
- Overly long sentences that a real person couldn't deliver in one breath
- Missing contractions that make speech sound stilted
- Dialogue that reads well on the page but sounds unnatural when performed
- Technical accuracy that sacrifices speakability

**The test**: Read every line aloud at conversational speed. Record yourself if possible. Where do you stumble, rephrase, or lose the thread? Those are the lines that need revision. For AI-generated voice (TTS), this is doubly important — TTS exposes clunky phrasing that a skilled actor might save.

---

### Principle 11: Power Dynamics

**The standard**: Dialogue reveals who holds power in a room. Look at who asks the questions and who gives the answers. Who interrupts, and who gets interrupted. Who speaks first, and who waits. Who uses the other person's name (a dominance marker), and who avoids it. Power dynamics in dialogue mirror the scene's dramatic architecture — and when they shift, the story moves.

**What to look for**:
- Clear high/low status markers (fewer words = higher status; over-explaining = lower status)
- Status shifts within a scene (the person who starts in control loses it, or vice versa)
- Question patterns (who is interrogating, who is evading)
- Interruption dynamics (who cuts whom off, and what it reveals)
- Name usage (using someone's name can be intimate or controlling depending on context)
- Silence as power (the person who can tolerate silence longest often holds the room)

**Red flags**:
- Static power dynamics throughout a scene (no shift, no play)
- A character who should be powerful speaks like a subordinate (or vice versa) without the script acknowledging it
- Scenes where no one controls the conversation — dialogue drifts without direction
- Power shifts that happen because the plot needs them, not because a character earns them
- Every scene has the same character in the dominant position

**The test**: Track who "wins" each exchange within a scene. Draw the power curve. If it's a flat line, the dynamics aren't working.

---

### Principle 12: Truth and Authenticity

**The standard**: This is the gut check — the principle that encompasses all others. Does this sound like something a human being would actually say in this situation? Not a clever writer, not an AI, not a mouthpiece for the author's opinions — a living person in this specific moment, under this specific pressure, with this specific history. If a character feels like a vessel for theme rather than a person, the truth of the scene is lost.

**What to look for**:
- Lines that feel discovered rather than constructed
- Emotional logic that tracks (the character says this because of who they are and what just happened, not because the plot needs it)
- Imperfection in speech that reveals character (grammatical quirks, trailing off, changing direction mid-sentence)
- Moments where a character surprises even themselves
- The sense that the character exists beyond the edges of the scene

**Red flags**:
- Characters who always have the perfect response (real people fumble, especially in emotional moments)
- Dialogue that sounds like a thesis statement about the story's theme
- Lines that serve the audience's understanding rather than the character's reality
- Perfect articulation of complex feelings in the moment (people rarely have that clarity in real time)
- Characters who never say the wrong thing, never misunderstand, never talk past each other
- The "author's voice" speaking through a character who shouldn't have that perspective

**The test**: Ask yourself: "Would this person actually say this, in this way, right now?" Not "is it clever" or "does it advance the plot" — but is it *true* to who they are in this moment? If there's even a flicker of doubt, the line needs examination.

---

## Review Process

### Step 1: Read-Through

Read the entire script in one sitting without taking notes. Let it wash over you. After finishing, write down three things:
1. Which character's voice stuck with you most (and why)
2. Which scene felt the most alive
3. Which moment pulled you out of the story

This gut response is data — it tells you where the dialogue is working at an instinctive level.

### Step 2: Voice Isolation Audit

Extract all dialogue for each character into a separate list (no scene context, no action lines — just their words in sequence).

For each character, fill in:

| Character | Vocab Level | Sentence Style | Verbal Tics | Emotional Range | Distinguishable? |
|-----------|-------------|----------------|-------------|-----------------|-------------------|
| | | | | | Y/N |

**Flag**: Any character marked "N" in distinguishable needs targeted dialogue-doctor attention.

### Step 3: Scene-by-Scene Principle Audit

For each scene, score all 12 principles on a 1-5 scale:

| Principle | Score | Notes |
|-----------|-------|-------|
| 1. Voice & Idiolect | | |
| 2. Emotional Resonance | | |
| 3. Subtext vs. Text | | |
| 4. Directness | | |
| 5. Pacing & Rhythm | | |
| 6. Exposition | | |
| 7. Action Beats | | |
| 8. Conflict & Stakes | | |
| 9. Tone Consistency | | |
| 10. Ear Test | | |
| 11. Power Dynamics | | |
| 12. Truth & Authenticity | | |
| **Scene Average** | | |

**Scoring scale**:
- **5** — Exceptional. This scene could teach the principle.
- **4** — Strong. Minor opportunities but fundamentally works.
- **3** — Adequate. Functional but not distinctive. Doesn't hurt the story.
- **2** — Weak. Principle is underserved. Specific fixes needed.
- **1** — Failing. Principle is violated in a way that damages the scene.

### Step 4: Line-Level Flagging

For any scene scoring 2 or below on any principle, flag the specific lines with:
- The offending line (quoted)
- Which principle(s) it violates
- Why it fails (brief explanation)
- Suggested direction for the dialogue-doctor (not a rewrite — a diagnosis)

Example:
```
SC02, Line 14 — KODA: "I calculated that the optimal outcome—"
  Violates: #1 (Voice), #12 (Truth)
  Issue: Generic robot phrasing. Any AI character could say this.
         Koda's voice should reflect three years of learning Noor's
         specific patterns, not factory-default optimization language.
  Direction: Replace optimization language with Noor-specific observations.
```

### Step 5: Strengths Report

Document what's working. The dialogue-doctor needs to know what to protect as much as what to fix. List:
- Lines or exchanges that exemplify the 12 principles
- Character voice moments that are distinctive and true
- Scenes where the principles work in concert (subtext + power dynamics + rhythm)

### Step 6: Priority Revision List

Produce a ranked list of scenes for dialogue-doctor attention:

| Priority | Scene | Key Issues | Principles Affected |
|----------|-------|------------|---------------------|
| 1 (Critical) | | | |
| 2 (High) | | | |
| 3 (Medium) | | | |

---

## Scoring Summary

### Per-Scene Score
Average of all 12 principle scores (1-5 scale). Reported in the scene audit table.

### Per-Character Score
Average principle scores across all scenes where the character appears. Highlights characters whose voice needs the most work.

### Overall Dialogue Health Score

| Category | Weight | Score (1-5) | Weighted |
|----------|--------|-------------|----------|
| Voice Distinction (P1) | 15% | | |
| Emotional Impact (P2) | 10% | | |
| Subtext Depth (P3) | 15% | | |
| Economy (P4, P6) | 10% | | |
| Musicality (P5) | 10% | | |
| Craft (P7) | 5% | | |
| Tension (P8) | 10% | | |
| World Fit (P9) | 5% | | |
| Speakability (P10) | 5% | | |
| Power Architecture (P11) | 5% | | |
| Authenticity (P12) | 10% | | |
| **TOTAL** | 100% | | |

**Thresholds**:
- **4.0+** — Strong dialogue. Proceed to story-critic; dialogue-doctor pass optional.
- **3.0-3.9** — Solid foundation with specific weaknesses. Dialogue-doctor pass recommended with targeted focus.
- **2.0-2.9** — Significant issues. Dialogue-doctor pass required before story-critic.
- **Below 2.0** — Fundamental problems. May need screenplay-writer revision before dialogue work.

---

## Review Report Format

```markdown
# Dialogue Review: EP{{XX}}

## Overall Score: {{X.X}}/5.0
## Recommendation: {{PROCEED / DIALOGUE-DOCTOR PASS / REVISION NEEDED}}

### Gut Response (Step 1)
- **Strongest voice**: {{CHARACTER}} — {{WHY}}
- **Most alive scene**: SC{{XX}} — {{WHY}}
- **Pulled me out**: SC{{XX}} — {{WHY}}

### Voice Isolation (Step 2)

| Character | Vocab Level | Sentence Style | Verbal Tics | Range | Distinct? |
|-----------|-------------|----------------|-------------|-------|-----------|
| | | | | | |

### Scene-by-Scene Audit (Step 3)

#### SC{{XX}}: {{SCENE_NAME}}
| Principle | Score | Notes |
|-----------|-------|-------|
| 1-12... | | |

### Flagged Lines (Step 4)
- SC{{XX}}, Line {{N}} — {{CHARACTER}}: "{{LINE}}"
  - Violates: #{{N}} ({{PRINCIPLE}})
  - Issue: {{EXPLANATION}}
  - Direction: {{GUIDANCE}}

### Strengths to Preserve (Step 5)
1. {{STRENGTH}} — {{EXAMPLE}}
2. {{STRENGTH}} — {{EXAMPLE}}

### Priority Revision List (Step 6)

| Priority | Scene | Key Issues | Principles |
|----------|-------|------------|------------|
| 1 | | | |
| 2 | | | |

### Scoring Summary

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| ... | | | |
| **TOTAL** | 100% | | **{{SCORE}}** |
```

---

## Notes

- This skill is diagnostic, not prescriptive. It identifies problems; the dialogue-doctor fixes them.
- Always lead with strengths. Writers need to know what to protect.
- Be specific in flagging — "the dialogue feels off" is useless. "Line 14 uses optimization language that any AI could say, losing Koda's specific knowledge of Noor" is actionable.
- The 12 principles are not equally important in every genre. A comedy may lean hard into Pacing (P5) and Ear Test (P10) while a thriller prioritizes Power Dynamics (P11) and Stakes (P8). Weight your attention accordingly.
- For AI-generated content (TTS voiceover), Principle 10 (Ear Test) carries extra weight — there's no skilled actor to save a clunky line.
- Trust your gut response in Step 1. Analytical review confirms or challenges it, but instinct is data.
