$ErrorActionPreference = "Stop"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$out = "$env:TEMP\neuron-intro"
$profile = Join-Path $out "cdp-profile"
New-Item -ItemType Directory -Force -Path $profile | Out-Null
Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $chrome } | Out-Null

$proc = Start-Process -FilePath $chrome -PassThru -WindowStyle Hidden -ArgumentList @(
  "--headless=new",
  "--disable-gpu",
  "--hide-scrollbars",
  "--remote-debugging-port=9333",
  "--user-data-dir=$profile",
  "--window-size=1440,900",
  "about:blank"
)

$wsUrl = $null
for ($i = 0; $i -lt 40; $i++) {
  try {
    $tabs = Invoke-RestMethod "http://127.0.0.1:9333/json" -TimeoutSec 2
    $page = $tabs | Where-Object { $_.type -eq "page" } | Select-Object -First 1
    if ($page.webSocketDebuggerUrl) { $wsUrl = $page.webSocketDebuggerUrl; break }
  } catch {}
  Start-Sleep -Milliseconds 250
}
if (-not $wsUrl) { throw "CDP endpoint not ready" }

$socket = [System.Net.WebSockets.ClientWebSocket]::new()
$ct = [System.Threading.CancellationToken]::None
$socket.ConnectAsync([Uri]$wsUrl, $ct).Wait()

$script:nextId = 1
function Send-Raw([string]$json) {
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)
  $seg = [ArraySegment[byte]]::new($bytes)
  $socket.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
}
function Recv-Raw {
  $ms = New-Object System.IO.MemoryStream
  do {
    $buf = New-Object byte[] 131072
    $seg = [ArraySegment[byte]]::new($buf)
    $res = $socket.ReceiveAsync($seg, $ct).Result
    if ($res.Count -gt 0) { $ms.Write($buf, 0, $res.Count) }
    if ($res.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { break }
  } while (-not $res.EndOfMessage)
  [Text.Encoding]::UTF8.GetString($ms.ToArray())
}
function Invoke-Cdp([string]$method, $params) {
  $id = $script:nextId
  $script:nextId++
  $payload = @{ id = $id; method = $method }
  if ($null -ne $params) { $payload.params = $params }
  Send-Raw (($payload | ConvertTo-Json -Compress -Depth 8))
  while ($true) {
    $raw = Recv-Raw
    if (-not $raw) { continue }
    $msg = $raw | ConvertFrom-Json
    if ($msg.id -eq $id) { return $msg }
  }
}

$expr = @'
(function () {
  function box(el) {
    if (!el) return null;
    var r = el.getBoundingClientRect();
    return {
      x: Math.round(r.x), y: Math.round(r.y),
      w: Math.round(r.width), h: Math.round(r.height),
      cx: Math.round(r.x + r.width / 2),
      cy: Math.round(r.y + r.height / 2)
    };
  }
  var pre = document.getElementById("site-preloader");
  var brain = document.getElementById("preloader-brain-wrap");
  var word = document.getElementById("preloader-wordmark");
  var img = document.getElementById("preloader-brain");
  var cs = pre ? getComputedStyle(pre) : null;
  var waves = document.querySelectorAll("#preloader-waves span");
  var visWaves = 0;
  waves.forEach(function (n) { if (parseFloat(getComputedStyle(n).opacity) > 0.05) visWaves++; });
  var sparks = document.querySelectorAll(".preloader-synapses span");
  var visSparks = 0;
  sparks.forEach(function (n) { if (parseFloat(getComputedStyle(n).opacity) > 0.05) visSparks++; });
  return JSON.stringify({
    vw: innerWidth, vh: innerHeight,
    reduce: matchMedia("(prefers-reduced-motion: reduce)").matches,
    preDisplay: cs && cs.display,
    preOpacity: cs && cs.opacity,
    brain: box(brain),
    brainOpacity: brain ? getComputedStyle(brain).opacity : null,
    word: box(word),
    clip: word ? getComputedStyle(word).clipPath : null,
    img: img ? img.naturalWidth : 0,
    waves: waves.length,
    visWaves: visWaves,
    sparks: sparks.length,
    visSparks: visSparks,
    body: document.body.className
  });
})()
'@

function Read-State {
  $res = Invoke-Cdp "Runtime.evaluate" @{ expression = $expr; returnByValue = $true }
  return $res.result.result.value
}

Invoke-Cdp "Emulation.setDeviceMetricsOverride" @{ width = 1440; height = 900; deviceScaleFactor = 1; mobile = $false } | Out-Null
Invoke-Cdp "Emulation.setEmulatedMedia" @{ features = @(@{ name = "prefers-reduced-motion"; value = "no" }) } | Out-Null
Invoke-Cdp "Page.enable" @{} | Out-Null
Invoke-Cdp "Page.navigate" @{ url = "http://127.0.0.1:8000/?lang=uz&intro=cdp1" } | Out-Null

$log = New-Object System.Collections.Generic.List[string]
$shotEarly = $false
$shotMain = $false
for ($i = 0; $i -lt 28; $i++) {
  Start-Sleep -Milliseconds 300
  $state = Read-State
  $log.Add(("t={0} {1}" -f ($i * 300), $state))
  $obj = $state | ConvertFrom-Json
  $brainOn = $false
  if ($obj.brainOpacity) { $brainOn = [double]$obj.brainOpacity -gt 0.9 }
  $clip = [string]$obj.clip
  $opening = $clip -match "100%"
  $open = $clip -match "inset\(0px 0%"
  $preOn = $false
  if ($obj.preOpacity) { $preOn = [double]$obj.preOpacity -gt 0.85 }
  if (-not $shotEarly -and $preOn -and $brainOn -and -not $open) {
    $png = Invoke-Cdp "Page.captureScreenshot" @{ format = "png" }
    [IO.File]::WriteAllBytes((Join-Path $out "intro-early.png"), [Convert]::FromBase64String($png.result.data))
    $shotEarly = $true
    $log.Add("SHOT early")
  }
  if (-not $shotMain -and $preOn -and $brainOn -and $open) {
    $png = Invoke-Cdp "Page.captureScreenshot" @{ format = "png" }
    [IO.File]::WriteAllBytes((Join-Path $out "intro-main.png"), [Convert]::FromBase64String($png.result.data))
    $shotMain = $true
    $log.Add("SHOT main")
    break
  }
}

# Mobile reload
Invoke-Cdp "Emulation.setDeviceMetricsOverride" @{ width = 390; height = 844; deviceScaleFactor = 1; mobile = $true } | Out-Null
Invoke-Cdp "Page.navigate" @{ url = "http://127.0.0.1:8000/?lang=uz&intro=cdp2" } | Out-Null
$shotMobile = $false
for ($i = 0; $i -lt 28; $i++) {
  Start-Sleep -Milliseconds 300
  $state = Read-State
  $log.Add(("m t={0} {1}" -f ($i * 300), $state))
  $obj = $state | ConvertFrom-Json
  $brainOn = $false
  if ($obj.brainOpacity) { $brainOn = [double]$obj.brainOpacity -gt 0.9 }
  $clip = [string]$obj.clip
  $open = $clip -match "inset\(0px 0%"
  $preOn = $false
  if ($obj.preOpacity) { $preOn = [double]$obj.preOpacity -gt 0.85 }
  if (-not $shotMobile -and $preOn -and $brainOn -and $open) {
    $png = Invoke-Cdp "Page.captureScreenshot" @{ format = "png" }
    [IO.File]::WriteAllBytes((Join-Path $out "intro-mobile.png"), [Convert]::FromBase64String($png.result.data))
    $shotMobile = $true
    $log.Add("SHOT mobile")
    break
  }
}

$log | Set-Content -Encoding utf8 (Join-Path $out "states.txt")
try { $socket.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "done", $ct).Wait(1000) } catch {}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Output "early=$shotEarly main=$shotMain mobile=$shotMobile"
