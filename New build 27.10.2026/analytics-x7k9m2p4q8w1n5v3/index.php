<?php
$expected = "PSW6rr29V8XNeiKa-HzfWJkv_hFRCMAdbQkU57vuaBk";

function neuron_analytics_given_token($expected)
{
    if (isset($_GET["t"]) && is_string($_GET["t"]) && hash_equals($expected, trim($_GET["t"]))) {
        return trim($_GET["t"]);
    }

    $chunks = array(
        isset($_SERVER["QUERY_STRING"]) ? $_SERVER["QUERY_STRING"] : "",
        isset($_SERVER["REDIRECT_QUERY_STRING"]) ? $_SERVER["REDIRECT_QUERY_STRING"] : "",
        isset($_SERVER["REQUEST_URI"]) ? $_SERVER["REQUEST_URI"] : "",
        isset($_SERVER["REDIRECT_URL"]) ? $_SERVER["REDIRECT_URL"] : "",
    );
    $haystack = implode("?", $chunks);
    if (strpos($haystack, $expected) !== false) {
        return $expected;
    }
    return "";
}

$given = neuron_analytics_given_token($expected);
$allowed = ($given !== "" && hash_equals($expected, $given));

header("X-Robots-Tag: noindex, nofollow, noarchive");
header("Cache-Control: no-store");

if (!$allowed) {
    http_response_code(404);
    header("Status: 404 Not Found");
    header("Content-Type: text/html; charset=utf-8");
    echo "<!DOCTYPE html><html><head><meta name=\"robots\" content=\"noindex,nofollow\"><title>404</title></head><body><p>404 Not Found</p></body></html>";
    exit;
}

http_response_code(200);
header("Status: 200 OK");
header("Content-Type: text/html; charset=utf-8");

$candidates = array(
    __DIR__ . DIRECTORY_SEPARATOR . "dashboard.html",
    dirname(__DIR__) . DIRECTORY_SEPARATOR . "server" . DIRECTORY_SEPARATOR . "app" . DIRECTORY_SEPARATOR . "templates" . DIRECTORY_SEPARATOR . "analytics_dashboard.html",
);
foreach ($candidates as $path) {
    if (is_file($path)) {
        readfile($path);
        exit;
    }
}

echo "<!DOCTYPE html><html><head><title>NeurON analytics</title></head><body><p>Analytics template missing</p></body></html>";
