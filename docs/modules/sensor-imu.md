# Modül S3c — IMU (Ek sensör, ortak sorumluluk)

- **Sorumlu:** Üye A + Üye B (ortak) · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Başlamadı
- **İş bölümü önerisi:** Üye A sensör entegrasyonu (xacro + bridge), Üye B görselleştirme (`imu_monitor` + rqt_plot). Raporda katkı tablosuna bu şekilde yazılır; değişirse burada güncellenir.
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/imu.xacro`, `src/serabot_bringup/config/bridge/imu.yaml`, `src/serabot_sensors/serabot_sensors/imu_monitor.py` (+ testi)
- **Bağımlı olduğu:** S1 (`base_link`), S2 (imu sistemi), `INTERFACES.md` §2.4, §2.5, §4
- **Ona bağımlı olanlar:** S4 (AVOID durumunda dönüş açısı)

## Görevler

- [ ] `imu.xacro` — `imu_link` (küçük kutu), `imu_joint`, `<gazebo reference="imu_link">` içinde `imu` sensörü, 100 Hz, gürültü (`<gz_frame_id>imu_link`)
- [ ] `config/bridge/imu.yaml` — `/imu` GZ→ROS
- [ ] `imu_monitor.py` — quaternion → roll/pitch/yaw (derece) → `/imu/rpy` (`Vector3Stamped`). Dönüşüm saf fonksiyon, pytest ile test.
- [ ] Görselleştirme: `rqt_plot /imu/rpy/vector/z /imu/angular_velocity/z` (veya PlotJuggler) — robot dönerken grafik ekran görüntüsü
- [ ] Doğrulama: `ros2 topic hz /imu`, `ros2 topic echo /imu --once`

## Tamamlanma kriteri

- `/imu` ~100 Hz, `frame_id = imu_link`; robot yerinde dönerken `angular_velocity.z` ≈ komut edilen açısal hız (Linux).
- `/imu/rpy` yaw değeri dönüşle tutarlı değişiyor (Linux).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
