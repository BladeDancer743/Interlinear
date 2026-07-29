(function exposeLayoutEngine(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.InterlinearLayout = api;
})(typeof globalThis === "object" ? globalThis : window, function createLayoutEngine() {
  const MODES = new Set(["margin", "focus", "list"]);

  function estimateCardHeight(note, width = 272) {
    const charactersPerLine = Math.max(12, Math.floor(width / 13));
    const lines = Math.max(1, Math.ceil(String(note || "").length / charactersPerLine));
    return 62 + lines * 18;
  }

  function decideAnnotationLayout(input) {
    const annotations = Array.isArray(input.annotations) ? input.annotations : [];
    const count = annotations.length;
    if (!count) {
      return { mode: "none", reason: "empty", sideSpace: 0 };
    }

    const preferred = String(input.preferred || "auto");
    const viewportWidth = Math.max(1, Number(input.viewportWidth) || 1);
    const pageWidth = Math.max(1, Number(input.pageWidth) || 1);
    const pageHeight = Math.max(1, Number(input.pageHeight) || 1);
    const sideSpace = Math.max(0, viewportWidth - pageWidth - 96);
    const longest = Math.max(...annotations.map((item) => String(item.note || "").length));
    const estimatedHeight = annotations.reduce(
      (total, item) => total + estimateCardHeight(item.note),
      Math.max(0, count - 1) * 12,
    );

    if (MODES.has(preferred)) {
      return { mode: preferred, reason: "manual", sideSpace };
    }
    if (
      viewportWidth < 720 ||
      pageWidth / viewportWidth > 0.88 ||
      count > 12 ||
      longest > 420
    ) {
      return { mode: "list", reason: "compact-or-dense", sideSpace };
    }
    if (
      sideSpace >= 300 &&
      count <= 10 &&
      longest <= 260 &&
      estimatedHeight <= pageHeight * 0.92
    ) {
      return { mode: "margin", reason: "wide-canvas", sideSpace };
    }
    return { mode: "focus", reason: "limited-side-space", sideSpace };
  }

  function distributeMarginItems(items, pageHeight, gap = 12) {
    const height = Math.max(1, Number(pageHeight) || 1);
    const ordered = [...items]
      .map((item) => ({
        ...item,
        anchorY: Number(item.anchorY) || 0,
        height: Math.max(1, Number(item.height) || 1),
      }))
      .sort((left, right) => left.anchorY - right.anchorY);
    const required =
      ordered.reduce((total, item) => total + item.height, 0) +
      Math.max(0, ordered.length - 1) * gap;
    if (required > height) return null;

    let previousBottom = 0;
    for (const item of ordered) {
      const desired = Math.max(0, Math.min(item.anchorY - item.height / 2, height - item.height));
      item.top = Math.max(desired, previousBottom);
      previousBottom = item.top + item.height + gap;
    }

    const overflow = Math.max(0, previousBottom - gap - height);
    if (overflow) {
      ordered[ordered.length - 1].top -= overflow;
      for (let index = ordered.length - 2; index >= 0; index -= 1) {
        const next = ordered[index + 1];
        ordered[index].top = Math.min(
          ordered[index].top,
          next.top - gap - ordered[index].height,
        );
      }
    }

    const underflow = Math.max(0, -ordered[0].top);
    if (underflow) {
      for (const item of ordered) item.top += underflow;
    }
    return ordered;
  }

  return {
    decideAnnotationLayout,
    distributeMarginItems,
    estimateCardHeight,
  };
});
