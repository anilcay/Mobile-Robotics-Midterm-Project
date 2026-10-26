# Mimari Karar Kayıtları (ADR)

Yeni karar en alta eklenir. Format: bağlam → karar → sonuç. Bir karar değişirse eski kayıt silinmez; durumu `Değiştirildi (ADR-xxx)` yapılır.

---

## ADR-001 — Hedef platform: ROS 2 Lyrical + Gazebo Jetty
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Proje dökümanı değerlendirmenin ROS 2 Lyrical ve Gazebo Jetty ile yapılacağını söylüyor.
- **Karar:** Hedef Ubuntu 26.04 + ROS 2 Lyrical + Gazebo Jetty (gz-sim 10), `ros_gz` paketleri.
- **Sonuç:** Kaynaklar az olduğu için eklenti ve bridge adları kurulumda doğrulanacak (`INTERFACES.md`'de ⚠ işaretli).

## ADR-002 — Windows'ta geliştirme, katmanlı doğrulama
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Üye A şimdilik Windows 10'da kalıyor; ROS 2/Gazebo yerelde çalışmıyor.
- **Karar:** Kod Linux hedefli yazılır. Doğrulama: (1) Windows'ta statik kontroller ve saf mantık testleri, (2) GitHub Actions CI'da `colcon build/test`, (3) en geç 30 Ekim'e kadar bir Linux ortamında (WSL2/VM/Üye B) simülasyon testi.
- **Sonuç:** Simülasyon davranışı geç doğrulanır; risk "Linux'ta doğrulanmadı" işaretleriyle görünür tutulur.

## ADR-003 — Senaryo: SeraBot (sera denetim robotu)
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Üç senaryo değerlendirildi: sera denetimi, arama-kurtarma, tenis topu toplama.
- **Karar:** Sera denetim robotu. Teknik riski düşük; çekirdek davranış (LiDAR ile engelden kaçma) Üye A'nın modülüne dayanıyor, kamera katmanı opsiyonel.
- **Sonuç:** Kamera modülündeki gecikme demoyu bloklamaz.

## ADR-004 — Diferansiyel sürüş, gz DiffDrive sistemi (ros2_control değil)
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** `/cmd_vel` ile hareket gerekiyor. Seçenekler: gz-sim DiffDrive sistemi veya ros2_control + gz_ros2_control.
- **Karar:** gz-sim `DiffDrive` + `JointStatePublisher` sistemleri, `ros_gz_bridge` ile.
- **Sonuç:** Daha az bağımlılık ve sürüm riski. `/cmd_vel` tipi `geometry_msgs/msg/Twist`.

## ADR-005 — Sensör seti: LiDAR, kamera, IMU
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** 2 kişilik grup → en az 3 sensör tipi. Her üye bir sensörden sorumlu, ek sensör açıkça atanmalı.
- **Karar:** LiDAR (Üye A), RGB kamera (Üye B), IMU (ortak). Bumper/contact sensörü zaman kalırsa 4. sensör.
- **Sonuç:** IMU davranışta dönüş açısı ölçümü için kullanılır, böylece "ek" sensör de işlevsel.

## ADR-006 — Paket yapısı ve dosya sahipliği
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Birden çok Claude oturumu ve iki kişi aynı repoda paralel çalışıyor.
- **Karar:** 5 paket (`description`, `gazebo`, `bringup`, `sensors`, `behavior`). Her sensörün kendi xacro dosyası ve kendi bridge yaml'ı var; launch her yaml için ayrı bridge node'u başlatır. Paylaşılan dosyalar (ana xacro, RViz config, paket manifestleri, `INTERFACES.md`) S0'a ait. Sahiplik tablosu `CLAUDE.md`'de.
- **Sonuç:** Paralel geliştirmede dosya çakışması olmaz; arayüz değişiklikleri tek noktadan geçer.

## ADR-007 — Dil kuralı
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Karar:** Kod, yorumlar, commit mesajları ve README İngilizce; `CLAUDE.md` ve `docs/` Türkçe.

## ADR-008 — Dünyada sadece primitif geometri
- **Tarih:** 2026-10-24 · **Durum:** Değiştirildi (ADR-018)
- **Bağlam:** Gazebo Fuel modelleri çalışma anında internet gerektirir; demo sırasında risk.
- **Karar:** Sera dünyası kutu/silindir/küre gibi primitiflerle repoda tanımlanır.
- **Sonuç:** Çevrimdışı çalışır, tekrarlanabilir.

## ADR-009 — Davranış: saf mantık + ince ROS katmanı, kamera opsiyonel katman
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Karar:** Durum makinesi ROS'tan bağımsız `logic.py` içinde, pytest ile test edilir. Çekirdek: CRUISE/AVOID/EMERGENCY (LiDAR + IMU). TRACK/INSPECT `use_camera` ile açılır.
- **Sonuç:** Mantık Windows'ta test edilebilir; sunumda karar kuralı net anlatılır.

## ADR-010 — Git akışı
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Karar:** `main` dalı; paylaşılan klasörde branch değiştirilmez. Commit mesajları `[modül] ...` önekli. Üye B kendi klonunda çalışır, kendi hesabından commit'ler (tercihen feature branch + PR). Commit/push kullanıcı onayıyla.
- **Sonuç:** Commit geçmişi kişisel katkıyı gösterir (ders şartı).

## ADR-011 — Linux ortamı: Üye B'nin sanal makinesi
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Üye A Windows'ta kalıyor; simülasyon testi ve canlı demo için Linux gerekli (ADR-002).
- **Karar:** Üye B sanal makineye Ubuntu 26.04 + ROS 2 Lyrical + Gazebo Jetty kurar. Simülasyon doğrulaması (Linux seviyesi) bu VM'de yapılır.
- **Sonuç:** VM'de 3D hızlandırma zayıf olabilir; `gpu_lidar` ve kamera render gerektirir. VM'de 3D hızlandırma açılmalı (VMware Workstation Player tercih; VirtualBox'ta sorun çıkarsa `LIBGL_ALWAYS_SOFTWARE=1` ile yazılımsal render denenir). Modeller düşük poligonlu tutulur (ADR-012). Simülasyon geri bildirimi Üye B'ye bağlı olduğu için doğrulama turları planlanmalı.

## ADR-012 — Görsel model Blender'da, çarpışma modeli primitif
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Ekip tasarımın kaliteli ve özgün görünmesini istiyor; robot modeli oturumu (S1) Blender'a bağlanarak (Blender MCP) çalışacak.
- **Karar:** Her link'in `visual` geometrisi Blender'da modellenen mesh; `collision` geometrisi kutu/silindir/küre primitifleri. Kurallar `INTERFACES.md` §4.1'de (birim, eksen, orijin, format, poligon bütçesi). Kaynak `.blend` dosyası repoda tutulur.
- **Sonuç:** Görünüm kaliteli, fizik kararlı ve hızlı kalır. Mesh formatının (DAE / glTF / OBJ) hem RViz2 hem Gazebo Jetty'de renkleriyle yüklendiği ⚠ doğrulanacak; doğrulanana kadar boyutlar primitif modelle birebir aynı tutulur, böylece mesh'ler sonradan yerine takılabilir. *Format kısmı ADR-015 ile güncellendi.*

## ADR-013 — Paket iskeleti kuralları
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Paralel çalışan modüllerin aynı manifest/kurulum dosyalarını düzenlemesi çakışma yaratır.
- **Karar:** S0 tüm paket manifestlerini (`package.xml`, `CMakeLists.txt`, `setup.py`) önceden yazar. Python entry point'leri önceden kayıtlıdır. Ana xacro'nun include ettiği her dosya, makro adı ve parametresi sabit bir `PLACEHOLDER` olarak oluşturulur (`INTERFACES.md` §8). Xacro include'ları göreli yoldur (Windows'ta ROS'suz kontrol için). `GZ_SIM_RESOURCE_PATH` ortam kancalarıyla ayarlanır. Python stil kontrolü `ament_flake8` (max 99 karakter). Lisans geçici olarak Apache-2.0 (kesin karar bekliyor).
- **Sonuç:** Modüller sadece kendi dosyalarına dokunarak ilerler. Yeni bağımlılık veya entry point gerekiyorsa açık istek yazılır.

## ADR-014 — GitHub Actions CI
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Karar:** Her push (main) ve PR'da `ros:lyrical` konteynerinde: `rosdep install` → `colcon build` → `xacro` + `check_urdf` → `colcon test`.
- **Sonuç:** Linux tarafındaki derleme/URDF hataları Üye B'nin VM'ine gerek kalmadan yakalanır. Simülasyon davranışı CI kapsamında değildir.

## ADR-015 — Mesh formatı: `.glb`, yedek `.obj` + `.mtl`
- **Tarih:** 2026-10-24 · **Durum:** Kabul (Linux doğrulaması bekliyor)
- **Bağlam:** S1, kullanılan Blender 5.2.3'te Collada (`.dae`) dışa aktarımının olmadığını tespit etti; mevcut seçenekler glTF/GLB, OBJ, FBX, STL, PLY, USD. STL renk taşımaz, FBX/USD'nin RViz2 desteği belirsiz.
- **Karar:** Görsel mesh'ler glTF Binary (`.glb`) olarak dışa aktarılır; renk ve malzeme tek dosyada gömülüdür. Gazebo Jetty glTF'yi destekler; RViz2 `.dae`/`.stl` dışındaki formatları assimp ile yükler. Yükleme veya yön sorunu çıkarsa yedek `.obj` + `.mtl`. Ayrıntılar `INTERFACES.md` §4.1.
- **Sonuç:** Gerçek mesh'lerden önce bir yön/renk test küpü Üye B'nin VM'inde iki formatta denenir; glTF'nin Y-up ekseninin doğru çevrildiği bu testle belirlenir. Test sonucu §4.1'e ve bu kayda yazılır.
- **Test sonucu (2026-10-24, Üye A VM, Docker — ADR-016):** RViz2'de `glb_yup` ve `obj` doğru, `glb_zup` 90° dönük; Gazebo Jetty 10.5.0'da `glb_zup` ve `obj` doğru, `glb_yup` dönük. Renkler hepsinde yükleniyor, Gazebo'da "dosya bulunamadı" hatası yok (`package://` + `GZ_SIM_RESOURCE_PATH` kancası doğrulandı). **Karar: yedek format `.obj` + `.mtl` birincil oldu**; `.glb` kullanılmaz.

## ADR-016 — Docker tabanlı Lyrical ortamı ve Üye A'nın test VM'i
- **Tarih:** 2026-10-24 · **Durum:** Kabul
- **Bağlam:** Üye A'nın VirtualBox VM'inde Ubuntu 20.04 (ROS 1 Noetic, Gazebo Classic) var; Lyrical/Jetty bu sürüme kurulamaz. Yeni bir 26.04 VM kurmak zaman alıyor ve host'ta (7.9 GB RAM) iki VM aynı anda çalışamıyor.
- **Karar:** Mevcut VM'de Docker ile `ros:lyrical` tabanlı geliştirme imajı (`docker/Dockerfile`, `docker/run.sh`). Claude VM'e SSH anahtarıyla (sadece localhost NAT yönlendirmesi) bağlanır; çalışma ağacı `scripts/sync_to_vm.sh` ile kopyalanır. `sudo` adımlarında şifreyi kullanıcı girer. Ayrıntılar `docs/DEV_ENVIRONMENT.md`.
- **Sonuç:** Simülasyon testleri Üye B'yi beklemeden Üye A'nın VM'inde yapılabilir (ADR-011'i tamamlar, yerine geçmez). Ortam CI ile aynı taban imajı kullanır. VM'de 3D hızlandırma kapalı olduğundan render yavaş olabilir. Üye B'ye doğrudan Ubuntu 26.04 önerilir; Docker yedek yol.

## ADR-017 — `base_link` tekerlek aksının ortasında
- **Tarih:** 2026-10-24 · **Durum:** Kabul (ADR'siz önceki "ofset kabul edildi" kararının yerine)
- **Bağlam:** Aks `base_link`'in 0.12 m gerisindeydi. gz DiffDrive odometriyi dönme merkezi (aks ortası) için hesaplayıp `base_footprint` adıyla yayınlıyor. VM testinde (ADR-016) yerinde dönüşte gövdenin ~0.12 m yarıçaplı yay çizdiği ve `/odom`'un gerçek konumdan ~0.14 m saptığı ölçüldü; RViz'de (`odom` sabit çerçevesi) LiDAR noktaları dönüşlerde kayar, hata birikir.
- **Karar:** `base_link` (ve `base_footprint`) aks ortasına taşınır. Robotun dış görünüşü ve ölçüleri değişmez; `base_link`'e göre montaj noktaları x'te +0.12 m kayar (`INTERFACES.md` §4, v0.6). IMU dönme merkezine (`x = 0`) yerleşir.
- **Sonuç:** `odom → base_footprint` fiziksel olarak doğru olur. S1 `properties.xacro`'yu günceller; şasi mesh'i kendi merkezinde kalabilir, ofset `visual` `origin` ile verilir (§4.1 istisnası). Sensör modülleri henüz başlamadığı için başka etkilenen yok.

## ADR-018 — Karma sera dünyası
- **Tarih:** 2026-10-26 · **Durum:** Kabul (ADR-008'in yerine)
- **Bağlam:** ADR-008 internet bağımlılığını önlemek için sadece primitif geometri öngörüyordu. Repoda tutulan Blender modelleri de çevrimdışı çalışır; ekip robot gibi çevrenin de özenli görünmesini istiyor.
- **Karar:** Çarpışma ve LiDAR'ın gördüğü yapı (duvarlar, bitki yatakları, saksılar) SDF primitifleri; görsel süsler (bitkiler, domatesler, sera iskeleti) Blender'da `.obj` + `.mtl` olarak `serabot_gazebo/models/` altında. Önce primitif dünya çalışır hale getirilir, süsler sonra. Dünya görselleri ≤ 150k üçgen. Kurallar `INTERFACES.md` §4.2.
- **Sonuç:** Sensör davranışı öngörülebilir kalır, kamera görüntüsü ve demo zenginleşir. VM'in yazılımsal render'ı nedeniyle bütçe aşılmamalı; S2 gerçek zaman oranını ölçüp raporlar.

## ADR-019 — Tekerlek çarpışması küre ve iki mesh renk seti
- **Tarih:** 2026-10-26 · **Durum:** Kabul (S1 isteği)
- **Bağlam:** S1, VM testlerinde silindir tekerlek çarpışmasının odometride yaw sapmasına yol açtığını ölçtü; ayrıca aynı `.mtl` renkleri RViz2 (sRGB) ve Gazebo (doğrusal) arasında farklı göründü.
- **Karar:** Tekerlek `collision` geometrisi küre r = 0.08 m (görsel değişmez); robotun çarpışma genişliği 0.52 m olur. Mesh'ler iki renk setiyle üretilir (`meshes/` RViz, `meshes/gazebo/` Gazebo); xacro argümanı `gazebo_mesh_colors` seçer, Gazebo'ya spawn edilen URDF `true` ile üretilir.
- **Sonuç:** S2 spawn'ı ayrı bir xacro çıktısından yapar (`INTERFACES.md` §6). S4 dar geçit/engel eşiklerinde 0.52 m genişliği hesaba katar.

## ADR-020 — Davranış parametreleri, `headless` argümanı, ortak klasörler
- **Tarih:** 2026-10-27 · **Durum:** Kabul (S3/S4 istekleri)
- **Karar:** (1) S4'ün eklediği davranış parametreleri ve `WAIT` durumu sözleşmeye girer (`INTERFACES.md` §2.5, §7); karar kuralının ayrıntısı `docs/modules/behavior.md`. (2) `bringup.launch.py`'ye `headless` argümanı (varsayılan `false`) eklenir; S2 uygular. VM'de Gazebo GUI'siz çalışmak RTF'yi ≈ 0.38'den ≈ 0.48'e çıkarır (S3 ölçümü); canlı demoda RViz tek görsel olabilir. (3) Ortak klasörler: `scripts/sim/` (test/ölçüm betikleri) ve `docs/report/<modül>/` (rapor görselleri); her oturum kendi dosyasını ekler. (4) Repo köküne ament_flake8 ayarlarını yansıtan `.flake8`.
- **Sonuç:** Test betikleri repoya girer, tekrar üretilebilir. Demo makinesi seçimi (VM mi, Üye B'nin makinesi mi) RTF'ye göre yapılmalı.
