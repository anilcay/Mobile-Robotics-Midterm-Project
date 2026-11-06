# Modül S3c — IMU (Ek sensör, ortak sorumluluk)

- **Sorumlu:** Üye A + Üye B (ortak) · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Entegrasyon (xacro + bridge, Üye A) VM'de doğrulandı (`930c993`) · `imu_monitor` + grafik (Üye B) tamam, Linux'ta doğrulandı (2026-11-04) — commit bekliyor (Üye B'nin hesabından)
- **İş bölümü önerisi:** Üye A sensör entegrasyonu (xacro + bridge), Üye B görselleştirme (`imu_monitor` + rqt_plot). Raporda katkı tablosuna bu şekilde yazılır; değişirse burada güncellenir.
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/imu.xacro`, `src/serabot_bringup/config/bridge/imu.yaml`, `src/serabot_sensors/serabot_sensors/imu_monitor.py` (+ testi)
- **Bağımlı olduğu:** S1 (`base_link`), S2 (imu sistemi), `INTERFACES.md` §2.4, §2.5, §4
- **Ona bağımlı olanlar:** S4 (AVOID durumunda dönüş açısı)

## Görevler

- [x] `imu.xacro` — `imu_link` (S1'in `imu.obj` görseli, kutu collision), `imu_joint`, `<gazebo reference="imu_link">` içinde `imu` sensörü, 100 Hz, gürültü (`<gz_frame_id>imu_link`) — Üye A
- [x] `config/bridge/imu.yaml` — `/imu` GZ→ROS — Üye A
- [x] `imu_monitor.py` — quaternion → roll/pitch/yaw (derece) → `/imu/rpy` (`Vector3Stamped`). Dönüşüm saf fonksiyon (`imu_math.py`), pytest ile test. — Üye B
- [x] Görselleştirme: dönüş grafiği `docs/report/sensors/imu_turn.png` (`scripts/sim/imu_turn_record.py` + `imu_turn_plot.py`); canlı: `rqt_plot /imu/rpy/vector/z /imu/angular_velocity/z` — Üye B
- [ ] `rqt_plot` pencere ekran görüntüsü (demo sırasında elle) — Üye B
- [x] Doğrulama: `/imu` hızı, frame, durağan ivme, yerinde dönüş — Üye A

## Tamamlanma kriteri

- `/imu` ~100 Hz, `frame_id = imu_link`; robot yerinde dönerken `angular_velocity.z` ≈ komut edilen açısal hız (Linux). ✅
- `/imu/rpy` yaw değeri dönüşle tutarlı değişiyor (Linux). ✅ (odometriyle en çok 1.56° fark)

## Yapılanlar

**2026-10-26 — `imu.xacro` + `imu.yaml` (Üye A)**

- Makro `serabot_imu(parent)` (§8 değişmedi). `imu_joint` fixed, `${imu_x} ${imu_y} ${imu_z}` = (0, 0, 0) → **dönme merkezi** (aks ortası, `../properties.xacro`).
- Görsel `${mesh_dir}/imu.obj` (şasinin içinde kalır, dışarıdan görünmez); yedek yeşil kutu. Collision/inertial: mesh sınır kutusu 0.03 × 0.025 × 0.009 m, 0.01 kg.
- Sensör: `imu`, topic `imu`, `gz_frame_id imu_link`, 100 Hz, `always_on`. Gaussian gürültü (tipik MEMS): açısal hız σ = 2e-4 rad/s, doğrusal ivme σ = 1.7e-2 m/s² (her eksen). Değerler dosyada `imu_*` property'leri.
- Bridge: `/imu` `sensor_msgs/msg/Imu` ← `gz.msgs.IMU` (`bridge_imu`).

### Yerleşim gerekçesi (rapor için)

- **Dönme merkezinde (aks ortası):** diferansiyel sürüşte robot bu nokta etrafında döner. IMU burada olunca yerinde dönüşte merkezcil ivme (ω²r) ve teğetsel ivme ölçmez; `linear_acceleration` sadece yerçekimi + ileri ivmelenmeyi gösterir, `angular_velocity.z` doğrudan dönüş hızıdır. Ölçüm aşağıda: dönerken ivme x/y ≈ 0.
- **`base_link` ile aynı eksenler:** dönüşüm gerekmez; IMU ekseni = robot ekseni (REP-103: x ileri, z yukarı).

**2026-11-04 — `imu_monitor` + grafik (Üye B)**

- Dosyalar: `serabot_sensors/imu_math.py` (saf dönüşüm), `serabot_sensors/imu_monitor.py` (node), `test/test_imu_math.py` (11 test), ortak `serabot_sensors/spin.py` (bkz. `sensor-camera.md`: `EventsExecutor`, `/clock` CPU yükü).
- Dönüşüm: birim quaternion → roll/pitch/yaw, Z-Y-X (tf2 `getRPY` ile aynı): `roll = atan2(2(wx+yz), 1−2(x²+y²))`, `pitch = asin(2(wy−zx))` (±1'e kırpılır → gimbal kilidinde NaN yok), `yaw = atan2(2(wz+xy), 1−2(y²+z²))`. Quaternion önce normalize edilir; sıfır quaternion → `ValueError` (node mesajı atlar, uyarı log'u).
- Node: abone `/imu` (`qos_profile_sensor_data`), yayın `/imu/rpy` (`Vector3Stamped`: x = roll, y = pitch, z = yaw, **derece**; header IMU mesajından → `imu_link` + IMU zaman damgası). Parametresi yok.
- Testler: kimlik → 0; z etrafında 90° → yaw +90 (sola dönüş pozitif, REP-103); 180°; Gazebo örneği (z 0.974, w 0.226) → yaw 153.9°; 4 gidiş-dönüş (rpy → quaternion → rpy); normalize edilmemiş quaternion; gimbal kilidi; sıfır quaternion.

## Doğrulama

**`imu_monitor` (Üye B, 2026-11-04)** — Ortam: Üye B dizüstü, WSL2 Ubuntu 26.04 + Lyrical + Jetty 10.5.0 (doğrudan kurulum).
- Windows pytest 24 geçti (serabot_sensors); Linux `colcon test --packages-select serabot_sensors` 25 test, 0 hata (ament_flake8 dahil).
- Launch (`sensors:=true`, varsayılan) node'u otomatik başlatıyor, `use_sim_time` True ✅. `/imu/rpy` **100.0 Hz (sim)**, `frame_id imu_link` ✅; durağan: roll/pitch/yaw ≈ 0 (1e-7°).
- Yerinde dönüş (`scripts/sim/imu_turn_record.py`, 1 s dur, 6 s `angular.z` 0.8 rad/s, 2 s dur; 899 örnek, `docs/report/sensors/imu_turn.csv`): yaw 0° → **−90.55°** (= 269.45° dönüş, beklenen ≈ 268.9° — Üye A ölçümüyle aynı); `/odom` 0° → −91.11°. **|IMU yaw − odom yaw| en çok 1.56°, ortalama 0.63°** — fark odometrinin 30 Hz yayınından (0.8 rad/s × 1/30 s = 1.5°). Düz zeminde roll/pitch 0.000° ✅. Grafik: `docs/report/sensors/imu_turn.png`.
- Tekrarlamak için: `ros2 launch serabot_bringup bringup.launch.py` → `python3 scripts/sim/imu_turn_record.py /tmp/turn.csv` → `python3 scripts/sim/imu_turn_plot.py /tmp/turn.csv /tmp/turn.png`; canlı grafik `ros2 run rqt_plot rqt_plot /imu/rpy/vector/z /imu/angular_velocity/z`.

**Entegrasyon (Üye A)** — Ortam: Üye A VM'i, Docker, Lyrical + Jetty 10.5.0. Statik: xacro dört varyantta ✅, `check_urdf` ✅ (`imu_link` `base_link` çocuğu), `gz sdf -p` sensör pozu `0 0 0.08` (`base_footprint`'e göre = aks yüksekliği) ✅.

**Çalışma zamanı (`bringup.launch.py`):**
- Log: `bridge_imu: Creating GZ->ROS Bridge: [/imu (gz.msgs.IMU) -> /imu (sensor_msgs/msg/Imu)]` ✅
- **Hız:** zaman damgalarından **100.00 Hz** (30 s, 981 mesaj; GUI'siz 2755 mesaj) ✅. `ros2 topic hz /imu` duvar saatiyle ≈ 35 Hz = 100 Hz × RTF (≈0.35).
- `frame_id='imu_link'` ✅; kovaryans köşegenleri gürültüden dolduruluyor: açısal hız 4.0e-8 (= σ²), ivme 2.89e-4 (= σ²) ✅
- **Durağan:** `linear_acceleration.z` ortalama **9.800 m/s²**, sd 0.0172 (≈ σ 0.017) ✅; `angular_velocity.z` ortalama 0.0000 (±0.0006) ✅
- **Yerinde dönüş** (`/cmd_vel` angular.z = 0.8 rad/s, 6 s simülasyon zamanı, ilk 1 s ivmelenme hariç):
  - `angular_velocity.z` ortalama **0.8000 rad/s**, sd 0.0002 (499 mesaj) ✅; `/odom` twist 0.8000 ✅
  - Dönerken `linear_acceleration` x **0.0003**, y **−0.0005 m/s²** → dönme merkezinde merkezcil ivme yok ✅
  - Jiroskop integrali 268.2°; beklenen 0.8 × 6 s = 275.0° − ivmelenme rampası (ω²/2α = 0.8²/(2·3.0) rad ≈ 6.1°) ≈ 268.9° ✅
  - Örnek mesaj (dönüş ortası): `orientation z=0.974 w=0.226`, `angular_velocity z=0.79975`, `linear_acceleration x=0.016 y=−0.025 z=9.789`
- RTF ölçümleri: `sensor-lidar.md` "Doğrulama" (sensörlerin etkisi ölçülemeyecek kadar küçük).

**Tekrarlamak için:**
```bash
ros2 launch serabot_bringup bringup.launch.py
ros2 topic echo /imu --once           # frame_id: imu_link, linear_acceleration.z ≈ 9.8
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{angular: {z: 0.8}}"
ros2 topic echo /imu --field angular_velocity.z   # ≈ 0.8
```

## Açık istekler (S0'a)

- Rapor klasörü ve ölçüm betikleri: `sensor-lidar.md` "Açık istekler" (ortak).
- (Üye B) PROGRESS / REQUIREMENTS: R9 IMU grafiği ✅ (`imu_turn.png`), S3c tamam.

## Açık sorunlar

—
