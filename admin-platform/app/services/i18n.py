UI={
"BG":{"dashboard":"Табло","products":"Продукти","presence":"Присъствие на продукти","suppliers":"Доставчици / Преглед","imports":"Импорт задачи","sync":"Ежедневна синхронизация","audit":"Одит лог","users":"Потребители","roles":"Роли и права","languages":"Езици","system":"СИСТЕМА","catalog":"КАТАЛОГ","logout":"Изход"},
"EN":{"dashboard":"Dashboard","products":"Products","presence":"Product Presence","suppliers":"Suppliers / Browse","imports":"Import Jobs","sync":"Daily Existing Product Sync","audit":"Audit Log","users":"Users","roles":"Roles & Permissions","languages":"Languages","system":"SYSTEM","catalog":"CATALOG","logout":"Logout"},
"RU":{"dashboard":"Панель","products":"Товары","presence":"Наличие товаров по каналам","suppliers":"Поставщики / Просмотр","imports":"Задачи импорта","sync":"Ежедневная синхронизация","audit":"Журнал аудита","users":"Пользователи","roles":"Роли и права","languages":"Языки","system":"СИСТЕМА","catalog":"КАТАЛОГ","logout":"Выход"},
"RO":{"dashboard":"Panou","products":"Produse","presence":"Prezența produselor","suppliers":"Furnizori / Navigare","imports":"Joburi import","sync":"Sincronizare zilnică","audit":"Jurnal audit","users":"Utilizatori","roles":"Roluri și permisiuni","languages":"Limbi","system":"SISTEM","catalog":"CATALOG","logout":"Ieșire"},
"GR":{"dashboard":"Πίνακας","products":"Προϊόντα","presence":"Παρουσία προϊόντων","suppliers":"Προμηθευτές / Περιήγηση","imports":"Εργασίες εισαγωγής","sync":"Ημερήσιος συγχρονισμός","audit":"Αρχείο ελέγχου","users":"Χρήστες","roles":"Ρόλοι και δικαιώματα","languages":"Γλώσσες","system":"ΣΥΣΤΗΜΑ","catalog":"ΚΑΤΑΛΟΓΟΣ","logout":"Έξοδος"}}
def ui_for(code):
    code=(code or "BG").upper()
    base=UI["EN"].copy();base.update(UI.get(code,UI["BG"]))
    return base
