/* First-party visit beacon. Posts page views and map-link clicks to /api/v1/analytics/hit. */
(function () {
  var KEY = "neuron_vid";

  function visitorId() {
    try {
      var id = localStorage.getItem(KEY);
      if (!id) {
        id =
          typeof crypto !== "undefined" && crypto.randomUUID
            ? crypto.randomUUID()
            : "v" + Date.now().toString(36) + Math.random().toString(36).slice(2);
        localStorage.setItem(KEY, id);
      }
      return id;
    } catch (e) {
      return "anonymous";
    }
  }

  function send(path) {
    try {
      var lang = document.documentElement.getAttribute("data-lang") || "uz";
      var payload = JSON.stringify({
        path: path || "/",
        lang: String(lang).toLowerCase(),
        referrer: document.referrer || "",
        visitor_id: visitorId(),
        href: location.href,
      });
      var url = "/api/v1/analytics/hit";
      if (navigator.sendBeacon) {
        var accepted = navigator.sendBeacon(
          url,
          new Blob([payload], { type: "application/json" })
        );
        if (accepted) return;
      }
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
        keepalive: true,
        credentials: "same-origin",
      }).catch(function () {});
    } catch (e) {}
  }

  function boot() {
    var path = location.pathname || "/";
    if (path.indexOf("/analytics-x7k9m2p4q8w1n5v3") === 0) return;
    send(path + location.search + location.hash);
    document.addEventListener("click", function (event) {
      var node = event.target;
      var card = node && node.closest ? node.closest("[data-map]") : null;
      if (!card) return;
      var map = String(card.getAttribute("data-map") || "map")
        .toLowerCase()
        .replace(/[^a-z0-9_-]/g, "");
      send("/geo-click/" + (map || "map"));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
