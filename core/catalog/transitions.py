from .enums import ProductLifecycle


_ALLOWED_PRODUCT_TRANSITIONS = {
    ProductLifecycle.DRAFT: {ProductLifecycle.ACTIVE, ProductLifecycle.RETIRED},
    ProductLifecycle.ACTIVE: {ProductLifecycle.PAUSED, ProductLifecycle.RETIRED},
    ProductLifecycle.PAUSED: {ProductLifecycle.ACTIVE, ProductLifecycle.RETIRED},
    ProductLifecycle.RETIRED: set(),
}


def transition_product_lifecycle(
    current: ProductLifecycle,
    target: ProductLifecycle,
) -> ProductLifecycle:
    if target == current:
        return current
    if target not in _ALLOWED_PRODUCT_TRANSITIONS[current]:
        raise ValueError(f"invalid product lifecycle transition: {current.value} -> {target.value}")
    return target


def require_hard_delete_confirmation(
    *,
    operator_approved: bool,
    permission_granted: bool,
    literal_confirmation: str,
) -> bool:
    if not operator_approved:
        raise PermissionError("operator approval is required")
    if not permission_granted:
        raise PermissionError("hard-delete permission is required")
    if literal_confirmation != "DELETE":
        raise ValueError("literal DELETE confirmation is required")
    return True
