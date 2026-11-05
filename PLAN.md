# Build plan (v1)

Each slice is small and works end to end: after it ships, the live site is a little better and nothing is half-built.
Every slice follows this loop: write the test or checklist first → write the smallest code that passes → run it and show it working → explain it → commit → tick it off here → wait for Kenneth.

🔍 = fresh-eyes review checkpoint (Phase 4).

- [ ] **Slice 1: Hello, internet.** A bare `index.html` with the name (`<h1>`), the pitch, and working GitHub, LinkedIn and Email links, **deployed to the free subdomain**. This proves the whole pipeline (code → GitHub → live URL) on day one.
- [ ] **Slice 2: Dark theme and page layout.** `styles.css` with dark colours, the accent colour, fonts, and the empty section structure (Hero, Projects, About, How I built this, Contact). Responsive at 375, 768 and 1280 px.
- [ ] **Slice 3: Projects.** Three project cards with real text, optimized images (Larpslator token blurred), tech tags and GitHub links. Cards stack on phones.
- 🔍 **Review 1** (slices 1–3)
- [ ] **Slice 4: About, How I built this and Contact.** Real copy for the remaining sections, approved by Kenneth.
- [ ] **Slice 5: Particle name (desktop).** A `<canvas>` behind the real `<h1>` that draws the name as particles, scatters them from the mouse, and springs them back.
- [ ] **Slice 6: Particle name, part 2: touch, resize and reduced motion.** Taps and drags work on phones, the effect rebuilds when the window size changes, and reduced-motion users get a still name.
- 🔍 **Review 2** (slices 4–6)
- [ ] **Slice 7: Résumé button.** Link the phone-free PDF (needs the file from Kenneth).
- [ ] **Slice 8: Launch check.** Lighthouse, link check, console check, page weight, and SEO basics (page title, description, preview image for shared links).
- 🔍 **Final review**, then Phase 5: fix → retest → re-review → confirm every "Done means" item in PRD.md with proof.
