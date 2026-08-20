# M99 Platform v1.0 Target Architecture

M99 Knowledge Platform is the canonical control plane for product knowledge,
supplier evidence, channel content, pricing, availability and integrations.

Canonical model:
ProductGroup -> ProductVariant -> SupplierOffer -> Evidence
             -> ChannelPresence -> ChannelContent -> ChannelPrice
             -> InventoryMapping

Lifecycles:
KnowledgeStatus: draft -> imported -> validated -> official -> approved -> deprecated
ProductLifecycle: draft -> active -> paused -> retired
PublicationStatus: not_published -> draft -> published -> suspended -> removed

Hard deletion is exceptional and requires explicit operator permission,
literal DELETE confirmation and an audit event.

Target stable namespaces:
core/identity
core/catalog
core/evidence
core/suppliers
core/pricing
core/availability
core/content
core/seo
core/publishing
core/channels
core/governance

Development DB: SQLite
Production target DB: PostgreSQL
Schema migrations: Alembic

Suppliers -> M99 Canonical Master <-> Dolibarr -> Channels
