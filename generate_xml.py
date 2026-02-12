#!/usr/bin/env python3
"""Generate plugins.xml for a static QGIS plugin repository.

Scans the plugins/ directory for ZIP files, reads metadata.txt from each,
and produces a plugins.xml that QGIS Plugin Manager can consume.

Usage:
    python generate_xml.py [--base-url URL]

Examples:
    python generate_xml.py
    python generate_xml.py --base-url https://example.github.io/QGIS-Plugin-Repository/plugins
"""

import argparse
import configparser
import io
import os
import sys
import zipfile
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent


METADATA_FIELDS = [
    "description",
    "about",
    "version",
    "qgisMinimumVersion",
    "qgisMaximumVersion",
    "homepage",
    "tracker",
    "repository",
    "author",
    "email",
    "icon",
    "tags",
    "category",
    "experimental",
    "deprecated",
]

# metadata.txt key -> XML element name
XML_TAG_MAP = {
    "description": "description",
    "about": "about",
    "version": "version",
    "qgisMinimumVersion": "qgis_minimum_version",
    "qgisMaximumVersion": "qgis_maximum_version",
    "homepage": "homepage",
    "tracker": "tracker",
    "repository": "repository",
    "author": "author_name",
    "email": "email",
    "icon": "icon",
    "tags": "tags",
    "category": "category",
    "experimental": "experimental",
    "deprecated": "deprecated",
}


def find_metadata(zf):
    """Find and return the path to metadata.txt inside a ZIP file."""
    for name in zf.namelist():
        parts = name.split("/")
        if len(parts) == 2 and parts[1] == "metadata.txt":
            return name
    return None


def parse_metadata(zf, metadata_path):
    """Parse metadata.txt from a ZIP and return a dict of values."""
    with zf.open(metadata_path) as f:
        content = f.read().decode("utf-8")
    config = configparser.ConfigParser()
    config.read_string(content)
    if not config.has_section("general"):
        return None
    return dict(config.items("general"))


def build_plugin_element(metadata, zip_filename, base_url):
    """Build an XML element for a single plugin."""
    name = metadata.get("name", os.path.splitext(zip_filename)[0])
    version = metadata.get("version", "0.0.0")

    plugin_el = Element("pyqgis_plugin", name=name, version=version)

    for meta_key in METADATA_FIELDS:
        xml_tag = XML_TAG_MAP[meta_key]
        value = metadata.get(meta_key.lower(), "")
        SubElement(plugin_el, xml_tag).text = value

    SubElement(plugin_el, "file_name").text = zip_filename

    if base_url:
        url = base_url.rstrip("/") + "/" + zip_filename
    else:
        url = "plugins/" + zip_filename
    SubElement(plugin_el, "download_url").text = url

    return plugin_el


def main():
    parser = argparse.ArgumentParser(
        description="Generate plugins.xml for a QGIS plugin repository."
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="Base URL for download links (e.g. https://example.com/plugins). "
        "Defaults to relative paths (plugins/<filename>).",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugins_dir = os.path.join(script_dir, "plugins")
    output_path = os.path.join(script_dir, "plugins.xml")

    if not os.path.isdir(plugins_dir):
        print(f"Error: plugins/ directory not found at {plugins_dir}", file=sys.stderr)
        sys.exit(1)

    zip_files = sorted(f for f in os.listdir(plugins_dir) if f.endswith(".zip"))
    if not zip_files:
        print("Warning: No ZIP files found in plugins/", file=sys.stderr)

    root = Element("plugins")

    for zip_filename in zip_files:
        zip_path = os.path.join(plugins_dir, zip_filename)
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                metadata_path = find_metadata(zf)
                if metadata_path is None:
                    print(f"  Skipping {zip_filename}: no metadata.txt found", file=sys.stderr)
                    continue
                metadata = parse_metadata(zf, metadata_path)
                if metadata is None:
                    print(f"  Skipping {zip_filename}: no [general] section in metadata.txt", file=sys.stderr)
                    continue
        except zipfile.BadZipFile:
            print(f"  Skipping {zip_filename}: not a valid ZIP file", file=sys.stderr)
            continue

        plugin_el = build_plugin_element(metadata, zip_filename, args.base_url)
        root.append(plugin_el)
        print(f"  Added: {metadata.get('name', zip_filename)} {metadata.get('version', '?')}")

    indent(root, space="    ")
    tree = ElementTree(root)
    tree.write(output_path, encoding="unicode", xml_declaration=True)
    # Add trailing newline
    with open(output_path, "a") as f:
        f.write("\n")

    print(f"\nWrote {output_path} ({len(root)} plugin(s))")


if __name__ == "__main__":
    main()
