# PRD: Kenneth Wu, personal portfolio site (v1)

## Goal

A one-page personal website for **Kenneth Wu**, a first-year Computer Science student at **McMaster University** (BASc, expected 2030).

- **Main audience:** recruiters and internship hiring managers, who will spend about 30 seconds on the page. They should immediately see who Kenneth is, what he has built, and how to contact him or get his résumé.
- **Second goal:** show that Kenneth can use AI to build polished, interactive frontends. **The site itself is the proof**, and a short "How I built this" section explains the process.

## Scope

### In v1

1. **Hero**
   - Kenneth's name drawn as an **interactive particle effect**. Particles scatter away from the mouse (or a finger tap on phones) and spring back into the letters. It nods to his Physics Visualizer.
   - One-line pitch (draft: "First-year CS student at McMaster building hardware, AI tools and interactive software").
   - Buttons: **Résumé** (phone-free PDF), **GitHub** (github.com/kennethwu08), **LinkedIn** (linkedin.com/in/kenneth-wu-6857a0396), **Email** (wu1410@mcmaster.ca).
2. **Projects**: three cards, in this order:
   - **Larpslator** (LARPHacks 2026, Nov 2026, team of 4): ESP32 clip-on badge that translates Korean ↔ English live with context-aware jargon. Highlight: **100% jargon accuracy vs. 93% for a plain translator**. Role: hardware, web dashboard, FastAPI backend, glossary, ElevenLabs TTS. Image: dashboard screenshot, **with the local address and token painted over**. Link: GitHub repo only (no live demo).
   - **Walk In My World** (Jul–Aug 2026, team of 3): 3D disability-awareness simulator, 7 experience modes, 4 scenarios, an Accessibility Lab with 20+ effects, grounded in WHO/CDC/NIH research. Images: menu and classroom (ADHD) screenshots. Link: GitHub (bernardkim0805-cmyk).
   - **Physics Visualizer** (Jun 2026): desktop app covering 8 Grade 11–12 physics topics, with a Gemini-powered whiteboard tutor, packaged with PyInstaller. Images: menu and momentum screenshots. Link: GitHub.
   - Each card has an image, a one-line description, Kenneth's role, tech tags, the date, and a GitHub link.
3. **About**: 2–3 sentences covering McMaster, his interests, and awards (Computer Science Award 2026, DECA Provincial Qualifier).
4. **How I built this**: short write-up of the AI-assisted workflow (PRD → plan → slice-by-slice build → independent review), with emphasis on what Kenneth directed and decided.
5. **Contact**: email and links.
6. **Look and feel:** dark theme, one accent colour (**default: electric blue**, which can be changed), clean and fast to scan. All the motion is in the hero.
7. **Works on phones:** responsive from 360 px wide upward. The hero reacts to touch.
8. **Accessible:** real text for the name (screen readers and search engines), alt text on every image, keyboard navigation with visible focus, readable contrast. If the visitor's system asks for reduced motion, the hero shows a still version.
9. **Tech:** plain HTML, CSS and JavaScript with no framework, hosted on a **free subdomain**. The host is chosen in Phase 2.

### Not in v1

- Blog
- Contact form (an email link is enough)
- Light theme or theme toggle
- Separate detail pages for each project
- Custom domain (can be added later)
- Live Larpslator demo link (it needs a running backend)
- 3D tilting cards, or hover-to-play project videos
- Analytics or a visitor counter
- Any framework, build step or CMS

### Needed from Kenneth

- [ ] **Phone-free résumé PDF** (export a copy of the résumé with the phone number removed). Needed before the résumé slice.
- [ ] Final approval of the one-line pitch and the About text.

## Done means

Each item must be checked with proof (a screenshot, command output or tool report).

- [ ] The site is live at a public free-subdomain URL over HTTPS.
- [ ] The page has exactly one `<h1>` containing "Kenneth Wu" as real text.
- [ ] The hero particles form the name, scatter from the mouse on desktop, and return to place.
- [ ] On a touch device (or mobile emulation), tapping or dragging over the name scatters the particles.
- [ ] With reduced motion turned on, the name appears still and readable, with no animation.
- [ ] The Résumé button opens a PDF that **does not contain a phone number**.
- [ ] The GitHub, LinkedIn and Email buttons go to the correct addresses.
- [ ] All three project cards appear in the right order with facts that match the résumé, and every GitHub link resolves (no 404s).
- [ ] The Larpslator image has the local address and token unreadable.
- [ ] The About, How I built this and Contact sections are present.
- [ ] No sideways scrolling and nothing overlapping at 375 px, 768 px or 1280 px wide.
- [ ] Every image has meaningful alt text, and every link and button can be reached with Tab and shows a visible focus ring.
- [ ] Lighthouse (mobile) scores **≥ 90** for Performance, Accessibility, Best Practices and SEO.
- [ ] No errors in the browser console.
- [ ] Total page weight is under 2 MB on first load.
- [ ] Nothing from the "Not in v1" list was built.
