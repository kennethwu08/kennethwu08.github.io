# Build plan (v1)

Each slice is small and works end to end: after it ships, the live site is a little better and nothing is half-built.
Every slice follows this loop: write the test or checklist first → write the smallest code that passes → run it and show it working → explain it → commit → tick it off here → wait for Kenneth.

🔍 = fresh-eyes review checkpoint (Phase 4).

- [x] **Slice 1: Hello, internet.** ✅ Live at https://kennethwu08.github.io (9/9 checks pass on the live site). A bare `index.html` with the name (`<h1>`), the pitch, and working GitHub, LinkedIn and Email links, **deployed to the free subdomain**. This proves the whole pipeline (code → GitHub → live URL) on day one.
- [x] **Slice 2: Dark theme and page layout.** ✅ `styles.css` with dark colours, the accent colour, fonts, and the empty section structure (Hero, Projects, About, How I built this, Contact). Responsive at 375, 768 and 1280 px.
- [x] **Slice 3: Projects.** ✅ Three project cards with real text, optimized images (Larpslator token painted over), tech tags and GitHub links. Cards stack on phones.
- 🔍 **Review 1** (slices 1–3) ✅ PASS, with 0 Critical, 0 High, 6 Medium and 5 Low problems. Phase 5 fixes:
  - Re-review (a new reviewer that hadn't seen the first one): ✅ PASS, with 0 Critical, 0 High, 2 Medium and 7 Low problems. It found test gaps (a focus ring removed on links, `aria-hidden` on the hero, a two-column layout on phones, named colours). All four now fail a check.
  - Tests: 49 → 65 checks. Added `tests/layout_check.js` for the browser checks at 320, 360, 375, 768 and 1280 px. Every sabotage the reviewer tried now fails a check.
  - Cards: shorter descriptions, the word "disability-awareness" added, accurate Larpslator alt text, thumb-sized GitHub links, and the Physics inset moved off the topic labels.
  - Design rules from the impeccable and hallmark skills (applied by hand, because their tools need Node or a downloaded binary): no middle-dot meta strings, no thick coloured left border, every colour through a `:root` variable, `overflow-x: clip`, `minmax(0, …)` grid columns, and styled text selection, link underlines and scrollbar.
  - Still waiting on Kenneth: the card facts (Korean ↔ English, "7 hours", the Physics team size, the scenario count) and his own role on Walk In My World and Physics Visualizer.
- [ ] **Slice 4: About, How I built this and Contact.** Real copy for the remaining sections, approved by Kenneth.
- [ ] **Slice 5: Particle name (desktop).** A `<canvas>` behind the real `<h1>` that draws the name as particles, scatters them from the mouse, and springs them back.
- [ ] **Slice 6: Particle name, part 2: touch, resize and reduced motion.** Taps and drags work on phones, the name may wrap to two lines at 320–360 px (the particles must follow the real `<h1>` box), the effect rebuilds when the window size changes, and reduced-motion users get a still name.
- 🔍 **Review 2** (slices 4–6)
- [ ] **Slice 7: Résumé button.** Link the phone-free PDF (needs the file from Kenneth). Rename the hero `<nav>` label to "Résumé and contact links".
- [ ] **Slice 8: Launch check.** Lighthouse, link check, console check, page weight, and SEO basics (page title, description, preview image for shared links).
- 🔍 **Final review**, then Phase 5: fix → retest → re-review → confirm every "Done means" item in PRD.md with proof.
