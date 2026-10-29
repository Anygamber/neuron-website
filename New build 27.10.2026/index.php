<?php
/**
 * Apache / cPanel homepage.
 * Renders index.html with title, description, and canonical for ?lang=
 * before any client script runs. Passenger uses server/app/seo_html.py
 * and the same seo-meta.json.
 */
declare(strict_types=1);

function neuron_swap_html(string $html, string $pattern, string $value): string
{
    $next = preg_replace_callback(
        $pattern,
        static function (array $m) use ($value): string {
            return $m[1] . $value . $m[2];
        },
        $html,
        1
    );
    return is_string($next) ? $next : $html;
}

function neuron_inject_geo(string $html): string
{
    $tags = [
        'geo.region' => 'UZ-TK',
        'geo.placename' => 'Tashkent',
        'geo.position' => '41.3549516;69.3108567',
        'ICBM' => '41.3549516, 69.3108567',
    ];
    $missing = [];
    foreach ($tags as $name => $value) {
        $pattern = '/(<meta\s+name="' . preg_quote($name, '/') . '"\s+content=")[^"]*(")/i';
        if (preg_match($pattern, $html)) {
            $html = neuron_swap_html(
                $html,
                $pattern,
                htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8')
            );
            continue;
        }
        $missing[] = '<meta name="' . htmlspecialchars($name, ENT_QUOTES | ENT_HTML5, 'UTF-8')
            . '" content="' . htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8') . '" />';
    }
    if ($missing === []) {
        return $html;
    }
    $block = implode("\n  ", $missing);
    $next = preg_replace(
        '/(<meta\s+name="theme-color"\s+content="[^"]*"\s*\/?>)/i',
        $block . "\n  $1",
        $html,
        1
    );
    return is_string($next) ? $next : $html;
}

function neuron_inject_google_site_verification(string $html): string
{
    if (stripos($html, 'name="google-site-verification"') !== false) {
        return $html;
    }
    $tag = '<meta name="google-site-verification" content="Shz3pfUKHM2TyL6iZdIZepvHQAAe4klejX5C31PNIyQ" />';
    $next = preg_replace('/<\/head>/i', "  {$tag}\n</head>", $html, 1);
    return is_string($next) ? $next : $html;
}

function neuron_apply_visible_copy(string $html, array $graph): string
{
    $nodes = $graph['@graph'] ?? [];
    if (!is_array($nodes)) {
        return $html;
    }
    $text = static function (string $value): string {
        return htmlspecialchars($value, ENT_NOQUOTES | ENT_HTML5, 'UTF-8');
    };
    $attr = static function (string $value): string {
        return htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    };
    foreach ($nodes as $node) {
        if (!is_array($node)) {
            continue;
        }
        $type = $node['@type'] ?? '';
        $types = is_array($type) ? $type : [$type];
        if (in_array('FAQPage', $types, true)) {
            $entities = $node['mainEntity'] ?? [];
            if (!is_array($entities)) {
                continue;
            }
            foreach ($entities as $i => $question) {
                if (!is_array($question)) {
                    continue;
                }
                $n = $i + 1;
                $name = (string)($question['name'] ?? '');
                $answerNode = $question['acceptedAnswer'] ?? [];
                $answer = is_array($answerNode) ? (string)($answerNode['text'] ?? '') : '';
                if ($name !== '') {
                    $html = neuron_swap_html(
                        $html,
                        '/(<[^>]*\sdata-i18n="faq\.q' . $n . '"[^>]*>)[^<]*(<\/)/',
                        $text($name)
                    );
                }
                if ($answer !== '') {
                    $html = neuron_swap_html(
                        $html,
                        '/(<[^>]*\sdata-i18n="faq\.a' . $n . '"[^>]*>)[^<]*(<\/)/',
                        $text($answer)
                    );
                }
            }
        }
        if (!in_array('Physician', $types, true)) {
            continue;
        }
        $id = (string)($node['@id'] ?? '');
        if (!preg_match('/#doctor-([a-z0-9-]+)$/', $id, $slugMatch)) {
            continue;
        }
        $slug = $slugMatch[1];
        $name = (string)($node['name'] ?? '');
        $role = (string)($node['medicalSpecialty'] ?? '');
        if ($name !== '') {
            $key = 'doc.' . $slug . '.name';
            $quoted = preg_quote($key, '/');
            $html = neuron_swap_html(
                $html,
                '/(<[^>]*\sdata-i18n="' . $quoted . '"[^>]*>)[^<]*(<\/)/',
                $text($name)
            );
            $html = neuron_swap_html(
                $html,
                '/(alt=")[^"]*("\s+data-i18n-alt="' . $quoted . '")/',
                $attr($name)
            );
        }
        if ($role !== '') {
            $key = 'doc.' . $slug . '.role';
            $html = neuron_swap_html(
                $html,
                '/(<[^>]*\sdata-i18n="' . preg_quote($key, '/') . '"[^>]*>)[^<]*(<\/)/',
                $text($role)
            );
        }
    }
    return $html;
}

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
$html = neuron_inject_geo($html);
$html = neuron_inject_google_site_verification($html);

$schemaRaw = file_get_contents($root . '/schema-i18n.json');
$schema = json_decode($schemaRaw === false ? '' : $schemaRaw, true);
if (is_array($schema) && isset($schema['graphs']) && is_array($schema['graphs'])) {
    $schemaCode = isset($schema['graphs'][$lang]) ? $lang : (string)($schema['default'] ?? 'uz');
    $graph = $schema['graphs'][$schemaCode] ?? null;
    if (is_array($graph)) {
        $payload = json_encode(
            $graph,
            JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT
        );
        if (is_string($payload)) {
            $next = preg_replace_callback(
                '/(<script\s+type="application\/ld\+json"\s+id="neuron-schema-org">)(.*?)(<\/script>)/is',
                static function (array $m) use ($payload): string {
                    return $m[1] . "\n" . $payload . "\n  " . $m[3];
                },
                $html,
                1
            );
            if (is_string($next)) {
                $html = neuron_apply_visible_copy($next, $graph);
            }
        }
    }
}

header('Content-Type: text/html; charset=UTF-8');
header('Content-Language: ' . (string)($pack['htmlLang'] ?? $lang));
echo $html;
