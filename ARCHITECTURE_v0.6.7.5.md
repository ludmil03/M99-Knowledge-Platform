# v0.6.7.5 — Cherokee WW601 Real Product Publish

This milestone converts the proven Cherokee WW601 pilot from preview/readiness into a controlled real **WRITE_DRAFT** workflow.

## Scope

Required write channels: `mela99.com`, `rabotni-drehi.com`, `medicinski-drehi.com`, `laviro.ro`, `alviro.ro`.

`m99.eu` remains in the publication plan but is explicitly `TASK_ONLY / TEMPORARILY_EXCLUDED_TECHNICAL_PROBLEMS`. No request that can create or update a product may be sent to m99.eu in v0.6.7.5.

## Product identity

- Cherokee / WW Revolution / WW601 / Navy
- supplier alias: WWE601
- Stenso reference: 08001931
- manufacturer item: CK-WW601--

## Commercial rule

Exact Stenso price is re-read before write. Expected pilot observation is 25.20 EUR. Conversion is `EUR × 1.95583`, then M99 price is `× 0.987`, rounded to 2 decimals. Expected result: **48.65 BGN**. The 97.79 BGN free-delivery threshold must never be interpreted as product price.

## Safety gates

1. exact Stenso page must still identify WWE601 / 08001931;
2. exact EUR price must be extracted from the product price area;
3. calculated price must pass sanity validation;
4. all five required channels must pass credential/platform preflight;
5. content must come from the existing v0.6.7.4.2/v0.6.7.4.4 Cherokee content engine;
6. write state is draft/inactive only;
7. readback is mandatory;
8. no stock claim is created from visible sizes;
9. no write to m99.eu;
10. no automatic activation.

## Operator contract

Installer never writes to websites. Real website writes require running the explicit real-write launcher and typing the literal confirmation shown by the launcher.
