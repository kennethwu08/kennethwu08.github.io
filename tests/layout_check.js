// Layout check: things the Python script can't see because they need a real browser.
//
// How to run: open the site, resize the window (or use the browser's device toolbar)
// to 320, 360, 375, 768 and 1280 px wide, and at each width paste this whole file into
// the browser console. It prints PASS/FAIL lines and returns the results.

(() => {
  const MIN_TAP_HEIGHT = 32; // px; card links and buttons should be at least this tall
  const width = window.innerWidth;
  const results = [];
  const check = (name, ok, detail = "") => results.push({ name, ok, detail });

  const page = document.documentElement;
  check("no sideways scrolling", page.scrollWidth <= width, `scrollWidth ${page.scrollWidth}`);

  const offscreen = [...document.querySelectorAll("body *")].filter((el) => {
    const box = el.getBoundingClientRect();
    return box.width > 0 && (box.right > width + 1 || box.left < -1);
  });
  check("nothing sticks out past the screen edge", offscreen.length === 0,
        offscreen.map((el) => el.tagName + "." + el.className).join(", "));

  const h1 = document.querySelector("h1");
  const h1Box = h1.getBoundingClientRect();
  check("the name is visible", h1Box.width > 0 && getComputedStyle(h1).visibility !== "hidden");
  check("the name fits inside the hero", h1.scrollWidth <= h1.clientWidth,
        `${Math.round(h1Box.height)} px tall`);

  const targets = [...document.querySelectorAll(".button, .project-body > a")];
  const small = targets.filter((el) => el.getBoundingClientRect().height < MIN_TAP_HEIGHT);
  check(`links are at least ${MIN_TAP_HEIGHT} px tall`, small.length === 0,
        small.map((el) => `${el.textContent.trim()} ${Math.round(el.getBoundingClientRect().height)}px`).join(", "));

  // Keyboard focus: every link must show an outline when focused.
  // Browsers only draw focus rings in the active window, so this can't run in a background tab.
  if (!document.hasFocus()) {
    check("every link shows a focus outline", false,
          "not checked: click on the page first so its window is active, then rerun");
  } else {
    const active = document.activeElement;
    const noRing = [...document.querySelectorAll("a")].filter((el) => {
      el.focus({ focusVisible: true });
      const style = getComputedStyle(el);
      return style.outlineStyle === "none" || parseFloat(style.outlineWidth) === 0;
    });
    active?.focus?.();
    check("every link shows a focus outline", noRing.length === 0,
          noRing.map((el) => el.textContent.trim()).join(", "));
  }

  // Each inset screenshot must stay inside its card.
  document.querySelectorAll(".project-inset").forEach((inset) => {
    const card = inset.closest(".project").getBoundingClientRect();
    const box = inset.getBoundingClientRect();
    check(`inset stays in its card: ${inset.getAttribute("src")}`,
          box.top >= card.top && box.bottom <= card.bottom && box.right <= card.right);
  });

  const columns = getComputedStyle(document.querySelector(".project")).gridTemplateColumns.split(" ").length;
  check(`cards use ${width >= 768 ? 2 : 1} column(s)`, columns === (width >= 768 ? 2 : 1), `${columns} found`);

  results.forEach((r) => console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}${r.detail ? `  (${r.detail})` : ""}`));
  return { width, passed: results.filter((r) => r.ok).length, total: results.length,
           failed: results.filter((r) => !r.ok) };
})();
