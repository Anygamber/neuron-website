/* USD price converter for the English version.
   Rate: Central Bank of Uzbekistan, cached in memory + localStorage. */
(function () {
  var CBU_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/USD/";
  var CACHE_KEY = "neuron_usd_uzs_v1";
  var CACHE_TTL = 6 * 60 * 60 * 1000;
  var FALLBACK_RATE = 12800;
  /* English USD prices are the local tariff plus 20% for international patients. */
  var FOREIGN_MARKUP = 1.2;
  var AMOUNT_RE = /\d{1,3}(?:[ \u00A0]\d{3})+|\d{5,}/g;

  var memoryRate = null;
  var pending = null;

  function readCache() {
    try {
      var raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || typeof data.rate !== "number" || !isFinite(data.rate) || data.rate < 1000) return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function writeCache(rate) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({ rate: rate, ts: Date.now() }));
    } catch (e) { /* private mode */ }
  }

  function currentRate() {
    if (memoryRate && memoryRate >= 1000) return memoryRate;
    var cached = readCache();
    if (cached && Date.now() - cached.ts < CACHE_TTL) {
      memoryRate = cached.rate;
      return cached.rate;
    }
    return FALLBACK_RATE;
  }

  function parseRate(payload) {
    var row = Array.isArray(payload) ? payload[0] : payload;
    if (!row || row.Rate == null) return 0;
    var rate = parseFloat(String(row.Rate).replace(/\s/g, "").replace(",", "."));
    return isFinite(rate) && rate >= 1000 ? rate : 0;
  }

  function fetchUsdUzsRate() {
    if (pending) return pending;
    var cached = readCache();
    if (cached && Date.now() - cached.ts < CACHE_TTL) {
      memoryRate = cached.rate;
      return Promise.resolve(cached.rate);
    }
    pending = fetch(CBU_URL, { headers: { Accept: "application/json" } })
      .then(function (res) {
        if (!res.ok) throw new Error("cbu " + res.status);
        return res.json();
      })
      .then(function (payload) {
        var rate = parseRate(payload);
        if (!rate) throw new Error("cbu rate");
        memoryRate = rate;
        writeCache(rate);
        return rate;
      })
      .catch(function () {
        if (cached && cached.rate >= 1000) {
          memoryRate = cached.rate;
          return cached.rate;
        }
        memoryRate = FALLBACK_RATE;
        return FALLBACK_RATE;
      })
      .finally(function () {
        pending = null;
      });
    return pending;
  }

  function roundUsd(value) {
    if (!isFinite(value) || value <= 0) return 0;
    var step = 1;
    if (value >= 1000) step = 50;
    else if (value >= 200) step = 10;
    else if (value >= 40) step = 5;
    var rounded = Math.round(value / step) * step;
    if (rounded < 1) return 1;
    return rounded;
  }

  function formatUsd(uzs) {
    var usd = roundUsd((Number(uzs) / currentRate()) * FOREIGN_MARKUP);
    return "$" + usd.toLocaleString("en-US");
  }

  function parseAmounts(raw) {
    var found = String(raw == null ? "" : raw).match(AMOUNT_RE) || [];
    return found.map(function (token) {
      return Number(String(token).replace(/[ \u00A0]/g, ""));
    }).filter(function (n) { return n > 0; });
  }

  function detectMode(raw) {
    var s = String(raw == null ? "" : raw).trim();
    var count = parseAmounts(s).length;
    if (/^(по|each)\b/i.test(s)) return "each";
    if (/^(до|up to)\b/i.test(s)) return "upto";
    if (/от\b/i.test(s) && /до\b/i.test(s) && count >= 2) return "from-to";
    if (/^(от|from)\b/i.test(s)) return count >= 2 ? "from-to" : "from";
    if (count >= 2) return "range";
    return "exact";
  }

  function formatByMode(mode, amounts) {
    var a = formatUsd(amounts[0]);
    var b = amounts[1] ? formatUsd(amounts[1]) : "";
    if (mode === "from") return "from " + a;
    if (mode === "from-to") return "from " + a + " to " + b;
    if (mode === "range") return a + " – " + b;
    if (mode === "each") return "each " + a;
    if (mode === "upto") return "up to " + a;
    return a;
  }

  function formatUzsText(raw) {
    var amounts = parseAmounts(raw);
    if (!amounts.length) return String(raw == null ? "" : raw);
    return formatByMode(detectMode(raw), amounts);
  }

  function isEnglish() {
    return document.documentElement.getAttribute("data-lang") === "en";
  }

  function applyDom() {
    if (!isEnglish()) return;
    document.querySelectorAll("[data-price-uzs]").forEach(function (el) {
      var amounts = String(el.getAttribute("data-price-uzs") || "")
        .split(/[,|]/)
        .map(function (part) { return Number(part); })
        .filter(function (n) { return n > 0; });
      if (!amounts.length) return;
      var dollars = amounts.map(formatUsd);
      var tpl = el.getAttribute("data-price-tpl");
      if (tpl) {
        var html = tpl;
        dollars.forEach(function (dollarsText, index) {
          html = html.split("{" + index + "}").join(dollarsText);
        });
        el.innerHTML = html;
        return;
      }
      el.textContent = formatByMode(el.getAttribute("data-price-mode") || "exact", amounts);
    });
    var note = document.querySelector('[data-i18n="prices.currency"]');
    if (note) {
      var rate = currentRate();
      var shown = (Math.round(rate * 100) / 100).toLocaleString("en-US");
      note.textContent = "USD prices for international patients include a 20% surcharge · 1 USD = " + shown + " UZS (Central Bank of Uzbekistan)";
    }
  }

  function publish(rate, changed) {
    memoryRate = rate;
    applyDom();
    if (changed) {
      window.dispatchEvent(new CustomEvent("neuron:fxupdate", { detail: { rate: rate } }));
    }
  }

  window.addEventListener("neuron:langchange", applyDom);

  function boot() {
    var before = currentRate();
    applyDom();
    fetchUsdUzsRate().then(function (rate) {
      publish(rate, Math.abs(rate - before) > 0.001);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.NeuronFx = {
    CBU_URL: CBU_URL,
    FALLBACK_RATE: FALLBACK_RATE,
    FOREIGN_MARKUP: FOREIGN_MARKUP,
    getRate: currentRate,
    fetchUsdUzsRate: fetchUsdUzsRate,
    formatUsd: formatUsd,
    formatUzsText: formatUzsText,
    parseAmounts: parseAmounts,
    detectMode: detectMode,
    applyDom: applyDom
  };
})();
