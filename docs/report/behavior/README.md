# Davranış (S4) — rapor ve sunum malzemesi

Kaynak: Üye A VM'i (Docker, ROS 2 Lyrical + Gazebo Jetty), 2026-10-26. Ayrıntılı sonuçlar: [docs/modules/behavior.md](../../modules/behavior.md).

Koşu ayarları: `ros2 launch serabot_bringup bringup.launch.py behavior:=true rviz:=false`, dünya `greenhouse.sdf`, varsayılan spawn (−4.0, 0.875, 0), `config/behavior.yaml` varsayılanları (`centering_gain` 0.5, `rotate_margin` 0.02), `use_camera: false`. Süre 180 s sim zamanı, gerçek zaman oranı ≈ 0.5–0.6.

| Dosya | İçerik |
|---|---|
| `behavior_design.md` | Rapor/sunum metni: giriş-çıkış topic tablosu, tarama analizi, durum diyagramı (Mermaid), karar kuralı tablosu, eşiklerin gerekçesi, parametreler, demo komutları |
| `state_diagram.png` | Durum diyagramı (rapor/slayt için görsel; `behavior_design.md` §4 ile aynı) |
| `run3_trajectory.png` | run3'te robotun Gazebo'daki gerçek konumu (`/world/greenhouse/dynamic_pose/info`), renk = sim zamanı. Gri: duvarlar, kahverengi: bitki yatakları, turuncu: saksılar. Çarpışma yok; gövde ile engeller arasındaki en kısa mesafe 0.106 m (kırmızı ×). Yol 37.1 m |
| `gazebo_screenshot.png` | Koşu sırasında Gazebo görüntüsü (**run2**'den; davranış kodu aynı, ayarlar run3'ten önceki: ortalama kapalı). Robot sol altta, batı dönüş alanında |
| `run3_transitions.log` | `behavior_node`'un durum geçişi logları, gerekçesiyle (örn. `CRUISE -> AVOID: front 0.55 m < 0.55 m; turning right`, `AVOID -> CRUISE: turned 176 deg (imu), front 0.98 m`). 16 AVOID, 0 EMERGENCY |
| `run3_states.csv` | Bag'den: her `/behavior/state` mesajı (10 Hz) ve o anki son `/cmd_vel` (`linear.x` m/s, `angular.z` rad/s). `wall_t` = bag kayıt zamanı (duvar saati, Unix s). CRUISE 1540, AVOID 368 adım |

Notlar:
- Tek koşu sonucu. Kamera katmanı (TRACK/INSPECT) Gazebo'da denenmedi.
- Ham bag (`/behavior/state`, `/cmd_vel`, `/odom`, `/scan`, `/imu`, `/rosout`) VM'de `~/serabot_ws/test_runs/run3/bag` altında; boyutu nedeniyle repoya konmadı.
