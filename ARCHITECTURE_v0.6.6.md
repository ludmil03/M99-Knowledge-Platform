# M99 Knowledge Platform v0.6.6
## Controlled Single Product Publish

v0.6.6 is the first write-capable channel version.

Target is intentionally limited to:
- channel: mela99.com
- product: M99 100002
- manufacturer item: 701.183121_80013
- one product only
- one channel only

### Modes

DRY_RUN
- no HTTP write;
- builds gates, action and audit preview.

WRITE_DRAFT
- real POST/PUT allowed;
- product stays inactive (`active=0`);
- new CREATE goes to hidden Test category ID 938;
- no sale price is changed unless separately approved.

PUBLISH_LIVE
- real POST/PUT allowed;
- product may become active;
- approved pricing and availability are mandatory.

### Existing Channel Identity Lock

For UPDATE, the current channel identity is protected:
- product ID: KEEP;
- slug/link_rewrite: KEEP;
- URL: KEEP;
- old channel reference / legacy identifier: KEEP;
- product name: KEEP by default.

A product name may change only when:
1. the new name is marked `PROVEN_BETTER`;
2. the operator separately approves the name change.

Even when the name is changed, the existing slug/link_rewrite and URL remain
unchanged.

### Full Snapshot Update

Before UPDATE:
1. GET the complete current product XML;
2. save it as rollback snapshot;
3. mutate only approved fields;
4. never regenerate link_rewrite;
5. preserve existing reference when already populated;
6. PUT the complete mutated snapshot back.

This avoids accidental loss of fields not managed by M99.

### CREATE

For a new product:
- BG/EN names are generated from CONTENT_READY content;
- BG/EN slugs are generated once;
- Test category ID 938 is used in WRITE_DRAFT;
- active=0 in WRITE_DRAFT;
- LIVE creation requires approved sale price.

After first create, product name + slug + URL become Channel Identity and the
same UPDATE protection rules apply.

### Required gates

Every write requires:
- live v0.6.5 internal discovery;
- decision exactly EXISTING or NEW;
- CONTENT_READY;
- one-product scope;
- mela99.com-only scope;
- operator approval;
- exact typed confirmation;
- audit enabled;
- rollback enabled.

LIVE additionally requires:
- pricing approval;
- availability approval;
- approved price for CREATE.

### Credentials

The mela99.com Webservice key is entered locally into PowerShell and exists only
in that process. It is not written to Git, JSON, audit files or environment files.

### Audit / rollback

Every attempt creates an audit JSON under:
`output/publish_audit/`

UPDATE captures original XML under:
`output/publish_rollback/`

CREATE is never automatically deleted as rollback. Product deletion remains a
separate operator-controlled action.

### Important

Do not run WRITE_DRAFT or PUBLISH_LIVE before:
1. v0.6.5 LIVE GET-only discovery succeeds for mela99.com;
2. the discovery result has been reviewed.

The intended first real test is WRITE_DRAFT. It performs a real API write but
keeps the product inactive. After verification, PUBLISH_LIVE may be tested.
