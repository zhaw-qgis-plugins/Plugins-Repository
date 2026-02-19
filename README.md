# ZHAW QGIS Plugins Repository

Static QGIS plugin repository served via GitHub Pages. QGIS reads `plugins.xml`
to discover and install plugins.

Repository URL (add this in QGIS): https://zhaw-qgis-plugins.github.io/Plugins-Repository/plugins.xml

Instructions for users are available on the GitHub Pages website: https://zhaw-qgis-plugins.github.io/Plugins-Repository

The following readme is aimed at developers:



## Repository structure

```
plugins/                   # Plugin ZIP files (served alongside the site)
    roe_deer_corridor_demo.zip
plugins.xml                # QGIS plugin index (generated, do not edit manually)
index.qmd                  # User documentation source (Quarto)
index.html                 # Rendered output (generated)
generate_xml.py            # Regenerates plugins.xml from ZIPs in plugins/
_quarto.yml                # Quarto project config (pre-render + resources)
style.css                  # Stylesheet for index.html
```

## Publishing workflow

Publishing is driven from the [`roe-deer-demo`](https://github.com/zhaw-qgis-plugins/roe-deer-demo)
repository via `make publish`, which copies the new ZIP to `plugins/` in this repo (locally! so a bit brittle). 

Afterwards, render and deploy:

```bash
quarto render
quarto publish gh-pages
```

`_quarto.yml` wires everything together:

- `pre-render: generate_xml.py` — regenerates `plugins.xml` before the document renders
- `resources` — copies `plugins/*.zip` and `plugins.xml` into the published site
