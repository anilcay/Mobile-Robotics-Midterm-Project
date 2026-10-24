# Modül S1 — Robot Modeli (`serabot_description`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Primitif model tamam (Windows statik kontrolleri geçti, Linux'ta doğrulanmadı) · Tasarım konsepti sırada
- **Sahip olunan yollar:** `src/serabot_description/` — ana `urdf/serabot.urdf.xacro` (S0) ve `urdf/sensors/` (sensör sahipleri) hariç
- **Bağımlı olduğu:** `INTERFACES.md` §3 (frame'ler), §4 (boyutlar), §5 (eklentiler)
- **Ona bağımlı olanlar:** S2 (spawn), S3a/b/c (montaj linkleri), S4 (tekerlek geometrisi)

## Çalışma yöntemi

Görsel model **Blender'da** hazırlanır; çarpışma modeli primitif kalır (ADR-012). Mesh kuralları: `INTERFACES.md` §4.1. Önce primitif görselli çalışan URDF yapılır, mesh'ler hazır oldukça `visual` blokları mesh'e çevrilir — böylece S2 ve sensör modülleri mesh'leri beklemez.

## Görevler

- [x] `urdf/properties.xacro` — tüm boyut/kütle sabitleri (`INTERFACES.md` §4)
- [x] `urdf/inertial_macros.xacro` — kutu, silindir, küre inertia makroları
- [x] `urdf/chassis.xacro` — `base_footprint`, `base_link`, şasi görseli (sera yeşili gövde, kiremit rengi ön tampon şeridi)
- [x] `urdf/wheels.xacro` — sol/sağ tekerlek makrosu (`continuous`), caster (sürtünmesiz küre)
- [x] `urdf/camera_mast.xacro` — `camera_mast_link` (direk); kamera sensörü değil, sadece montaj noktası
- [x] `urdf/gazebo_drive.xacro` — DiffDrive + JointStatePublisher eklentileri, tekerlek sürtünme (`mu1/mu2`) ayarları
- [x] `urdf/materials.xacro` — renkler (RViz + Gazebo)
- [x] `launch/display.launch.py` — robot_state_publisher + joint_state_publisher_gui + RViz (`rviz/model.rviz`)
- [x] Ana xacro'ya eklenmesi gereken include'ları "Açık istekler"e yaz — gerek yok: her S1 dosyası yardımcıları kendisi include ediyor, ana xacro değişmedi
- [ ] Blender tasarımı: sera temalı özgün gövde (konsept → onay → modelleme), link başına mesh dışa aktarımı, `meshes/source/serabot.blend`
- [ ] Mesh formatının RViz2 ve Gazebo'da renkleriyle yüklendiğini doğrula (Üye B'nin VM'i), `visual` bloklarını mesh'e çevir
- [ ] Rapor için tasarım görselleri (Blender render, ön/yan/üst görünüş)

## Tamamlanma kriteri

- `xacro serabot.urdf.xacro` hatasız URDF üretiyor (Windows'ta statik kontrol). ✅
- `check_urdf` hatasız; TF ağacı `ARCHITECTURE.md` §4 ile birebir (Linux). ⏳
- Gazebo'da robot yere düzgün oturuyor, devrilmiyor; `/cmd_vel` ile ileri gidip dönüyor (S2 ile birlikte, Linux). ⏳

## Yapılanlar

- **Blender bağlantısı (2026-10-24):** Blender MCP yerine harici indirme gerektirmeyen yerel köprü yazıldı: `blender/bridge_server.py` (Blender içinde, sadece `127.0.0.1:9877`), `blender/bridge_client.py` (Windows Python'dan kod gönderir). Ortam: Blender 5.2.3 LTS (Steam), EEVEE, GTX 1650; Unit Scale 1.0. Köprü üzerinden sahne sorgusu ve EEVEE render testi geçti.
  - Başlatma: `"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --python src/serabot_description/blender/bridge_server.py`
  - Kullanım: `python src/serabot_description/blender/bridge_client.py <script.py>` veya `-c "<kod>"`; kod `result` değişkeniyle JSON değer döndürebilir.
  - `blender/` klasörü CMake ile kurulmaz (sadece geliştirme aracı).
- **Primitif model (2026-10-24):**
  - `properties.xacro`: §4 değerleri + türetilmiş değerler. Sözleşme dışı seçimler: tekerlek 0.5 kg, caster 0.1 kg, direk 0.3 kg (r = 0.015 m), tekerlek `mu` = 1.0, caster `mu` = 0, DiffDrive ivme sınırları 1.0 m/s² / 3.0 rad/s². Toplam kütle 7.4 kg, ağırlık merkezi x = −0.02 m (aks ile caster arasında).
  - Sensör montaj noktaları da property olarak var: `lidar_x/y/z`, `imu_x/y/z`, `camera_z` — sensör xacro'ları `../properties.xacro` include edip bunları kullanabilir.
  - Geometri: şasi `base_link`'e göre z = −0.06…+0.06 (zeminden 2 cm yukarıda), direk tabanı şasi üst yüzeyinde (zeminden 0.14 m), kamera yüksekliği 0.44 m, caster zemine değiyor, tekerlek iç yüzü ile şasi arası 1 cm.
  - `materials.xacro`: renkler `serabot_material` makrosuyla `<visual>` içine **satır içi** yazılır (üst seviye `<material>` yok) → dosya birden çok yerden include edilse de "material is not unique" hatası olmaz. Kullanım: `<xacro:serabot_material name="dark"/>` (green, leaf, terracotta, dark, grey, rubber, red).
  - `display.launch.py`: argümanlar `use_sim_time` (varsayılan **false** — Gazebo'suz `/clock` yok), `rviz`, `use_lidar`, `use_camera`, `use_imu`.
  - `launch/` ve `rviz/` içindeki `.gitkeep` dosyaları silindi (klasörler artık dolu).

## Doğrulama

**Windows (yapıldı, geçti):**
- `xacro serabot.urdf.xacro` → hatasız, uyarısız URDF.
- Statik kontrol betiği (`check_urdf` benzeri, Python): §3 joint/parent/child/tipleri, §4 konumları (base_link 0.08, tekerlekler (−0.12, ±0.18, 0.08), caster altı z = 0, direk tabanı 0.14, kamera 0.44), her link'te visual+collision, inertia pozitif + üçgen eşitsizliği, DiffDrive/JointStatePublisher parametreleri §5 ile birebir, yinelenen material yok → **tümü geçti**.
- Bir sensör dosyası `../properties.xacro`, `../materials.xacro`, `../inertial_macros.xacro` include ettiğinde (kopya klasörde denendi) uyarısız çalışıyor.
- `py_compile` + `flake8 --max-line-length 99 src/` → temiz. `model.rviz` geçerli YAML.
- Blender'da URDF primitifleri kurulup render alındı; görünüm ölçülerle tutarlı.

**Linux — Üye B'nin VM'inde çalıştırılacak (Linux'ta doğrulanmadı):**

Repo kökü workspace köküdür (`src/` doğrudan altında); komutlar repo kökünden:

```bash
colcon build --packages-select serabot_description && source install/setup.bash
```

1. URDF ayrıştırma:
   ```bash
   xacro src/serabot_description/urdf/serabot.urdf.xacro > /tmp/serabot.urdf && check_urdf /tmp/serabot.urdf
   ```
   Beklenen: `Successfully Parsed XML`; kök `base_footprint` → `base_link` → `left_wheel_link`, `right_wheel_link`, `caster_link`, `camera_mast_link` (+ sensör linkleri dolduruldukça).
2. RViz görüntüleme:
   ```bash
   ros2 launch serabot_description display.launch.py
   ```
   Beklenen: RViz'de yeşil gövde, siyah tekerlekler, ön tarafta turuncu şerit, arkada direk; TF eksenleri görünür. joint_state_publisher_gui kaydırıcıları tekerlekleri döndürür. Terminalde hata yok.
3. SDF dönüşümü ve sürtünme:
   ```bash
   gz sdf -p /tmp/serabot.urdf > /tmp/serabot.sdf && grep -n -A3 "<mu>" /tmp/serabot.sdf
   ```
   Beklenen: hata yok; caster çarpışmasında `mu` 0, tekerleklerde 1.
4. Gazebo'da sürüş (S2 bringup'ı beklemeden, ROS'suz):
   ```bash
   gz sim -r empty.sdf
   ```
   İkinci terminalde:
   ```bash
   gz service -s /world/empty/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 2000 --req 'sdf_filename: "/tmp/serabot.urdf", name: "serabot"'
   gz topic -t /cmd_vel -m gz.msgs.Twist -p 'linear: {x: 0.25}'
   gz topic -t /cmd_vel -m gz.msgs.Twist -p 'angular: {z: 0.8}'
   gz topic -e -t /odom -n 1
   gz topic -l | grep joint_states
   ```
   Beklenen: robot yere oturur, devrilmez, sekmez; ilk komutla +x yönünde ileri gider, ikinciyle saat yönünün tersine döner; `/odom` mesajında `child_frame_id: base_footprint`; `/joint_states` topic'i listede.

Sonuçları (geçti/kaldı + hata çıktısı) bu bölüme yazın.

## Açık istekler (S0'a)

—

## Açık sorunlar

- **Mesh formatı:** Blender 5.2'de Collada (`.dae`) dışa aktarımı yok. S0 kararı (ADR-015, `INTERFACES.md` v0.4 §4.1): `.glb`, yedek `.obj` + `.mtl`. Gerçek mesh'lerden önce yön/renk test küpü (`.glb` + `.obj`) hazırlanıp Üye B'nin VM'inde RViz2 ve Gazebo'da denenecek (Linux'ta doğrulanmadı).
- **Odometri ofseti (kabul edildi):** Sözleşmeye göre aks `base_link`'in 0.12 m gerisinde. gz DiffDrive odometriyi aks merkezine göre hesaplayıp `base_footprint` adıyla yayınlıyor; yerinde dönüşte `/odom` konumunda küçük hata olur. Davranış harita kullanmadığı ve dönüş açısını IMU'dan aldığı için sözleşme korundu (kullanıcı kararı, 2026-10-24).
- **⚠ Doğrulanacak (Linux):** JointStatePublisher'ın `<topic>/joint_states</topic>` parametresini Jetty'de desteklediği; caster'ın `mu1/mu2` değerinin sabit joint birleştirmesinden (lumping) sonra da çarpışmaya uygulandığı (Doğrulama 3. adım).
