/* First-screen city panel and Ministry of Health news.
   Rates, weather, Kp and AQI paint from cache or a recent snapshot, then refresh. */
(function () {
  var FX_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/";
  var WX_URL = "https://api.open-meteo.com/v1/forecast?latitude=41.2995&longitude=69.2401&current=temperature_2m,weather_code,is_day&timezone=Asia/Tashkent";
  var AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=41.2995&longitude=69.2401&current=us_aqi,pm2_5";
  var KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json";
  var NEWS_URL = "https://api-portal.gov.uz/authorities/news/category?code_name=news&page=1";

  var TTL = {
    fx: 6 * 60 * 60 * 1000,
    wx: 30 * 60 * 1000,
    aq: 30 * 60 * 1000,
    kp: 30 * 60 * 1000,
    news: 20 * 60 * 1000
  };

  var FALLBACK = {
    fx: { USD: 12055.9, EUR: 13572.53, RUB: 144.16, date: "17.10.2026" },
    wx: { temp: 19.5, code: 0, isDay: 1 },
    aq: { aqi: 89, pm: 27 },
    kp: { kp: 0.33 }
  };

  var COPY = {
    ru: {
      clear: "Ясно",
      mainly: "Малооблачно",
      cloudy: "Облачно",
      overcast: "Пасмурно",
      fog: "Туман",
      drizzle: "Морось",
      rain: "Дождь",
      snow: "Снег",
      showers: "Ливни",
      storm: "Гроза",
      quiet: "Спокойно",
      unsettled: "Неустойчиво",
      gstorm: "Магнитная буря",
      good: "Хорошее",
      moderate: "Умеренное",
      sensitive: "Вредно для чувствительных",
      unhealthy: "Вредное",
      very: "Очень вредное",
      hazardous: "Опасное"
    },
    uz: {
      clear: "Ochiq",
      mainly: "Kam bulutli",
      cloudy: "Bulutli",
      overcast: "Bulutli",
      fog: "Tuman",
      drizzle: "Mayda yomg‘ir",
      rain: "Yomg‘ir",
      snow: "Qor",
      showers: "Jala",
      storm: "Momaqaldiroq",
      quiet: "Tinch",
      unsettled: "Beqaror",
      gstorm: "Magnit bo‘roni",
      good: "Yaxshi",
      moderate: "O‘rtacha",
      sensitive: "Sezgirlar uchun zararli",
      unhealthy: "Zararli",
      very: "Juda zararli",
      hazardous: "Xavfli"
    },
    en: {
      clear: "Clear",
      mainly: "Mainly clear",
      cloudy: "Cloudy",
      overcast: "Overcast",
      fog: "Fog",
      drizzle: "Drizzle",
      rain: "Rain",
      snow: "Snow",
      showers: "Showers",
      storm: "Thunderstorm",
      quiet: "Quiet",
      unsettled: "Unsettled",
      gstorm: "Geomagnetic storm",
      good: "Good",
      moderate: "Moderate",
      sensitive: "Unhealthy for sensitive groups",
      unhealthy: "Unhealthy",
      very: "Very unhealthy",
      hazardous: "Hazardous"
    }
  };

  function lang() {
    var value = (document.documentElement.getAttribute("data-lang") || "uz").toLowerCase();
    return value === "ru" || value === "en" || value === "uz" ? value : "uz";
  }

  function text(key) {
    if (window.NeuronI18n && window.NeuronI18n.t) {
      var value = window.NeuronI18n.t(lang(), key);
      if (value) return value;
    }
    return "";
  }

  function copy(key) {
    return (COPY[lang()] || COPY.uz)[key] || COPY.en[key] || "";
  }

  function govLang() {
    return lang() === "ru" ? "ru" : lang() === "en" ? "en" : "oz";
  }

  function readCache(key) {
    try {
      var data = JSON.parse(localStorage.getItem(key) || "null");
      if (!data || !data.payload) return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function writeCache(key, payload) {
    try {
      localStorage.setItem(key, JSON.stringify({ ts: Date.now(), payload: payload }));
    } catch (e) { /* private mode */ }
  }

  function fresh(entry, ttl) {
    return !!(entry && Date.now() - entry.ts < ttl);
  }

  function formatRate(value) {
    var parts = Number(value).toFixed(2).split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    return parts[0] + "." + parts[1];
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function weatherKey(code) {
    var n = Number(code);
    if (n === 0) return "clear";
    if (n === 1 || n === 2) return "mainly";
    if (n === 3) return "overcast";
    if (n === 45 || n === 48) return "fog";
    if (n >= 51 && n <= 57) return "drizzle";
    if (n >= 61 && n <= 67) return "rain";
    if (n >= 71 && n <= 77) return "snow";
    if (n >= 80 && n <= 82) return "showers";
    if (n >= 95) return "storm";
    return "cloudy";
  }

  function weatherIcon(code) {
    var kind = weatherKey(code);
    if (kind === "clear" || kind === "mainly") {
      return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.1 5.1l1.6 1.6M17.3 17.3l1.6 1.6M18.9 5.1l-1.6 1.6M6.7 17.3l-1.6 1.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
    }
    if (kind === "rain" || kind === "drizzle" || kind === "showers" || kind === "storm") {
      return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 16h10a4 4 0 0 0 .4-8 5.5 5.5 0 0 0-10.6 1.6A3.5 3.5 0 0 0 7 16z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9 18.5l-.8 2M12 18.5l-.8 2M15 18.5l-.8 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
    }
    if (kind === "snow") {
      return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v18M4.5 7.5l15 9M19.5 7.5l-15 9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
    }
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17h11a4 4 0 0 0 .3-8 6 6 0 0 0-11.5 1.5A3.5 3.5 0 0 0 7 17z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';
  }

  function kpLevel(kp) {
    var n = Number(kp);
    if (n >= 5) return { key: "gstorm", tone: "bad" };
    if (n >= 4) return { key: "unsettled", tone: "warn" };
    return { key: "quiet", tone: "ok" };
  }

  function aqiLevel(aqi) {
    var n = Number(aqi);
    if (n <= 50) return { key: "good", tone: "ok" };
    if (n <= 100) return { key: "moderate", tone: "warn" };
    if (n <= 150) return { key: "sensitive", tone: "warn" };
    if (n <= 200) return { key: "unhealthy", tone: "bad" };
    if (n <= 300) return { key: "very", tone: "bad" };
    return { key: "hazardous", tone: "bad" };
  }

  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function setTone(id, tone) {
    var el = document.getElementById(id);
    if (el) el.setAttribute("data-tone", tone);
  }

  function paintFx(payload) {
    var box = document.getElementById("pulseFxRates");
    if (!box || !payload) return;
    var rows = [
      ["USD", payload.USD],
      ["EUR", payload.EUR],
      ["RUB", payload.RUB]
    ];
    box.innerHTML = rows.map(function (row) {
      return "<span><b>" + row[0] + "</b> " + formatRate(row[1]) + "</span>";
    }).join("");
    var link = document.getElementById("pulseFx");
    if (link) {
      var cbu = lang() === "en" ? "en" : lang() === "ru" ? "ru" : "uz";
      link.href = "https://cbu.uz/" + cbu + "/arkhiv-kursov-valyut/";
    }
  }

  function paintWx(payload) {
    if (!payload) return;
    var icon = document.getElementById("pulseWxIcon");
    if (icon) icon.innerHTML = weatherIcon(payload.code);
    setText("pulseWxTemp", Math.round(Number(payload.temp)) + "°");
    setText("pulseWxState", copy(weatherKey(payload.code)) + " · " + text("pulse.wxCity"));
  }

  function paintKp(payload) {
    if (!payload) return;
    var level = kpLevel(payload.kp);
    var shown = Number(payload.kp);
    setText("pulseKpValue", "Kp " + (Math.round(shown * 10) / 10));
    setText("pulseKpState", copy(level.key));
    setTone("pulseKp", level.tone);
  }

  function paintAq(payload) {
    if (!payload) return;
    var level = aqiLevel(payload.aqi);
    setText("pulseAqValue", String(Math.round(Number(payload.aqi))));
    setText("pulseAqState", copy(level.key) + " · " + text("pulse.pm") + " " + Math.round(Number(payload.pm)));
    setTone("pulseAq", level.tone);
  }

  function paintNotes() {
    setText("pulseWxNote", text("pulse.noteWx"));
    setText("pulseKpNote", text("pulse.noteKp"));
    setText("pulseAqNote", text("pulse.noteAq"));
  }

  function portalHref() {
    return "https://gov.uz/" + govLang() + "/ssv";
  }

  function articleHref(id) {
    return "https://gov.uz/" + govLang() + "/ssv/news/view/" + encodeURIComponent(id);
  }

  function formatDate(raw) {
    var match = String(raw || "").match(/(\d{4})-(\d{2})-(\d{2})/);
    if (!match) return "";
    return match[3] + "." + match[2] + "." + match[1];
  }

  function paintNews(items) {
    var grid = document.getElementById("mohGrid");
    var portal = document.getElementById("mohPortal");
    if (portal) portal.href = portalHref();
    if (!grid) return;
    var list = Array.isArray(items) ? items.slice(0, 3) : [];
    if (!list.length) {
      grid.innerHTML =
        '<article class="moh-card moh-card--empty">' +
          "<h3>" + escapeHtml(text("moh.emptyTitle")) + "</h3>" +
          "<p>" + escapeHtml(text("moh.emptyText")) + "</p>" +
          '<a class="moh-more" href="' + escapeHtml(portalHref()) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(text("moh.all")) + "</a>" +
        "</article>";
      return;
    }
    grid.innerHTML = list.map(function (item) {
      var iso = String(item.date || "").slice(0, 10);
      var summary = String(item.anons || "").replace(/\s+/g, " ").trim();
      if (summary.length > 220) summary = summary.slice(0, 217).replace(/\s+\S*$/, "") + "…";
      return (
        '<article class="moh-card">' +
          '<time datetime="' + escapeHtml(iso) + '">' + escapeHtml(formatDate(item.date)) + "</time>" +
          "<h3>" + escapeHtml(item.title || "") + "</h3>" +
          "<p>" + escapeHtml(summary) + "</p>" +
          '<a class="moh-more" href="' + escapeHtml(articleHref(item.id)) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(text("moh.read")) + "</a>" +
        "</article>"
      );
    }).join("");
  }

  function bindToggles() {
    document.querySelectorAll(".pulse-card[data-pulse-toggle]").forEach(function (card) {
      if (card.dataset.bound) return;
      card.dataset.bound = "1";
      card.addEventListener("click", function () {
        var open = card.classList.toggle("is-open");
        card.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
  }

  function refresh(key, ttl, url, options, parse, paint) {
    var cached = readCache(key);
    if (cached) paint(cached.payload);
    if (fresh(cached, ttl)) return Promise.resolve(cached.payload);
    return fetch(url, options || { headers: { Accept: "application/json" } })
      .then(function (res) {
        if (!res.ok) throw new Error(String(res.status));
        return res.json();
      })
      .then(function (payload) {
        var next = parse(payload);
        if (!next) throw new Error("empty");
        writeCache(key, next);
        paint(next);
        return next;
      })
      .catch(function () {
        if (!cached) paint(FALLBACK[key.split("_").pop()] || null);
        return null;
      });
  }

  function boot() {
    bindToggles();
    paintNotes();
    paintFx(FALLBACK.fx);
    paintWx(FALLBACK.wx);
    paintKp(FALLBACK.kp);
    paintAq(FALLBACK.aq);

    refresh("neuron_pulse_fx_v1", TTL.fx, FX_URL, null, function (rows) {
      if (!Array.isArray(rows)) return null;
      var out = { date: "" };
      rows.forEach(function (row) {
        if (row.Ccy === "USD" || row.Ccy === "EUR" || row.Ccy === "RUB") {
          out[row.Ccy] = parseFloat(String(row.Rate).replace(",", "."));
          out.date = row.Date || out.date;
        }
      });
      if (!(out.USD && out.EUR && out.RUB)) return null;
      return out;
    }, paintFx);

    refresh("neuron_pulse_wx_v1", TTL.wx, WX_URL, null, function (payload) {
      var current = payload && payload.current;
      if (!current || current.temperature_2m == null) return null;
      return { temp: current.temperature_2m, code: current.weather_code, isDay: current.is_day };
    }, paintWx);

    refresh("neuron_pulse_aq_v1", TTL.aq, AQ_URL, null, function (payload) {
      var current = payload && payload.current;
      if (!current || current.us_aqi == null) return null;
      return { aqi: current.us_aqi, pm: current.pm2_5 };
    }, paintAq);

    refresh("neuron_pulse_kp_v1", TTL.kp, KP_URL, null, function (rows) {
      if (!Array.isArray(rows) || !rows.length) return null;
      var last = rows[rows.length - 1];
      if (!last || last.Kp == null) return null;
      return { kp: Number(last.Kp) };
    }, paintKp);

    loadNews();
  }

  function loadNews() {
    var key = "neuron_moh_news_v2_" + govLang();
    var cached = readCache(key);
    if (cached && Array.isArray(cached.payload) && cached.payload.length) paintNews(cached.payload);
    if (fresh(cached, TTL.news)) return;
    fetch(NEWS_URL, {
      headers: {
        Accept: "application/json",
        language: govLang(),
        code: "ssv"
      }
    })
      .then(function (res) {
        if (!res.ok) throw new Error(String(res.status));
        return res.json();
      })
      .then(function (payload) {
        var rows = payload && payload.data;
        if (!Array.isArray(rows) || !rows.length) throw new Error("empty");
        var seen = {};
        var items = [];
        rows.forEach(function (item) {
          var title = String(item.title || "").trim();
          if (!title || seen[title]) return;
          seen[title] = 1;
          items.push({
            id: item.id,
            title: title,
            anons: item.anons || "",
            date: item.date || ""
          });
        });
        items = items.slice(0, 3);
        writeCache(key, items);
        paintNews(items);
      })
      .catch(function () {
        if (!(cached && cached.payload && cached.payload.length)) paintNews([]);
      });
  }

  window.addEventListener("neuron:langchange", function () {
    paintNotes();
    var fx = readCache("neuron_pulse_fx_v1");
    var wx = readCache("neuron_pulse_wx_v1");
    var aq = readCache("neuron_pulse_aq_v1");
    var kp = readCache("neuron_pulse_kp_v1");
    paintFx((fx && fx.payload) || FALLBACK.fx);
    paintWx((wx && wx.payload) || FALLBACK.wx);
    paintAq((aq && aq.payload) || FALLBACK.aq);
    paintKp((kp && kp.payload) || FALLBACK.kp);
    loadNews();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
