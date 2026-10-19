<?php
/**
 * Static-host fallback for the hidden analytics page.
 * The running FastAPI app serves this path itself. If Apache serves the
 * directory directly, this file checks the same ANALYTICS_SECRET_TOKEN
 * from the environment or server/.env and does not store the secret here.
 */
header("X-Robots-Tag: noindex, nofollow, noarchive");
header("Cache-Control: no-store");

function neuron_analytics_expected_token(): string
{
    $fromEnv = getenv("ANALYTICS_SECRET_TOKEN");
    if (is_string($fromEnv) && trim($fromEnv) !== "") {
        return trim($fromEnv);
    }

    $envFile = dirname(__DIR__) . DIRECTORY_SEPARATOR . "server" . DIRECTORY_SEPARATOR . ".env";
    if (!is_file($envFile)) {
        return "";
    }
    $lines = file($envFile, FILE_IGNORE_NEW_LINES);
    if (!$lines) {
        return "";
    }
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === "" || $line[0] === "#") {
            continue;
        }
        $prefix = "ANALYTICS_SECRET_TOKEN=";
        if (strpos($line, $prefix) === 0) {
            return trim(substr($line, strlen($prefix)), " \t\"'");
        }
    }
    return "";
}

function neuron_analytics_deny(): void
{
    http_response_code(404);
    header("Content-Type: text/html; charset=utf-8");
    echo "<!DOCTYPE html><html><head><meta name=\"robots\" content=\"noindex,nofollow\"><title>404</title></head><body><p>404 Not Found</p></body></html>";
    exit;
}

$given = isset($_GET["t"]) ? (string) $_GET["t"] : (isset($_GET["token"]) ? (string) $_GET["token"] : "");
$expected = neuron_analytics_expected_token();
if ($expected === "" || !hash_equals($expected, $given)) {
    neuron_analytics_deny();
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
