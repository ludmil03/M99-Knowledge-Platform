# M99 v0.7.0 — Admin Platform Foundation

Първи работещ foundation за преминаване от standalone importer scripts към многопотребителски M99 Admin Panel.

Включено:
- FastAPI backend;
- SQLite development DB, готова архитектура за PostgreSQL;
- вход чрез username или email + password;
- Argon2 password hashing;
- signed session cookie;
- Users / Roles / Permissions data model;
- M99_SUPER_ADMIN и CHANNEL_MANAGER;
- PrestaShop-style admin layout;
- Dashboard;
- Products;
- Product Presence;
- Suppliers / Browse & Import foundation;
- Import Jobs;
- Daily Existing Product Sync contract;
- Audit Log;
- всички web targets + Dolibarr като ERP target.

Това е Foundation, без website writes, supplier scraping, Dolibarr write, stock write, activation или DELETE.

Първо стартиране:
1. Разархивирай в постоянна папка или използвай safe installer.
2. RUN_M99_ADMIN_FIRST_SETUP.bat
3. Създай Super Admin username/email/password.
4. RUN_M99_ADMIN.bat
5. Отвори http://127.0.0.1:8070

Следващ vertical slice v0.7.0.1:
- Users UI;
- Roles/Permissions UI;
- channel-level permissions;
- Supplier Browser URL import;
- Stenso single-product ImportJob;
- target selection само за NEW products;
- Product Presence detail.
