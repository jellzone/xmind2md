#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xmind2md: Convert an .xmind mind map into a Markdown outline.

Features
- Supports XMind 2020/Zen (content.json) and XMind 8 (content.xml) packages.
- Preserves sheet titles, topics (hierarchy), notes, labels, markers, and hyperlinks (when present).
- Outputs a clean Markdown outline using headings for sheet/root, and nested bullet lists for child topics.
- CLI usage:
    python xmind2md.py input.xmind -o output.md [--max-depth N] [--no-notes] [--no-labels] [--no-markers]

Limitations
- Images/attachments are not extracted; links to them (if any) are printed as plain text.
- Relationships, boundaries, and summaries from XMind are not rendered (basic listing only when found).

Author: ChatGPT
License: MIT
"""
import zipfile
import json
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any, Tuple
import re
import os
import sys
import argparse
import textwrap

def _md_escape(text: str) -> str:
    """Escape Markdown special chars lightly to avoid broken formatting."""
    if text is None:
        return ""
    # Minimal escaping for brackets/parentheses used in links/labels.
    return (text
            .replace('[', r'\[')
            .replace(']', r'\]')
            .replace('(', r'\(')
            .replace(')', r'\)')
            .replace('*', r'\*')
            .replace('_', r'\_')
            .replace('#', r'\#')
            )

def _norm_ws(s: Optional[str]) -> str:
    return re.sub(r'[ \t]+\n', '\n', s or '').strip()

def _indent(level: int) -> str:
    return '  ' * level

def _add_note_lines(lines: List[str], note: str, level: int) -> None:
    note = _norm_ws(note)
    if not note:
        return
    # Render notes as a nested blockquote under the item
    for ln in note.splitlines():
        if ln.strip() == '':
            lines.append(f"{_indent(level+1)}>")
        else:
            lines.append(f"{_indent(level+1)}> {ln}")

def _format_line(title: str,
                 hyperlink: Optional[str] = None,
                 labels: Optional[List[str]] = None,
                 markers: Optional[List[str]] = None) -> str:
    t = _md_escape(title) if title else "(untitled)"
    if hyperlink:
        # ensure parentheses don't break the link
        safe_url = hyperlink.replace(')', r'\)')
        t = f"[{t}]({safe_url})"
    # append labels as inline tags
    suffix = []
    if labels:
        for lb in labels:
            lb = str(lb).strip()
            if lb:
                suffix.append(f"`{_md_escape(lb)}`")
    if markers:
        for mk in markers:
            mk = str(mk).strip()
            if mk:
                suffix.append(f"<{_md_escape(mk)}>")
    if suffix:
        t += " " + " ".join(suffix)
    return t

# ----------------------- JSON (XMind 2020/Zen) -----------------------

def _json_get_note(topic: Dict[str, Any]) -> str:
    notes = topic.get('notes') or {}
    # Common: {"notes":{"plain":{"content":"..."}}}
    plain = notes.get('plain') or {}
    if isinstance(plain, dict):
        return _norm_ws(plain.get('content'))
    # Sometimes notes may be directly a string (rare)
    if isinstance(notes, str):
        return _norm_ws(notes)
    return ""

def _json_get_labels(topic: Dict[str, Any]) -> List[str]:
    lbs = topic.get('labels') or {}
    # Either {"labels":{"labels":[...]}} or {"labels":[...]}
    if isinstance(lbs, dict):
        res = lbs.get('labels') or []
        if isinstance(res, list):
            return [str(x) for x in res]
        return []
    if isinstance(lbs, list):
        return [str(x) for x in lbs]
    return []

def _json_get_markers(topic: Dict[str, Any]) -> List[str]:
    # Markers may be under "markers": [{"markerId": "..."}] or ["..."]
    mks = topic.get('markers') or []
    out = []
    if isinstance(mks, list):
        for m in mks:
            if isinstance(m, dict):
                mid = m.get('markerId') or m.get('id') or m.get('marker-id')
                if mid: out.append(str(mid))
            elif isinstance(m, str):
                out.append(m)
    # Some versions use "marker-refs": [{"markerId": "..."}]
    mrefs = topic.get('marker-refs') or topic.get('markerRefs') or []
    if isinstance(mrefs, list):
        for m in mrefs:
            if isinstance(m, dict):
                mid = m.get('markerId') or m.get('id')
                if mid: out.append(str(mid))
    return out

def _json_children(topic: Dict[str, Any]) -> List[Dict[str, Any]]:
    ch = topic.get('children') or {}
    # Common: {"children":{"attached":[...]}} ; also "detached"
    res = []
    for k in ('attached', 'detached'):
        arr = ch.get(k) or []
        if isinstance(arr, list):
            res.extend(arr)
    return res

def _walk_json_topic(lines: List[str],
                     topic: Dict[str, Any],
                     level: int,
                     opts) -> None:
    if opts.max_depth is not None and level > opts.max_depth:
        return
    title = topic.get('title') or ""
    hyperlink = topic.get('hyperlink') or topic.get('href') or None
    labels = _json_get_labels(topic) if opts.labels else None
    markers = _json_get_markers(topic) if opts.markers else None
    item = _format_line(title, hyperlink, labels, markers)
    lines.append(f"{_indent(level)}- {item}")
    if opts.notes:
        note = _json_get_note(topic)
        _add_note_lines(lines, note, level)
    for child in _json_children(topic):
        _walk_json_topic(lines, child, level + 1, opts)

def _parse_content_json(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    """Return list of sheets from content.json (XMind Zen/2020)."""
    with zf.open('content.json') as fp:
        data = json.load(fp)
    # data can be {"rootTopic":..., "title":...} for single sheet,
    # or {"sheets":[...]} or a list of sheets
    if isinstance(data, dict) and 'sheets' in data:
        sheets = data['sheets']
    elif isinstance(data, dict) and 'rootTopic' in data:
        sheets = [data]
    elif isinstance(data, list):
        sheets = data
    else:
        raise ValueError("Unrecognized JSON structure in content.json")
    return sheets

# ----------------------- XML (XMind 8) -----------------------

def _strip_ns(tag: str) -> str:
    return tag.split('}')[-1] if '}' in tag else tag

def _find_child(elem, localname: str):
    for c in list(elem):
        if _strip_ns(c.tag) == localname:
            return c
    return None

def _find_children(elem, localname: str) -> List[Any]:
    out = []
    for c in list(elem):
        if _strip_ns(c.tag) == localname:
            out.append(c)
    return out

def _xml_text(elem) -> str:
    if elem is None:
        return ""
    return (elem.text or "").strip()

def _xml_get_topic_title(topic_el) -> str:
    return _xml_text(_find_child(topic_el, 'title'))

def _xml_get_topic_hyperlink(topic_el) -> Optional[str]:
    # XMind 8 uses 'xlink:href' or 'href'
    for attr in ('{http://www.w3.org/1999/xlink}href', 'href', 'xlink:href'):
        if attr in topic_el.attrib:
            return topic_el.attrib.get(attr)
    return None

def _xml_get_topic_labels(topic_el) -> List[str]:
    labels_el = _find_child(topic_el, 'labels')
    if labels_el is None:
        return []
    return [_xml_text(lb) for lb in _find_children(labels_el, 'label') if _xml_text(lb)]

def _xml_get_topic_notes(topic_el) -> str:
    notes_el = _find_child(topic_el, 'notes')
    if notes_el is None:
        return ""
    # usually <notes><plain> ... text ... </plain></notes>
    plain_el = _find_child(notes_el, 'plain')
    if plain_el is None:
        return ""
    # Some files wrap note content in CDATA or inside another node; extract text with .text (ElementTree collapses it)
    return _xml_text(plain_el)

def _xml_get_topic_markers(topic_el) -> List[str]:
    # Markers: <markers><marker marker-id="priority-1"/></markers>
    markers_el = _find_child(topic_el, 'markers')
    out = []
    if markers_el is None:
        return out
    for mk in _find_children(markers_el, 'marker'):
        mid = mk.attrib.get('marker-id') or mk.attrib.get('markerId') or mk.attrib.get('id')
        if mid:
            out.append(mid)
    return out

def _xml_topic_children(topic_el) -> List[Any]:
    # Structure: <children><topics type="attached"><topic>...</topic></topics></children>
    children_el = _find_child(topic_el, 'children')
    out = []
    if children_el is None:
        return out
    for topics_el in _find_children(children_el, 'topics'):
        # type can be attached/detached; include both
        for t in _find_children(topics_el, 'topic'):
            out.append(t)
    return out

def _walk_xml_topic(lines: List[str], topic_el, level: int, opts) -> None:
    if opts.max_depth is not None and level > opts.max_depth:
        return
    title = _xml_get_topic_title(topic_el)
    hyperlink = _xml_get_topic_hyperlink(topic_el)
    labels = _xml_get_topic_labels(topic_el) if opts.labels else None
    markers = _xml_get_topic_markers(topic_el) if opts.markers else None
    lines.append(f"{_indent(level)}- " + _format_line(title, hyperlink, labels, markers))
    if opts.notes:
        note = _xml_get_topic_notes(topic_el)
        _add_note_lines(lines, note, level)
    for child in _xml_topic_children(topic_el):
        _walk_xml_topic(lines, child, level + 1, opts)

def _parse_content_xml(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    with zf.open('content.xml') as fp:
        tree = ET.parse(fp)
    root = tree.getroot()
    sheets = []
    for sheet in _find_children(root, 'sheet'):
        title = _xml_text(_find_child(sheet, 'title')) or 'Untitled Sheet'
        topic_el = _find_child(sheet, 'topic')
        sheets.append({'title': title, 'root_el': topic_el})
    return sheets

# ----------------------- Converter -----------------------

class Opts:
    def __init__(self, notes=True, labels=True, markers=True, max_depth=None):
        self.notes = notes
        self.labels = labels
        self.markers = markers
        self.max_depth = max_depth  # None or int

def convert_xmind_to_markdown(input_path: str,
                              output_path: Optional[str] = None,
                              notes: bool = True,
                              labels: bool = True,
                              markers: bool = True,
                              max_depth: Optional[int] = None) -> str:
    """
    Convert a .xmind file to Markdown; returns the Markdown string.
    If output_path is provided, also saves to that file (UTF-8).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    opts = Opts(notes=notes, labels=labels, markers=markers, max_depth=max_depth)
    lines: List[str] = []

    with zipfile.ZipFile(input_path, 'r') as zf:
        names = set(zf.namelist())
        is_json = 'content.json' in names
        is_xml = 'content.xml' in names

        if is_json:
            sheets = _parse_content_json(zf)  # list of dicts with rootTopic
            for i, sheet in enumerate(sheets, 1):
                stitle = sheet.get('title') or f'Sheet {i}'
                lines.append(f"# {stitle}")
                root = sheet.get('rootTopic') or {}
                # Some files store root as {'title':...} or include 'children'
                rtitle = root.get('title') or 'Root'
                lines.append(f"## {rtitle}")
                if opts.notes:
                    _add_note_lines(lines, _json_get_note(root), 0)
                for child in _json_children(root):
                    _walk_json_topic(lines, child, 0, opts)
                # blank line between sheets
                lines.append("")
        elif is_xml:
            sheets = _parse_content_xml(zf)
            for i, sheet in enumerate(sheets, 1):
                stitle = sheet.get('title') or f'Sheet {i}'
                lines.append(f"# {stitle}")
                root_el = sheet.get('root_el')
                if root_el is None:
                    lines.append("_(No root topic found)_\n")
                    continue
                rtitle = _xml_get_topic_title(root_el) or 'Root'
                lines.append(f"## {rtitle}")
                if opts.notes:
                    _add_note_lines(lines, _xml_get_topic_notes(root_el), 0)
                for child in _xml_topic_children(root_el):
                    _walk_xml_topic(lines, child, 0, opts)
                lines.append("")
        else:
            raise ValueError("This .xmind file doesn't contain content.json or content.xml")

    md = "\n".join(lines).rstrip() + "\n"
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
    return md

def main():
    parser = argparse.ArgumentParser(description="Convert XMind (.xmind) to Markdown (.md).")
    parser.add_argument("input", help="Path to input .xmind file")
    parser.add_argument("-o", "--output", help="Path to output .md file (defaults to input name with .md)")
    parser.add_argument("--max-depth", type=int, default=None, help="Limit output depth (0 = only first level topics)")
    parser.add_argument("--no-notes", action="store_true", help="Do not include topic notes")
    parser.add_argument("--no-labels", action="store_true", help="Do not include topic labels")
    parser.add_argument("--no-markers", action="store_true", help="Do not include topic markers")

    args = parser.parse_args()

    in_path = args.input
    out_path = args.output or (os.path.splitext(in_path)[0] + ".md")

    md_text = convert_xmind_to_markdown(
        in_path,
        output_path=out_path,
        notes=not args.no_notes,
        labels=not args.no_labels,
        markers=not args.no_markers,
        max_depth=args.max_depth
    )
    print(f"Converted to: {out_path}")
    # Print a short preview to stdout
    preview = "\n".join(md_text.splitlines()[:40])
    print("--- Preview (first 40 lines) ---")
    print(preview)

if __name__ == "__main__":
    main()
