# Arayüz Sözleşmesi

**Sürüm:** 0.2 (taslak) — 2026-10-24 · 0.2: mesh kuralları eklendi (§4.1, ADR-012)

Bu dosya modüller arasındaki **tek doğru kaynaktır**. Modüller burada yazan topic, frame, mesaj tipi ve boyutları kullanır. Değişiklik sadece S0 tarafından, `DECISIONS.md` kaydı ile yapılır; diğer oturumlar değişiklik isteğini kendi modül dosyasına yazar.

`⚠ doğrulanacak` işaretli maddeler Jetty/Lyrical kurulumunda ilk iş kontrol edilecek.

## 1. Genel

- Robot/model adı: `serabot`
- Dünya adı: `greenhouse`
- Tüm node'lar: `use_sim_time: true`
- Gazebo ve ROS tarafında topic adları aynı tutulur (bridge sadece tip çevirir).
- Sensör abonelikleri: `qos_profile_sensor_data` (best effort; bridge'in reliable yayınıyla uyumlu).

## 2. Topic'ler

### 2.1 Sürüş ve durum (sahip: S1 / S2 — `config/bridge/base.yaml`)

| ROS topic | ROS tipi | Gazebo tipi | Yön | Kaynak |
|---|---|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | `gz.msgs.Clock` | GZ→ROS | Dünya |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `gz.msgs.Twist` | ROS→GZ | Davranış node'u / teleop |
| `/odom` | `nav_msgs/msg/Odometry` | `gz.msgs.Odometry` | GZ→ROS | DiffDrive |
| `/tf` | `tf2_msgs/msg/TFMessage` | `gz.msgs.Pose_V` | GZ→ROS | DiffDrive (sadece `odom→base_footprint`) |
| `/joint_states` | `sensor_msgs/msg/JointState` | `gz.msgs.Model` | GZ→ROS | JointStatePublisher sistemi |

Not: `/cmd_vel` tipi `Twist` (stamped değil). Lyrical'da `teleop_twist_keyboard` varsayılanının `Twist` olduğu ⚠ doğrulanacak; değilse `stamped:=false` parametresi kullanılır.

### 2.2 LiDAR (sahip: Üye A — `config/bridge/lidar.yaml`)

| ROS topic | ROS tipi | Gazebo tipi | Yön | Frame |
|---|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | `gz.msgs.LaserScan` | GZ→ROS | `lidar_link` |

Özellikler: `gpu_lidar`, 360 örnek, -π..π, 10 Hz, `range_min` 0.25 m (direği ve gövdeyi dışarıda bırakmak için), `range_max` 8.0 m, gaussian gürültü σ=0.01.

### 2.3 Kamera (sahip: Üye B — `config/bridge/camera.yaml`)

| ROS topic | ROS tipi | Gazebo tipi | Yön | Frame |
|---|---|---|---|---|
| `/camera/image_raw` | `sensor_msgs/msg/Image` | `gz.msgs.Image` | GZ→ROS | `camera_optical_link` |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | `gz.msgs.CameraInfo` | GZ→ROS | `camera_optical_link` |

Özellikler: 640×480, RGB8, 15 Hz, yatay FOV 1.047 rad (60°). Camera info topic adının Gazebo'da nasıl türetildiği ⚠ doğrulanacak.

### 2.4 IMU (sahip: ortak — `config/bridge/imu.yaml`)

| ROS topic | ROS tipi | Gazebo tipi | Yön | Frame |
|---|---|---|---|---|
| `/imu` | `sensor_msgs/msg/Imu` | `gz.msgs.IMU` | GZ→ROS | `imu_link` |

Özellikler: 100 Hz, açısal hız ve doğrusal ivmede gaussian gürültü.

### 2.5 Uygulama topic'leri (ROS içi)

| Topic | Tip | Yayıncı | Abone | Açıklama |
|---|---|---|---|---|
| `/camera/target` | `geometry_msgs/msg/PointStamped` | `color_detector` | `behavior_node` | Sadece hedef görülünce yayınlanır. `point.x` = yatay ofset [-1, 1] (sol negatif), `point.y` = görüntü alanı oranı [0, 1], `point.z` = 0. Son mesajdan 0.5 s geçtiyse "hedef yok". |
| `/camera/image_annotated` | `sensor_msgs/msg/Image` | `color_detector` | rqt_image_view | Tespit kutusu çizilmiş görüntü (görselleştirme). |
| `/imu/rpy` | `geometry_msgs/msg/Vector3Stamped` | `imu_monitor` | rqt_plot | Roll/pitch/yaw, derece (görselleştirme). |
| `/behavior/state` | `std_msgs/msg/String` | `behavior_node` | — | Aktif durum adı (CRUISE, AVOID, …), sunum ve hata ayıklama için. |

## 3. Frame'ler

| Frame | Ebeveyn | Joint tipi | Yayıncı |
|---|---|---|---|
| `odom` | — | — | — |
| `base_footprint` | `odom` | — | DiffDrive (`/tf`) |
| `base_link` | `base_footprint` | fixed | robot_state_publisher |
| `left_wheel_link`, `right_wheel_link` | `base_link` | continuous | robot_state_publisher |
| `caster_link` | `base_link` | fixed | robot_state_publisher |
| `lidar_link` | `base_link` | fixed | robot_state_publisher |
| `imu_link` | `base_link` | fixed | robot_state_publisher |
| `camera_mast_link` | `base_link` | fixed | robot_state_publisher |
| `camera_link` | `camera_mast_link` | fixed | robot_state_publisher |
| `camera_optical_link` | `camera_link` | fixed (rpy = -π/2, 0, -π/2) | robot_state_publisher |

Joint adları: `left_wheel_joint`, `right_wheel_joint` (DiffDrive bunları kullanır), diğerleri `<link_adı_kökü>_joint`.

Sensör mesajlarındaki `frame_id`, SDF'te `<gz_frame_id>` ile yukarıdaki frame'lere ayarlanır (⚠ etiket adı doğrulanacak).

## 4. Robot boyutları ve montaj noktaları

Başlangıç değerleri — S1 `properties.xacro`'da bunları kullanır. Diğer modüller bu sayılara güvenir; değişiklik sözleşme değişikliğidir.

| Parametre | Değer |
|---|---|
| Şasi (L × W × H) | 0.45 × 0.30 × 0.12 m |
| Şasi kütlesi | 6.0 kg |
| Tekerlek yarıçapı / genişliği | 0.08 m / 0.04 m |
| Tekerlekler arası mesafe (merkezden merkeze) | 0.36 m |
| Tekerlek aksı konumu (`base_link`'e göre) | x = -0.12 m |
| `base_link` yüksekliği (`base_footprint`'e göre) | z = 0.08 m (aks yüksekliği) |
| Caster | küre, r = 0.03 m, x = +0.17 m, sürtünmesiz |
| `lidar_link` (`base_link`'e göre) | x = +0.10, z = +0.10 m |
| `imu_link` (`base_link`'e göre) | x = 0, y = 0, z = 0 |
| `camera_mast_link` (`base_link`'e göre) | x = -0.15, z = +0.06 m (şasi üstü); direk yüksekliği 0.30 m |
| `camera_link` (`camera_mast_link`'e göre) | z = +0.30 m → zeminden ≈ 0.44 m, pitch 0 |

### 4.1 Mesh kuralları (Blender → URDF)

| Kural | Değer |
|---|---|
| Birim / ölçek | Metre; Blender'da Unit Scale 1.0, nesnelerde ölçek uygulanmış (Apply Scale) |
| Eksenler | REP-103: X ileri, Y sol, Z yukarı (dışa aktarımda "Z up, X forward") |
| Orijin | Her mesh'in orijini, bağlı olduğu link frame'inin orijininde (örn. tekerlek mesh'i aks merkezinde) |
| Parçalama | Her link için ayrı mesh dosyası: `chassis`, `wheel` (sol/sağ aynı mesh), `caster`, `camera_mast`, `lidar`, `camera`, `imu` |
| Dosya yolu | `src/serabot_description/meshes/<link>.<ext>`; kaynak `src/serabot_description/meshes/source/serabot.blend` |
| URDF referansı | `package://serabot_description/meshes/<link>.<ext>` |
| Format | Aday: `.dae` (renk/malzeme taşır). Blender sürümü desteklemiyorsa `.glb` veya `.obj`. RViz2 + Gazebo Jetty uyumu ⚠ doğrulanacak |
| Poligon bütçesi | Robot toplamı ≤ 50k üçgen (VM'de akıcı simülasyon için) |
| Çarpışma | Mesh kullanılmaz; §4'teki boyutlarla primitif geometri |
| Dış ölçüler | Mesh'in sınır kutusu §4'teki boyutlara uyar (görsel ile çarpışma modeli örtüşmeli) |

## 5. Gazebo eklentileri

| Eklenti | Nerede | Sahip |
|---|---|---|
| `gz-sim-diff-drive-system` (`gz::sim::systems::DiffDrive`) | Robot (`gazebo_drive.xacro`) | S1 |
| `gz-sim-joint-state-publisher-system` | Robot (`gazebo_drive.xacro`) | S1 |
| `gz-sim-physics-system`, `gz-sim-user-commands-system`, `gz-sim-scene-broadcaster-system` | Dünya | S2 |
| `gz-sim-sensors-system` (`render_engine: ogre2`) — LiDAR ve kamera için | Dünya | S2 |
| `gz-sim-imu-system` — IMU için | Dünya | S2 |

DiffDrive parametreleri: `left_joint=left_wheel_joint`, `right_joint=right_wheel_joint`, `wheel_separation=0.36`, `wheel_radius=0.08`, `topic=/cmd_vel`, `odom_topic=/odom`, `tf_topic=/tf`, `frame_id=odom`, `child_frame_id=base_footprint`, `odom_publish_frequency=30`.

## 6. Launch argümanları

`serabot_bringup/launch/bringup.launch.py`:

| Argüman | Varsayılan | Açıklama |
|---|---|---|
| `world` | `greenhouse.sdf` | `serabot_gazebo/worlds` altındaki dünya dosyası |
| `rviz` | `true` | RViz2'yi aç |
| `behavior` | `false` | Davranış node'unu başlat |
| `sensors` | `true` | Yardımcı sensör node'larını (`color_detector`, `imu_monitor`) başlat |
| `x`, `y`, `yaw` | `0.0` | Spawn pozisyonu (S2 dünyaya göre güncelleyecek) |

Xacro argümanları (`serabot.urdf.xacro`): `use_lidar`, `use_camera`, `use_imu` — varsayılan `true`.

## 7. Parametreler (davranış — varsayılanlar `config/behavior.yaml`)

| Parametre | Varsayılan | Birim |
|---|---|---|
| `forward_speed` | 0.25 | m/s |
| `turn_speed` | 0.8 | rad/s |
| `front_sector_deg` | 30 | derece (± yarım açı) |
| `obstacle_distance` | 0.55 | m |
| `clear_distance` | 0.8 | m |
| `emergency_distance` | 0.3 | m |
| `turn_angle_deg` | 60 | derece |
| `use_camera` | false | — |
| `inspect_area` | 0.08 | oran |
| `inspect_duration` | 3.0 | s |
| `control_rate` | 10.0 | Hz |
