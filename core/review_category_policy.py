from __future__ import annotations


REVIEW_CATEGORY_ID = "938"


def apply_review_category_policy(
    *,
    is_existing_product: bool,
    existing_category_ids: list[str] | None,
    review_category_id: str = REVIEW_CATEGORY_ID,
) -> dict:
    existing = [str(x) for x in (existing_category_ids or []) if str(x).strip()]
    # Deduplicate while preserving order.
    existing = list(dict.fromkeys(existing))

    if is_existing_product:
        # Existing categorization is part of channel structure and may influence
        # navigation / breadcrumbs / SEO. Never replace it merely for review.
        categories = list(existing)
        if review_category_id not in categories:
            categories.append(review_category_id)
        return {
            "mode": "KEEP_EXISTING_PLUS_REVIEW",
            "review_category_id": review_category_id,
            "original_category_ids": existing,
            "write_category_ids": categories,
            "remove_original_categories": False,
            "operator_queue_visible": True,
        }

    # New draft products have no inherited category history. During review they
    # live only in the central hidden operator category.
    return {
        "mode": "REVIEW_ONLY_FOR_NEW_DRAFT",
        "review_category_id": review_category_id,
        "original_category_ids": [],
        "write_category_ids": [review_category_id],
        "remove_original_categories": False,
        "operator_queue_visible": True,
    }


def publication_category_policy(
    *,
    is_existing_product: bool,
    original_category_ids: list[str],
    approved_target_category_ids: list[str] | None,
    review_category_id: str = REVIEW_CATEGORY_ID,
) -> dict:
    if is_existing_product:
        # After review, simply remove the temporary queue category.
        target = [x for x in original_category_ids if x != review_category_id]
        return {
            "action": "RESTORE_EXISTING_WITHOUT_REVIEW_CATEGORY",
            "category_ids": target,
        }

    approved = [
        str(x) for x in (approved_target_category_ids or [])
        if str(x).strip() and str(x) != review_category_id
    ]
    if not approved:
        return {
            "action": "BLOCK_PUBLICATION_NO_APPROVED_TARGET_CATEGORY",
            "category_ids": [review_category_id],
        }
    return {
        "action": "MOVE_NEW_PRODUCT_TO_APPROVED_CATEGORIES",
        "category_ids": list(dict.fromkeys(approved)),
    }
