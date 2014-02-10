% e-Skolastik Yardım Sayfaları

Kullanıcılar için
===================
Profilimi nasıl düzenleyeceğim?
---------------------------------------------------
Öncelikle profil yönetim ekranındaki + işareti ile bir bölüm ekleyin. Her bölümün altına A+ N+ işaretlerini kullanarak
akademik yayınlar veya akademik olmayan yayınlar/belgeler ekleyebilirsiniz. 
Akademik yayınlar bibliyografik bilgileri (yazar, bölüm, editçrler, vb.) girebileceğiniz şekilde
tasarlanmıştır. Bunun dışındaki (ders notu, vs.) yayınları akademik olmayan belge olarak girebilirsiniz.

Ayrıca bölümleri kendi içinde alt bölümlere ayırmak için S+ ikonu ile "altbölüm ayracı" ekleyebilirsiniz. Altbölüm
ayracına "açıklama" girerek bu ayracın tamamını bir altbölüm gibi de kullanabilirsiniz. 

Profil yönetim ekranının en üstündeki profil ayarları kısmına gireceğiniz açıklama ve seçeceğiniz resim (max 1MB)
profilinizin en üstünde gözükecektir. Bu açıklama kısmına iletişim bilgilerinizi eklemeniz önerilir.

Profilinizdeki yayınlar için bir veya birden fazla dosya ekleyebilirsiniz. Bu dosyalar en fazla 5MB olabilir.

e-Skolastik profilimi alıp başka bir yere koyabilir miyim?
---------------------------------------------------------------
e-Skolastik bunu yapabilmeniz için tasarlanmıştır. Tabii profilinizi her değiştirdiğinizde aktarma işlemini 
tekrarlamanız gerekeceğini unutmayın.

Linux kullanıcıları 'wget' programı ile bu işlemi kolayca yapabilirler. Programa profil linkinizi verip uygun 
seçenekleri kullanarak profil sayfanızı ve onun içine gömülü diğer dosyaları yerel dosya sisteminize indirebilirsiniz.

Örnek:
    wget -r -p  -I /files -I /bigfiles http://e-skolastik.appspot.com/MehmetGencer/

Yayın dışındaki şeyleri nasıl listeleyebilirim?
------------------------------------------------
Örneğin üyesi bulunduğunuz meslek örgütlerini listeleyeceksiniz. Bunun en pratik yolu
bunun için bir bölüm veya bölü ayracının açıklama kısmını kullanmaktır. Açıklama kısımlarına
girdiğinizde beliren editör size bu kısımlara liste girme imkanı verir.

İleri düzey kullanıcılar için
==============================
Yönetim sayfasında sağ üst köşedeki 'Gelişmiş ayarları göster' seçeneği ile normalde gözükmeyen bazı 
ayarları görünür hale getirebilirsiniz. Bu yeni ayarlar kendi sayfa tasarımınızı oluşturmak, metin parçacıklarının
tercümesini girmek gibi işlevleri etkinleştirir.

Kendi tasarımınızı yapma
-------------------------
e-Skolastik profil sayfaları http://akdubya.github.com/dustjs/ şablonları kullanılarak görüntülenir. 
Tüm profil bilgileriniz tek bir JSON veri yapısı olarak seçilen dust.js şablonuna verilir
ve bu şablondan çıkan HTML profil sayfasını oluşturur. Bu işlemlerin tamamı istemcide (web tarayıcı) yapılmaktadır.

Kendi tasarımınızı yapabilmek için iki bilgiye ihtiyacınız olacak. Birincisi profil bilgilerinizin JSON veri yapısı.
Aşağıdaki -basitleştirilmiş- örnekte birden fazla sayıda olabilecek listeler ... ile gösterilmiştir:

      {
        "title": "Profil başlığı",
        "profiledesc": "Profil açıklaması",
        "profilePicture": { 
          "fileUrl": "/files/ag9kZXZ-ZS1za29sYXN0aWtyIgsSB1Byb2ZpbGUYAQwLEg5Qcm9maWxlUGljdHVyZRi5Fww",
          "fileName": "foto.jpg"
        },
        "sections": [
          {
            "secdesc": "Bölüm açıklaması",
            "sectionKey": 111, //Bu bölüme sistem tarafından verilmiş tekil bir sayı.
            "publications": [
              {
                "title": "yayın 1",
                "publicationKey":222, //Bu yayına sistem tarafından verilmiş tekil bir sayı
                "desc": "yayın açıklaması",
                "ispub": true, //eğer doğru ise bu bir akademik yayındır ve aşağıdaki "pubinfo" alanları kullanılır
                               //Değilse sadece başlık ve açıklama alanları kullanılmalıdır.
                "issep": false, //Bu bir alt-bölüm ayracı ise 'true' değerini alır.
                "pubtype": "inproceedings",
                "pfiles": [
                  { 
                    "fileUrl": "/files/ag9kZXZ-ZS1za29sYXN0aWtyQwsSB1Byb2ZpbGUYAQwLEgdTZWN0aW9uGOkHDAsSC1B1YmxpY2F0aW9uGOsHDAsSD1B1YmxpY2F0aW9uRmlsZRjvBww",
                    "fileName": "makale.pdf"
                  }, ...],
                "pubinfo": {
                  "publisher": "Springer",
                  ...
                  //Burada çok sayıda bilgi alanı var. Bunlar BibTeX standardına göre düzenlenmiştir.
                  //ancak aşağıda göreceğiniz üzere yayınların bibliyografik özetini citeproc-js kullanarak
                  //bu alanları hiç işlemeden çıkartabileceksiniz.
                },
                "authors": [{"name": "Mehmet Gençer"}, ...]
              }, ...
          ]
      }

Kendi tasarımınızı yaparken ikinci olarak yukarıdaki veri yapısını tarayıp HTML üretecek dust.js döngülerini
kurmanız gerekecektir. Yeni bir tasarım yaratınca öntanımlı olarak gelen aşağıdaki dust.js kodu
çok kısa bir şekilde bunu yapıyor:

    <div class="estemplate" tid="default">
      Profil: {title} <br/>
      {#sections}
        Bölüm: {.title}&lt;br/&gt;
        Açıklama: {.secdesc}&lt;br/&gt;
        {#publications}
          {.title}
        {/publications}
      {/sections}
      </div>

Dust.js kullanırken sadece {...} kodları özel bir anlam taşır. Bunun dışında kalanlar HTML.
Örneğin {title} kodu JSON veri yapısında en üst düzeydeki "title" alanının içeriğini görüntüler.

{#sections} ile başlayıp {/sections} ile biten kısım ise JSON yapısında bir liste olan
"sections" alanının her liste elemanı için tekrar edilecek bir döngüdür. Her tekrarda eldeki liste elemanını,
ki bu örnekte bir sözlük (map, dictionary), kullanabileceğimiz dust.js veri alanlarına eklenir.
Bu yüzden section döngüsünün içerisinde {.title} dediğimizde en derindeki "title" isimli alan anlaşılır.
sadece {title} yazsaydık en yüksekteki (yani profil'e ait 'title') anlaşılırdı.

'sections' döngüsünün içinde de bir 'publications' döngüsü bulunmaktadır. Orada da bir {.title} var,
ve bu kez yayın'ın başlığını kastediyoruz. İsterseniz 'publications' döngüsünün içine de bir döngü ekleyip
yayına ait dosyaları listeleyebilirsiniz (en sondaki örnek)
Tasarımlarda koşullu işlemler de yaptırabilirsiniz. Örneğin yayınlarda akademik olan (daha doğrusu standart kalıplara
uyan) ve olmayan ayırımı var. Bu ayırımı bize söyleyen "ispub" veri alanı, ki mantıksal (doğru/yanlış değeri alan)
bir veri alanıdır. Bunun için koşullu bir tasarım yapmak istersek dust.js'te mantıksal alanlara göre
koşullu işlem için kullanılan {?ispub}...{:else}...{/ispoub} kalıbını kullanmamız gerekecek:
      
      <div class="estemplate" tid="default">
      Profil: {title} <br/>
      {#sections}
        Bölüm: {.title}<br/>
        Açıklama: {.secdesc}<br/>
        {#publications}
          {.title}
          {?ispub}
           Bu akademik bir yayın...
          {:else}
           Akademik olmayan yayın. Açıklama: {.desc}
          {/ispub}
        {/publications}
      {/sections}
      </div>

Bu son örnekte ".ispub" kullanmaya gerek duymadan "ispub" kullandık. Daha derinlerde aynı ismi taşıyan 
veri olmadığından bir karışıklık çıkmıyor.

Yayın bilgilerinin alıntılamaya uygun bibliyografik formatlaması için altyapıda citeproc-js kullanılmıştır.
Bundan yararlanmak için akademik tipteki yayının içinde {#citeproc/} kodunu koymanız yeterli olur:

      
      <div class="estemplate" tid="default">
      Profil: {title} <br/>
      {#sections}
        Bölüm: {.title}<br/>
        Açıklama: {.secdesc}<br/>
        {#publications}
          {.title}
          {?ispub}
           {#citeproc/}
          {:else}
           Akademik olmayan yayın. Açıklama: {.desc}
          {/ispub}
        {/publications}
      {/sections}
      </div>

Son olarak bu tasarıma (1) Türkçe bilmeyen ziyaretçilere de hitap etmesi için tercüme, ve (2) yayın dosyalarını 
görüntüleme ekleyelim. Tercüme için {#i18n msg="tercümesi yapılacak metin"/} benzeri bir kod kullanın. Tabii tercümenin
gerçekleşmesi için gelişmiş ayarlar ekranının sonundaki kısmı kullanarak tercümelerinizi yapın (büyük/küçük harf hassastır).
Artık ziyaretçiler web tarayıcılarında hangi dili tercih ettilerse profil sayfasındaki yazılar o dile çevrilir. 'msg' 
parametresine değer olarak bir alan ismi de verebilirsiniz (mesela makale başlıklarını tercüme etmek için!). 
Verilen metnin tercümesi bulunamazsa aynen kendisi yazılır. Dolayısıyla bu şekilde bir tasarım ile
zaman içerisinde tercüme kataloğunuzu genişletebilirsiniz.
"Bölüm", "Açıklama" gibi kimi kelimeler sistemin tercüme kataloğunda zaten bulunduğundan onları yapmanız gerekmeyebilir.

      <div class="estemplate" tid="default">
      Profil: {title} <br/>
      {#sections}
        {#i18n msg="Bölüm"/} : {#i18n msg=.title/}<br/>
        Açıklama: {.secdesc}<br/>
        {#publications}
          {.title}
          {?ispub}
            {#citeproc/}
          {:else}
            Akademik olmayan yayın. Açıklama: {.desc}
          {/ispub}
          {#files}
            <a href='{.fileUrl}'>{.fileName}</a>
          {/files}
        {/publications}
      {/sections}
      </div>

Yukarıdaki örneklerin pek te iyi bir tasarım görüntüsü üretmeyeceğini belirteyim. 
Tasarım mekaniğini anlatabilmek için HTML kodlarını en azda tuttum.

Tasarımlarınızda ayrıca HTML/CSS stili yaratabilmeniz için bir "stil" kutusu vardır.
Tasarımınızdaki HTML elemanlarına 'class' tanımlayarak bu stilleri etkinleştirebilirsiniz.

Yaptığınız tasarımlar başka kullanıcılar tarafından da kullanılabilecektir (stil ve tercümeleri dahil). 
Eğer bunu istemiyorsanız 
(çok spesifik bir amacı varsa, vb.) tasarımın açıklama kısmına bunu not düşmeyi unutmayın. Aksi takdirde
tasarımınıza niteliklerini ifade eden bir isim ve açıklama vermeye çalışın.

Geliştiriciler için
=====================================
(Henüz yazılmamıştır)
