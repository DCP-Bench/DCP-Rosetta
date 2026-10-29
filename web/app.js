(function () {
  "use strict";

  var sortKey = "name";
  var sortDirection = 1;
  var FILTER_GROUPS = ["instances", "paradigm", "framework", "language"];
  /* The catalogue shows one problem type at a time, as a tab. */
  var TYPES = ["optimization", "satisfaction"];
  var activeType = TYPES[0];
  /* With a model filter in use, the catalogue shows the problems that have
     a model matching it ("yes") or the ones that have none ("no"). */
  var modelledMode = "yes";

  /* The filters that pick models rather than problems. Each model is tested
     against all of them at once: Choco and Java is Choco's Java models, and
     MIP and Choco is none, as Choco has no MIP model. The catalogue hands
     them to a problem page in its address, and the page shows them as chips. */
  var MODEL_FILTERS = ["paradigm", "framework", "language"];

  function modelMatches(filters, solver, languages, paradigms) {
    function any(picked, values) {
      return !picked.length || values.some(function (value) { return picked.indexOf(value) !== -1; });
    }
    return any(filters.framework, [solver]) && any(filters.language, languages) &&
      any(filters.paradigm, paradigms);
  }

  function anyModelFilter(filters) {
    return MODEL_FILTERS.some(function (group) { return filters[group].length > 0; });
  }

  /* The model filters a query string names. A binding's ID as a solver
     (framework=choco_java, from older links) is its solver and its language. */
  function readModelFilters(search) {
    var params = new URLSearchParams(search);
    var filters = {};
    MODEL_FILTERS.forEach(function (group) {
      filters[group] = params.getAll(group).join(",").split(",").filter(Boolean);
    });
    var bindings = (window.DCP_LABELS && window.DCP_LABELS.binding) || {};
    filters.framework = filters.framework.map(function (value) {
      var binding = bindings[value];
      if (binding && filters.language.indexOf(binding.language) === -1) filters.language.push(binding.language);
      return binding ? binding.solver : value;
    }).filter(function (value, i, all) { return all.indexOf(value) === i; });
    return filters;
  }

  /* `search` with some parameters replaced, or dropped when given null or an
     empty list; the others are kept as written. Lists are joined with commas,
     as the catalogue writes them. */
  function withParams(search, changes) {
    var kept = (search || "").replace(/^\?/, "").split("&").filter(function (pair) {
      return pair && !Object.prototype.hasOwnProperty.call(changes, decodeURIComponent(pair.split("=")[0]));
    });
    Object.keys(changes).forEach(function (key) {
      var value = changes[key];
      if (value === null || value === undefined || (Array.isArray(value) && !value.length)) return;
      var text = Array.isArray(value) ? value.map(encodeURIComponent).join(",") : encodeURIComponent(value);
      kept.push(encodeURIComponent(key) + "=" + text);
    });
    return kept.length ? "?" + kept.join("&") : "";
  }

  /* Names compare by code point, the order generate_site.py gives the
     problem pages' prev/next links. */
  function valueForSort(problem, key) {
    if (key === "instances") return problem.instances || 0;
    if (key === "models") return modelCount(problem);
    return problem.id || "";
  }

  /* Ties on a count keep the problems in name order. */
  function compareProblems(a, b) {
    var av = valueForSort(a, sortKey);
    var bv = valueForSort(b, sortKey);
    var result = av < bv ? -1 : (av > bv ? 1 : 0);
    if (result) return result * sortDirection;
    return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
  }

  function setSort(key) {
    if (sortKey === key) {
      sortDirection *= -1;
    } else {
      sortKey = key;
      sortDirection = 1;
    }
    renderCards();
  }

  function selectedFilterValues(group) {
    var selector = 'input[data-filter-group="' + group + '"]:checked';
    return Array.prototype.map.call(document.querySelectorAll(selector), function (input) {
      return input.value;
    });
  }

  var FILTER_NAMES = { instances: "Instances", paradigm: "Paradigm", framework: "Solver", language: "Language" };

  function catalogueModelFilters() {
    var filters = {};
    MODEL_FILTERS.forEach(function (group) { filters[group] = selectedFilterValues(group); });
    return filters;
  }

  function modelFiltersInUse() {
    return anyModelFilter(catalogueModelFilters());
  }

  /* The models a problem has that the model filters accept, each by its
     integration ID. */
  function matchingModels(problem) {
    var info = (window.DCP_DATA && window.DCP_DATA.modelInfo) || {};
    var filters = catalogueModelFilters();
    return Object.keys(problem.models || {}).filter(function (id) {
      var model = info[id] || {};
      return modelMatches(filters, model.solver, [model.language], problem.models[id]);
    });
  }

  /* The Models column: the solvers with a model of the problem, or with the
     model filters in use, the solvers with a model they accept. Choco's Java
     and Python models count once. */
  function modelCount(problem) {
    var info = (window.DCP_DATA && window.DCP_DATA.modelInfo) || {};
    var ids = modelFiltersInUse() ? matchingModels(problem) : Object.keys(problem.models || {});
    var solvers = {};
    ids.forEach(function (id) { solvers[(info[id] || {}).solver || id] = true; });
    return Object.keys(solvers).length;
  }

  /* A filter in use reads its choice and is marked, so a narrowed list
     never looks like the whole catalogue. */
  function updateFilterButton(group) {
    var values = selectedFilterValues(group);
    var button = document.getElementById("filter-" + group);
    if (!button || !FILTER_NAMES[group]) return;
    var label = FILTER_NAMES[group] + ": ";
    if (!values.length) {
      label += "All";
    } else if (values.length === 1) {
      var input = document.querySelector('input[data-filter-group="' + group + '"][value="' + values[0] + '"]');
      label += input ? input.parentElement.textContent.trim() : "1 selected";
    } else {
      label += values.length + " selected";
    }
    button.textContent = label;
    button.classList.toggle("has-value", values.length > 0);
  }

  function closeMenus() {
    document.querySelectorAll(".filter-menu.open").forEach(function (menu) {
      menu.classList.remove("open");
      var trigger = menu.querySelector(".filter-trigger");
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function initFilterMenus() {
    document.querySelectorAll(".filter-menu").forEach(function (menu) {
      menu.addEventListener("click", function (event) { event.stopPropagation(); });
      var trigger = menu.querySelector(".filter-trigger");
      if (trigger) {
        trigger.addEventListener("click", function () {
          var open = !menu.classList.contains("open");
          closeMenus();
          menu.classList.toggle("open", open);
          trigger.setAttribute("aria-expanded", open ? "true" : "false");
        });
      }
      menu.querySelectorAll('input[data-filter-group]').forEach(function (input) {
        input.addEventListener("change", function () {
          updateFilterButton(input.getAttribute("data-filter-group"));
          renderCards();
        });
      });
      updateFilterButton(menu.getAttribute("data-filter-menu"));
    });
    document.addEventListener("click", closeMenus);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenus();
    });
  }

  /* The catalogue's state lives in its URL, so a filtered view can be shared
     and the "All problems" link on a problem page comes back to it. */
  var CATALOGUE_KEY = "dcp-catalogue";

  function currentQuery() {
    var params = [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim();
    if (q) params.push("q=" + encodeURIComponent(q));
    FILTER_GROUPS.forEach(function (group) {
      var values = selectedFilterValues(group);
      if (values.length) params.push(group + "=" + values.map(encodeURIComponent).join(","));
    });
    if (modelledMode === "no" && modelFiltersInUse()) params.push("modelled=no");
    if (sortKey !== "name" || sortDirection !== 1) {
      params.push("sort=" + (sortDirection === 1 ? "" : "-") + sortKey);
    }
    return params.join("&");
  }

  /* Reset clears the filters, search and sort; the tab stays where it is. */
  function syncState() {
    var query = currentQuery();
    var reset = document.getElementById("reset-filters");
    if (reset) reset.disabled = !query;
    if (activeType !== TYPES[0]) query = "type=" + activeType + (query ? "&" + query : "");
    if (window.history && history.replaceState) {
      history.replaceState(null, "", window.location.pathname + (query ? "?" + query : ""));
    }
    try { sessionStorage.setItem(CATALOGUE_KEY, window.location.href); } catch (e) { /* private mode */ }
  }

  /* With a model filter in use (index.html?framework=choco from the Solvers
     page), a problem link carries the filters to the problem page, which
     shows only the models they accept, and opens one of those rather than
     the reference model: the first picked solver's, and with a language
     picked, on that language's tab. */
  function problemHref(problem) {
    var href = "problems/" + problem.id + ".html";
    var filters = catalogueModelFilters();
    if (!anyModelFilter(filters)) return href;
    var info = window.DCP_DATA.modelInfo || {};
    var matching = matchingModels(problem);
    var first = filters.framework.map(function (solver) {
      return matching.filter(function (id) { return info[id].solver === solver; })[0];
    }).filter(Boolean)[0] || matching[0];
    var changes = { paradigm: filters.paradigm, framework: filters.framework, language: filters.language };
    if (first) changes.model = filters.language.length ? first : info[first].solver;
    return href + withParams("", changes);
  }

  /* Long ids may break after an underscore, never inside a word. */
  function breakable(node, text) {
    text.split("_").forEach(function (part, i, parts) {
      node.appendChild(document.createTextNode(part + (i < parts.length - 1 ? "_" : "")));
      if (i < parts.length - 1) node.appendChild(document.createElement("wbr"));
    });
    return node;
  }

  var COLUMNS = [
    { label: "Name", key: "name" },
    { label: "Description" },
    { label: "Instances", key: "instances", num: true },
    { label: "Models", key: "models", num: true,
      title: "Solvers with an accepted generated model, or with one the paradigm, solver and language filters accept" }
  ];

  function el(tag, className) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    return node;
  }

  function renderTable(container, data) {
    var table = el("table", "plain problem-list");
    var headRow = el("tr");
    COLUMNS.forEach(function (column) {
      var th = el("th", column.num ? "num" : "");
      if (column.title) th.title = column.title;
      if (!column.key) {
        th.textContent = column.label;
      } else {
        var button = el("button", "list-sort");
        button.type = "button";
        button.textContent = column.label +
          (sortKey === column.key ? (sortDirection === 1 ? " \u2191" : " \u2193") : "");
        button.addEventListener("click", function () { setSort(column.key); });
        th.setAttribute("aria-sort", sortKey !== column.key ? "none" :
          (sortDirection === 1 ? "ascending" : "descending"));
        th.appendChild(button);
      }
      headRow.appendChild(th);
    });
    table.appendChild(el("thead")).appendChild(headRow);

    var body = table.appendChild(el("tbody"));
    data.forEach(function (problem) {
      var row = body.appendChild(el("tr"));
      var link = el("a");
      link.href = problemHref(problem);
      breakable(link, problem.id);
      row.appendChild(el("td", "list-name")).appendChild(link);
      row.appendChild(el("td", "list-desc")).appendChild(el("div", "clamp")).textContent = problem.snippet;
      /* No instances: the description fixes the data. */
      var instances = row.appendChild(el("td", "num"));
      instances.textContent = problem.instances ? String(problem.instances) : "\u2013";
      if (!problem.instances) instances.title = "No separate instances: the description fixes the data";
      row.appendChild(el("td", "num")).textContent = String(modelCount(problem));
    });
    container.appendChild(table);
  }

  function renderCards() {
    var countEl = document.getElementById("result-count");
    var sections = document.querySelectorAll(".problem-section");
    if (!sections.length || !window.DCP_DATA) return;

    var data = window.DCP_DATA.problems || [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim().toLowerCase();
    var instances = selectedFilterValues("instances");
    var modelFilters = modelFiltersInUse();

    var filtered = data.filter(function (problem) {
      if (instances.length) {
        var instanceType = problem.instances === 0 ? "none" : (problem.instances === 1 ? "single" : "multiple");
        if (instances.indexOf(instanceType) === -1) return false;
      }
      if (q) {
        /* The whole description is searched, not just the shown snippet. */
        if (problem.haystack === undefined) {
          problem.haystack = (problem.id + " " + (problem.text || problem.snippet)).toLowerCase();
        }
        if (problem.haystack.indexOf(q) === -1) return false;
      }
      return true;
    });

    var switcher = document.querySelector(".mode-switch");
    if (modelFilters) {
      var modelled = function (problem) { return matchingModels(problem).length > 0; };
      var split = { yes: filtered.filter(modelled), no: filtered.filter(function (problem) { return !modelled(problem); }) };
      filtered = split[modelledMode];
      if (switcher) {
        switcher.querySelectorAll(".mode-btn").forEach(function (btn) {
          var mode = btn.getAttribute("data-mode");
          btn.classList.toggle("active", mode === modelledMode);
          btn.setAttribute("aria-pressed", mode === modelledMode ? "true" : "false");
          btn.querySelector(".tab-count").textContent = split[mode].length;
        });
      }
    }
    if (switcher) switcher.hidden = !modelFilters;

    filtered.sort(compareProblems);
    if (countEl) {
      countEl.textContent = filtered.length === data.length ? data.length + " problems"
        : filtered.length + " of " + data.length + " problems match";
    }
    var byType = {};
    TYPES.forEach(function (kind) {
      byType[kind] = filtered.filter(function (problem) {
        return (problem.type || "satisfaction") === kind;
      });
    });
    document.querySelectorAll(".type-tab").forEach(function (tab) {
      var kind = tab.getAttribute("data-type");
      var active = kind === activeType;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.querySelector(".tab-count").textContent = byType[kind].length;
    });
    Array.prototype.forEach.call(sections, function (section) {
      var kind = section.getAttribute("data-type");
      section.hidden = kind !== activeType;
      var container = section.querySelector(".problem-table");
      container.innerHTML = "";
      if (kind !== activeType) return;
      if (byType[kind].length) {
        renderTable(container, byType[kind]);
        return;
      }
      /* Nothing here, but a search may well match in the other tab. */
      var empty = container.appendChild(el("p", "desc empty-state"));
      empty.textContent = "No " + kind + " problems match. ";
      var other = TYPES.filter(function (type) { return type !== kind && byType[type].length; })[0];
      if (other) {
        var jump = empty.appendChild(el("button", "link-btn"));
        jump.type = "button";
        jump.textContent = "Show the " + byType[other].length + " matching " + other + " problem" +
          (byType[other].length === 1 ? "" : "s") + ".";
        jump.addEventListener("click", function () { showType(other); });
      }
    });
    syncState();
  }

  function showType(kind) {
    if (TYPES.indexOf(kind) === -1) return;
    activeType = kind;
    renderCards();
  }

  /* Restore the catalogue from its URL, which is also how another page hands
     it a filter: paradigms.html links index.html?framework=swipl, and
     ?framework=choco&language=java for one interface. A solver's checkbox also
     answers to its bindings' IDs, which older links use: framework=choco_python
     ticks Choco and Python. Unknown values simply match no checkbox. */
  function applyQueryFilters() {
    if (!window.URLSearchParams) return;
    var params = new URLSearchParams(window.location.search);
    var search = document.getElementById("filter-q");
    if (search && params.get("q")) search.value = params.get("q");
    if (TYPES.indexOf(params.get("type")) !== -1) activeType = params.get("type");
    if (params.get("modelled") === "no") modelledMode = "no";
    var sort = params.get("sort") || "";
    var key = sort.replace(/^-/, "");
    if (COLUMNS.some(function (column) { return column.key === key; })) {
      sortKey = key;
      sortDirection = sort.charAt(0) === "-" ? -1 : 1;
    }
    FILTER_GROUPS.forEach(function (group) {
      var values = params.getAll(group).join(",").split(",");
      values.forEach(function (value) {
        if (!value) return;
        value = value.replace(/"/g, "");
        var input = document.querySelector('input[data-filter-group="' + group + '"][value="' + value + '"]');
        var alias = !input && document.querySelector('input[data-filter-group="' + group + '"][data-aliases~="' + value + '"]');
        var model = alias && (window.DCP_DATA.modelInfo || {})[value];
        var language = model && document.querySelector('input[data-filter-group="language"][value="' + model.language + '"]');
        if (language) language.checked = true;
        if (input || alias) (input || alias).checked = true;
      });
      updateFilterButton(group);
    });
  }

  function initIndex() {
    if (!window.DCP_DATA) return;
    initFilterMenus();
    applyQueryFilters();
    var search = document.getElementById("filter-q");
    if (search) search.addEventListener("input", renderCards);
    document.querySelectorAll(".type-tab").forEach(function (tab) {
      tab.addEventListener("click", function () { showType(tab.getAttribute("data-type")); });
    });
    document.querySelectorAll(".mode-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        modelledMode = btn.getAttribute("data-mode");
        renderCards();
      });
    });
    var reset = document.getElementById("reset-filters");
    if (reset) reset.addEventListener("click", function () {
      var searchInput = document.getElementById("filter-q");
      if (searchInput) searchInput.value = "";
      document.querySelectorAll('input[data-filter-group]').forEach(function (input) {
        input.checked = false;
      });
      closeMenus();
      FILTER_GROUPS.forEach(updateFilterButton);
      sortKey = "name";
      sortDirection = 1;
      modelledMode = "yes";
      renderCards();
    });
    renderCards();
  }

  function escHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* Where a URL in prose ends: before trailing punctuation, and before a
     closing parenthesis it did not open. url_end in generate_site.py does the
     same for the metadata links. */
  function urlEnd(url) {
    var end = url.length;
    while (end) {
      var ch = url.charAt(end - 1);
      var head = url.slice(0, end);
      if (".,;:!?'".indexOf(ch) !== -1 ||
          (ch === ")" && head.split("(").length < head.split(")").length)) {
        end -= 1;
      } else {
        break;
      }
    }
    return end;
  }

  /* Escape text and wrap its URLs in links. */
  function linkify(text) {
    var out = "";
    var last = 0;
    var pattern = /https?:\/\/[^\s<>"]+/g;
    var match;
    while ((match = pattern.exec(text))) {
      var url = match[0].slice(0, urlEnd(match[0]));
      out += escHtml(text.slice(last, match.index)) + '<a href="' + escHtml(url).replace(/"/g, "&quot;") +
        '" target="_blank" rel="noopener">' + escHtml(url) + "</a>";
      last = match.index + url.length;
      pattern.lastIndex = last;
    }
    return out + escHtml(text.slice(last));
  }

  /* $$..$$, \[..\], \(..\), and $..$ only where it cannot be a price:
     "$20 and $5" stays text. MATH_RE in generate_site.py matches the same,
     to decide which pages load KaTeX. */
  var MATH = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?=[^\s\d$])([^$\n]*?[^\s$\\])\$(?!\d)/g;

  /* Some descriptions escape their backslashes for Markdown: \\times for
     \times, \\* for a plain asterisk. */
  function renderMath(source, tex, display) {
    if (!window.katex) return escHtml(source);
    tex = tex.replace(/\\\\\*/g, "*").replace(/\\\\(?=[A-Za-z])/g, "\\");
    return katex.renderToString(tex, { displayMode: display, throwOnError: false });
  }

  /* Math is set aside before Markdown runs, so that a_1 and a_m are not
     read as emphasis, and put back as KaTeX afterwards. */
  function initMarkdown() {
    if (!window.marked) return;
    document.querySelectorAll(".md-desc").forEach(function (el) {
      var maths = [];
      var text = el.textContent.replace(MATH, function (all, block, bracket, paren, dollar) {
        var display = block !== undefined || bracket !== undefined;
        maths.push(renderMath(all, block || bracket || paren || dollar, display));
        return "MATHTOKEN" + (maths.length - 1) + "END";
      });
      text = text.replace(/\\\\\*/g, "\\*");
      el.innerHTML = marked.parse(linkify(text)).replace(/MATHTOKEN(\d+)END/g, function (token, i) {
        return maths[Number(i)];
      });
    });
  }

  function initTabs() {
    var model = window.URLSearchParams ? new URLSearchParams(window.location.search).get("model") : null;
    document.querySelectorAll(".tab-group").forEach(function (group) {
      var bar = group.querySelector(".tab-bar");
      if (!bar) return;
      var buttons = bar.querySelectorAll(".tab-btn");
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var name = btn.getAttribute("data-tab");
          buttons.forEach(function (b) { b.classList.toggle("active", b === btn); });
          Array.prototype.forEach.call(group.children, function (el) {
            if (el.classList.contains("tab-pane")) {
              el.classList.toggle("active", el.getAttribute("data-pane") === name);
            }
          });
        });
      });
      /* problems/x.html?model=choco opens that solver's tab and scrolls to it;
         ?model=choco_python opens the solver, then its Python tab. */
      var name = model && model.replace(/"/g, "");
      var wanted = name && (bar.querySelector('.tab-btn[data-tab="' + name + '"]') ||
        bar.querySelector('.tab-btn[data-aliases~="' + name + '"]'));
      if (wanted) {
        wanted.click();
        (group.closest(".page-section") || group).scrollIntoView();
      }
    });
  }

  /* Solvers page: a paradigm row expands to the solvers behind it. A link to
     #cp, or to anything inside that group, opens the group it lands in. One
     button shows or hides every group at once. */
  function initParadigms() {
    var groups = document.querySelectorAll("tbody.paradigm");
    if (!groups.length) return;
    var expandAll = document.querySelector(".expand-all");
    var toggles = Array.prototype.filter.call(groups, function (group) {
      return group.querySelector(".row-toggle[aria-expanded]");
    });

    function syncExpandAll() {
      if (!expandAll) return;
      var allOpen = toggles.every(function (group) {
        return !group.classList.contains("collapsed");
      });
      expandAll.textContent = allOpen ? "Hide all" : "Show all";
      expandAll.setAttribute("aria-pressed", allOpen ? "true" : "false");
    }

    function setOpen(group, open) {
      var btn = group.querySelector(".row-toggle[aria-expanded]");
      if (!btn) return;
      group.classList.toggle("collapsed", !open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      syncExpandAll();
    }

    if (expandAll) {
      expandAll.addEventListener("click", function () {
        var open = expandAll.getAttribute("aria-pressed") !== "true";
        toggles.forEach(function (group) { setOpen(group, open); });
      });
    }

    Array.prototype.forEach.call(groups, function (group) {
      var row = group.querySelector(".paradigm-row");
      row.addEventListener("click", function (event) {
        if (event.target.closest("a, .info-wrap")) return;
        setOpen(group, group.classList.contains("collapsed"));
      });
    });

    function openFromHash() {
      if (!location.hash) return;
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      var group = target && target.closest("tbody.paradigm");
      if (group) setOpen(group, true);
    }
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
  }

  function initCopy() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var target = document.getElementById(btn.getAttribute("data-copy"));
        if (!target) return;
        var done = function () {
          var old = btn.textContent;
          btn.classList.add("copied");
          btn.textContent = "Copied ✓";
          setTimeout(function () {
            btn.textContent = old;
            btn.classList.remove("copied");
          }, 1200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(target.textContent).then(done, done);
        } else {
          done();
        }
      });
    });
  }

  /* Point a link to the catalogue at the catalogue as it was left: its
     search, sort, tab and filters, kept in this tab's session. With `filters`,
     the model filters a problem page now has replace the ones it was left with. */
  function catalogueLink(link, filters) {
    var base = link.getAttribute("href").split("?")[0];
    var search = "";
    var left;
    try { left = sessionStorage.getItem(CATALOGUE_KEY); } catch (e) { left = null; }
    if (left) {
      var at = new URL(left, window.location.href);
      var here = new URL(base, window.location.href);
      if (at.pathname.replace(/index\.html$/, "") === here.pathname.replace(/index\.html$/, "")) search = at.search;
    }
    if (filters) {
      var changes = { paradigm: filters.paradigm, framework: filters.framework, language: filters.language };
      /* "Not modelled" means nothing once no model filter is left. */
      if (!anyModelFilter(filters)) changes.modelled = null;
      search = withParams(search, changes);
    }
    link.href = base + search;
  }

  function catalogueNavLink() {
    return document.querySelector('header nav a[href$="index.html"]');
  }

  /* Pages other than the catalogue and a problem page (which keeps its own
     links in step with its filters): the nav returns to the catalogue as left. */
  function initBackLink() {
    if (document.getElementById("filter-q") || document.querySelector(".model-group")) return;
    var nav = catalogueNavLink();
    if (nav) catalogueLink(nav, null);
  }

  /* Programmatic tab switches that should not rewrite the address. */
  var quietClicks = 0;

  function quietClick(button) {
    quietClicks += 1;
    try { button.click(); } finally { quietClicks -= 1; }
  }

  /* Problem pages: the model filters the catalogue handed over in the
     address (?paradigm=mip&framework=scip&language=python), shown as chips
     above the models. Only the models they accept are offered, and a chip's
     × removes its filter. The address, the way back to the catalogue and the
     previous/next links all follow, so the filters hold from page to page
     until removed, here or in the catalogue. */
  function initModelFilters() {
    var group = document.querySelector(".model-group");
    var bar = document.querySelector(".model-filters");
    if (!group || !bar || !window.URLSearchParams) return;
    var labels = window.DCP_LABELS || {};
    var filters = readModelFilters(window.location.search);
    /* Whether this page has a say in the catalogue's model filters: it was
       opened with some, or one was removed here. Opened without any, it
       leaves the catalogue's as they were. */
    var own = anyModelFilter(filters);
    var chips = Array.prototype.slice.call(group.querySelectorAll(".model-picker .tab-btn[data-paradigms]"));
    var reference = group.querySelector('.model-picker .tab-btn[data-tab="ground_truth"]');
    var crumb = document.querySelector(".crumb");
    var nav = catalogueNavLink();
    var pager = Array.prototype.slice.call(document.querySelectorAll(".pager a"));
    pager.forEach(function (link) { link.setAttribute("data-base", link.getAttribute("href").split("?")[0]); });

    function words(text) { return (text || "").split(" ").filter(Boolean); }

    function accepted(chip) {
      return modelMatches(filters, chip.getAttribute("data-tab"), words(chip.getAttribute("data-languages")),
        words(chip.getAttribute("data-paradigms")));
    }

    function apply() {
      var shown = chips.filter(function (chip) {
        chip.hidden = !accepted(chip);
        return !chip.hidden;
      });
      group.querySelectorAll(".model-picker .picker-row:not(.reference-row)").forEach(function (row) {
        row.hidden = !row.querySelector(".tab-btn:not([hidden])");
      });
      group.querySelectorAll(".binding-bar").forEach(function (tabs) {
        tabs.querySelectorAll(".tab-btn").forEach(function (tab) {
          tab.hidden = filters.language.length > 0 && filters.language.indexOf(tab.getAttribute("data-language")) === -1;
        });
        /* A language tab the filters hide gives way to the first they keep. */
        var active = tabs.querySelector(".tab-btn.active");
        var first = tabs.querySelector(".tab-btn:not([hidden])");
        if (active && active.hidden && first) quietClick(first);
      });
      render(shown.length);
    }

    function label(key, value) {
      return ((labels[key] || {})[value]) || value;
    }

    function render(shown) {
      bar.innerHTML = "";
      bar.hidden = !anyModelFilter(filters);
      if (bar.hidden) return;
      bar.appendChild(el("span", "filter-label")).textContent = "Filtered by";
      var count = 0;
      MODEL_FILTERS.forEach(function (key) {
        filters[key].forEach(function (value) {
          count += 1;
          var chip = bar.appendChild(el("button", "filter-chip"));
          chip.type = "button";
          chip.title = "Remove this filter";
          chip.setAttribute("aria-label", "Remove the filter " + FILTER_NAMES[key] + ": " + label(key, value));
          chip.appendChild(el("span", "filter-chip-group")).textContent = FILTER_NAMES[key];
          chip.appendChild(el("span", "filter-chip-value")).textContent = label(key, value);
          var x = chip.appendChild(el("span", "filter-chip-x"));
          x.setAttribute("aria-hidden", "true");
          x.textContent = "\u00d7";
          chip.addEventListener("click", function () { remove(key, value); });
        });
      });
      if (count > 1) {
        var clear = bar.appendChild(el("button", "link-btn filter-clear"));
        clear.type = "button";
        clear.textContent = "Clear all";
        clear.addEventListener("click", function () { remove(null, null); });
      }
      bar.appendChild(el("span", "filter-count")).textContent =
        shown + " of " + chips.length + " model" + (chips.length === 1 ? "" : "s");
      if (!shown) {
        bar.appendChild(el("p", "filter-empty")).textContent =
          "No model of this problem matches these filters; the reference model is shown.";
      }
    }

    /* Keep the address and every way off the page in step with the filters,
       and once this page has a say, hand them to the catalogue as well. */
    function sync() {
      var changes = { paradigm: filters.paradigm, framework: filters.framework, language: filters.language };
      if (window.history && history.replaceState) {
        history.replaceState(null, "", window.location.pathname + withParams(window.location.search, changes) +
          window.location.hash);
      }
      pager.forEach(function (link) { link.href = link.getAttribute("data-base") + withParams("", changes); });
      [crumb, nav].forEach(function (link) { if (link) catalogueLink(link, own ? filters : null); });
      if (own && crumb) {
        try { sessionStorage.setItem(CATALOGUE_KEY, crumb.href); } catch (e) { /* private mode */ }
      }
    }

    function remove(key, value) {
      MODEL_FILTERS.forEach(function (group) {
        if (key === null || group === key) {
          filters[group] = filters[group].filter(function (item) { return key !== null && item !== value; });
        }
      });
      own = true;
      apply();
      sync();
      var next = bar.querySelector(".filter-chip") || group.querySelector(".model-picker .tab-btn.active");
      if (next) next.focus();
    }

    apply();
    /* Open a model the filters accept: the one the address names when they
       accept it, else the first offered. With none, the reference. */
    var active = group.querySelector(".model-picker .tab-btn.active");
    var named = new URLSearchParams(window.location.search).get("model");
    if (anyModelFilter(filters) && active && (active.hidden || (!named && active === reference))) {
      var offered = chips.filter(function (chip) { return !chip.hidden; })[0];
      quietClick(offered || reference);
    }
    sync();
  }

  /* Problem pages: the left and right arrow keys step through the models in
     the order of the pills, wrapping round, while the Models section is on
     screen. On a device with a keyboard, a hint says so whenever the section
     is on screen, until the reader closes it. */
  var HINT_CLOSED = "dcp-model-keys-hint-closed";

  function stored(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }

  /* The light theme is the default. The button in the nav switches to dark
     and back, and the choice holds on every page until it is switched again. */
  var THEME_KEY = "dcp-theme";

  function initTheme() {
    var toggle = document.querySelector(".theme-toggle");
    if (!toggle) return;
    var root = document.documentElement;
    var meta = document.querySelector('meta[name="theme-color"]');
    function sync() {
      var dark = root.getAttribute("data-theme") === "dark";
      toggle.setAttribute("aria-pressed", dark ? "true" : "false");
      toggle.title = dark ? "Switch to the light theme" : "Switch to the dark theme";
      if (meta) meta.setAttribute("content", getComputedStyle(root).getPropertyValue("--bg").trim());
    }
    sync();
    toggle.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") !== "dark";
      function apply() {
        if (dark) root.setAttribute("data-theme", "dark");
        else root.removeAttribute("data-theme");
        sync();
      }
      store(THEME_KEY, dark ? "dark" : "light");
      /* A cross-fade between the themes, where the browser has one. */
      var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (document.startViewTransition && !still) document.startViewTransition(apply);
      else apply();
    });
  }

  function initModelKeys() {
    var group = document.querySelector(".model-group");
    if (!group) return;
    var section = group.closest(".page-section") || group;
    var buttons = Array.prototype.slice.call(group.querySelectorAll(".model-picker .tab-btn"));
    if (buttons.length < 2) return;

    /* The address names the model on show, so a copied link opens it: the
       solver, or the binding once a language tab is picked. */
    var tabs = buttons.concat(Array.prototype.slice.call(group.querySelectorAll(".binding-bar .tab-btn")));
    tabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (quietClicks || !window.history || !history.replaceState) return;
        var name = btn.getAttribute("data-tab");
        var query = withParams(window.location.search, { model: name === "ground_truth" ? null : name });
        history.replaceState(null, "", window.location.pathname + query + window.location.hash);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.defaultPrevented) return;
      if (event.target.closest && event.target.closest("input, textarea, select, [contenteditable]")) return;
      var box = group.getBoundingClientRect();
      if (box.top >= window.innerHeight || box.bottom <= 0) return;
      /* Only the models the filters offer. */
      var offered = buttons.filter(function (btn) { return !btn.hidden; });
      var current = 0;
      offered.forEach(function (btn, i) {
        if (btn.classList.contains("active")) current = i;
      });
      var step = event.key === "ArrowRight" ? 1 : -1;
      offered[(current + step + offered.length) % offered.length].click();
      /* A shorter model could leave the reader below it: bring the pills back. */
      if (section.getBoundingClientRect().top < 0) section.scrollIntoView();
      event.preventDefault();
    });

    var keyboard = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (stored(HINT_CLOSED) || !keyboard || !window.IntersectionObserver) return;
    var hint = document.createElement("div");
    hint.className = "key-hint";
    hint.setAttribute("role", "status");
    hint.innerHTML = '<kbd>←</kbd><kbd>→</kbd><span>switch models</span>' +
      '<button type="button" aria-label="Close this hint">×</button>';
    document.body.appendChild(hint);
    /* Any part of the section on screen counts: a long model can be taller
       than the window, so a share of it would never be visible. */
    var observer = new IntersectionObserver(function (entries) {
      hint.classList.toggle("shown", entries[entries.length - 1].isIntersecting);
    });
    observer.observe(group);
    hint.querySelector("button").addEventListener("click", function () {
      store(HINT_CLOSED, "1");
      observer.disconnect();
      hint.remove();
    });
  }

  function init() {
    initTheme();
    initIndex();
    initBackLink();
    initMarkdown();
    initTabs();
    initModelKeys();
    initModelFilters();
    initCopy();
    initParadigms();
    if (window.hljs) hljs.highlightAll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
