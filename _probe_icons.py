import urllib.request

css = urllib.request.urlopen(
    "https://cdn.jsdelivr.net/npm/lucide-static@0.460.0/font/lucide.min.css",
    timeout=20,
).read().decode("utf-8", "replace")
names = [
    "stethoscope",
    "receipt",
    "tag",
    "user-check",
    "users",
    "hospital",
    "building-2",
    "microscope",
    "cpu",
    "map-pin",
    "phone",
]
for name in names:
    print(name, (".icon-" + name + ":") in css or (".icon-" + name + "::") in css)
