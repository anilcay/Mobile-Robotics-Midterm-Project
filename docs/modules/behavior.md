# Modül S4 — Davranış (`serabot_behavior`)

- **Sorumlu:** Üye A · **Faz:** F3 (1–3 Kas), saf mantık ve testleri F1'den itibaren yazılabilir · **Durum:** Devam ediyor — çekirdek (CRUISE/AVOID/EMERGENCY) VM'de Gazebo'da 3 dk çarpışmasız (run3); kamera katmanı Gazebo'da denenmedi
- **Sahip olunan yollar:** `src/serabot_behavior/`, `src/serabot_bringup/config/behavior.yaml`
- **Bağımlı olduğu:** `/scan` (S3a), `/imu` (S3c), `/camera/target` (S3b, opsiyonel), `INTERFACES.md` §2, §7
- **Ona bağımlı olanlar:** Demo, rapor (karar kuralı açıklaması)

## Tasarım

Durum makinesi taslağı: `ARCHITECTURE.md` §6. Kesinleşen karar kuralı aşağıda (`serabot_behavior/logic.py`).

### Geometri

- LiDAR noktaları `base_link`'e taşınır: `x = 0.22 + r·cosθ`, `y = r·sinθ`. Gövde kutusu içine düşen noktalar (x −0.105…+0.345, |y| ≤ 0.26) kendi gövdesi sayılıp atılır.
- **Yerinde dönüş yarıçapı** = gövdenin `base_link`'e en uzak noktası = ön köşe (0.345, ±0.15) → **0.376 m** (parametrelerden türetilir).
- `front_min` (LiDAR mesafesi): ±`front_sector_deg` sektörü **veya** gövde koridoru (|y| ≤ 0.26 + 0.05, gövde önünün ilerisi) içindeki en yakın nokta. Koridor kontrolü, sektörün kaçırdığı yakın yan engelleri (örn. 50°, 0.4 m) yakalar.
- `rotate_clear_left/right`: o yöne dönerken ön köşelerin süpürdüğü yay (−23.5° … +113.5°, `rotate_sweep_deg` = 90) içindeki noktalar için `mesafe − 0.376`, diğer yönlerde `mesafe − 0.26`. `rotate_margin` (0.02) altındaysa o yöne dönülmez.
- `left_mean/right_mean`: (30°, 100°] yan sektörlerin ortalaması (dönüş yönü seçimi). `rear_gap`: şasi arkası ile arkadaki en yakın nokta arası.
- Temizlik: `nan`, `-inf`, `< range_min` atılır; `+inf` ve `> range_max` → `range_max`.

### Karar kuralı

| Durum | Komut (`linear`, `angular`) | Geçiş |
|---|---|---|
| WAIT | 0, 0 | `/scan` yok veya `scan_timeout` (0.5 s) eski → her durumdan WAIT; tarama gelince → CRUISE |
| CRUISE | `forward_speed`, `centering_gain·(sol_min − sağ_min)` (0.5, ±0.3 rad/s; yan mesafeler 1.0 m'de kırpılır) | `front_min < emergency_distance` → EMERGENCY; `front_min < obstacle_distance` → AVOID; `use_camera` ve taze hedef → TRACK |
| AVOID | 0, ±`turn_speed` | Girişte: dönüş için yeri olan taraflardan ortalaması büyük olan seçilir ve kilitlenir; iki tarafta da yer yoksa → EMERGENCY. Dönülen açı ≥ `turn_angle_deg` **ve** `front_min > clear_distance` → CRUISE; dönerken yer kalmazsa → EMERGENCY |
| EMERGENCY | −`backup_speed` (arka `rear_gap > rear_clear_distance` ise, değilse 0), 0 | `backup_duration` doldu → AVOID |
| TRACK | `track_speed`, `−track_gain·offset` (±`turn_speed` ile sınırlı) | `front_min < emergency_distance` → EMERGENCY; hedef kayboldu (> 0.5 s) → CRUISE; alan ≥ `inspect_area` **veya** `front_min < obstacle_distance` (yatağa varıldı) → INSPECT |
| INSPECT | 0, 0 | `inspect_duration` doldu → AVOID; `target_cooldown` süresince hedefler yok sayılır |

- **Dönüş açısı:** IMU `ω_z` mesaj damgalarıyla integre edilir. IMU `imu_timeout` (0.3 s) içinde gelmediyse o adımda `turn_speed · dt` yedeği kullanılır (`turn_source` = `imu` / `time`).
- **AVOID'de acil durum yok:** `emergency_distance` 0.3 m (LiDAR) ≈ `base_link`'ten 0.52 m > 0.376 m; yerinde dönüş güvenli olduğu sürece geri çekilmeye gerek yok. Bu, EMERGENCY ↔ AVOID döngüsünü önler.
- **ARCHITECTURE §6'dan farklar:** WAIT eklendi; TRACK'te engel → AVOID yerine INSPECT (hedef yatağın üstünde, yatağa varmak = hedefe varmak); EMERGENCY girişi dönüş yeri olmamasını da kapsar.
### Node (`behavior_node.py`)

- Abonelik: `/scan`, `/imu`, `/camera/target` (sadece `use_camera: true` ise) — hepsi `qos_profile_sensor_data`. Yayın: `/cmd_vel` (`Twist`), `/behavior/state` (`String`, her adımda).
- `/scan` geldiğinde özetlenir (`analyze_scan`); `control_rate` (10 Hz) zamanlayıcısı node saatiyle (sim zamanı) `update()` çağırır. Mesaj damgası 0 ise node zamanı kullanılır.
- Durum değişince gerekçe INFO log'una yazılır, örn. `CRUISE -> AVOID: front 0.52 m < 0.55 m; turning left`.
- Parametreler `BehaviorParams` alanlarından otomatik tanımlanır (+ `control_rate`); `behavior.yaml` ile birebir aynı (Windows'ta betikle karşılaştırıldı). Çalışırken parametre değişikliği desteklenmez (node yeniden başlatılır).
- Kapanış: rclpy'nin sinyal işleyicisi kapalı; SIGINT ve SIGTERM `KeyboardInterrupt`'a çevrilir, 3 kez sıfır `Twist` yayınlanır, sonra kapanır. Döngü `spin_once(timeout_sec=0.1)`: `/clock` yokken de (sim-time zamanlayıcıları durur) sinyal işlenir. SIGKILL'de sıfır hız gönderilemez.

- Tüm zamanlar sim zamanı (gerçek zaman oranından bağımsız). Her durum değişiminde `Command.reason` gerekçe metni taşır (log için).

- **Girdi:** `/scan` (`sensor_msgs/msg/LaserScan`), `/imu` (`sensor_msgs/msg/Imu`), `/camera/target` (`geometry_msgs/msg/PointStamped`, opsiyonel)
- **Çıktı:** `/cmd_vel` (`geometry_msgs/msg/Twist`), `/behavior/state` (`std_msgs/msg/String`)
- **Parametreler:** `INTERFACES.md` §7

## Görevler

- [x] `serabot_behavior/logic.py` — ROS'suz saf mantık: tarama sektör analizi (ön/sol/sağ min ve ortalama, `inf`/`nan` temizliği), IMU yaw-rate integrasyonu, durum geçişleri, `(linear, angular)` çıktısı
- [x] `test/test_logic.py` — pytest: engel yok → CRUISE; önde engel → AVOID ve açık tarafa dönüş; dönüş açısı tamamlanınca → CRUISE; acil mesafe → EMERGENCY; hedef ofset işareti → dönüş yönü
- [x] `serabot_behavior/behavior_node.py` — abonelikler (`qos_profile_sensor_data`), parametreler, 10 Hz zamanlayıcı, `/cmd_vel` + `/behavior/state` yayını; kapanırken sıfır hız yayınla
- [x] `config/behavior.yaml` varsayılanları
- [x] Gazebo'da parametre ayarı (eşikler, hızlar) ve sonuçların kaydı (çekirdek; kamera katmanı hariç)
- [x] Sunum/rapor için: durum diyagramı, karar kuralı, topic/mesaj tipi tablosu — [docs/report/behavior/](../report/behavior/README.md): `behavior_design.md` (tablolar + Mermaid diyagram + demo komutları), `state_diagram.png`, run3 yörünge grafiği, Gazebo ekran görüntüsü, geçiş logu, durum CSV'si

## Tamamlanma kriteri

- `python -m pytest src/serabot_behavior/test` geçiyor (Windows).
- Gazebo'da robot 3 dakika boyunca sera koridorlarında duvara/saksıya çarpmadan dolaşıyor (Linux).
- `use_camera:=true` ile kırmızı ürüne yönelip duruyor (Linux, opsiyonel).

## Yapılanlar

- 2026-10-26: `serabot_behavior/logic.py` (tarama analizi, `YawIntegrator`, `BehaviorStateMachine`), `test/test_logic.py` (24 test durumu), `test/conftest.py` (kaynak ağacından pytest için `sys.path`).
- 2026-10-26: `serabot_behavior/behavior_node.py`, `serabot_bringup/config/behavior.yaml` (§7 varsayılanları aynen + yeni parametreler, float değerler ondalıklı).

## Doğrulama

- 2026-10-26, Windows: `python -m pytest src/serabot_behavior/test` → 24 geçti, 1 atlandı (ament_flake8 yok). `flake8 --max-line-length 99 --import-order-style google` temiz.
- 2026-10-26, Windows: `behavior_node.py` `py_compile` + flake8 temiz; `behavior.yaml` anahtar/tip/değerleri `BehaviorParams` ile aynı. rclpy Windows'ta yok → node **çalıştırılmadı**.
- 2026-10-26, Üye A VM (Docker, Lyrical + Jetty): `colcon build` + `colcon test` (serabot_behavior) → 25 test, 0 hata (ament_flake8 dahil; centering testi sonradan eklendi, Windows'ta 26/26).
- 2026-10-26, VM Gazebo testi: `bringup.launch.py behavior:=true rviz:=false`, varsayılan spawn (−4.0, 0.875, 0), `greenhouse.sdf`, 180 s sim zamanı, gerçek zaman oranı ≈ 0.5–0.6. Çarpışma, Gazebo'dan alınan gerçek pozdan (`/world/greenhouse/dynamic_pose/info`) gövde izdüşümü (şasi kutusu + tekerlek küreleri) ile duvar/yatak/saksı arasındaki en kısa mesafe olarak hesaplandı (§4.2 yerleşimi). Yatak/saksı yüksekliği LiDAR düzleminin (0.18 m) üstünde, hepsi görülüyor.

| Koşu | Ayar | Yol | Ziyaret edilen 1×1 m hücre | En küçük açıklık | Durum geçişleri | Sonuç |
|---|---|---|---|---|---|---|
| run1 | `centering_gain` 0, `rotate_margin` 0.05 | 26.1 m | 16/60 | 0.100 m | 15 AVOID, 18 EMERGENCY | Çarpışma yok; batı dönüş alanında takılıyor |
| run2 | aynı | 15.4 m | 12/60 | 0.115 m | 9 AVOID, 31 EMERGENCY | Çarpışma yok; t ≈ 90 s'den sonra 1.0 m'lik kuzey koridorunda AVOID↔EMERGENCY kilidi |
| **run3** | `centering_gain` 0.5, `rotate_margin` 0.02 | **37.1 m** | **29/60** | **0.106 m** | 16 AVOID, 0 EMERGENCY | **Çarpışma yok, kilit yok**; iki dönüş alanı ve güney-orta koridor boydan boya |

- run3 bag'i (`/behavior/state`, `/cmd_vel`, `/odom`, `/scan`, `/imu`, `/rosout`): CRUISE 1540, AVOID 368 adım (10 Hz). Kapanışta son iki `/cmd_vel` sıfır → kapanışta durma doğrulandı. Ayrıca sim'siz testte SIGINT → node çıktı ve sıfır `Twist` yayınladı.
- run2 kilidinin nedeni: robot koridorda duvara 0.4 m'ye kadar çapraz yaklaştı, gövde koridoru kontrolü duvarı "önde" gördü (AVOID), 0.376 + 0.05 m dönüş payı iki yönde de sağlanmadı, düz geri gitmek yanal konumu değiştirmedi. Çözüm: koridor ortalama (çapraz yaklaşmayı önler) + payı 0.02 m'ye indirmek (0.4 m'de dönüş geometrik olarak çarpışmasız).
- Tek koşu (run3) sonucu; tekrar edilebilirlik ve kamera katmanı (`use_camera: true`) Gazebo'da **doğrulanmadı**.

**Tekrar etme (VM):** test betikleri şu an repo dışında (VM'de `~/serabot_ws/test_runs/`: `run_behavior.sh` başlatma + 120 s'de poz gelmezse yeniden deneme + bag + kapanış; `gt_logger.py` gerçek poz kaydı; `bag_states.py` durum özeti; Windows'ta `analyze_gt.py` açıklık + yörünge grafiği). Elle: `ros2 launch serabot_bringup bringup.launch.py behavior:=true` ve ayrı terminalde `ros2 bag record -o run --topics /behavior/state /cmd_vel`.

## Açık istekler (S0'a)

1. **INTERFACES §7'ye yeni parametreler** (mevcut varsayılanlar değişmiyor; hepsi `behavior.yaml`'da olacak): `side_sector_deg` 100, gövde geometrisi (`lidar_offset_x` 0.22, `body_front_x` 0.345, `body_rear_x` −0.105, `chassis_half_width` 0.15, `body_half_width` 0.26 — §4'ten türetilmiş), `side_margin` 0.05, `rotate_margin` 0.02, `rotate_sweep_deg` 90, `backup_speed` 0.1, `backup_duration` 1.5, `rear_clear_distance` 0.15, `scan_timeout` 0.5, `imu_timeout` 0.3, `target_timeout` 0.5 (§2.5), `track_gain` 0.8, `track_speed` 0.12, `target_cooldown` 8.0, `centering_gain` 0.5, `centering_range` 1.0, `max_centering` 0.3. Ayrıca `/behavior/state` değer listesine `WAIT`.
2. **ARCHITECTURE §6 diyagramı** yukarıdaki farklara göre güncellenebilir (WAIT, TRACK → INSPECT yatağa varınca).
3. **DEV_ENVIRONMENT §4 notları** (VM testinde öğrenildi): (a) Lyrical'da `ros2 bag record` topic'leri `--topics` ile ister; (b) arka planda başlatılan betikten çalışan `ros2 launch`/`ros2 bag` SIGINT'i yok sayılmış olarak devralır → `kill -INT` etkisiz, bag `metadata.yaml`'sız kalır; çözüm SIGINT'i `SIG_DFL`'e çevirip exec etmek; (c) Gazebo sunucusu bazen hiç açılmıyor (`ros_gz_sim create` sürekli "Requesting list of world names"), bir kez 18 dk bekledi — test betiği ilk pozu 120 s bekleyip yeniden başlatmalı.
4. **Test betiklerinin yeri:** `run_behavior.sh` / `gt_logger.py` / `analyze_gt.py` diğer modüllerin Gazebo testleri için de kullanılabilir; `scripts/` altına (S0) mı yoksa `serabot_behavior/tools/` altına mı konacağı kararı.

## Açık sorunlar

- `inspect_area` 0.08: 6 cm'lik domates 60° FOV'da ancak ~0.2 m'de görüntünün %8'ini kaplar; yatak yüzünden bu kadar yaklaşılamaz. Bu yüzden TRACK'te yatağa varmak da INSPECT'i tetikliyor. Kamera modülü hazır olunca alan değeri ölçülüp ayarlanmalı.
- Koridor ortalaması koridorlarda hafif yılankavi iz bırakıyor (run3 grafiği); çarpışma riski yaratmadı, istenirse kazanç düşürülebilir.
- Orta-kuzey koridor (y = +0.875) saksı (−0.5, 1.30) yüzünden robot için tıkalı: gövde koridoru (|y| ≤ 0.31) saksının kenarına 1.5 cm yakın; robot orada geri dönüyor (çarpışmıyor).
- Arka kontrol: kamera direği (LiDAR'a 0.235 m, `range_min` içinde) arkadaki ışınları gölgeleyebilir mi? gpu_lidar'ın yakın kırpma davranışı VM'de kontrol edilecek. Geri çekilme kısa (0.1 m/s × 1.5 s).
