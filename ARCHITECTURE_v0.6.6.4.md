# M99 Knowledge Platform v0.6.6.4
## Controlled S3S Master WRITE_DRAFT

First real write target:
- mela99.com
- product ID 2076
- M99 100017
- Diadora GLOVE A.BOX LOW PRO S3S
- master state must be EXISTING_CONFIRMED

### Central Review Category

Category 938 is the single operator review queue.

New products:
- during WRITE_DRAFT: category 938 only;
- active=0;
- after operator approval they must receive approved production categories
  before live publication.

Existing improved products:
- all current categories/subcategories are preserved;
- category 938 is added temporarily;
- no current category is removed merely for review;
- after approval, category 938 may be removed and the original categories remain.

This gives the operator one place to review all changed/new products without
destroying existing navigation, breadcrumbs or channel categorization.

### Existing Master Identity

For product 2076:
- product ID: KEEP;
- current product name: KEEP by default;
- current slug/link_rewrite: KEEP;
- URL: KEEP;
- current reference: KEEP as legacy identity.

A name change remains possible only when independently marked PROVEN_BETTER
and explicitly approved by the operator. Name change never regenerates URL.

### WRITE_DRAFT

The real write procedure:
1. verify local master-selection JSON says MASTER_SELECTED and
   EXISTING_CONFIRMED for 2076;
2. require local API key and explicit operator approval;
3. require exact typed confirmation:
   WRITE_DRAFT UPDATE 2076 M99 100017 MELA99
4. GET complete current product XML;
5. save rollback XML before write;
6. mutate only approved content + active=0 + add review category 938;
7. preserve original categories, images, combinations, ID, reference and URL;
8. PUT complete snapshot;
9. immediately GET product again and save readback snapshot;
10. write audit JSON.

Products 2100 and 2147 remain untouched.

### Safety

This installer performs no website write.
Only scripts/RUN_V0664_S3S_MASTER_WRITE_DRAFT.bat performs the real write,
after explicit operator confirmation.
