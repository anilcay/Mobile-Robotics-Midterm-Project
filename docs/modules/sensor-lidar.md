# Modül S3a — LiDAR (Sensör A)

- **Sorumlu:** Üye A (anilcay) · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Uygulandı, VM'de (Docker, Lyrical + Jetty 10.5.0) doğrulandı — commit bekliyor
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/lidar.xacro`, `src/serabot_bringup/config/bridge/lidar.yaml`, `serabot_sensors` içindeki lidar dosyaları (gerekirse)
- **Bağımlı olduğu:** S1 (`base_link`), S2 (sensors sistemi), `INTERFACES.md` §2.2, §4
- **Ona bağımlı olanlar:** S4 (davranışın birincil girdisi)

## Görevler

- [x] `lidar.xacro` — `lidar_link` (S1'in `lidar.obj` görseli + silindir collision + inertial), `lidar_joint`, `<gazebo reference="lidar_link">` içinde `gpu_lidar` sensörü (`INTERFACES.md` §2.2 değerleri, `<gz_frame_id>lidar_link`)
- [x] `config/bridge/lidar.yaml` — `/scan` GZ→ROS
- [x] RViz LaserScan görselleştirmesi — `serabot.rviz`'de zaten var (S0: `/scan`, Best Effort, Flat Squares 0.04 m, kırmızı, Fixed frame `odom`); istek gerekmedi
- [x] Doğrulama: hız, frame, mesafe karşılaştırması, öz-görme kontrolü, RViz ekran görüntüsü
- [ ] Rapor ekran görüntülerini `docs/report/` altına taşıma (S0 onayı bekliyor — "Açık istekler")

## Tamamlanma kriteri

- `/scan` ~10 Hz yayınlanıyor, `frame_id = lidar_link` (Linux). ✅
- RViz'de tarama noktaları duvar ve saksılarla örtüşüyor; robotun kendi gövdesi/direği taramada görünmüyor (Linux). ✅

## Yapılanlar

**2026-10-26 — `lidar.xacro` + `lidar.yaml`**

- Makro `serabot_lidar(parent)` (§8 sözleşmesi değişmedi). `lidar_joint` fixed, `${lidar_x} ${lidar_y} ${lidar_z}` = (0.22, 0, 0.10) — değerler `../properties.xacro`'dan.
- Görsel: `${mesh_dir}/lidar.obj` (renk setini `gazebo_mesh_colors` seçer); `use_mesh_visuals=false` iken koyu silindir yedek.
- Collision: mesh sınır silindiri r 0.042 m, h 0.06 m, merkez z −0.02 (mesh z −0.05…+0.01). Kütle 0.15 kg, `inertial_cylinder`. Sabitler dosya içinde `lidar_*` property'leri (sözleşme dışı: kütle, gövde ölçüleri).
- Sensör: `gpu_lidar`, topic `scan`, `gz_frame_id lidar_link`, 10 Hz, 360 örnek, −π…π, 0.25–8.0 m, çözünürlük 0.01 m, gaussian σ 0.01, `visualize` kapalı.
- Bridge: `/scan` `sensor_msgs/msg/LaserScan` ← `gz.msgs.LaserScan`. `bringup.launch.py` her dolu bridge yaml'ı için ayrı `parameter_bridge` başlatıyor (`bridge_lidar`); launch'ta değişiklik gerekmedi.

### Yerleşim gerekçesi (rapor için)

- **Önde, şasi üstünde, ortada (x = +0.22, z = +0.10 → zeminden 0.18 m):** tarama düzlemi şasi üst yüzeyinin (0.14 m) ve tekerleklerin (0.16 m) üstünde, böylece gövde ışınları kesmez. Duvarlar (1.0 m), bitki yatakları (0.40 m) ve saksılar (0.35 m) bu yükseklikte görülür — sera engellerinin hepsi tek 2D düzlemde yakalanır.
- **Önde olması:** ileri yöndeki engellere en kısa mesafe ve en geniş görüş; davranışın ±30° ön sektörü robotun önünden ölçülür.
- **`range_min` 0.25 m:** LiDAR "çakıl" mesh'i (r 0.042) ve kamera direği (0.235 m) bu yarıçapın içinde kalır → robot kendini görmez (§2.2).

## Doğrulama

Ortam: Üye A VM'i, Docker `serabot-dev:lyrical`, Gazebo Jetty 10.5.0, llvmpipe. `scripts/sync_to_vm.sh` + `colcon build` ✅.

**Statik (Windows + VM):**
- Xacro → URDF dört varyantta ✅: varsayılan (`meshes/lidar.obj`), `gazebo_mesh_colors:=true` (`meshes/gazebo/lidar.obj`), `use_lidar:=false` (lidar_link yok), `use_imu:=false`.
- VM: `check_urdf` ✅ (`lidar_link` `base_link` çocuğu). `gz sdf -p`: sabit joint birleştirmesiyle sensör `base_footprint` linkine taşınıyor, pozu `0.22 0 0.18` ✅ (zeminden 0.18 m). sdformat uyarısı "`gz_frame_id` … not defined in SDF. Copying" — zararsız, frame_id aşağıda doğrulandı.

**Çalışma zamanı (`ros2 launch serabot_bringup bringup.launch.py`, robot spawn noktasında (−4.0, 0.875), +x'e bakıyor):**
- Log: `bridge_lidar: Creating GZ->ROS Bridge: [/scan (gz.msgs.LaserScan) -> /scan (sensor_msgs/msg/LaserScan)]` ✅
- `ros2 topic info /scan` → `sensor_msgs/msg/LaserScan`, 1 yayıncı ✅
- **Hız:** mesaj zaman damgalarından (simülasyon zamanı) **10.00 Hz** (30 s, 99 mesaj) ✅. `ros2 topic hz /scan` duvar saatiyle 3.8 Hz gösteriyor = 10 Hz × RTF (≈0.37); sensör hızı doğru, simülasyon gerçek zamandan yavaş.
- **Mesaj alanları:** `frame_id='lidar_link'`, `angle_min=-3.1416`, `angle_max=3.1416`, `angle_increment=0.01750` (2π/359), 360 ışın, `range_min=0.25`, `range_max=8.0` ✅
- **Mesafeler — §4.2 yerleşiminin 2D ışın izlemesiyle karşılaştırma** (30 tarama ortalaması; LiDAR dünyada (−3.78, 0.875)):

| Yön | Hedef | Beklenen [m] | Ölçülen [m] |
|---|---|---|---|
| 0° | Koridor boyunca doğu duvarı (8.78 m) | > 8 → `inf` | `inf` ✅ |
| +45° | Kuzey yatağın batı ucu (x = −3) | 1.103 | 1.099 ✅ |
| −45° | Orta yatağın batı ucu | 1.103 | 1.100 ✅ |
| +90° | Kuzey duvar (y = 3) | 2.125 | 2.124 ✅ |
| −90° | Güney duvar (y = −3) | 3.875 | 3.876 ✅ |
| ±135° | Batı duvar (x = −5) | 1.725 | 1.732 / 1.733 ✅ |
| +7.4° | Saksı (−0.5, 1.30) | 3.158 | 3.161 ✅ |
| −15.5° | Saksı (1.0, −0.45) | 2.332 | 2.371 ✅ (< 5 cm) |
| −44.9° | Saksı (−1.6, −1.30) | 1.096 | 1.100 ✅ |
| −14.6° | Saksı (4.2, −1.20) | 2.489 | 2.502 ✅ |
| −98.9° | Saksı (−4.2, −1.80) | 2.558 | 2.563 ✅ |

  342 karşılaştırılabilir ışında ortalama hata **−1.0 mm**. 5 cm'den büyük sapma 12 ışında, hepsi yatak kenarlarına sığ açıyla (±10–17°) değen ışınlar — 1° ışın aralığında yüzey neredeyse ışına paralel; ölçüm hatası değil geometrik. +4.5°'de beklenmeyen 3.26 m dönüşü: (−0.5, 1.30) saksısının kenarı (ışın izlemesi ince ışın varsayıyor).
- **Öz-görme:** tüm taramalarda en küçük sonlu okuma **0.977 m** (yatak köşesi, beklenen 0.9995 − gürültü); 0.30 m altında **0 okuma** ✅. Şasi, tekerlek, direk ve LiDAR mesh'i taramada görünmüyor; S1'in "çakıl mesh'i ~0.03–0.05 m okuma verir mi" uyarısı geçersiz (ışın `range_min`'den başlıyor).
- **Arka kör sektör:** kamera direği LiDAR'ın tam arkasında 0.235 m'de → 177°…−177° arası **8 ışın** sürekli dönüşsüz (`inf`). Kısa okuma değil, sadece ±3.5°'lik gölge. Davranış ön ±30° sektörünü kullandığı için etkisi yok; S4'e not ("Açık sorunlar").
- **RViz:** LaserScan noktaları duvar, yatak uçları ve saksılarla örtüşüyor ✅ (ekran görüntüsü: robot dönüş testinden sonra ~270° dönmüş halde). Dosya: oturum geçici klasöründe `shots/rviz_laserscan.png` — `docs/report/` önerisi "Açık istekler"de.
- **Gerçek zaman oranı** (sensörlerle; `/clock` Δsim/Δwall, 2 × 30 s; S2 yöntemi):

| Koşul | RTF |
|---|---|
| Gazebo GUI + RViz (`bringup.launch.py`) | 0.367 / 0.389 (S2 sensörsüz ≈ 0.39) |
| GUI'siz sunucu + RViz | 0.463 / 0.484 |
| GUI'siz sunucu, RViz yok, **sensörsüz** | 0.832 / 0.802 |
| GUI'siz sunucu, RViz yok, **LiDAR + IMU** | 0.895 / 0.901 |

  → Sensörlerin RTF'ye ölçülebilir etkisi yok (fark çalıştırmalar arası oynama içinde). Darboğaz yazılımsal render'lı iki GUI (Gazebo GUI ~%100 CPU, RViz ~%90). GUI'siz ölçüm `bringup.launch.py` yerine elle yapıldı (`gz sim -s -r`, `ros_gz_sim create`, üç bridge); `bringup.launch.py`'de headless argümanı yok, Gazebo GUI'yi kapatmak `on_exit_shutdown` ile tüm launch'ı kapatıyor.

**Tekrarlamak için komutlar (VM'i olmayanlar için):**
```bash
ros2 launch serabot_bringup bringup.launch.py
ros2 topic info /scan                 # sensor_msgs/msg/LaserScan, 1 publisher
ros2 topic echo /scan --once --field header   # frame_id: lidar_link
ros2 topic hz /scan                   # duvar saatiyle ~10 × RTF; RTF 1'e yakınsa ~10 Hz
```
Beklenen: spawn noktasında 90° ışını ≈ 2.12 m, −90° ≈ 3.88 m, 0° `inf`, 0.30 m altında okuma yok.

## Açık istekler (S0'a)

- **Rapor klasörü:** ekran görüntüleri ve ölçüm çıktıları için `docs/report/sensors/` (veya S0'ın seçtiği yer) — klasör `docs/` altında olduğu için S0 oluşturur/onaylar; onaylanırsa `rviz_laserscan.png` buraya konur.
- **(S2'ye, isteğe bağlı) `headless` launch argümanı:** Gazebo'yu `-s` ile başlatma seçeneği. Ölçüm: GUI + RViz RTF ≈ 0.38, GUI'siz ≈ 0.48 (RViz açık), ≈ 0.90 (ikisi de kapalı). Canlı demoda RViz tek görsel olarak yeterliyse Gazebo GUI'yi kapatmak RTF'yi ≈ 0.38'den ≈ 0.48'e çıkarır.
- **(Araç önerisi) ölçüm betikleri:** bu oturumda kullanılan `sensor_probe.py` (hız/frame/ışın istatistiği), `rtf.py` (30 s RTF), `imu_turn.py` (yerinde dönüş testi) ve ışın izleme karşılaştırması `scripts/` altına konabilir (S0 sahibi). İstenirse içerik hazır.

## Açık sorunlar

- **Arka kör sektör (bilgi, S4'e):** 177°…−177° (8 ışın) her zaman `inf` — kamera direğinin gölgesi. Arka yöne bakan bir mantık yazılırsa bu ışınlar yok sayılmalı.
- Sığ açılı yatak kenarlarındaki birkaç cm'lik sapmalar geometrik; düzeltme gerekmiyor.
