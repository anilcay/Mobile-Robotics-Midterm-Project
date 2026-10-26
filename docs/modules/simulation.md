# Modül S2 — Simülasyon ve Bringup (`serabot_gazebo`, `serabot_bringup`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Başlamadı
- **Sahip olunan yollar:** `src/serabot_gazebo/`, `src/serabot_bringup/launch/`, `src/serabot_bringup/config/bridge/base.yaml`
- **Bağımlı olduğu:** S1 (robot_description), `INTERFACES.md` §2.1, §5, §6
- **Ona bağımlı olanlar:** Tüm sensör modülleri ve S4 (çalışan simülasyon)

## Görevler

- [ ] `worlds/greenhouse.sdf` — yaklaşık 10 × 6 m sera: dış duvarlar, 3 bitki sırası (yükseklik ≥ 0.4 m, LiDAR düzleminde görünür), koridorlarda saksı engelleri, sıraların üstünde kamera yüksekliğinde (~0.4–0.5 m) kırmızı "domates" küreleri ve yeşil yapraklar. Karma dünya (ADR-018, `INTERFACES.md` §4.2): önce primitiflerle çalışan dünya, sonra Blender süsleri (`models/<model>/`, `.obj`). Koridor genişliği robotun çarpışma genişliğine (0.52 m) göre rahat dönebilecek kadar olmalı (≥ 1.0 m önerilir).
- [ ] Dünya eklentileri: physics, user-commands, scene-broadcaster, sensors (`ogre2`), imu (`INTERFACES.md` §5)
- [ ] `config/bridge/base.yaml` — `/clock`, `/cmd_vel`, `/odom`, `/tf`, `/joint_states`
- [ ] `launch/bringup.launch.py` — dünya + robot_state_publisher + spawn + `config/bridge/*.yaml` için ayrı bridge node'ları + RViz; argümanlar `INTERFACES.md` §6
- [ ] `behavior:=true` ve `sensors:=true` argümanlarıyla ilgili node'ları koşullu başlat (node'lar hazır değilse yer tutucu olarak bırak)
- [ ] Spawn noktasını dünyaya göre belirle, `INTERFACES.md` §6 güncellemesi için açık istek yaz

## Tamamlanma kriteri

- `ros2 launch serabot_bringup bringup.launch.py` tek komutla dünyayı, robotu ve RViz'i açıyor (Linux).
- `ros2 run teleop_twist_keyboard teleop_twist_keyboard` ile robot sürülebiliyor; RViz'de `odom` frame'inde hareket görünüyor (Linux).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
