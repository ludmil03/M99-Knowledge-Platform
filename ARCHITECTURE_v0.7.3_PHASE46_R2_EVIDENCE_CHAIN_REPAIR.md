# M99 v0.7.3 — Phase 4.6 R2 — Evidence Chain Repair

Status before operator acceptance: CANDIDATE / NOT YET ACCEPTED.

Scope: repair the proven R37 PREPARE Jinja syntax failure and preserve supplier variant evidence through Hydration -> PREPARE -> Identity -> DRAFT -> Canonical Preview. R37 remains free of channel-write logic. Phase 4.6 live m99.eu write remains in the separate accepted R1 control plane and is not invoked by this installer.

RIVER acceptance fixture: Calenda product 31809 / supplier ref 93100; 4 colour variants; 24 Color x Size rows; 20 IN_STOCK; 4 OUT_OF_STOCK; 4 colour-specific images. Supplier availability is evidence and is never M99 physical stock.

R2 stores a supplier evidence snapshot plus Identity result in ImportJobItem.detection for newly created DRAFTs. Canonical Preview prefers that immutable DRAFT snapshot and only uses live hydration as compatibility fallback for pre-R2 DRAFTs.

No DB migration. No m99.eu write. No Dolibarr write. No stock write. No automatic Git commit/push.

The Manufacturer official-source/canonical mapping blocker remains OPEN; PROMO STARS remains supplier brand evidence and is not silently promoted to canonical Manufacturer.


## FIX4 — Unicode-safe subprocess capture

Real Windows acceptance reached gate 9/10 after 586 maintained tests passed.
The installer then failed in Python's subprocess reader thread because
`text=True` selected the local cp1251 codec, while Git diff output contained
UTF-8 bytes including byte `0x98`.

The release driver now captures subprocess stdout/stderr as raw bytes
(`text=False`, `stdout=PIPE`, `stderr=PIPE`) and decodes them explicitly as
UTF-8 with replacement fallback. Diagnostic output can therefore never turn
into `None` because a locale decoder thread crashed.

This change is installer-only. It does not alter application runtime,
repository product logic, database state, supplier evidence, or channel writes.
