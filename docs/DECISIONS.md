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
- **Tarih:** 2026-10-24 · **Durum:** Kabul
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
- **Sonuç:** Görünüm kaliteli, fizik kararlı ve hızlı kalır. Mesh formatının (DAE / glTF / OBJ) hem RViz2 hem Gazebo Jetty'de renkleriyle yüklendiği ⚠ doğrulanacak; doğrulanana kadar boyutlar primitif modelle birebir aynı tutulur, böylece mesh'ler sonradan yerine takılabilir.
