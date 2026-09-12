(function () {
  const icons = {
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
    basket: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m7 11 2-7"/><path d="m17 11-2-7"/><path d="M3 11h18l-2 9H5z"/></svg>',
    apple: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 7c2-3 5-3 6-1-2 0-4 2-4 4"/><path d="M12 8C9 5 4 7 4 12c0 4 3 8 6 8 1 0 1.5-.5 2-.5s1 .5 2 .5c3 0 6-4 6-8 0-5-5-7-8-4Z"/></svg>',
    milk: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 2h6v4l2 3v11a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V9l2-3Z"/><path d="M8 12h8"/></svg>',
    snow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/></svg>',
    can: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5"/><path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg>',
    sparkles: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8Z"/></svg>',
    "arrow-right": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>'
  };

  const state = {
    data: { categories: [], products: [] },
    activeCategory: "all",
    query: ""
  };

  const els = {
    categoryContainers: Array.from(document.querySelectorAll("[data-header-categories], [data-hero-categories]")),
    products: document.querySelector("[data-products]"),
    searches: Array.from(document.querySelectorAll("[data-search]")),
    clearSearchButtons: Array.from(document.querySelectorAll("[data-clear-search]")),
    empty: document.querySelector("[data-empty]"),
    resultsCount: document.querySelector("[data-results-count]"),
  };

  document.querySelectorAll("[data-icon]").forEach((node) => {
    node.innerHTML = icons[node.dataset.icon] || icons.basket;
  });

  function normalize(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/[أإآ]/g, "ا")
      .replace(/ة/g, "ه")
      .replace(/ى/g, "ي")
      .trim();
  }

  function money(value) {
    return new Intl.NumberFormat("ar-EG", { maximumFractionDigits: 2 }).format(value);
  }

  function categoryById(id) {
    return state.data.categories.find((cat) => cat.id === id);
  }

  function renderHeaderCategories() {
    if (!els.categoryContainers.length) return;

    const allButton = headerCategoryLink({ id: "all", name: "كل المنتجات" });
    const categoryButtons = state.data.categories.map((category) => headerCategoryLink(category));
    const markup = [allButton, ...categoryButtons].join("");
    els.categoryContainers.forEach((container) => {
      container.innerHTML = markup;
    });
  }

  function headerCategoryLink(category) {
    const active = category.id === state.activeCategory ? " active" : "";
    return `
      <a class="category-link${active}" href="#" data-category-id="${category.id}">
        ${category.name}
      </a>
    `;
  }

  function filteredProducts() {
    const query = normalize(state.query);
    const queryWords = query.split(' ').filter(w => w.length > 0);

    return state.data.products
      .filter((item) => {
        if (state.activeCategory === "all") return true;
        return item.categoryId === state.activeCategory;
      })
      .filter((item) => {
        if (queryWords.length === 0) return true;
        const haystack = normalize(`${item.name} ${item.unit} ${categoryById(item.categoryId)?.name || ""}`);
        return queryWords.every(word => haystack.includes(word));
      });
  }

  function renderProducts() {
    const products = filteredProducts();
    if (!els.products) return;
    els.products.innerHTML = products.map(productCard).join("");

    const categoryName = state.activeCategory === "all" ? "كل الأقسام" : categoryById(state.activeCategory)?.name || "القسم";
    if (els.resultsCount) {
      els.resultsCount.textContent = `${products.length} منتج في ${categoryName}`;
    }
    if (els.empty) {
      els.empty.hidden = products.length > 0;
    }
  }

  function syncSearchInputs(source) {
    els.searches.forEach((input) => {
      if (input !== source) input.value = state.query;
    });
  }

  function updateHeaderState() {
    document.body.classList.toggle("is-scrolled", window.scrollY > 180);
  }

  function productCard(product) {
    const category = categoryById(product.categoryId);
    const status = product.status || (product.available !== false ? "متوفر" : "غير موجود حاليا");
    const isUnavailable = status !== "متوفر";
    const image = product.image
      ? `<img src="${product.image}" alt="${product.name}" loading="lazy" decoding="async" width="900" height="900">`
      : `<div class="placeholder" aria-hidden="true">${icons[category?.icon || "basket"] || icons.basket}</div>`;

    return `
      <article class="product-card${isUnavailable ? " unavailable" : ""}">
        <div class="product-media">${image}</div>
        <div class="product-body">
          <div>
            <h3>${product.name}</h3>
            <span class="status-badge ${isUnavailable ? "status-unavailable" : "status-available"}">${status}</span>
          </div>
          <div class="product-meta">
            <span class="price">${money(product.price)} <small>جنيه</small></span>
            <span class="unit">${product.unit}</span>
          </div>
        </div>
      </article>
    `;
  }

  function render() {
    renderHeaderCategories();
    renderProducts();
  }

  async function init() {
    try {
      const response = await fetch("data/products.json", { cache: "no-store" });
      if (!response.ok) throw new Error("Data file not found");
      state.data = await response.json();
      
      state.activeCategory = 'all';
      render();
    } catch (error) {
      if (els.resultsCount) els.resultsCount.textContent = "تعذر تحميل ملف المنتجات.";
      if (els.products) els.products.innerHTML = "";
      if (els.empty) els.empty.hidden = false;
      console.error(error);
    }
  }

  els.categoryContainers.forEach((container) => {
    container.addEventListener("click", (event) => {
      const link = event.target.closest(".category-link");
      if (link && link.dataset.categoryId) {
        event.preventDefault();
        state.activeCategory = link.dataset.categoryId;
        render();
      }
    });
  });

  els.searches.forEach((input) => {
    input.addEventListener("input", (event) => {
      state.query = event.target.value;
      syncSearchInputs(event.target);
      renderProducts();
    });
  });

  els.clearSearchButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.query = "";
      syncSearchInputs();
      renderProducts();
      const formSearch = button.closest("form")?.querySelector("[data-search]");
      formSearch?.focus();
    });
  });

  window.addEventListener("scroll", updateHeaderState, { passive: true });
  window.addEventListener("load", updateHeaderState);
  window.addEventListener("pageshow", updateHeaderState);
  updateHeaderState();

  init();
})();
