# M99 v0.7.3 Phase 4.5 Revision 20 — Progressive Hydration Performance

## Real performance problem
Eager category hydration made Supplier Browser wait for every discovered
product URL before returning HTML. A category with ~40 products therefore
required ~40 supplier HTTP reads before the operator saw the page.

## Revision 20
Category inspection is fast:
1. read category page once;
2. discover product URLs;
3. render UI immediately with WAITING rows;
4. browser calls local `/supplier-browser/hydrate-product` progressively;
5. max 4 concurrent live supplier hydrations;
6. each row becomes selectable only after PASS.

## Cache
In-process hydration cache TTL: 10 minutes.
Repeated inspection of the same product avoids unnecessary live reads.

## Safety
- zero selected by default;
- checkbox disabled until PASS;
- create-job re-verifies selected supplier URLs;
- supplier remains read-only;
- manufacturer enrichment remains separate;
- no DRAFT or channel write from installer.
