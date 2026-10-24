# Modül S3b — Kamera (Sensör B)

- **Sorumlu:** Üye B · **Faz:** F2 (29 Eki–1 Kas) · **Durum:** Başlamadı
- **Önemli:** Bu modül **Üye B'nin kendi GitHub hesabından** commit'lenir (ders şartı). Üye A'nın oturumları bu dosyaları yazmaz; sadece inceler ve öneri verir.
- **Sahip olunan yollar:** `src/serabot_description/urdf/sensors/camera.xacro`, `src/serabot_bringup/config/bridge/camera.yaml`, `src/serabot_sensors/serabot_sensors/color_detector.py` (+ testi)
- **Bağımlı olduğu:** S1 (`camera_mast_link`), S2 (sensors sistemi, dünyadaki kırmızı ürünler), `INTERFACES.md` §2.3, §2.5, §4
- **Ona bağımlı olanlar:** S4 (opsiyonel TRACK/INSPECT katmanı)

## Görevler

- [ ] `camera.xacro` — `camera_link` + `camera_optical_link` (rpy = -π/2, 0, -π/2), `<gazebo reference="camera_link">` içinde `camera` sensörü (`INTERFACES.md` §2.3, `<gz_frame_id>camera_optical_link`)
- [ ] `config/bridge/camera.yaml` — `/camera/image_raw`, `/camera/camera_info` GZ→ROS
- [ ] Görselleştirme: RViz Image paneli ve/veya `rqt_image_view /camera/image_raw`
- [ ] `color_detector.py` — HSV eşikleme ile kırmızı nesne tespiti → `/camera/target` (`PointStamped`, sözleşme `INTERFACES.md` §2.5) ve `/camera/image_annotated`. Eşikler ROS parametresi; saf işleme fonksiyonu ayrı ve test edilebilir.
- [ ] Doğrulama komutları ve ekran görüntüleri: `ros2 topic hz /camera/image_raw`, görüntü penceresi, tespit kutulu görüntü
- [ ] Rapor için: yerleşim gerekçesi, topic/mesaj tipleri, kanıt ekran görüntüleri

## Tamamlanma kriteri

- `/camera/image_raw` ~15 Hz, `frame_id = camera_optical_link`; görüntüde bitki sıraları ve kırmızı ürünler görünüyor (Linux).
- Kırmızı ürün görüş alanındayken `/camera/target` yayınlanıyor, `point.x` ürün solda iken negatif (Linux).

## Yapılanlar

—

## Doğrulama

—

## Açık istekler (S0'a)

—

## Açık sorunlar

—
