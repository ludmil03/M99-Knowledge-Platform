from __future__ import annotations

from copy import deepcopy
import xml.etree.ElementTree as ET


def _strip_namespace(tag: str) -> str:
    return tag.split('}', 1)[1] if '}' in tag else tag


def _child(parent, tag):
    if parent is None:
        return None
    for node in list(parent):
        if _strip_namespace(node.tag) == tag:
            return node
    return None


def _schema_child_map(schema_node):
    return {_strip_namespace(x.tag): x for x in list(schema_node)}


def _prune_node(data_node, schema_node):
    allowed = _schema_child_map(schema_node)
    for child in list(data_node):
        tag = _strip_namespace(child.tag)
        schema_child = allowed.get(tag)
        if schema_child is None:
            data_node.remove(child)
            continue

        if not list(child) or not list(schema_child):
            continue

        if tag in {
            'name', 'description', 'description_short', 'link_rewrite',
            'meta_title', 'meta_description', 'available_now', 'available_later'
        }:
            # Language rows are variable/repeated; preserve the live current values.
            continue

        if tag in {
            'categories', 'images', 'combinations', 'product_option_values',
            'product_features', 'tags', 'stock_availables', 'accessories'
        }:
            templates = list(schema_child)
            if templates:
                record_schema = templates[0]
                for record in list(child):
                    _prune_node(record, record_schema)
            continue

        _prune_node(child, schema_child)


def build_writable_product_snapshot(current_product_xml: str, blank_product_schema_xml: str) -> str:
    current_root = ET.fromstring(current_product_xml)
    schema_root = ET.fromstring(blank_product_schema_xml)
    current_product = current_root.find('.//product')
    schema_product = schema_root.find('.//product')
    if current_product is None:
        raise ValueError('Current product XML has no product node')
    if schema_product is None:
        raise ValueError('Blank product schema XML has no product node')

    filtered_root = deepcopy(current_root)
    filtered_product = filtered_root.find('.//product')
    _prune_node(filtered_product, schema_product)

    current_id = (current_product.findtext('id') or '').strip()
    filtered_id = filtered_product.find('id')
    if filtered_id is None:
        filtered_id = ET.Element('id')
        filtered_product.insert(0, filtered_id)
    filtered_id.text = current_id

    return ET.tostring(filtered_root, encoding='utf-8', xml_declaration=True).decode('utf-8')


def removed_top_level_fields(current_product_xml: str, writable_product_xml: str) -> list[str]:
    current = ET.fromstring(current_product_xml).find('.//product')
    writable = ET.fromstring(writable_product_xml).find('.//product')
    before = {_strip_namespace(x.tag) for x in list(current)}
    after = {_strip_namespace(x.tag) for x in list(writable)}
    return sorted(before - after)
