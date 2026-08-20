from enum import Enum


class KnowledgeStatus(str, Enum):
    DRAFT = "draft"
    IMPORTED = "imported"
    VALIDATED = "validated"
    OFFICIAL = "official"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class ProductLifecycle(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class PublicationStatus(str, Enum):
    NOT_PUBLISHED = "not_published"
    DRAFT = "draft"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class ChannelKind(str, Enum):
    WEBSITE = "website"
    MARKETPLACE = "marketplace"
    ERP = "erp"
    INTERNAL = "internal"
