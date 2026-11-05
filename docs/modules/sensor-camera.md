# Modül S3b — Kamera (Sensör B)

- **Sorumlu:** Üye B (Enes Çelik) · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Tamam (Linux'ta doğrulandı, 2026-11-04) — commit bekliyor (Üye B'nin hesabından)
- **Önemli:** Bu modül **Üye B'nin kendi GitHub hesabından** commit'lenir (ders şartı). Üye A'nın oturumları bu dosyaları yazmaz; sadece inceler ve öneri verir.
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/camera.xacro`, `src/serabot_bringup/config/bridge/camera.yaml`, `src/serabot_sensors/serabot_sensors/color_detector.py`, `color_detection.py` (saf işleme), `test/test_color_detection.py`; ortak (kamera + IMU, Üye B yazdı): `serabot_sensors/spin.py`, `test/conftest.py`; ölçüm: `scripts/sim/camera_check.py`, `camera_track_record.py`, `camera_track_plot.py`; rapor: `docs/report/sensors/camera_*`
- **Bağımlı olduğu:** S1 (`camera_mast_link`), S2 (sensors sistemi, dünyadaki kırmızı ürünler), `INTERFACES.md` §2.3, §2.5, §4
- **Ona bağımlı olanlar:** S4 (opsiyonel TRACK/INSPECT katmanı)

## Görevler

- [x] `camera.xacro` — `camera_link` + `camera_optical_link` (rpy = -π/2, 0, -π/2), `<gazebo reference="camera_link">` içinde `camera` sensörü (`INTERFACES.md` §2.3, `<gz_frame_id>camera_optical_link`)
- [x] `config/bridge/camera.yaml` — `/camera/image_raw`, `/camera/camera_info` GZ→ROS
- [x] Görselleştirme: RViz Image paneli (S0 config'inde hazır) ve `rqt_image_view /camera/image_annotated`
- [x] `color_detector.py` — HSV eşikleme ile kırmızı nesne tespiti → `/camera/target` (`PointStamped`, sözleşme `INTERFACES.md` §2.5) ve `/camera/image_annotated`. Eşikler ROS parametresi; saf işleme `color_detection.py`'de, 13 pytest testi.
- [x] Doğrulama komutları ve ekran görüntüleri: `scripts/sim/camera_check.py`, `docs/report/sensors/camera_corridor_{raw,annotated}.png`
- [ ] Rapor için: RViz kamera paneli ve `rqt_image_view` pencere ekran görüntüleri (demo sırasında elle alınacak)

## Tamamlanma kriteri

- `/camera/image_raw` ~15 Hz, `frame_id = camera_optical_link`; görüntüde bitki sıraları ve kırmızı ürünler görünüyor (Linux). ✅
- Kırmızı ürün görüş alanındayken `/camera/target` yayınlanıyor, `point.x` ürün solda iken negatif (Linux). ✅ (sağdaki salkım +0.91; işaret birim testinde de)

## Yapılanlar

**2026-11-04 — kamera sensörü (`camera.xacro`, `camera.yaml`)**

- Makro `serabot_camera(parent)` (§8 değişmedi). `camera_joint` fixed, `camera_mast_link` üstünde z = `camera_z` (= direk yüksekliği 0.30 m) → `base_link`'ten z = 0.36, zeminden **0.44 m**, pitch 0.
- `camera_link`: görsel `${mesh_dir}/camera.obj` (S1'in "çiçek tomurcuğu" mesh'i, mercek +x'te), yedek koyu kutu. Collision/inertial: mesh sınır kutusu 0.078 × 0.054 × 0.056 m (x merkezi +0.001), 0.05 kg.
- `camera_optical_link`: `camera_optical_joint` rpy (−π/2, 0, −π/2) → z ileri, x sağ, y aşağı (REP-103 optik). Geometrisi/kütlesi olmayan saf koordinat frame'i (bilinçli olarak `visual`/`inertial` yok).
- Sensör: `camera`, topic `camera/image_raw`, `camera_info_topic` `camera/camera_info`, `gz_frame_id camera_optical_link`, 15 Hz, 640×480 `R8G8B8`, yatay FOV 1.047 rad, clip 0.05–15 m (yakın düzlem mercekten 1 cm ileride → kamera kendi gövdesini görmez), gaussian gürültü σ = 0.007. Değerler dosyada `camera_*` property'leri.
- Görüş alanı kontrolü: dikey FOV ±23.4°; şasi ön kenarı −38.7°, LiDAR −45° → robotun kendi parçaları görüntüde yok (görüntüde doğrulandı).
- Bridge: `/camera/image_raw` (`gz.msgs.Image` → `sensor_msgs/msg/Image`), `/camera/camera_info` (`gz.msgs.CameraInfo` → `sensor_msgs/msg/CameraInfo`), ikisi de GZ→ROS (`bridge_camera`).

### Yerleşim gerekçesi (rapor için)

- **Direğin tepesinde, zeminden 0.44 m:** domatesler yatak kenarlarında z ≈ 0.45–0.53 m'de (§4.2). Kamera ürün yüksekliğinde ve düz (pitch 0) bakınca salkımlar görüntünün orta bandında, yatakların üstünde görünür; aşağı eğik kamera ise ürünleri yataklarla örtüşen bir açıdan görürdü.
- **Arkada (`base_link`'ten x = −0.03):** direk dönme merkezine yakın; yerinde dönüşte kamera neredeyse sadece döner, görüntü yana kaymaz. LiDAR'ın tarama düzlemi (0.18 m) ile çakışmaz (direk `range_min` içinde).
- **60° yatay FOV:** 1.25 m'lik koridorda iki yandaki yatakların kenarı ~1.1 m ileriden itibaren görüş alanına girer; yakın ve uzak salkımlar aynı karede.

**2026-11-04 — `color_detector` (`color_detection.py` + node)**

- **Saf işleme (`color_detection.py`, ROS'suz):** BGR → HSV; kırmızı iki ton bandının birleşimi (H ≤ `hue_low_max` veya H ≥ `hue_high_min`), S ≥ `saturation_min`, V ≥ `value_min`; `morph_kernel` (5 px) kapanış ile bir salkımın domatesleri tek blob olur; `connectedComponentsWithStats` ile **en büyük blob** hedef seçilir (genelde en yakın salkım); alanı `min_area_ratio`'dan küçükse hedef yok.
  - `offset = (cx − W/2) / (W/2)` ∈ [−1, 1], sol negatif; `area_ratio` = blob pikseli / görüntü pikseli.
  - `annotate()`: kırmızı pikseller pembe boyanır, hedef yeşil kutu + artı, orta çizgi, durum yazısı.
- **Eşikler ölçümle seçildi** (spawn karesi, `docs/report/sensors/camera_corridor_raw.png`):

  | Yüzey | H | S | V |
  |---|---|---|---|
  | Domates | 0 (en çok 12, anti-alias kenarı) | 245–255 (min 130) | 101–228 |
  | Yatak (ahşap) | 13–15 | ≈ 140 | ≈ 87 |
  | Yapraklar | 45–56 | — | — |

  Varsayılanlar: `hue_low_max` 8, `hue_high_min` 170, `saturation_min` 120, `value_min` 60, `morph_kernel` 5, `min_area_ratio` 0.0005. Bu karede tüm domates pikselleri yakalanıyor, yataklardan 0 piksel.
- **Node (`color_detector.py`):** abone `/camera/image_raw`; yayın `/camera/target` (sadece hedef varken; header = görüntü header'ı, yani `camera_optical_link` + görüntü zaman damgası; `point.z` = 0) ve `/camera/image_annotated` (sadece abonesi varsa çizilir). Parametreler `ColorParams` alanlarından otomatik tanımlanır. Hedef görülme/kaybolma INFO log'una yazılır.
- **QoS istisnası (bilinçli):** kamera aboneliği `qos_profile_sensor_data` değil, **reliable, KEEP_LAST 1**. Neden: 640×480 RGB kare ≈ 0.9 MB, Fast DDS paylaşımlı bellek segmentinden büyük → UDP parçalarıyla gidiyor, best-effort okuyucu bir parça kaybolunca tüm kareyi kaybediyor. Ölçüm (aynı anda, işlem yapmayan abonelerle, sim zamanı): best-effort **1.75 Hz, en büyük boşluk 2.44 s**; reliable depth 1 **15.15 Hz, en büyük boşluk 0.067 s**. Bridge reliable yayınladığı için uyumlu; depth 1 → node geride kalırsa eski kare kuyruğa girmez, hep en yeni kare işlenir. (Açık istek 1.)
- **`spin.py` (kamera + IMU node'ları):** `use_sim_time` ile her node `/clock`'u (~1 kHz) dinliyor; varsayılan rclpy executor'ı bunu Python'da işlediği için **boşta bekleyen bir node bile ≈ %53–60 CPU** harcıyor. `EventsExecutor` (rclpy deneysel, C++) aynı node'u **≈ %28**'e indiriyor, sim zamanlayıcıları aynı çalışıyor. Yoksa `SingleThreadedExecutor`'a düşer. (S4 için öneri: Açık istek 4.)
- **Testler (`test/test_color_detection.py`, 13 test):** kırmızı yok / kahverengi yatak / yeşil yaprak → hedef yok; sol → offset < 0, sağ → > 0, orta → 0; alan oranı ve kutu; en büyük blob seçimi; ton sarması (H 175); koyu/soluk kırmızı reddi; küçük blob eşiği; kapanışın salkımı birleştirmesi; `annotate` girdiyi değiştirmiyor.

## Doğrulama

Ortam: Üye B dizüstü, **WSL2 Ubuntu 26.04 + ROS 2 Lyrical + Gazebo Jetty 10.5.0 (doğrudan apt kurulumu)**, RTX 3050 (WSLg d3d12). Docker/VM kullanılmadı.

**Statik:**
- Windows: `python -m pytest src/serabot_sensors/test` → 24 geçti, 1 atlandı (ament_flake8 yok); `flake8 src/serabot_sensors scripts/sim/camera_check.py` temiz.
- Linux: `colcon build` ✅, `colcon test --packages-select serabot_sensors` → **25 test, 0 hata** (ament_flake8 dahil); `check_urdf`: `camera_mast_link → camera_link → camera_optical_link` ✅; `gz sdf -p`: kamera sensörü, `camera_info_topic` SDF'e geçiyor ✅.

**Çalışma zamanı (`ros2 launch serabot_bringup bringup.launch.py`, varsayılan spawn, robot duruyor):**
- `bridge_camera` iki köprüyü kuruyor; `/camera/image_raw`, `/camera/camera_info` ROS ve Gazebo tarafında ✅
- `/camera/image_raw`: **15.15 Hz (sim)**, en büyük boşluk 0.067 s, `frame_id camera_optical_link`, 640×480 `rgb8` ✅
- `/camera/camera_info`: `frame_id camera_optical_link`, 640×480, fx = fy = **554.4** (= 320 / tan 30°), cx 320, cy 240 ✅ → Gazebo `camera_info` topic adını `camera_info_topic` ile verdik; ⚠ maddesi kapandı.
- TF `base_link → camera_optical_link`: (−0.030, 0, 0.360), RPY (−90°, 0, −90°) ✅
- Görüntü: koridor, iki yanda yataklar, kamera yüksekliğinde kırmızı domatesler, ileride saksı (−0.5, 1.30) — `docs/report/sensors/camera_corridor_raw.png` ✅
- `color_detector` (launch `sensors:=true` ile otomatik): `/camera/target` **15.15 Hz (sim), her kare**, en büyük boşluk 0.067 s (davranışın `target_timeout` 0.5 s'sinin çok altında); spawn'da hedef sağdaki en yakın salkım: offset **+0.908**, alan **0.0060** ✅ — `camera_corridor_annotated.png` (yataklarda/saksıda yanlış tespit yok)
- Görüntü işleme maliyeti (spawn karesi): `imgmsg_to_cv2` 2.1 ms + `detect_red` 5.0 ms (+ `annotate` 4.6 ms, sadece abone varsa).
- Gerçek zaman oranı: kamera ile GUI + RViz ≈ **0.40–0.66** (kamerasız ≈ 0.85; kamera render'ı). Üye A VM'inde ölçülmedi.
- Simülasyon 15 dakikadan uzun çökmeden çalıştı (2026-11-04). Önceki iki Gazebo `Segmentation fault` (2026-11-02) muhtemelen GUI penceresi kapatılırken; tekrar görülürse not edilecek.

**Kamera katmanı ile davranış (TRACK / INSPECT), 2026-11-04** — S4'ün `behavior_node`'u, dosyalarına dokunmadan sadece çalışma anında `-p use_camera:=true` ile; diğer parametreler `behavior.yaml` varsayılanı. Varsayılan spawn (−4.0, 0.875, 0), `greenhouse.sdf`, GUI + RViz.

- **run2 (120 s sim):** **5 inceleme** (CRUISE → TRACK → INSPECT → AVOID → CRUISE), 0 EMERGENCY; adım sayısı (10 Hz) CRUISE 646, AVOID 185, TRACK 187, INSPECT 150. run1 (90 s, ayrı launch) geçiş zamanları ve pozları run2'nin ilk 90 s'siyle neredeyse aynı (±0.1 s, ±2 cm) → tekrarlanabilir.
- İlk döngü: spawn'da sağdaki salkım (offset **+0.91**, alan 0.0060) → `CRUISE -> TRACK: target seen` → robot sağa dönerek 0.12 m/s ilerliyor, offset **+0.05**'e iniyor (hedef görüntünün ortasında) → `TRACK -> INSPECT: bed reached, front 0.54 m` → 3 s dur → `INSPECT -> AVOID: inspection done` → 62° dönüş (IMU) → CRUISE.
- INSPECT'i her seferinde "yatağa varıldı" (`front_min < obstacle_distance`) tetikledi; alan en çok **%1.5** oldu (eşik `inspect_area` %8 → S4'ün açık sorunu doğrulandı).
- Bu koşunun haritası: `camera_track_map_before.png` (odometri tabanlı).
- **Gözlem:** kamera açıkken robot batı dönüş alanından (x −4.4…−3.4) çıkmıyor: yatak uçlarındaki salkımlar hep görüş alanında, `target_cooldown` (8 s) bitince yeni bir hedefe yöneliyor; koridorlara girmiyor (Açık istek 6) → **2026-11-05'te düzeltildi (ADR-021)**, aşağıda.

**Düzeltme sonrası (2026-11-05, ADR-021: `resume_patrol` + `target_cooldown` 20):** ayar karşılaştırma tablosu `docs/modules/behavior.md` "Doğrulama"da (9/60 → 21/60 hücre). Rapor görselleri bu koşudan (`exp_resume_cd20`, 180 s, spawn'dan, Gazebo gerçek pozu): `camera_track_map.png` (iki koridor boydan boya, 7 inceleme, en küçük gövde açıklığı **0.128 m**, EMERGENCY yok), `camera_track_track_1.png`, `camera_track_inspect_{1,2}.png`, veriler `camera_track_states.csv`, `camera_track_path.csv` (`gt_*` sütunları gerçek poz).

**Uçtan uca demo testi (2026-11-05):** gerçek demo komutu `ros2 launch serabot_bringup bringup.launch.py behavior:=true use_camera:=true` (Gazebo GUI + RViz):
- Node'lar: `bridge_{base,camera,imu,lidar}`, `robot_state_publisher`, `color_detector`, `imu_monitor`, `behavior_node`, `rviz` ✅. Parametreler: `use_camera=True`, `target_cooldown=20.0`, `resume_patrol=True`, `use_sim_time=True`, `color_detector` `hue_low_max=8` (yaml'dan) ✅.
- RViz `/camera/image_raw` ve `/camera/image_annotated` abonelikleri **RELIABLE** ✅ (`ros2 topic info -v`).
- 180 s (gerçek poz kaydı launch'tan ~20 s sonra başladı): 20/60 hücre, 7 inceleme, en küçük açıklık **0.123 m**, EMERGENCY 0 ✅; RTF ≈ 0.71.
- Ctrl+C (SIGINT): `color_detector`, `imu_monitor`, `behavior_node`, `robot_state_publisher` temiz kapanıyor ✅. **Bilinen sorun:** Gazebo (gz-sim 10.5.0) **kapanırken** `Segmentation fault` veriyor (GUI'li ve `headless`'ta, her seferinde); RViz ve iki bridge de onunla birlikte "died" görünüyor. Çalışma sırasında hiç görülmedi (180 s'lik koşular, 15+ dk açık kalan oturum) → demo etkilenmez; 2026-11-02'deki iki çökme de büyük olasılıkla kapanıştı.
- Tekrarlamak: `scripts/sim/camera_track_record.py` başındaki komutlar; grafik `python3 scripts/sim/camera_track_plot.py OUT_DIR OUT_DIR/map.png`.

**Tekrarlamak için:**
```bash
ros2 launch serabot_bringup bringup.launch.py
python3 scripts/sim/camera_check.py --seconds 10 --out-dir /tmp   # hızlar, frame'ler, PNG'ler
ros2 run rqt_image_view rqt_image_view /camera/image_annotated     # tespit kutulu görüntü
ros2 topic echo /camera/target                                     # point.x = offset, point.y = alan
```

## Açık istekler (S0'a)

> 2026-11-05: 1, 2, 3, 6 ve 5'in bir kısmı ekip içinde anlaşılarak **Üye B tarafından uygulandı** (ADR-021, INTERFACES v0.10). 4 (S4 executor) açık, isteğe bağlı.

1. ✅ **QoS istisnası (INTERFACES §1):** "Sensör abonelikleri `qos_profile_sensor_data`" kuralına istisna: büyük görüntüler (`/camera/image_raw`, `/camera/image_annotated`) **reliable** okunmalı (ölçüm yukarıda). Buna bağlı olarak `serabot_bringup/rviz/serabot.rviz` içindeki `Camera` (Image) panelinin `Reliability Policy`'si `Best Effort` → **`Reliable`** olmalı; aksi halde RViz'deki kamera görüntüsü takılarak (≈ 2 Hz) gelir. İsteğe bağlı: aynı config'e `/camera/image_annotated` için ikinci bir Image paneli.
2. ✅ **`color_detector` parametre dosyası (CLAUDE.md §5):** eşiklerin varsayılanları şu an `ColorParams` dataclass'ında (node bunlardan parametre tanımlıyor; launch sadece `use_sim_time` veriyor). Kurala tam uyum için `serabot_bringup/config/color_detector.yaml` (değerler yukarıdaki tabloda) ve `bringup.launch.py` `_helper_nodes`'un bunu `color_detector`'a vermesi (S2). Davranışı değiştirmez.
3. ✅ **DEV_ENVIRONMENT.md'ye yeni ortam:** WSL2 + Ubuntu 26.04 + doğrudan apt (Docker'sız). Gerekli değişkenler: `GALLIUM_DRIVER=d3d12`, `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA` (yoksa `llvmpipe`), `QT_QPA_PLATFORM=xcb` (yoksa RViz "Invalid parentWindowHandle" ile çöküyor). Gazebo donmuş görünürse `/stats` `paused: true` olabilir (GUI'den ▶).
4. **S4'e öneri (`/clock` CPU yükü):** `behavior_node` de Python + `use_sim_time`; aynı ≈ %55 CPU'luk `/clock` yükü onda da var. `serabot_sensors/spin.py`'deki `EventsExecutor` yaklaşımı ( `spin_once` döngüsü yerine) değerlendirilebilir.
5. **PROGRESS / REQUIREMENTS:** R7–R9 kamera ✅ (Linux'ta doğrulandı), açık konu #3'ün camera_info kısmı kapandı. S4 tamamlanma kriteri "`use_camera:=true` ile kırmızı ürüne yönelip duruyor" ✅ (yukarıdaki run1/run2).
6. ✅ (`resume_patrol` + `target_cooldown` 20 + `use_camera` launch argümanı, ADR-021) **S4'e (davranış, karar onların):** kamera katmanı çalışıyor ama robotu dönüş alanında tutuyor (yukarıdaki gözlem). Seçenekler: `target_cooldown`'u uzatmak (örn. 20–30 s), INSPECT sonrası AVOID yerine düz CRUISE'a dönmek, ya da demo için iki mod göstermek (`use_camera:=false` devriye, `true` denetim). Ayrıca `behavior:=true` launch'ında `use_camera`'yı açacak bir yol (launch argümanı veya `behavior.yaml`) demo için gerekli; şu an sadece `ros2 run ... -p use_camera:=true` ile açılabiliyor.

## Açık sorunlar

- `inspect_area` (S4) 0.08: TRACK testinde alan en çok **%1.5** → alan eşiği pratikte tetiklenmiyor, INSPECT'i "yatağa varmak" tetikliyor (çalışıyor; eşik S4'ün kararı).
- En büyük blob seçimi: iki yanda da salkım varken hedef sağ/sol arasında atlayabilir. TRACK testinde titreme görülmedi (TRACK süreleri 1.6–5 s, offset düzgün 0'a iniyor); görülürse "önceki hedefe en yakın blob" eklenebilir.
