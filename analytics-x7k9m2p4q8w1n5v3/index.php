<?php
header("X-Robots-Tag: noindex, nofollow, noarchive");
header("Cache-Control: no-store");

$expected = "PSW6rr29V8XNeiKa-HzfWJkv_hFRCMAdbQkU57vuaBk";
$given = isset($_GET["t"]) ? (string) $_GET["t"] : "";

if (!hash_equals($expected, $given)) {
    http_response_code(404);
    header("Content-Type: text/html; charset=utf-8");
    echo "<!DOCTYPE html><html><head><meta name=\"robots\" content=\"noindex,nofollow\"><title>404</title></head><body><p>404 Not Found</p></body></html>";
    exit;
}

$template = dirname(__DIR__) . DIRECTORY_SEPARATOR . "server" . DIRECTORY_SEPARATOR . "app" . DIRECTORY_SEPARATOR . "templates" . DIRECTORY_SEPARATOR . "analytics_dashboard.html";
if (!is_file($template)) {
    http_response_code(500);
    header("Content-Type: text/plain; charset=utf-8");
    echo "Analytics template missing";
    exit;
}

header("Content-Type: text/html; charset=utf-8");
readfile($template);
