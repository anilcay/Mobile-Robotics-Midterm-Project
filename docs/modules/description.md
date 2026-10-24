# Modül S1 — Robot Modeli (`serabot_description`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Primitif model tamam (CI'da `check_urdf` geçti; Gazebo'da doğrulanmadı) · Konsept B (Saksı) Blender'da modellendi · Mesh yön/renk testi Üye B'yi bekliyor
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
- [x] Blender tasarımı: konsept B (Saksı) seçildi ve modellendi, `meshes/source/serabot.blend`
- [x] Yön/renk test küpü (ADR-015): `meshes/test/`, `urdf/test/mesh_test.urdf.xacro`
- [ ] Test küpü sonucu (Üye B VM) → dışa aktarım ayarını seç, link başına mesh dışa aktarımı
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
  - Commit `9ba0913`, push edildi.
- **Tasarım konseptleri (2026-10-24, kullanıcı B'yi seçti):** Üçü de §4 sınır kutusunda, sensör/direk konumları aynı.
  - **A — Cam sera:** alt gövde sera yeşili, üst yarı buzlu cam panelli + beyaz alüminyum çerçeve, sırt çizgisi; beyaz direk ve kamera kutusu; LiDAR beyaz "havalandırma bacası" içinde; kiremit rengi ön tampon.
  - **B — Saksı:** pişmiş toprak renginde, aşağı doğru daralan saksı gövdesi + koyu kenar bandı; üst yüzey toprak dokusu; direk yeşil "bitki sapı" + yaprak braketi, kamera tomurcuk biçimli kapsül; LiDAR çakıl taşı kubbesi.
  - **C — Tarla aracı:** grafit gövde + yaprak yeşili üst panel, pahlı ön yüz, sarı-siyah ikaz şeridi; tırtıklı lastikler; direk payandalı, anten + kırmızı LED; LiDAR siyah puck + yeşil halka.
- **CI (2026-10-24):** `9ba0913` için GitHub Actions yeşil — `colcon build`, `xacro` + `check_urdf`, `colcon test` Linux konteynerinde geçti.
- **Yön/renk test küpü (2026-10-24, ADR-015):** `blender/make_orientation_test.py` ile 0.2 m gri küp + kırmızı ok (+X), yeşil ok (+Y), mavi kapak (+Z). Üç dosya: `meshes/test/orientation_cube_yup.glb` (glTF varsayılan "+Y Up" dönüşümü), `orientation_cube_zup.glb` (dönüşümsüz, ham Blender eksenleri), `orientation_cube.obj` + `.mtl` (Z yukarı, Y ileri = ham eksenler). Dosya içi kontrol (Windows): dört malzeme ayrı ayrı, `doubleSided: false`; `yup` dosyasında Blender +Z → glTF +Y, +Y → −Z. `urdf/test/mesh_test.urdf.xacro` üç mesh'i primitif referansla yan yana gösterir. `display.launch.py`'ye `model` argümanı eklendi (varsayılan `serabot.urdf.xacro`).
- **Konsept B modeli (2026-10-24):** `blender/build_serabot.py` (prosedürel, tekrar üretilebilir; yardımcılar `blender/mesh_kit.py`, render `blender/render_serabot.py`).
  - Link mesh'leri (orijin = link frame): `chassis` (daralan saksı + kenar bandı + toprak + krem tabak/tampon + yan yaprak motifleri + arka bitki etiketi + çakıllar), `wheel` (simetrik — sol/sağ aynı mesh; tırtıklı lastik, krem jant, yaprak "çiçek" deseni), `caster` (metal bilye + krem yuva), `camera_mast` (boğumlu yeşil sap, toprakta filiz, iki yaprak), `camera` (tomurcuk; mercek +X), `lidar` (çakıl taşı, z = 0 tarama düzleminde koyu pencere bandı), `imu` (şasi içinde küçük kart).
  - Sınır kutuları: şasi tam 0.45 × 0.30 × 0.12; tekerlek r 0.08 × 0.04; caster r 0.03 (+ yuva). Üçgen sayısı: robot toplamı 15.6k (bütçe 50k).
  - LiDAR uyumu: sap yaprakları tarama düzleminin (direk tabanından +0.04 m) üstünde, toprak filizleri altında; sapın kendisi LiDAR'a ≈ 0.235 m, `range_min` 0.25 altında kalıyor.
  - Tüm malzemeler tek taraflı (backface culling açık → glTF `doubleSided: false`); amaç LiDAR/kameranın kendi gövdesinin iç yüzünü görmemesi.
  - Ara render'lar (perspektif ön/arka, ön, yan, üst) alındı. URDF `visual` blokları henüz primitif; mesh'e çevirme test küpü sonucundan sonra.

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

5. **Mesh yön/renk testi (ADR-015) — mesh dışa aktarımı bu sonuca bağlı:**
   ```bash
   ros2 launch serabot_description display.launch.py model:=test/mesh_test.urdf.xacro
   ```
   RViz'de +Y'den −Y'ye dört nesne: `ref_primitive`, `glb_yup`, `glb_zup`, `obj` (TF etiketlerinde adları görünür). Beklenen: en az bir mesh, referans ile **aynı yönde** (kırmızı ok TF'nin kırmızı X ekseni yönünde, yeşil ok Y, mavi kapak yukarıda) ve **renkli** (gri değil/beyaz değil). Hangilerinin doğru olduğunu yazın; ekran görüntüsü ekleyin.

   Gazebo'da aynı test:
   ```bash
   xacro src/serabot_description/urdf/test/mesh_test.urdf.xacro > /tmp/mesh_test.urdf
   gz sim -r empty.sdf
   gz service -s /world/empty/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 2000 --req 'sdf_filename: "/tmp/mesh_test.urdf", name: "mesh_test"'
   ```
   Beklenen: dört nesne (+Y'den −Y'ye aynı sıra) yerinde durur; mesh'ler bulunur (terminalde "Unable to find file" hatası yok — `package://` çözümü ve `GZ_SIM_RESOURCE_PATH` kancası da böylece doğrulanır); yön ve renkler referansla aynı. Hangi dosyanın RViz **ve** Gazebo'da doğru olduğunu yazın.

Sonuçları (geçti/kaldı + hata çıktısı) bu bölüme yazın.

## Açık istekler (S0'a)

- `.gitignore`'a `*.blend1` eklenmesi (Blender'ın kayıt yedeği; `build_serabot.py` şimdilik kayıttan sonra siliyor).

## Açık sorunlar

- **Mesh formatı:** Blender 5.2'de Collada (`.dae`) dışa aktarımı yok. S0 kararı (ADR-015, `INTERFACES.md` v0.4 §4.1): `.glb`, yedek `.obj` + `.mtl`. Gerçek mesh'lerden önce yön/renk test küpü (`.glb` + `.obj`) hazırlanıp Üye B'nin VM'inde RViz2 ve Gazebo'da denenecek (Linux'ta doğrulanmadı).
- **Odometri ofseti (kabul edildi):** Sözleşmeye göre aks `base_link`'in 0.12 m gerisinde. gz DiffDrive odometriyi aks merkezine göre hesaplayıp `base_footprint` adıyla yayınlıyor; yerinde dönüşte `/odom` konumunda küçük hata olur. Davranış harita kullanmadığı ve dönüş açısını IMU'dan aldığı için sözleşme korundu (kullanıcı kararı, 2026-10-24).
- **⚠ Doğrulanacak (Linux) — sensör kendi gövdesini görüyor mu:** LiDAR çakılı ve kamera tomurcuğu sensör noktasını sarıyor. Mesh'ler tek taraflı dışa aktarılıyor (içeriden görünmemeli). Mesh'ler URDF'e bağlandıktan sonra Üye A `/scan`'de ~0.03–0.05 m'de sabit okuma, Üye B görüntüde yeşil/koyu kaplama olup olmadığını kontrol etmeli. Sorun olursa sensör `visual`'ında pencere boşluğu bırakılır veya `visibility_flags` kullanılır.
- **⚠ Doğrulanacak (Linux):** JointStatePublisher'ın `<topic>/joint_states</topic>` parametresini Jetty'de desteklediği; caster'ın `mu1/mu2` değerinin sabit joint birleştirmesinden (lumping) sonra da çarpışmaya uygulandığı (Doğrulama 3. adım).
