# Modül S3a — LiDAR (Sensör A)

- **Sorumlu:** Üye A (anilcay) · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Başlamadı
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/lidar.xacro`, `src/serabot_bringup/config/bridge/lidar.yaml`, `serabot_sensors` içindeki lidar dosyaları (gerekirse)
- **Bağımlı olduğu:** S1 (`base_link`), S2 (sensors sistemi), `INTERFACES.md` §2.2, §4
- **Ona bağımlı olanlar:** S4 (davranışın birincil girdisi)

## Görevler

- [ ] `lidar.xacro` — `lidar_link` (silindir görsel + collision + inertial), `lidar_joint`, `<gazebo reference="lidar_link">` içinde `gpu_lidar` sensörü (`INTERFACES.md` §2.2 değerleri, `<gz_frame_id>lidar_link`)
- [ ] `config/bridge/lidar.yaml` — `/scan` GZ→ROS
- [ ] RViz'de LaserScan görselleştirmesi için `serabot.rviz`'e eklenecek ayarları açık istek olarak yaz (Fixed frame `odom`, `/scan`, renk, nokta boyutu)
- [ ] Doğrulama komutları ve ekran görüntüleri: `ros2 topic hz /scan`, `ros2 topic echo /scan --once`, RViz görüntüsü
- [ ] Rapor için: sensör yerleşim gerekçesi, topic/mesaj tipi, kanıt ekran görüntüleri (`docs/report/` altına)

## Tamamlanma kriteri

- `/scan` ~10 Hz yayınlanıyor, `frame_id = lidar_link` (Linux).
- RViz'de tarama noktaları duvar ve saksılarla örtüşüyor; robotun kendi gövdesi/direği taramada görünmüyor (Linux).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
