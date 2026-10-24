# Modül S1 — Robot Modeli (`serabot_description`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Model tamam — ADR-017 uygulandı, konsept B `.obj` mesh'leri URDF'e bağlandı; VM'de build, `check_urdf` ve yerinde dönüş testi geçti · Tekerlek çarpışması küre (odometri yaw sapması giderildi) · Mesh'ler RViz ve Gazebo'da yükleniyor · İki renk seti: `meshes/` (RViz, sRGB) + `meshes/gazebo/` (Gazebo, doğrusal), xacro `gazebo_mesh_colors` · S2/S0 isteği açık
- **Sahip olunan yollar:** `src/serabot_description/` — ana `urdf/serabot.urdf.xacro` (S0) ve `urdf/sensors/` (sensör sahipleri) hariç
- **Bağımlı olduğu:** `INTERFACES.md` §3 (frame'ler), §4 (boyutlar), §4.1 (mesh), §5 (eklentiler)
- **Ona bağımlı olanlar:** S2 (spawn), S3a/b/c (montaj linkleri, sensör mesh'leri), S4 (tekerlek geometrisi)

## Çalışma yöntemi

Görsel model **Blender'da** hazırlanır; çarpışma modeli primitif kalır (ADR-012). Mesh kuralları: `INTERFACES.md` §4.1. Model betikle üretilir (`blender/build_serabot.py`), elle düzenlenmez; değişiklik betikte yapılıp yeniden çalıştırılır.

## Görevler

- [x] `urdf/properties.xacro` — tüm boyut/kütle sabitleri (`INTERFACES.md` §4, v0.6)
- [x] `urdf/inertial_macros.xacro` — kutu, silindir, küre inertia makroları
- [x] `urdf/chassis.xacro` — `base_footprint`, `base_link`, şasi
- [x] `urdf/wheels.xacro` — sol/sağ tekerlek (`continuous`), caster (sürtünmesiz küre)
- [x] `urdf/camera_mast.xacro` — `camera_mast_link` (direk, montaj noktası)
- [x] `urdf/gazebo_drive.xacro` — DiffDrive + JointStatePublisher, tekerlek/caster sürtünmesi
- [x] `urdf/materials.xacro` — renkler (primitif yedek görseller ve sensör dosyaları için)
- [x] `launch/display.launch.py` + `rviz/model.rviz`
- [x] Blender tasarımı: konsept B (Saksı), `meshes/source/serabot.blend`
- [x] Yön/renk test küpü (ADR-015) → format `.obj` + `.mtl`
- [x] ADR-017: `base_link` aks ortasına
- [x] Link mesh'lerinin `.obj` + `.mtl` dışa aktarımı, `visual` bloklarının mesh'e çevrilmesi (primitif yedek bayrağıyla)
- [x] Rapor görselleri: `docs/report/serabot_{persp_front,persp_back,front,side,top}.png`
- [x] RViz ve Gazebo'da mesh'li modelin ekran görüntüsü (VM, 2026-10-24)
- [x] MTL renk değerleri için RViz/Gazebo karşılaştırması (doğrusal ve sRGB, VM ekran görüntüleriyle)
- [x] İki renk seti (kullanıcı kararı, seçenek c): `meshes/` sRGB + `meshes/gazebo/` doğrusal, xacro `gazebo_mesh_colors`
- [ ] Bringup'ın Gazebo'ya `gazebo_mesh_colors:=true` ile üretilmiş URDF'i spawn etmesi (S2, "Açık istekler")
- [x] Tekerlek çarpışması küre r = 0.08 (kullanıcı kararı; odometri yaw sapması %10.7 → %0.1)

## Tamamlanma kriteri

- `xacro serabot.urdf.xacro` hatasız URDF üretiyor. ✅ (Windows + CI + VM)
- `check_urdf` hatasız; TF ağacı `ARCHITECTURE.md` §4 ile birebir. ✅ (VM, 2026-10-24)
- Gazebo'da robot yere düzgün oturuyor, devrilmiyor; `/cmd_vel` ile ileri gidip dönüyor. ✅ (VM, S0, primitif model) · Yerinde dönüşte gövde yerinde kalıyor ✅ (VM, mesh'li model)

## Yapılanlar

- **Blender bağlantısı (2026-10-24):** Blender MCP yerine harici indirme gerektirmeyen yerel köprü: `blender/bridge_server.py` (Blender içinde, sadece `127.0.0.1:9877`), `blender/bridge_client.py` (Windows Python'dan kod gönderir; betik dosyasına `__file__` iletir). Ortam: Blender 5.2.3 LTS (Steam), EEVEE, GTX 1650; Unit Scale 1.0.
  - Başlatma: `"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --python src/serabot_description/blender/bridge_server.py`
  - Kullanım: `python src/serabot_description/blender/bridge_client.py <script.py>` veya `-c "<kod>"`; kod `result` değişkeniyle JSON değer döndürebilir.
  - `blender/` klasörü CMake ile kurulmaz (sadece geliştirme aracı).
- **Primitif model (2026-10-24, `9ba0913`):** `properties.xacro` (§4 değerleri + türetilmiş değerler), inertia/materyal yardımcıları, gövde makroları, `display.launch.py`. Sözleşme dışı seçimler: tekerlek 0.5 kg, caster 0.1 kg, direk 0.3 kg (r = 0.015 m), tekerlek `mu` = 1.0, caster `mu` = 0, DiffDrive ivme sınırları 1.0 m/s² / 3.0 rad/s². `materials.xacro` renkleri `serabot_material` makrosuyla `<visual>` içine satır içi yazar (birden çok include'da "material is not unique" olmaz). Sensör montaj noktaları property: `lidar_x/y/z`, `imu_x/y/z`, `camera_z`.
- **Tasarım konseptleri (2026-10-24):** A — Cam sera, **B — Saksı (seçildi)**, C — Tarla aracı.
- **Yön/renk test küpü (2026-10-24, `e343019`):** `blender/make_orientation_test.py`, `urdf/test/mesh_test.urdf.xacro`. S0'ın VM testi sonucu `.obj` + `.mtl` seçildi (ADR-015). `.glb` dosyaları ve test URDF'indeki glb nesneleri kaldırıldı (kullanıcı onayı); test artık primitif referans + `.obj`.
- **Konsept B modeli (2026-10-24):** `blender/build_serabot.py` (prosedürel), yardımcılar `blender/mesh_kit.py`, render `blender/render_serabot.py`.
  - Link mesh'leri: `chassis` (daralan saksı + kenar bandı + toprak + krem tabak/tampon + yan yaprak motifleri + arka bitki etiketi + çakıllar), `wheel` (simetrik — sol/sağ aynı mesh), `caster`, `camera_mast` (boğumlu sap, filiz, iki yaprak), `camera` (tomurcuk; mercek +X), `lidar` (çakıl taşı, z = 0 tarama düzleminde koyu pencere bandı), `imu`.
  - Üçgen: robot toplamı 15.6k (bütçe 50k). Sınır kutuları: şasi tam 0.45 × 0.30 × 0.12; tekerlek r 0.08 × 0.04; caster r 0.03.
  - LiDAR uyumu: sap yaprakları tarama düzleminin üstünde, filizler altında; sap yüzeyi LiDAR'a 0.235 m (`range_min` 0.25 altında).
- **ADR-017 uygulaması (2026-10-24):** `base_link` = aks ortası.
  - `properties.xacro`: `wheel_x` 0, yeni `chassis_x` +0.12, `caster_x` +0.29, `mast_x` −0.03, `lidar_x` +0.22, `imu_x` 0.
  - Şasi `visual`/`collision`/`inertial` origin'i `chassis_x`; şasi mesh'i kendi merkezinde (§4.1 istisnası). Diğer mesh'ler kendi link frame'inde.
  - **Kütle:** toplam 7.4 kg, ağırlık merkezi `base_footprint`'e göre (+0.100, 0, 0.088) m → aks (0) ile caster (+0.29) arasında; statik yük tekerleklerde %66, caster'da %34.
  - Blender önizleme konumları ve render kamerası yeni frame'lere göre güncellendi.
- **Mesh'ler URDF'te (2026-10-24):** `meshes/{chassis,wheel,caster,camera_mast,lidar,camera,imu}.obj` + `.mtl` (test küpü ayarları: ham Blender eksenleri, üçgenlenmiş, sadece seçili nesne). Şasi, tekerlekler, caster ve direk `visual`'ı mesh; `<material>` etiketi yok (renkler MTL'den). Çarpışmalar primitif.
  - **Primitif yedek:** `properties.xacro` → `use_mesh_visuals` (varsayılan `true`). `false` yapılırsa eski primitif görseller kullanılır (örn. VM'de yazılımsal render yavaşsa).
  - `lidar`, `camera`, `imu` mesh'leri hazır; sensör xacro'larına bağlanmaları sensör sahiplerinin işi (aşağıda "Açık istekler").
- **Tekerlek çarpışması küre (2026-10-24, kullanıcı kararı):** `wheels.xacro` — tekerlek `collision`'ı silindir yerine küre r = `wheel_radius` (0.08), aks merkezinde. Silindir zemine iç kenarından temas ediyor, etkin tekerlek aralığını ≈ 0.325 m'ye düşürüyordu (DiffDrive 0.36 varsayıyor) → `/odom` yerinde dönüşü %10.7 eksik bildiriyordu. Görsel mesh ve inertia (silindir) değişmedi. Yan etki: tekerlek çarpışma zarfı merkezden ±0.08 m (silindirde ±0.02) → robotun çarpışma genişliği 0.40 → 0.52 m; küre içte şasi kutusuyla örtüşür (aynı model, öz-çarpışma kapalı — etkisi yok).
- **Rapor görselleri (2026-10-24):** `docs/report/serabot_{persp_front,persp_back,front,side,top}.png` (1600 × 1066, EEVEE; kullanıcı onayıyla `docs/` altına). Yeniden üretmek için: `bridge_client.py -c "RENDER_DIR=r'<repo>\docs\report'; RES=(1600, 1066)"` ve ardından `bridge_client.py render_serabot.py`.

## Doğrulama

**Windows (2026-10-24, ADR-017 + mesh sonrası):**
- `xacro` → hatasız URDF (mesh varyantı ve `use_mesh_visuals=false` yedek varyantı).
- Statik kontrol betiği (Python), iki varyantta da **tümü geçti**: §3 joint'leri; §4 v0.6 konumları (base_link (0, 0, 0.08), tekerlekler (0, ±0.18, 0.08), `base_footprint` = aks ortasının izdüşümü, caster (0.29, 0, 0.03) zemine değiyor, direk tabanı (−0.03, 0, 0.14), kamera 0.44 m); şasi kutusu x −0.105 … +0.345, inertia ve mesh origin'i kutu merkezinde; LiDAR montaj property'leri; her link'te visual + primitif collision; mesh URI'leri `package://serabot_description/meshes/*.obj` ve `.obj` + `.mtl` dosyaları mevcut, mesh visual'larında `<material>` yok; inertia geçerli; ağırlık merkezi aks–caster arasında; DiffDrive/JointStatePublisher §5 ile birebir.
- `.obj` dosyaları bağımsız okundu: sınır kutuları yukarıdaki gibi, kullanılan her malzeme `.mtl`'de tanımlı.
- `flake8 --max-line-length 99 src/` → temiz.

**Linux — S0, Üye A VM'i (Docker, Lyrical + Gazebo Jetty 10.5.0), primitif model, ADR-017 öncesi (ayrıntı `PROGRESS.md`):**
1. `check_urdf` ✅
2. RViz model görüntüsü ✅
3. SDF + sürtünme: caster `mu` = 0, tekerlek `mu` = 1 ✅ — sabit joint birleştirmesinden sonra da uygulanıyor
4. Gazebo spawn, ileri sürüş ve dönüş; `/odom`, `/tf`, `/joint_states` ✅ — JointStatePublisher `<topic>` parametresi Jetty'de çalışıyor. Yerinde dönüşte gövde ~0.12 m yarıçaplı yay çiziyordu → ADR-017.
5. Mesh yön/renk testi ✅ — `.obj` RViz2 ve Gazebo'da doğru; `glb_yup` sadece RViz2'de, `glb_zup` sadece Gazebo'da doğru → `.obj` + `.mtl` (ADR-015).

**Linux — S1, aynı VM (2026-10-24), ADR-017 + mesh'li model:**
- `scripts/sync_to_vm.sh` → `colcon build --packages-select serabot_description` ✅; `check_urdf` ✅ (`base_footprint` → `base_link` → `camera_mast_link`, `caster_link`, `left/right_wheel_link`); 7 `.obj` + `.mtl` kurulu `share/` altında; `GZ_SIM_RESOURCE_PATH` `install/serabot_description/share` içeriyor.
- **Yerinde dönüş (GUI'siz Gazebo, `empty.sdf`, 0.8 rad/s, ~12 s)** — gerçek konum/yaw `/world/empty/pose/info`'dan, odometri `/odom`'dan; yaw robot durduktan sonra karşılaştırıldı:

  | Tekerlek çarpışması | Koşu | Dönüş | `base_footprint` kayması | `/odom` konum hatası | `/odom` yaw hatası |
  |---|---|---|---|---|---|
  | Silindir (önceki) | 1 / 2 | 471° / 502° | 1.6 / 1.6 mm | 1.6 / 1.6 mm | +50° / +54° (**+10.7%**) |
  | **Küre r = 0.08 (güncel)** | 1 / 2 | 370° / 397° | **0.3 / 0.7 mm** | **~0 / ~0 mm** | +0.5° / +0.4° (**+0.1%**) |

  Ölçüt (konum kayması ve `/odom` konum hatası < 0.02 m) iki durumda da ✅; ADR-017 öncesi ~0.12 m yay çiziyordu. Silindirde gövde odometrinin bildirdiğinden %10.7 fazla dönüyordu (etkin tekerlek aralığı ≈ 0.325 m) → küre seçildi.
- **Düz sürüş (küre, 0.25 m/s, ~6 s):** 1.32 m ileri; yanal sapma 0.0000 m, yön değişimi 0.00°, `/odom` konum hatası 4.9 mm, yaw hatası 0.00° ✅.
  - Ölçüm betiği gerçek konumu `/world/empty/pose/info`'dan, odometriyi `/odom`'dan `gz topic` ile okur; dönerken alınan örneklerde iki okuma arasındaki ~0.4 s yüzünden yaw farkı abartılı görünür, bu yüzden yaw sadece durunca karşılaştırıldı.
- **RViz'de mesh'li model (`display.launch.py`):** ✅ şasi, tekerlekler, caster ve direk mesh'leri doğru yerde ve yönde; `base_footprint` sabit çerçeve, TF etiketleri görünür; log'da hata yok; ~28 fps (llvmpipe). Kamera tomurcuğu ve LiDAR çakılı görünmez — sensör xacro'ları henüz boş (beklenen). **Renkler Blender render'larından belirgin koyu** (toprak neredeyse siyah, saksı koyu bordo) → Açık sorunlar.
- **Gazebo GUI'de mesh'li model (`empty.sdf` + spawn):** ✅ mesh'ler bulunuyor ("Unable to find file" yok), yön doğru, renkler yükleniyor; RViz'den açık ama yine Blender'dan koyu/kahverengimsi.
- Ekran görüntüleri (`VBoxManage controlvm ubuntu screenshotpng`) S1 oturumunda alındı; renk düzeltmesinden sonra rapor için yeniden alınacak.
- **MTL renk düzeltmesi (2026-10-24):** `mesh_kit.export_obj` dışa aktarımdan sonra `.mtl` `Kd` değerlerini doğrusaldan sRGB'ye çeviriyor. Yeniden aktarılan dosyalarda `Kd` tasarım paletiyle birebir (örn. toprak 0.27/0.19/0.14, saksı 0.78/0.39/0.23; önce 0.06/0.03/0.02 ve 0.57/0.13/0.04). Geometri değişmedi (vertex ve normal kümeleri commit'teki `.obj` ile aynı; Blender sadece normal sırasını farklı yazdığı için `.obj`'ler commit'teki haliyle bırakıldı). VM'de `colcon build` ✅, kurulu `chassis.mtl` yeni değerleri içeriyor. - **Doğrusal ve sRGB `Kd` karşılaştırması (VM, 2026-10-24, aynı kamera açıları):** RViz2'de sRGB değerler Blender render'larına çok daha yakın (saksı turuncu-kiremit; doğrusal değerlerde koyu bordo, toprak siyaha yakın). Gazebo Jetty'de ise sRGB değerlerle renkler soluk/pastel; doğrusal değerler daha doygun ve tasarıma daha yakın. Yorum: Gazebo (ogre2, gamma düzeltmeli PBS) MTL rengini doğrusal kabul ediyor, RViz2 (Ogre 1) ekran rengi olarak — `.glb` yön sorununa benzer bir uyuşmazlık. Ekran görüntüleri S1 oturumunda.
- **İki renk seti (2026-10-24, kullanıcı kararı):** `mesh_kit.export_obj(..., linear_dir=...)` her link için `meshes/<link>.obj` + sRGB `.mtl` (RViz2) yazar ve aynı `.obj`'yi Blender'ın doğrusal `.mtl`'iyle `meshes/gazebo/`'ya kopyalar. `properties.xacro`: `<xacro:arg name="gazebo_mesh_colors" default="false"/>` → `mesh_dir` `meshes/` ya da `meshes/gazebo/`.
  - Windows: iki setin `.obj`'leri bayt bayt aynı; Gazebo `Kd` = RViz `Kd`'nin doğrusal karşılığı (7 link, tolerans 2e-4). Statik kontrol üç varyantta tümü geçti (varsayılan → `meshes/*.obj`, `gazebo_mesh_colors:=true` → `meshes/gazebo/*.obj`, `use_mesh_visuals=false` → primitif). `.obj`'ler commit'teki haliyle bırakıldı (Blender yeniden aktarımda sadece normal sırasını değiştiriyor).
  - VM: `colcon build` ✅ (`share/.../meshes/gazebo/` kurulu, 14 dosya); `xacro ... gazebo_mesh_colors:=true` + `check_urdf` ✅; Gazebo'da bu URDF ile robot doygun, tasarıma yakın renklerde ✅ ("Unable to find file" yok). RViz'de varsayılan set (sRGB) önceki ekran görüntüsündeki gibi ✅.

**Tekrar üretme (VM'de, repo kökünden):**

```bash
scripts/sync_to_vm.sh
ssh serabot-vm 'cd serabot_ws && docker/run.sh exec "colcon build --packages-select serabot_description && xacro install/serabot_description/share/serabot_description/urdf/serabot.urdf.xacro > /tmp/serabot.urdf && check_urdf /tmp/serabot.urdf"'
```

RViz (VM masaüstünde): `ros2 launch serabot_description display.launch.py` · test küpü: `model:=test/mesh_test.urdf.xacro`. Gazebo: `gz sim -r empty.sdf` + `gz service -s /world/empty/create ... sdf_filename: "/tmp/serabot.urdf"`. Konteynerde iki Gazebo sunucusu aynı anda çalışırsa (aynı dünya adı) `/odom` ve `/cmd_vel` karışır — başlatmadan önce `ps -eo stat,args | grep gz-sim-mai[n]` ile kontrol edin.

## Açık istekler

- **S2'ye — Gazebo spawn renk seti:** `bringup.launch.py` robot_state_publisher için URDF'i varsayılan argümanlarla (`meshes/`, RViz renkleri), Gazebo'ya spawn edilecek URDF'i `gazebo_mesh_colors:=true` ile üretmeli (`meshes/gazebo/`, Gazebo renkleri). Yani spawn `robot_description` topic'inden değil, ayrı bir xacro çıktısından (`ros_gz_sim create -string` veya `-file`) yapılmalı. Argüman verilmezse model yine çalışır, sadece Gazebo'da renkler soluk olur.
- **S0'a — `INTERFACES.md`:** §6 xacro argümanlarına `gazebo_mesh_colors` (varsayılan `false`; Gazebo'ya spawn edilen URDF için `true`) eklenmesi; §4.1'e "renk seti: `meshes/<link>.obj` + sRGB `.mtl` (RViz2), `meshes/gazebo/<link>.obj` + doğrusal `.mtl` (Gazebo Jetty)" notu. Argüman `properties.xacro`'da tanımlı (ana xacro'da değişiklik gerekmiyor).
- **S0'a — `INTERFACES.md` §4.1 notu:** "Çarpışma: §4'teki boyutlarla primitif geometri" kuralına bir istisna: tekerlek çarpışması küre r = 0.08 (tekerlek genişliği 0.04 değil). Gerekçe ve ölçüm yukarıda (odometri yaw sapması). Robotun çarpışma genişliği 0.52 m — S4'ün dar geçit/engel mesafesi ayarlarında dikkate alınmalı.
- **Sensör sahiplerine (S0 iletir):** görsel mesh'ler hazır — `${mesh_dir}/lidar.obj`, `camera.obj`, `imu.obj` (`mesh_dir` `properties.xacro`'dan; renk setini `gazebo_mesh_colors` seçer; orijinleri kendi link frame'inde: `lidar_link`, `camera_link`, `imu_link`; `origin` 0, `<material>` etiketi yok). Montaj property'leri `../properties.xacro`'da (`lidar_x/y/z`, `imu_x/y/z`, `camera_z`). Primitif yedek için `use_mesh_visuals` property'sine uyulabilir.

## Açık sorunlar

- **İki renk seti bakımı:** `meshes/gazebo/*.obj` `meshes/*.obj` ile aynı olmalı; mesh'ler her zaman `build_serabot.py` ile birlikte üretilmeli (elle tek dosya değiştirilmemeli). RViz'de toprak hâlâ koyu görünüyor — RViz'in tek ve zayıf ışığı (renk değeri doğru).
- **VM ekran kilidi (çözüldü):** kullanıcı GNOME otomatik kilidini ve ekran karartmayı kapattı (`lock-enabled false`, `idle-delay 0`).
- **⚠ Doğrulanacak (Linux) — sensör kendi gövdesini görüyor mu:** LiDAR çakılı ve kamera tomurcuğu sensör noktasını sarıyor. OBJ'de tek/çift taraf bayrağı yok; Gazebo'nun malzemeyi tek taraflı (arka yüz gizli) çizip çizmediği sensörler eklenince görülecek. Üye A `/scan`'de ~0.03–0.05 m'de sabit okuma, Üye B görüntüde yeşil/koyu kaplama olup olmadığını kontrol etmeli. Sorun olursa sensör `visual`'ında pencere boşluğu bırakılır veya `visibility_flags` kullanılır.
- **Rapor görselleri boyutu:** 5 PNG toplam ~8 MB. Repo boyutu sorun olursa JPEG'e çevrilebilir.
