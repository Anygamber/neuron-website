<?php
/**
 * Apache / cPanel homepage.
 * Renders index.html with title, description, and canonical for ?lang=
 * before any client script runs. Passenger uses server/app/seo_html.py
 * and the same seo-meta.json.
 */
declare(strict_types=1);

$root = __DIR__;
$raw = file_get_contents($root . '/seo-meta.json');
$catalog = json_decode($raw === false ? '' : $raw, true);
if (!is_array($catalog) || !isset($catalog['languages']) || !is_array($catalog['languages'])) {
    http_response_code(500);
    header('Content-Type: text/plain; charset=UTF-8');
    echo "seo-meta.json is unreadable";
    exit;
}

$languages = $catalog['languages'];
$default = (string)($catalog['default'] ?? 'uz');
$requested = strtolower((string)($_GET['lang'] ?? ''));
$lang = isset($languages[$requested]) ? $requested : $default;
$pack = $languages[$lang];
if (!is_array($pack)) {
    http_response_code(500);
    header('Content-Type: text/plain; charset=UTF-8');
    echo "seo-meta.json language pack is invalid";
    exit;
}

$html = file_get_contents($root . '/index.html');
if ($html === false) {
    http_response_code(500);
    header('Content-Type: text/plain; charset=UTF-8');
    echo "index.html is missing";
    exit;
}

$esc = static function (string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
};

$title = $esc((string)($pack['title'] ?? ''));
$description = $esc((string)($pack['description'] ?? ''));
$keywords = $esc((string)($pack['keywords'] ?? ''));
$locale = $esc((string)($pack['ogLocale'] ?? ''));
$url = $esc((string)($pack['url'] ?? ''));
$htmlLang = $esc((string)($pack['htmlLang'] ?? $lang));

$replace = static function (string $html, string $pattern, string $value): string {
    $next = preg_replace_callback(
        $pattern,
        static function (array $m) use ($value): string {
            return $m[1] . $value . $m[2];
        },
        $html,
        1
    );
    return is_string($next) ? $next : $html;
};

$html = $replace($html, '/(<html\s+lang=")[^"]*(")/i', $htmlLang);
$html = $replace($html, '/(<html\b[^>]*\sdata-lang=")[^"]*(")/i', $htmlLang);
$html = $replace($html, '/(<title>)[^<]*(<\/title>)/i', $title);
$html = $replace($html, '/(<meta\s+name="description"\s+content=")[^"]*(")/i', $description);
$html = $replace($html, '/(<meta\s+name="keywords"\s+content=")[^"]*(")/i', $keywords);
foreach (
    [
        'og:title' => $title,
        'og:description' => $description,
        'og:locale' => $locale,
        'og:url' => $url,
    ] as $prop => $value
) {
    $quoted = preg_quote($prop, '/');
    $html = $replace(
        $html,
        '/(<meta\s+property="' . $quoted . '"\s+content=")[^"]*(")/i',
        $value
    );
}
foreach (
    [
        'twitter:title' => $title,
        'twitter:description' => $description,
    ] as $name => $value
) {
    $quoted = preg_quote($name, '/');
    $html = $replace(
        $html,
        '/(<meta\s+name="' . $quoted . '"\s+content=")[^"]*(")/i',
        $value
    );
}
$html = $replace($html, '/(<link\s+rel="canonical"\s+href=")[^"]*(")/i', $url);

header('Content-Type: text/html; charset=UTF-8');
header('Content-Language: ' . (string)($pack['htmlLang'] ?? $lang));
echo $html;
