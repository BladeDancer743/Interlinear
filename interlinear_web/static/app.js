const state = {
  health: null,
  documents: [],
  document: null,
  page: 1,
  pageData: null,
  zoom: 100,
  renderDpi: 160,
  loadToken: 0,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const elements = {
  cajCapability: $("#caj-capability"),
  cajDetail: $("#caj-detail"),
  cajDialog: $("#caj-dialog"),
  copyText: $("#copy-text"),
  documentCount: $("#document-count"),
  documentList: $("#document-list"),
  dropzone: $("#dropzone"),
  figureList: $("#figure-list"),
  figuresEmpty: $("#figures-empty"),
  fileInput: $("#file-input"),
  inspector: $("#inspector"),
  libraryPanel: $("#library-panel"),
  libraryPath: $("#library-path"),
  metadata: $("#metadata"),
  nextPage: $("#next-page"),
  openPdf: $("#open-pdf"),
  outlineEmpty: $("#outline-empty"),
  outlineList: $("#outline-list"),
  pageCanvas: $("#page-canvas"),
  pageImage: $("#page-image"),
  pageLoader: $("#page-loader"),
  pageNumber: $("#page-number"),
  pageSize: $("#page-size"),
  pageText: $("#page-text"),
  pageTotal: $("#page-total"),
  pageViewport: $("#page-viewport"),
  previousPage: $("#previous-page"),
  renderQuality: $("#render-quality"),
  searchForm: $("#search-form"),
  searchInput: $("#search-input"),
  searchResults: $("#search-results"),
  textEmpty: $("#text-empty"),
  textHeading: $("#text-heading"),
  thumbnailRail: $("#thumbnail-rail"),
  toast: $("#toast"),
  toolbarTitle: $("#toolbar-title span"),
  welcome: $("#welcome"),
  zoomIn: $("#zoom-in"),
  zoomOut: $("#zoom-out"),
  zoomReset: $("#zoom-reset"),
};

async function request(url, options) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("json") ? await response.json() : null;
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      typeof detail === "string" ? detail : detail?.message || "请求未完成";
    throw new Error(message);
  }
  return payload;
}

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("is-error", isError);
  elements.toast.classList.add("is-visible");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(
    () => elements.toast.classList.remove("is-visible"),
    3600,
  );
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "—";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(index ? 1 : 0)} ${units[index]}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function loadHealth() {
  state.health = await request("/api/health");
  const libraryLabel = state.health.library
    .replaceAll("\\", "/")
    .split("/")
    .filter(Boolean)
    .slice(-2)
    .join("/");
  elements.libraryPath.textContent = `PRIVATE LIBRARY · ${libraryLabel}`;
  const caj = state.health.caj;
  elements.cajCapability.classList.toggle("is-ready", caj.available);
  elements.cajCapability.classList.toggle("is-warning", !caj.available);
  elements.cajCapability.innerHTML = `<i></i> CAJ ${
    caj.available ? "就绪" : "需配置"
  }`;
  elements.cajDetail.textContent = caj.detail;
}

async function loadDocuments(preferredId = null) {
  const payload = await request("/api/documents");
  state.documents = payload.items;
  elements.documentCount.textContent = payload.count;
  renderDocumentList();
  if (preferredId) {
    await openDocument(preferredId);
  } else if (!state.document && state.documents.length) {
    await openDocument(state.documents[0].id);
  }
}

function renderDocumentList() {
  if (!state.documents.length) {
    elements.documentList.innerHTML = `
      <div class="library-empty">
        <span>01</span>
        <p>导入第一篇文档，开始逐页检查。</p>
      </div>`;
    return;
  }

  elements.documentList.innerHTML = state.documents
    .map(
      (item) => `
        <button class="document-card ${
          state.document?.id === item.id ? "is-active" : ""
        }" data-document-id="${item.id}">
          <span class="file-badge">${escapeHtml(item.source_format)}</span>
          <span>
            <strong>${escapeHtml(item.title)}</strong>
            <small>
              <span>${item.page_count} 页</span>
              <span>·</span>
              <span>${formatBytes(item.source_size)}</span>
            </small>
          </span>
        </button>`,
    )
    .join("");

  $$(".document-card").forEach((button) => {
    button.addEventListener("click", () => openDocument(button.dataset.documentId));
  });
}

async function openDocument(documentId) {
  try {
    const payload = await request(`/api/documents/${documentId}`);
    state.document = payload.document;
    state.page = 1;
    state.zoom = 100;
    elements.welcome.hidden = true;
    elements.pageCanvas.hidden = false;
    elements.searchInput.disabled = false;
    elements.pageNumber.disabled = false;
    elements.pageTotal.textContent = state.document.page_count;
    elements.pageNumber.max = state.document.page_count;
    elements.toolbarTitle.textContent = state.document.title;
    elements.openPdf.href = `/api/documents/${state.document.id}/pdf`;
    [elements.zoomIn, elements.zoomOut, elements.zoomReset].forEach(
      (button) => (button.disabled = false),
    );
    renderDocumentList();
    renderOutline();
    renderMetadata();
    renderThumbnails();
    await loadPage(1, true);
    elements.libraryPanel.classList.remove("is-open");
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderThumbnails() {
  const count = state.document?.page_count || 0;
  elements.thumbnailRail.innerHTML = Array.from({ length: count }, (_, index) => {
    const number = index + 1;
    return `
      <button class="thumbnail ${number === state.page ? "is-active" : ""}"
        data-page="${number}" title="第 ${number} 页">
        <img loading="lazy"
          src="/api/documents/${state.document.id}/pages/${number}/image?dpi=72"
          alt="第 ${number} 页缩略图">
        <span>${number}</span>
      </button>`;
  }).join("");
  $$(".thumbnail").forEach((button) => {
    button.addEventListener("click", () => loadPage(Number(button.dataset.page)));
  });
}

async function loadPage(number, resetScroll = false) {
  if (!state.document) return;
  const bounded = Math.max(1, Math.min(number, state.document.page_count));
  const token = ++state.loadToken;
  elements.pageLoader.hidden = false;
  try {
    const payload = await request(
      `/api/documents/${state.document.id}/pages/${bounded}`,
    );
    if (token !== state.loadToken) return;
    state.page = bounded;
    state.pageData = payload.page;
    elements.pageNumber.value = bounded;
    elements.previousPage.disabled = bounded <= 1;
    elements.nextPage.disabled = bounded >= state.document.page_count;
    elements.pageImage.src =
      `/api/documents/${state.document.id}/pages/${bounded}/image` +
      `?dpi=${state.renderDpi}`;
    await elements.pageImage.decode().catch(() => undefined);
    if (token !== state.loadToken) return;
    applyZoom();
    renderPageText();
    renderFigures();
    elements.pageSize.textContent =
      `${Math.round(state.pageData.width)} × ${Math.round(state.pageData.height)} pt`;
    $$(".thumbnail").forEach((thumbnail) => {
      thumbnail.classList.toggle(
        "is-active",
        Number(thumbnail.dataset.page) === bounded,
      );
    });
    document
      .querySelector(`.thumbnail[data-page="${bounded}"]`)
      ?.scrollIntoView({ block: "nearest" });
    if (resetScroll) {
      elements.pageViewport.scrollTo({ top: 0, left: 0 });
    }
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (token === state.loadToken) elements.pageLoader.hidden = true;
  }
}

function applyZoom() {
  if (!state.pageData) return;
  const cssWidth = Math.round(
    state.pageData.width * (96 / 72) * (state.zoom / 100),
  );
  elements.pageImage.style.width = `${cssWidth}px`;
  elements.zoomReset.textContent = `${state.zoom}%`;
  elements.renderQuality.textContent = `${state.renderDpi} DPI`;
}

function changeZoom(delta) {
  state.zoom = Math.max(40, Math.min(240, state.zoom + delta));
  state.renderDpi = state.zoom > 150 ? 240 : 160;
  applyZoom();
  if (state.document && state.zoom > 150) {
    const nextSource =
      `/api/documents/${state.document.id}/pages/${state.page}/image` +
      `?dpi=${state.renderDpi}`;
    if (!elements.pageImage.src.endsWith(nextSource)) {
      elements.pageImage.src = nextSource;
    }
  }
}

function renderPageText() {
  const text = (state.pageData?.text || "")
    .split("\n")
    .map((line) => line.trim())
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  elements.textHeading.textContent = `PAGE ${state.page} · TEXT`;
  elements.searchResults.hidden = true;
  elements.pageText.hidden = !text;
  elements.textEmpty.hidden = Boolean(text);
  elements.pageText.textContent = text;
  elements.copyText.disabled = !text;
}

function renderFigures() {
  const figures = state.pageData?.images || [];
  const vectors = state.pageData?.vectors || { path_groups: 0, bbox: [] };
  elements.figuresEmpty.hidden = figures.length > 0 || vectors.path_groups > 0;
  const vectorCard = vectors.path_groups
    ? `
      <article class="figure-card">
        <header>
          <strong>Vector paths</strong>
          <span>RENDERED</span>
        </header>
        <dl>
          <dt>绘制组</dt><dd>${vectors.path_groups}</dd>
          <dt>覆盖范围</dt>
          <dd>${vectors.bbox.slice(0, 2).map(Math.round).join(", ")}</dd>
        </dl>
      </article>`
    : "";
  elements.figureList.innerHTML =
    vectorCard +
    figures
    .map(
      (figure) => `
        <article class="figure-card">
          <header>
            <strong>Image ${String(figure.index).padStart(2, "0")}</strong>
            <span>${figure.xref ? `XREF ${figure.xref}` : "INLINE"}</span>
          </header>
          <dl>
            <dt>像素</dt><dd>${figure.width} × ${figure.height}</dd>
            <dt>颜色通道</dt><dd>${figure.colorspace}</dd>
            <dt>位深</dt><dd>${figure.bits_per_component} bit</dd>
            <dt>页面位置</dt>
            <dd>${figure.bbox.slice(0, 2).map(Math.round).join(", ")}</dd>
          </dl>
        </article>`,
    )
    .join("");
}

function renderOutline() {
  const outline = state.document?.outline || [];
  elements.outlineEmpty.hidden = outline.length > 0;
  elements.outlineList.innerHTML = outline
    .map(
      (item) => `
        <button class="outline-item" data-page="${item.page}"
          style="padding-left: ${8 + Math.max(0, item.level - 1) * 12}px">
          <span>${escapeHtml(item.title)}</span>
          <b>${item.page}</b>
        </button>`,
    )
    .join("");
  $$(".outline-item").forEach((button) => {
    button.addEventListener("click", () => loadPage(Number(button.dataset.page)));
  });
}

function renderMetadata() {
  const item = state.document;
  if (!item) {
    elements.metadata.innerHTML = "";
    return;
  }
  const rows = [
    ["题名", item.title],
    ["作者", item.author || "未写入 PDF 元数据"],
    ["主题", item.subject || "—"],
    ["关键词", item.keywords || "—"],
    ["源文件", item.original_name],
    ["格式", item.source_format.toUpperCase()],
    ["页数", `${item.page_count} 页`],
    ["文件大小", formatBytes(item.source_size)],
    ["SHA-256", item.sha256],
    ["导入时间", new Date(item.imported_at).toLocaleString("zh-CN")],
  ];
  elements.metadata.innerHTML = rows
    .map(
      ([label, value]) => `
        <div><dt>${label}</dt><dd>${escapeHtml(value)}</dd></div>`,
    )
    .join("");
}

async function importFile(file) {
  if (!file) return;
  if (!/\.(pdf|caj)$/i.test(file.name)) {
    showToast("仅支持 PDF 与 CAJ 文件。", true);
    return;
  }
  const data = new FormData();
  data.append("file", file);
  elements.dropzone.classList.add("is-busy");
  const originalLabel = $(".dropzone strong").textContent;
  $(".dropzone strong").textContent = `正在解析 ${file.name}`;
  try {
    const payload = await request("/api/documents/import", {
      method: "POST",
      body: data,
    });
    await loadDocuments(payload.document.id);
    showToast(`已导入：${payload.document.title}`);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    elements.dropzone.classList.remove("is-busy");
    $(".dropzone strong").textContent = originalLabel;
    elements.fileInput.value = "";
  }
}

async function searchDocument(query) {
  if (!state.document || !query.trim()) return;
  activateTab("text");
  elements.textHeading.textContent = `SEARCH · ${query.trim()}`;
  elements.pageText.hidden = true;
  elements.textEmpty.hidden = true;
  elements.searchResults.hidden = false;
  elements.searchResults.innerHTML = `<div class="empty-state"><p>正在检索整篇文档…</p></div>`;
  try {
    const payload = await request(
      `/api/documents/${state.document.id}/search?q=${encodeURIComponent(query)}`,
    );
    if (!payload.results.length) {
      elements.searchResults.innerHTML = `
        <div class="empty-state"><span>0</span><p>没有找到匹配内容。</p></div>`;
      return;
    }
    elements.searchResults.innerHTML = payload.results
      .map(
        (result) => `
          <button class="search-result" data-page="${result.page}">
            <small>PAGE ${result.page}</small>
            ${escapeHtml(result.excerpt)}
          </button>`,
      )
      .join("");
    $$(".search-result").forEach((button) => {
      button.addEventListener("click", () => loadPage(Number(button.dataset.page)));
    });
  } catch (error) {
    showToast(error.message, true);
  }
}

function activateTab(name) {
  $$(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.tab === name);
  });
  $$(".tab-panel").forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === `panel-${name}`);
  });
}

elements.fileInput.addEventListener("change", (event) => {
  importFile(event.target.files[0]);
});
$("#welcome-import").addEventListener("click", () => elements.fileInput.click());
elements.previousPage.addEventListener("click", () => loadPage(state.page - 1));
elements.nextPage.addEventListener("click", () => loadPage(state.page + 1));
elements.pageNumber.addEventListener("change", () =>
  loadPage(Number(elements.pageNumber.value), true),
);
elements.zoomOut.addEventListener("click", () => changeZoom(-20));
elements.zoomIn.addEventListener("click", () => changeZoom(20));
elements.zoomReset.addEventListener("click", () => {
  state.zoom = 100;
  state.renderDpi = 160;
  applyZoom();
});
elements.copyText.addEventListener("click", async () => {
  await navigator.clipboard.writeText(state.pageData?.text || "");
  showToast("当前页正文已复制");
});
elements.searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  searchDocument(elements.searchInput.value);
});
elements.cajCapability.addEventListener("click", () =>
  elements.cajDialog.showModal(),
);
$("#dialog-close").addEventListener("click", () => elements.cajDialog.close());
$("#mobile-library").addEventListener("click", () =>
  elements.libraryPanel.classList.toggle("is-open"),
);

$$(".tab").forEach((tab) => {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

["dragenter", "dragover"].forEach((eventName) => {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.add("is-dragging");
  });
});
["dragleave", "drop"].forEach((eventName) => {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.remove("is-dragging");
  });
});
elements.dropzone.addEventListener("drop", (event) => {
  importFile(event.dataTransfer.files[0]);
});

document.addEventListener("keydown", (event) => {
  const modifier = navigator.platform.includes("Mac") ? event.metaKey : event.ctrlKey;
  if (modifier && event.key.toLowerCase() === "k") {
    event.preventDefault();
    elements.searchInput.focus();
  }
  if (event.target.matches("input")) return;
  if (event.key === "ArrowLeft") loadPage(state.page - 1);
  if (event.key === "ArrowRight") loadPage(state.page + 1);
  if (event.key === "+" || event.key === "=") changeZoom(20);
  if (event.key === "-") changeZoom(-20);
});

Promise.all([loadHealth(), loadDocuments()]).catch((error) => {
  showToast(`本地服务连接失败：${error.message}`, true);
});
