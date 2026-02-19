# ZHAW QGIS Plugins Repository

Static QGIS plugin repository served via GitHub Pages. QGIS reads `plugins.xml`
to discover and install plugins.

**Repository URL (add this in QGIS):**
```
https://zhaw-qgis-plugins.github.io/Plugins-Repository/plugins.xml
```

## Repository structure

```
plugins/                   # Plugin ZIP files served via GitHub Pages
    roe_deer_corridor_demo.zip
plugins.xml                # QGIS plugin index (generated)
index.qmd                  # User documentation source (Quarto)
index.html                 # User documentation (generated from index.qmd)
generate_xml.py            # Script to regenerate plugins.xml from ZIPs
```

## Current publishing workflow

Publishing is driven from the [`roe-deer-demo`](https://github.com/zhaw-qgis-plugins/roe-deer-demo)
repository via `make publish`, which:

1. Zips the plugin source and copies the ZIP to `plugins/` in this repo
2. Runs `generate_xml.py` to regenerate `plugins.xml`

Afterwards, if `index.qmd` was changed, regenerate the documentation manually:

```bash
quarto render index.qmd
```

Then commit and push this repository:

```bash
git add plugins/ plugins.xml index.html
git commit -m "Publish vX.Y.Z"
git push
```

To regenerate `plugins.xml` in isolation (e.g. after manually dropping in a ZIP):

```bash
python generate_xml.py \
  --base-url https://zhaw-qgis-plugins.github.io/Plugins-Repository/plugins
```

## Planned improvement: gh-pages branch + GitHub Releases

The current setup mixes source files (`index.qmd`, `generate_xml.py`, images) with
generated outputs (`index.html`, `plugins.xml`) and binary assets (`plugins/*.zip`)
on `main`.

**Goal:** separate sources from deployables, and host ZIPs as GitHub Release assets
instead of committing them to the repository.

**Target layout:**

| Location | Contents |
|----------|----------|
| `main` branch | `index.qmd`, `generate_xml.py`, images |
| `gh-pages` branch | `index.html`, `plugins.xml` (deployed via `ghp-import`) |
| GitHub Releases (`roe-deer-demo`) | Plugin ZIP files |

**Target workflow:**

```bash
# 1. In roe-deer-demo: tag release and upload ZIP
gh release create vX.Y.Z roe_deer_corridor_demo.zip --title "vX.Y.Z"

# 2. In this repo: regenerate and deploy (single command)
make deploy
# → quarto render index.qmd
# → python generate_xml.py --base-url <github-release-download-url>
# → ghp-import -n -p -f _site/
```

`generate_xml.py` would need a small extension to accept a `--download-url` override
per plugin, so the `<download_url>` in `plugins.xml` can point to the GitHub Release
asset rather than a Pages-hosted path.
