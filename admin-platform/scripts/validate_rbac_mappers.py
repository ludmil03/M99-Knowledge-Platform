from sqlalchemy.orm import configure_mappers
from app.models.entities import User,Role,Permission
print("M99 RBAC MAPPER VALIDATION")
configure_mappers()
assert User.roles.property.back_populates=="users"
assert Role.users.property.back_populates=="roles"
assert Role.permissions.property.back_populates=="roles"
assert Permission.roles.property.back_populates=="permissions"
print("User.roles <-> Role.users: PASS")
print("Role.permissions <-> Permission.roles: PASS")
print("RBAC mapper validation: PASS")
