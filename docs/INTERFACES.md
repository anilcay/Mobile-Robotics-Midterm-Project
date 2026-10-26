# Arayüz Sözleşmesi

**Sürüm:** 0.7 (taslak) — 2026-10-24 · 0.2: mesh kuralları (§4.1, ADR-012) · 0.3: xacro makro sözleşmesi (§8) · 0.4: mesh formatı `.glb`, yedek `.obj` (§4.1, ADR-015) · 0.5: yön testi sonucu → `.obj` + `.mtl` (§4.1) · 0.6: `base_link` aks ortasına taşındı, montaj noktaları +0.12 m x (§4, ADR-017) · 0.7: renk setleri + `gazebo_mesh_colors`, tekerlek küre çarpışması (§4.1, §6, ADR-019), karma dünya (§4.2, ADR-018)

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
| `base_link` orijini | **Tekerlek aksının ortası** (dönme merkezi; DiffDrive odometrisiyle uyumlu, ADR-017) |
| `base_link` yüksekliği (`base_footprint`'e göre) | z = 0.08 m (aks yüksekliği); `base_footprint` aks ortasının zemindeki izdüşümü |
| Tekerlekler (`base_link`'e göre) | x = 0, y = ±0.18, z = 0 |
| Şasi kutusu merkezi (`base_link`'e göre) | x = +0.12, z = 0 (şasi x = −0.105 … +0.345) |
| Caster | küre, r = 0.03 m, x = +0.29, z = −0.05 m, sürtünmesiz |
| `lidar_link` (`base_link`'e göre) | x = +0.22, z = +0.10 m |
| `imu_link` (`base_link`'e göre) | x = 0, y = 0, z = 0 (dönme merkezi — dönüşte merkezcil ivme ölçmez) |
| `camera_mast_link` (`base_link`'e göre) | x = −0.03, z = +0.06 m (şasi üstü); direk yüksekliği 0.30 m |
| `camera_link` (`camera_mast_link`'e göre) | z = +0.30 m → zeminden ≈ 0.44 m, pitch 0 |

### 4.1 Mesh kuralları (Blender → URDF)

| Kural | Değer |
|---|---|
| Birim / ölçek | Metre; Blender'da Unit Scale 1.0, nesnelerde ölçek uygulanmış (Apply Scale) |
| Eksenler | REP-103: Blender sahnesinde X ileri, Y sol, Z yukarı modellenir. Dışa aktarılan dosyanın RViz2/Gazebo'da doğru yönde açıldığı yön testiyle doğrulanır (aşağıda) |
| Orijin | Her mesh'in orijini, bağlı olduğu link frame'inin orijininde (örn. tekerlek mesh'i aks merkezinde). İstisna: link orijini parçanın dışındaysa (ADR-017 sonrası `base_link` ↔ şasi) mesh parça merkezinde kalabilir; ofset `visual` `origin` ile `properties.xacro` değerinden verilir |
| Parçalama | Her link için ayrı mesh dosyası: `chassis`, `wheel` (sol/sağ aynı mesh), `caster`, `camera_mast`, `lidar`, `camera`, `imu` |
| Dosya yolu | `src/serabot_description/meshes/<link>.obj` + `.mtl` (RViz2 renk seti, sRGB) ve `meshes/gazebo/<link>.obj` + `.mtl` (Gazebo Jetty renk seti, doğrusal); kaynak `meshes/source/serabot.blend`. İki set her zaman `blender/build_serabot.py` ile birlikte üretilir |
| URDF referansı | `package://serabot_description/meshes/<link>.<ext>` |
| Format | **`.obj` + `.mtl`** (aynı klasörde, aynı ad; renkler MTL diffuse). `.glb` kullanılmaz: RViz2 ve Gazebo Jetty glTF eksen dönüşümünü farklı uyguluyor (ADR-015, yön testi). Blender 5.2'de `.dae` yok |
| OBJ dışa aktarım | S1'in test küpündeki ayarlar (`blender/make_orientation_test.py`): Blender ham eksenleri (Forward/Up dönüşümü yok — dosyada Z yukarı), Apply Modifiers açık, sadece seçili nesne (link başına bir dosya), malzemeler MTL'e yazılır |
| Yön ve renk testi | ✅ 2026-10-24, Üye A VM (Docker, Lyrical + Jetty 10.5.0): `orientation_cube.obj` RViz2 **ve** Gazebo'da doğru yön ve renkte. `glb_yup` yalnız RViz2'de, `glb_zup` yalnız Gazebo'da doğru |
| Poligon bütçesi | Robot toplamı ≤ 50k üçgen (VM'de akıcı simülasyon için) |
| Çarpışma | Mesh kullanılmaz; §4'teki boyutlarla primitif geometri. İstisna: tekerlek çarpışması küre r = 0.08 m (ADR-019) → robotun çarpışma genişliği **0.52 m** |
| Dış ölçüler | Mesh'in sınır kutusu §4'teki boyutlara uyar (görsel ile çarpışma modeli örtüşmeli) |

### 4.2 Dünya modelleri (karma, ADR-018)

| Kural | Değer |
|---|---|
| Çarpışma ve LiDAR geometrisi | Duvarlar, bitki yatakları, saksılar: SDF primitifleri (kutu/silindir); `collision` her zaman primitif |
| Görsel süs | Bitkiler, domatesler, sera iskeleti vb. Blender'da, `.obj` + `.mtl` (§4.1 kuralları, Gazebo renk seti); `src/serabot_gazebo/models/<model>/` altında, `model://` ile |
| Kamera hedefi | Kırmızı domatesler kamera yüksekliğinde (≈ 0.40–0.50 m) görünür olmalı; renk HSV ile ayrılabilir saf kırmızı tonda |
| Poligon bütçesi | Tüm dünya görselleri ≤ 150k üçgen (VM yazılımsal render) |
| Sıra | Önce sadece primitiflerle çalışan dünya; Blender süsleri sonra ve zaman kalırsa |

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

Xacro argümanları (`serabot.urdf.xacro`): `use_lidar`, `use_camera`, `use_imu` — varsayılan `true`; `gazebo_mesh_colors` — varsayılan `false` (RViz renk seti). `robot_state_publisher`'a giden URDF varsayılanla, Gazebo'ya spawn edilen URDF `gazebo_mesh_colors:=true` ile üretilir (spawn `robot_description` topic'inden değil, ayrı xacro çıktısından).

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

## 8. Xacro makro sözleşmesi

`src/serabot_description/urdf/serabot.urdf.xacro` (S0) aşağıdaki dosyaları göreli yolla include eder ve makroları çağırır. Dosyalar şu an `PLACEHOLDER`; sahipleri sadece makro gövdesini doldurur.

| Dosya | Makro | Parametre | Oluşturması gereken | Sahip |
|---|---|---|---|---|
| `chassis.xacro` | `serabot_chassis` | — | `base_footprint`, `base_link`, `base_joint` | S1 |
| `wheels.xacro` | `serabot_wheels` | — | `left/right_wheel_link`, `left/right_wheel_joint`, `caster_link`, `caster_joint` | S1 |
| `camera_mast.xacro` | `serabot_camera_mast` | — | `camera_mast_link`, `camera_mast_joint` | S1 |
| `gazebo_drive.xacro` | `serabot_gazebo_drive` | — | DiffDrive + JointStatePublisher `<gazebo>` blokları | S1 |
| `sensors/lidar.xacro` | `serabot_lidar` | `parent` (= `base_link`) | `lidar_link`, `lidar_joint`, gpu_lidar sensörü | Üye A |
| `sensors/camera.xacro` | `serabot_camera` | `parent` (= `camera_mast_link`) | `camera_link`, `camera_optical_link`, joint'ler, camera sensörü | Üye B |
| `sensors/imu.xacro` | `serabot_imu` | `parent` (= `base_link`) | `imu_link`, `imu_joint`, imu sensörü | Ortak |

Ortak yardımcılar (`properties.xacro`, `materials.xacro`, `inertial_macros.xacro`) S1'e aittir; diğer xacro dosyaları bunları kendi içinden göreli yolla include eder (xacro aynı dosyanın tekrar include edilmesine izin verir).

Gazebo kaynak yolu: `serabot_description` ve `serabot_gazebo` paketleri, ortam kancası (`hooks/*.dsv.in`) ile `GZ_SIM_RESOURCE_PATH`'e eklenir; böylece `package://serabot_description/meshes/...` ve `model://...` URI'leri Gazebo'da çözülür (⚠ doğrulanacak).
