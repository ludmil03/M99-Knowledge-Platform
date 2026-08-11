# M99 Knowledge Platform v0.6.6.4.1
## Safe Writable Product Payload + Error Diagnostics

Patch after the first v0.6.6.4 PUT returned HTTP 400.

The update no longer PUTs the raw full product GET snapshot. Immediately before write it fetches the live `/api/products?schema=blank` from mela99.com and filters the current product XML to fields/association shapes supported by that live schema. Current values remain the source of truth; the blank schema is used only as an allow-list/shape.

Then M99 applies the same controlled draft changes: product 2076 only, active=0, current name kept by default, slug/URL/reference kept, existing categories kept plus review category 938, duplicate products untouched.

Rollback now stores both the untouched full GET snapshot and a schema-filtered writable rollback payload. HTTP failures record status and a bounded server response excerpt in the audit without credentials.

Installer performs no website write.
