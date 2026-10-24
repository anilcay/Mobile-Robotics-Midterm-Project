# Modül S4 — Davranış (`serabot_behavior`)

- **Sorumlu:** Üye A · **Faz:** F3 (1–3 Kas), saf mantık ve testleri F1'den itibaren yazılabilir · **Durum:** Başlamadı
- **Sahip olunan yollar:** `src/serabot_behavior/`, `src/serabot_bringup/config/behavior.yaml`
- **Bağımlı olduğu:** `/scan` (S3a), `/imu` (S3c), `/camera/target` (S3b, opsiyonel), `INTERFACES.md` §2, §7
- **Ona bağımlı olanlar:** Demo, rapor (karar kuralı açıklaması)

## Tasarım

Durum makinesi taslağı: `ARCHITECTURE.md` §6. Kesinleşen karar kuralı bu dosyada güncellenecek.

- **Girdi:** `/scan` (`sensor_msgs/msg/LaserScan`), `/imu` (`sensor_msgs/msg/Imu`), `/camera/target` (`geometry_msgs/msg/PointStamped`, opsiyonel)
- **Çıktı:** `/cmd_vel` (`geometry_msgs/msg/Twist`), `/behavior/state` (`std_msgs/msg/String`)
- **Parametreler:** `INTERFACES.md` §7

## Görevler

- [ ] `serabot_behavior/logic.py` — ROS'suz saf mantık: tarama sektör analizi (ön/sol/sağ min ve ortalama, `inf`/`nan` temizliği), IMU yaw-rate integrasyonu, durum geçişleri, `(linear, angular)` çıktısı
- [ ] `test/test_logic.py` — pytest: engel yok → CRUISE; önde engel → AVOID ve açık tarafa dönüş; dönüş açısı tamamlanınca → CRUISE; acil mesafe → EMERGENCY; hedef ofset işareti → dönüş yönü
- [ ] `serabot_behavior/behavior_node.py` — abonelikler (`qos_profile_sensor_data`), parametreler, 10 Hz zamanlayıcı, `/cmd_vel` + `/behavior/state` yayını; kapanırken sıfır hız yayınla
- [ ] `config/behavior.yaml` varsayılanları
- [ ] Gazebo'da parametre ayarı (eşikler, hızlar) ve sonuçların kaydı
- [ ] Sunum/rapor için: durum diyagramı, karar kuralı, topic/mesaj tipi tablosu

## Tamamlanma kriteri

- `python -m pytest src/serabot_behavior/test` geçiyor (Windows).
- Gazebo'da robot 3 dakika boyunca sera koridorlarında duvara/saksıya çarpmadan dolaşıyor (Linux).
- `use_camera:=true` ile kırmızı ürüne yönelip duruyor (Linux, opsiyonel).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
