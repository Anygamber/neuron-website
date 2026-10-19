<?php
/**
 * Stats for the hidden analytics page.
 * Same folder as index.php: api.php?days=30&t=TOKEN
 */
$expected = "PSW6rr29V8XNeiKa-HzfWJkv_hFRCMAdbQkU57vuaBk";

function neuron_stats_token_ok($expected)
{
    if (isset($_GET["t"]) && is_string($_GET["t"]) && hash_equals($expected, trim($_GET["t"]))) {
        return true;
    }
    $chunks = array(
        isset($_SERVER["QUERY_STRING"]) ? $_SERVER["QUERY_STRING"] : "",
        isset($_SERVER["REDIRECT_QUERY_STRING"]) ? $_SERVER["REDIRECT_QUERY_STRING"] : "",
        isset($_SERVER["REQUEST_URI"]) ? $_SERVER["REQUEST_URI"] : "",
    );
    return strpos(implode("?", $chunks), $expected) !== false;
}

function neuron_stats_days()
{
    $raw = isset($_GET["days"]) ? trim((string) $_GET["days"]) : "30";
    if (!preg_match("/^(\d+)/", $raw, $match)) {
        return 30;
    }
    $days = (int) $match[1];
    if ($days < 1) {
        return 1;
    }
    if ($days > 365) {
        return 365;
    }
    return $days;
}

function neuron_stats_empty($days)
{
    $hours = array();
    for ($i = 0; $i < 24; $i++) {
        $hours[] = array("hour" => sprintf("%02d", $i), "views" => 0);
    }
    return array(
        "generated_at" => gmdate("c"),
        "period_days" => $days,
        "totals" => array(
            "pageviews_all" => 0,
            "pageviews_period" => 0,
            "unique_visitors_all" => 0,
            "unique_visitors_period" => 0,
        ),
        "by_lang" => new stdClass(),
        "by_source" => new stdClass(),
        "geo_clicks" => array(),
        "countries" => new stdClass(),
        "by_day" => array(),
        "by_hour" => $hours,
        "top_paths" => array(),
    );
}

function neuron_stats_map($rows)
{
    $out = array();
    foreach ($rows as $row) {
        $key = isset($row["k"]) ? (string) $row["k"] : "";
        if ($key === "") {
            continue;
        }
        $out[$key] = (int) $row["n"];
    }
    if (!$out) {
        return new stdClass();
    }
    return $out;
}

header("X-Robots-Tag: noindex, nofollow, noarchive");
header("Cache-Control: no-store");
header("Content-Type: application/json; charset=utf-8");

if (!neuron_stats_token_ok($expected)) {
    http_response_code(404);
    echo json_encode(array("detail" => "Not Found"));
    exit;
}

$days = neuron_stats_days();
$payload = neuron_stats_empty($days);
$dbFile = dirname(__DIR__) . DIRECTORY_SEPARATOR . "server" . DIRECTORY_SEPARATOR . "data" . DIRECTORY_SEPARATOR . "neuron.db";

if (!is_file($dbFile) || !class_exists("PDO")) {
    echo json_encode($payload);
    exit;
}

try {
    $pdo = new PDO("sqlite:" . $dbFile, null, null, array(
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ));
    $exists = $pdo->query("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'page_visits'")->fetch();
    if (!$exists) {
        echo json_encode($payload);
        exit;
    }

    $since = gmdate("Y-m-d H:i:s", time() - ($days * 86400));
    $page = "path NOT LIKE '/geo-click/%'";
    $geo = "path LIKE '/geo-click/%'";

    $payload["totals"]["pageviews_all"] = (int) $pdo->query("SELECT COUNT(*) FROM page_visits WHERE $page")->fetchColumn();
    $payload["totals"]["unique_visitors_all"] = (int) $pdo->query("SELECT COUNT(DISTINCT visitor_id) FROM page_visits WHERE $page")->fetchColumn();

    $period = $pdo->prepare("SELECT COUNT(*) FROM page_visits WHERE $page AND created_at >= ?");
    $period->execute(array($since));
    $payload["totals"]["pageviews_period"] = (int) $period->fetchColumn();

    $unique = $pdo->prepare("SELECT COUNT(DISTINCT visitor_id) FROM page_visits WHERE $page AND created_at >= ?");
    $unique->execute(array($since));
    $payload["totals"]["unique_visitors_period"] = (int) $unique->fetchColumn();

    $lang = $pdo->prepare("SELECT lang AS k, COUNT(*) AS n FROM page_visits WHERE $page AND created_at >= ? GROUP BY lang");
    $lang->execute(array($since));
    $payload["by_lang"] = neuron_stats_map($lang->fetchAll());

    $source = $pdo->prepare("SELECT source AS k, COUNT(*) AS n FROM page_visits WHERE $page AND created_at >= ? GROUP BY source");
    $source->execute(array($since));
    $payload["by_source"] = neuron_stats_map($source->fetchAll());

    $geoRows = $pdo->prepare("SELECT path AS k, COUNT(*) AS n FROM page_visits WHERE $geo AND created_at >= ? GROUP BY path ORDER BY n DESC");
    $geoRows->execute(array($since));
    $clicks = array();
    foreach ($geoRows->fetchAll() as $row) {
        $map = preg_replace("#^/geo-click/#", "", (string) $row["k"]);
        if ($map === "") {
            $map = "map";
        }
        $clicks[] = array("map" => $map, "views" => (int) $row["n"]);
    }
    $payload["geo_clicks"] = $clicks;

    $daysRows = $pdo->prepare("SELECT substr(created_at, 1, 10) AS d, COUNT(*) AS n FROM page_visits WHERE $page AND created_at >= ? GROUP BY substr(created_at, 1, 10) ORDER BY d");
    $daysRows->execute(array($since));
    $byDay = array();
    foreach ($daysRows->fetchAll() as $row) {
        if (!$row["d"]) {
            continue;
        }
        $byDay[] = array("date" => (string) $row["d"], "views" => (int) $row["n"]);
    }
    $payload["by_day"] = $byDay;

    $hourRows = $pdo->prepare("SELECT substr(created_at, 12, 2) AS h, COUNT(*) AS n FROM page_visits WHERE $page AND created_at >= ? GROUP BY substr(created_at, 12, 2)");
    $hourRows->execute(array($since));
    $hourMap = array();
    foreach ($hourRows->fetchAll() as $row) {
        $hour = preg_replace("/\D/", "", (string) $row["h"]);
        if ($hour === "") {
            continue;
        }
        $hourMap[sprintf("%02d", (int) $hour)] = (int) $row["n"];
    }
    $hours = array();
    for ($i = 0; $i < 24; $i++) {
        $key = sprintf("%02d", $i);
        $hours[] = array("hour" => $key, "views" => isset($hourMap[$key]) ? $hourMap[$key] : 0);
    }
    $payload["by_hour"] = $hours;

    $paths = $pdo->prepare("SELECT path AS k, COUNT(*) AS n FROM page_visits WHERE $page AND created_at >= ? GROUP BY path ORDER BY n DESC LIMIT 15");
    $paths->execute(array($since));
    $top = array();
    foreach ($paths->fetchAll() as $row) {
        $top[] = array("path" => (string) $row["k"], "views" => (int) $row["n"]);
    }
    $payload["top_paths"] = $top;
} catch (Exception $e) {
    $payload = neuron_stats_empty($days);
}

echo json_encode($payload);
