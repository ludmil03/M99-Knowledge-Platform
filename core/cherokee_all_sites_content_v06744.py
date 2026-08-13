PRODUCT={
 "brand":"Cherokee","collection":"WW Revolution","style":"WW601","supplier_alias":"WWE601",
 "manufacturer_item":"CK-WW601--","colour":"Navy","reference":"M99-CHEROKEE-WW601-NAVY"
}

CHANNEL_CONTENT={
"mela99.com":{
 "bg":{"name":"Дамска медицинска туника Cherokee WW Revolution WW601 Navy","short":"Професионална дамска медицинска туника Cherokee WW601 Navy с еластична материя, свободна кройка, два предни джоба и мрежести странични панели.","html":"<h2>Cherokee WW601 Navy</h2><p>Дамска медицинска туника от серията WW Revolution с 78% полиестер, 20% вискоза и 2% еластан.</p><h2>Функционалност</h2><p>Два предни джоба с примки за инструменти, мрежести странични панели, къси ръкави и извито V-образно деколте.</p><h2>Размери</h2><p>При доказания доставчик са наблюдавани 2XS–2XL; това не е текуща складова наличност.</p>","meta_title":"Cherokee WW601 Navy дамска медицинска туника | MELA99","meta_description":"Cherokee WW601 Navy дамска медицинска туника с еластична материя, V-образно деколте, 2 джоба и мрежести странични панели."},
 "en":{"name":"Cherokee WW Revolution WW601 Navy Women's Scrub Top","short":"Cherokee WW601 Navy women's scrub top with stretch fabric, relaxed fit, two front pockets and mesh side panels.","html":"<h2>Cherokee WW601 Navy</h2><p>WW Revolution women's scrub top in 78% polyester, 20% rayon and 2% spandex.</p><h2>Functionality</h2><p>Two front patch pockets with instrument loops, mesh side panels, short sleeves and a curved V-neckline.</p><h2>Sizes</h2><p>2XS–2XL were observed at the exact supplier product; this is not a live stock claim.</p>","meta_title":"Cherokee WW601 Navy Women's Scrub Top | MELA99","meta_description":"Cherokee WW601 Navy women's scrub top with stretch fabric, curved V-neck, 2 front pockets and mesh side panels."},
 "ru":{"name":"Женская медицинская туника Cherokee WW Revolution WW601 Navy","short":"Женская медицинская туника Cherokee WW601 Navy из эластичной ткани, с двумя карманами и сетчатыми боковыми панелями.","html":"<h2>Cherokee WW601 Navy</h2><p>Женская медицинская туника WW Revolution: 78% полиэстер, 20% вискоза и 2% эластан.</p><h2>Функциональность</h2><p>Два передних кармана, петли для инструментов, сетчатые боковые панели, короткие рукава и V-образный вырез.</p>","meta_title":"Cherokee WW601 Navy женская медицинская туника | MELA99","meta_description":"Cherokee WW601 Navy: эластичная ткань, V-образный вырез, 2 кармана и сетчатые боковые панели."}
},
"m99.eu":{},
"rabotni-drehi.com":{},
"medicinski-drehi.com":{},
"laviro.ro":{},
"alviro.ro":{}
}

def clone_site(base_site, target_site, langs, focus):
    src=CHANNEL_CONTENT[base_site]
    out={}
    for lang in langs:
        d=dict(src[lang if lang in src else "en"])
        d["meta_title"]=d["meta_title"].replace("MELA99",target_site.split(".")[0].upper())
        d["short"]=focus[lang]+" "+d["short"]
        d["html"]=f"<h2>{focus[lang]}</h2><p>{d['short']}</p>"+d["html"]
        out[lang]=d
    CHANNEL_CONTENT[target_site]=out

clone_site("mela99.com","m99.eu",["bg","en","ru"],{
 "bg":"Технически продуктов профил.","en":"Technical product profile.","ru":"Технический профиль продукта."})
clone_site("mela99.com","rabotni-drehi.com",["bg","en","ru"],{
 "bg":"Професионално работно облекло за активен работен ден.","en":"Professional workwear for an active working day.","ru":"Профессиональная рабочая одежда для активного дня."})
clone_site("mela99.com","medicinski-drehi.com",["bg","en","ru"],{
 "bg":"Медицинско облекло за здравни специалисти.","en":"Medical apparel for healthcare professionals.","ru":"Медицинская одежда для специалистов здравоохранения."})
clone_site("mela99.com","laviro.ro",["ro","en"],{
 "ro":"Bluză medicală profesională pentru personal medical.","en":"Professional medical scrub top for healthcare staff."})
clone_site("mela99.com","alviro.ro",["ro","en"],{
 "ro":"Profil profesional pentru piața medicală din România.","en":"Professional catalogue profile for the Romanian medical market."})
