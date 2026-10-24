# Modül S1 — Robot Modeli (`serabot_description`)

- **Sorumlu:** Üye A · **Faz:** F1 (26–28 Eki) · **Durum:** Başlamadı
- **Sahip olunan yollar:** `src/serabot_description/` — ana `urdf/serabot.urdf.xacro` (S0) ve `urdf/sensors/` (sensör sahipleri) hariç
- **Bağımlı olduğu:** `INTERFACES.md` §3 (frame'ler), §4 (boyutlar), §5 (eklentiler)
- **Ona bağımlı olanlar:** S2 (spawn), S3a/b/c (montaj linkleri), S4 (tekerlek geometrisi)

## Çalışma yöntemi

Görsel model **Blender'da** (Blender MCP bağlantısıyla) hazırlanır; çarpışma modeli primitif kalır (ADR-012). Mesh kuralları: `INTERFACES.md` §4.1. Önce primitif görselli çalışan URDF yapılır, mesh'ler hazır oldukça `visual` blokları mesh'e çevrilir — böylece S2 ve sensör modülleri mesh'leri beklemez.

## Görevler

- [ ] `urdf/properties.xacro` — tüm boyut/kütle sabitleri (`INTERFACES.md` §4)
- [ ] `urdf/inertial_macros.xacro` — kutu, silindir, küre inertia makroları
- [ ] `urdf/chassis.xacro` — `base_footprint`, `base_link`, şasi görseli (özgün görünüm: sera yeşili gövde, ön tampon şeridi vb.)
- [ ] `urdf/wheels.xacro` — sol/sağ tekerlek makrosu (`continuous`), caster (sürtünmesiz küre)
- [ ] `urdf/camera_mast.xacro` — `camera_mast_link` (direk); kamera sensörü değil, sadece montaj noktası
- [ ] `urdf/gazebo_drive.xacro` — DiffDrive + JointStatePublisher eklentileri, tekerlek sürtünme (`mu1/mu2`) ayarları
- [ ] `urdf/materials.xacro` — renkler (RViz + Gazebo)
- [ ] Blender tasarımı: sera temalı özgün gövde (konsept → onay → modelleme), link başına mesh dışa aktarımı, `meshes/source/serabot.blend`
- [ ] Mesh formatının RViz2 ve Gazebo'da renkleriyle yüklendiğini doğrula (Üye B'nin VM'i), `visual` bloklarını mesh'e çevir
- [ ] Rapor için tasarım görselleri (Blender render, ön/yan/üst görünüş)
- [ ] `launch/display.launch.py` — robot_state_publisher + joint_state_publisher_gui + RViz (`rviz/model.rviz`)
- [ ] Ana xacro'ya eklenmesi gereken include'ları "Açık istekler"e yaz (ana xacro S0'a ait)

## Tamamlanma kriteri

- `xacro serabot.urdf.xacro` hatasız URDF üretiyor (Windows'ta statik kontrol).
- `check_urdf` hatasız; TF ağacı `ARCHITECTURE.md` §4 ile birebir (Linux).
- Gazebo'da robot yere düzgün oturuyor, devrilmiyor; `/cmd_vel` ile ileri gidip dönüyor (S2 ile birlikte, Linux).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
