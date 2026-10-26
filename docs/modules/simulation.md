# Modül S2 — Simülasyon ve Bringup (`serabot_gazebo`, `serabot_bringup`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Devam ediyor — primitif dünya + bringup VM'de doğrulandı (2026-10-26)
- **Sahip olunan yollar:** `src/serabot_gazebo/`, `src/serabot_bringup/launch/`, `src/serabot_bringup/config/bridge/base.yaml`
- **Bağımlı olduğu:** S1 (robot_description), `INTERFACES.md` §2.1, §5, §6
- **Ona bağımlı olanlar:** Tüm sensör modülleri ve S4 (çalışan simülasyon)

## Görevler

- [x] `worlds/greenhouse.sdf` (primitif kısım; Blender süsleri bekliyor) — yaklaşık 10 × 6 m sera: dış duvarlar, 3 bitki sırası (yükseklik ≥ 0.4 m, LiDAR düzleminde görünür), koridorlarda saksı engelleri, sıraların üstünde kamera yüksekliğinde (~0.4–0.5 m) kırmızı "domates" küreleri ve yeşil yapraklar. Karma dünya (ADR-018, `INTERFACES.md` §4.2): önce primitiflerle çalışan dünya, sonra Blender süsleri (`models/<model>/`, `.obj`). Koridor genişliği robotun çarpışma genişliğine (0.52 m) göre rahat dönebilecek kadar olmalı (≥ 1.0 m önerilir).
- [x] Dünya eklentileri: physics, user-commands, scene-broadcaster, sensors (`ogre2`), imu (`INTERFACES.md` §5)
- [x] `config/bridge/base.yaml` — `/clock`, `/cmd_vel`, `/odom`, `/tf`, `/joint_states`
- [x] `launch/bringup.launch.py` — dünya + robot_state_publisher + spawn + `config/bridge/*.yaml` için ayrı bridge node'ları + RViz; argümanlar `INTERFACES.md` §6
- [x] `behavior:=true` ve `sensors:=true` argümanlarıyla ilgili node'ları koşullu başlat (node'lar hazır değilse yer tutucu olarak bırak)
- [x] Spawn noktasını dünyaya göre belirle, `INTERFACES.md` §6 güncellemesi için açık istek yaz

## Tamamlanma kriteri

- `ros2 launch serabot_bringup bringup.launch.py` tek komutla dünyayı, robotu ve RViz'i açıyor (Linux).
- `ros2 run teleop_twist_keyboard teleop_twist_keyboard` ile robot sürülebiliyor; RViz'de `odom` frame'inde hareket görünüyor (Linux).

## Yapılanlar

- **Primitif sera dünyası (2026-10-26):** `worlds/greenhouse.sdf`, `tools/generate_greenhouse.py` ile üretilir (yerleşim sabitleri tek yerde; SDF elle düzenlenmez). Dünya adı `greenhouse`, orijin sera merkezinde, yataklar x yönünde.
  - İç alan 10 × 6 m (x −5…5, y −3…3), duvarlar 0.1 m kalın, 1.0 m yüksek.
  - 3 bitki yatağı: 6.0 × 0.5 × 0.40 m, merkezleri y = −1.75 / 0 / +1.75; üstte toprak ve yeşil yaprak kutusu (0.36 m genişlik, 0.35 m yükseklik; sadece görsel, yatak sınırı içinde).
  - Koridorlar: yataklar arası 1.25 m (merkez y = ±0.875), duvar kenarı 1.0 m; iki uçta 2.0 m dönüş alanı (x −5…−3, 3…5).
  - 5 saksı (silindir r 0.15, h 0.35, statik, gri-mavi — kırmızıyla karışmasın): (−0.5, 1.30), (1.0, −0.45), (−1.6, −1.30) koridorlarda (yanında 0.90 m geçiş), (4.2, −1.20), (−4.2, −1.80) dönüş alanlarında.
  - Domatesler: saf kırmızı (1, 0, 0) küre r 0.04, z 0.46 / 0.53; her yatağın iki kenarında 5 salkım × 3 = 90 küre (sadece görsel).
  - Çarpışma: 13 primitif (zemin, 4 duvar, 3 yatak, 5 saksı). Eklentiler §5: physics, user-commands, scene-broadcaster, sensors (`ogre2`), imu. Gölgeler kapalı (yazılımsal render için).
- **`config/bridge/base.yaml` (2026-10-26):** §2.1'deki 5 topic.
- **`launch/bringup.launch.py` (2026-10-26):** argümanlar §6 (yeni argüman yok).
  - `ros_gz_sim/gz_sim.launch.py` ile `-r <world>`, `on_exit_shutdown: true` (Gazebo kapanınca launch kapanır).
  - `robot_state_publisher`: varsayılan xacro (RViz renkleri).
  - Spawn (ADR-019, S1 isteği): xacro Python API'siyle `gazebo_mesh_colors:=true` işlenir, geçici dosyaya (`/tmp/serabot_gazebo_*.urdf`) yazılır, `ros_gz_sim create -file` ile spawn; `-x/-y/-Y` launch argümanlarından.
  - Bridge: kurulu `config/bridge/*.yaml` dosyalarının her biri için `bridge_<ad>` adlı ayrı `parameter_bridge`; boş yaml atlanır (log). Sensör yaml'ları eklenince launch değişmeden devreye girer.
  - Yardımcı node'lar (`color_detector`, `imu_monitor`, `behavior_node`): modül (`importlib.util.find_spec`) yoksa log ile atlanır, launch bozulmaz. `config/behavior.yaml` varsa `behavior_node`'a verilir.
  - Tüm node'lar `use_sim_time: true`.
- **Spawn noktası:** (x, y, yaw) = (−4.0, 0.875, 0.0) — batı dönüş alanı, ortadaki iki yatak arasındaki koridorun girişi, koridora (+x) bakar. Varsayılan `0,0` ortadaki yatağın içine denk geliyor → açık istek.

## Doğrulama

**Windows (2026-10-26):** `py_compile` ✅, `flake8 --max-line-length 99` (serabot_bringup, serabot_gazebo) ✅, SDF XML ayrıştırma ✅, `base.yaml` 5 kayıt ✅.

**Linux — Üye A VM (Docker, Lyrical + Jetty 10.5.0), 2026-10-26:**
- `colcon build` ✅ (5 paket); `gz sdf -k greenhouse.sdf` → `Valid.` ✅
- `ros2 launch serabot_bringup bringup.launch.py x:=-4.0 y:=0.875` → tek komutla Gazebo GUI + robot + RViz açıldı ✅; "Entity creation successful" ✅; `bridge_base` 5 köprüyü kurdu ✅; `color_detector` / `imu_monitor` "not implemented yet, skipped" ile atlandı, launch devam etti ✅.
- `ros2 topic list`: `/clock`, `/cmd_vel`, `/joint_states`, `/odom`, `/robot_description`, `/tf`, `/tf_static` ✅ (`/scan` ve `/camera/image_raw` sadece RViz abonesi olarak görünüyor — sensör köprüleri henüz yok, beklenen).
- Sürüş: `ros2 topic pub -r 10 /cmd_vel` 0.25 m/s, ~6 s → Gazebo'da robot (−4.000, 0.875) → (−3.382, 0.875), yani 0.618 m ileri, yanal sapma 0; `/odom` x = 0.613 m (fark 5 mm) ✅. RViz'de `odom` sabit çerçevesinde model ve odometri oku izi hareket etti ✅ (ekran görüntüsü).
- Gazebo GUI'de mesh renkleri Gazebo setiyle (doygun) yüklendi; dünya yerleşimi beklendiği gibi ✅ (ekran görüntüsü).
- **Gerçek zaman oranı (süssüz, GUI + RViz açık, sensörsüz):** `/stats` örnekleri 0.41–0.84, tipik ~0.63–0.82 (GUI'de %63). Süslerden sonra tekrar ölçülecek.
- Ekran görüntüleri VBoxManage ile alındı (oturum çalışma alanında; rapor için gerekirse S0 `docs/report/` altına koyar).

**Tekrar üretme:**
```bash
scripts/sync_to_vm.sh
ssh serabot-vm 'cd serabot_ws && docker/run.sh exec "colcon build && gz sdf -k install/serabot_gazebo/share/serabot_gazebo/worlds/greenhouse.sdf"'
# VM masaüstünde (konteyner kabuğu):
ros2 launch serabot_bringup bringup.launch.py x:=-4.0 y:=0.875
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.25}}"
```

## Açık istekler (S0'a)

- **`INTERFACES.md` §6 — spawn varsayılanı:** `x` = −4.0, `y` = 0.875, `yaw` = 0.0 (batı dönüş alanı, y = +0.875 koridorunun girişi, +x yönüne bakar). Onaylanınca `bringup.launch.py` varsayılanlarını ben güncellerim. (§6 "S2 dünyaya göre güncelleyecek" diyor; yine de sözleşme tablosu olduğu için S0'a bırakıyorum.)
- **`serabot_bringup/package.xml`:** launch dosyası `yaml` (PyYAML) kullanıyor → `<exec_depend>python3-yaml</exec_depend>` eklenmesi. (ROS imajında zaten kurulu; sadece manifest doğruluğu.)
- **`INTERFACES.md` §4.2'ye not (isteğe bağlı):** dünya yerleşimi (yatak/koridor/saksı koordinatları) yukarıda; S4 ve kamera sahibi bunları test senaryolarında kullanabilir.

## Açık sorunlar

- **Arka planda başlatılan launch'ı durdurma:** `setsid nohup ros2 launch ... &` ile başlatılınca alt süreçler SIGINT'i yok sayıyor (arka plan işi); `pkill -TERM` ile launch kapanıyor ama `gz-sim`, bridge ve `robot_state_publisher` öksüz kalıyor. Kapatmak için: `pkill -TERM -f "^/opt/ros/lyrical/(lib/robot_state_publisher|lib/ros_gz_bridge|opt/gz_sim_vendor)"`. Sonraki GUI testlerinden önce `ps` ile kontrol edilmeli.
- **Gerçek zaman oranı ~0.6–0.8:** VM'de yazılımsal render (llvmpipe). Sensörler (gpu_lidar, kamera) eklenince düşmesi bekleniyor; süs bütçesi buna göre seçilecek.
- Doğrulanmadı: `headless` çalışma (argüman yok), `rviz:=false`, `behavior:=true` (node yok), sensör köprüleriyle birlikte çalışma.
