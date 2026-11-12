/* Search and filter the ProcessPI component catalogue. */
(() => {
  const init = () => {
    const input = document.getElementById("component-directory-search");
    const status = document.getElementById("component-directory-status");
    const directory = document.querySelector(".component-directory");
    if (!input || !status || !directory || input.dataset.ready === "true") return;
    input.dataset.ready = "true";
    const items = Array.from(directory.querySelectorAll("[data-component-item]"));
    const groups = Array.from(directory.querySelectorAll("[data-component-group]"));
    const filter = () => {
      const query = input.value.trim().toLocaleLowerCase();
      let visible = 0;
      for (const item of items) {
        const match = !query || item.dataset.component.includes(query);
        item.hidden = !match;
        if (match) visible += 1;
      }
      for (const group of groups) {
        group.hidden = !group.querySelector("[data-component-item]:not([hidden])");
      }
      status.textContent = query
        ? `${visible} matching component name${visible === 1 ? "" : "s"}.`
        : `Showing all ${items.length} exported component names.`;
    };
    input.addEventListener("input", filter);
    filter();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
