# İlerleme

Bu dosyayı sadece S0 (yönetici oturum) günceller; modüller kendi durumunu `docs/modules/<modül>.md` içine yazar.

**Son güncelleme:** 2026-11-06

## Takvim

| Faz | Tarih | Çıktı / bitiş kriteri | Durum |
|---|---|---|---|
| F0 Ortam ve iskelet | 24–26 Eki | Repo, `CLAUDE.md`, docs; paket iskeletleri; CI (`colcon build`) | Tamam |
| F1 Robot + dünya | 26–28 Eki | URDF/Xacro, sera dünyası, tek launch; `/cmd_vel` ile hareket — **M1** | Tamam |
| F2 Sensörler | 29 Eki–1 Kas | LiDAR, kamera, IMU entegre; topic'ler okunuyor, görselleştiriliyor — **M2** | Tamam |
| F3 Davranış | 1–3 Kas | Engelden kaçma (+ opsiyonel hedefe yönelme) Gazebo'da çalışıyor — **M3** | Tamam |
| F4 Entegrasyon | 4–5 Kas | Uçtan uca test, ekran görüntüleri, yedek demo videosu, README | Devam — uçtan uca test, README tamam; yedek video ve bazı ekran görüntüleri eksik |
| F5 Rapor | 5–7 Kas | Rapor 7 Kasım'da teslim (son tarih 8 Kasım 23:59) | Devam — taslak: `docs/report/1306220017_1306220032.pdf`; eksik kanıtlar eklenecek, Canvas teslimi bekliyor |
| Sunum | 9 Kas 11:10 | 8 dk sunum + demo, 2 dk soru | — |

**Linux ortamı:** Üye A VM'inde Docker (ADR-016), Üye B dizüstünde WSL2 + Ubuntu 26.04 (DEV_ENVIRONMENT §5). Canlı demo için Üye B'nin dizüstü önerilir (RTF ≈ 0.71).

## Modül durumu

| Modül | Sorumlu | Durum | Not |
|---|---|---|---|
| S0 Yönetici / docs | Üye A | Devam | Sözleşme v0.10; rapor taslağı hazır |
| S1 Robot modeli | Üye A | Büyük ölçüde tamam | ADR-017 uygulandı, konsept B `.obj` mesh'leri bağlı, iki renk seti, tekerlek küre çarpışması; VM'de build, `check_urdf`, yerinde dönüş testi geçti (`943e360`, `b460add`). Kalan: sensörler eklenince kendi gövdesini görme kontrolü |
| S2 Simülasyon | Üye A | Büyük ölçüde tamam | Primitif + süslü sera dünyası (78.7k üçgen), `base.yaml`, tek launch; VM'de tek komutla açılış, sürüş, RViz doğrulandı (`0f57b2f`, `07eee03`). Kalan: launch spawn varsayılanını INTERFACES v0.8'e çekmek; sensörlerle RTF ölçümü |
| S3a LiDAR | Üye A | Tamam (Linux'ta doğrulandı) | `/scan` 10 Hz, mesafeler dünya yerleşimiyle ort. −1 mm hata, öz-görme yok (`86676fc`). Kalan: ekran görüntüsünü `docs/report/sensors/`'a koymak |
| S3b Kamera | Üye B | Tamam (Linux'ta doğrulandı) | `/camera/image_raw` 15 Hz, `color_detector` her karede (`fa169a4`); kamera katmanı testi (`832502d`). Ortam: Üye B WSL2 + Ubuntu 26.04 (DEV_ENVIRONMENT §5). Kalan: RViz/rqt ekran görüntüleri |
| S3c IMU | Ortak | Tamam (Linux'ta doğrulandı) | Entegrasyon Üye A (`930c993`); `imu_monitor` `/imu/rpy` 100 Hz + dönüş grafiği, odometriyle ≤ 1.56° (`c0e4b22`, Üye B). Kalan: rqt_plot ekran görüntüsü |
| S4 Davranış | Üye A (+ Üye B kamera katmanı) | Tamam (Linux'ta doğrulandı) | Çekirdek run3 (`0412a74`). Kamera katmanı + `resume_patrol`, `target_cooldown` 20, `use_camera` launch argümanı (ADR-021, Üye B): 180 s gerçek pozla 21/60 hücre, 7 inceleme, çarpışma yok; 33 test |

## Tamamlananlar

- 2026-10-24 — Proje dökümanı analiz edildi, senaryo (SeraBot), mimari, sensör seti ve plan belirlendi.
- 2026-10-24 — `CLAUDE.md`, `docs/` (REQUIREMENTS, ARCHITECTURE, INTERFACES, DECISIONS, PROGRESS, modül dosyaları) oluşturuldu.
- 2026-10-24 — 5 paketin iskeleti, ana xacro + placeholder makrolar, RViz config (`serabot.rviz`), GitHub Actions CI eklendi. Statik kontroller (xacro, flake8, XML/YAML) Windows'ta geçti; RViz config Linux'ta doğrulanmadı.
- 2026-10-24 — CI yeşil (`6a352e9`): build, xacro + check_urdf, colcon test.
- 2026-10-24 — Mesh formatı `.glb` (yedek `.obj`) olarak belirlendi (ADR-015); S1 Blender 5.2.3'e yerel köprüyle bağlandı.
- 2026-10-24 — S1: primitif robot modeli, `display.launch.py`, konsept B (Saksı) Blender modeli (15.6k üçgen), yön/renk test küpü (`0e7c484`, `4a94476`; CI yeşil). S0 incelemesi: TF ağacı, tekerlek eksenleri ve DiffDrive parametreleri sözleşmeyle uyumlu. S1 açık isteği uygulandı: `.gitignore`'a `*.blend1`.
- 2026-10-24 — **Linux test ortamı hazır (ADR-016):** Üye A'nın VM'inde Docker ile Lyrical + Gazebo Jetty 10.5.0; Claude SSH ile erişiyor (`docs/DEV_ENVIRONMENT.md`). `colcon build` + `colcon test` geçti.
- 2026-10-24 — **S1 Linux doğrulaması (S0 tarafından, VM):** adım 1 `check_urdf` ✅; adım 2 RViz model görüntüsü ✅; adım 3 SDF + sürtünme (caster `mu`=0, tekerlek 1) ✅; adım 4 Gazebo'da spawn, ileri sürüş ve dönüş, `/odom`, `/tf`, `/joint_states` ✅ (yerinde dönüşte gövde ~0.12 m yarıçaplı yay çiziyor — odometri ofseti, aşağıdaki açık konu #7); adım 5 mesh yön/renk testi ✅ → format `.obj` + `.mtl` (ADR-015 sonucu, INTERFACES v0.5).
- 2026-10-24 — S1: ADR-017 uygulandı, `.obj` mesh'ler URDF'e bağlandı, Gazebo/RViz renk setleri, tekerlek küre çarpışması; VM'de doğrulandı (`943e360`, `b460add`). S0: S1 açık istekleri INTERFACES v0.7'ye işlendi (ADR-019).
- 2026-10-26 — Karma sera dünyası kararı (ADR-018, INTERFACES §4.2).
- 2026-10-26 — **M1 (robot + dünya + tek launch) Linux'ta sağlandı.** S2: sera dünyası (primitif çarpışma + Blender süsleri), `base.yaml`, `bringup.launch.py`; VM'de doğrulandı. Gerçek zaman oranı ≈ 0.39 (GUI + RViz, sensörsüz, 30 s ortalama) — süsler etkilemiyor, darboğaz yazılımsal render. S0: S2 istekleri uygulandı (spawn varsayılanı INTERFACES v0.8, `python3-yaml`), konteynere `--init` (öksüz süreç birikmesi).
- 2026-11-02 — Üye B ortamı: WSL2 + Ubuntu 26.04 + Lyrical + Jetty (doğrudan apt, GPU'lu WSLg), RTF ≈ 0.85 (kamerasız).
- 2026-11-04 — **M2 sağlandı:** kamera (`camera.xacro`, `camera.yaml`, `color_detector`) ve `imu_monitor` Linux'ta doğrulandı (`fa169a4`, `c0e4b22`); kamera katmanı Gazebo'da çalışıyor (`832502d`).
- 2026-11-05 — ADR-021 (Üye B, ekip onayıyla): büyük görüntülerde reliable QoS (RViz dahil), `use_camera` ve `headless` launch argümanları, `color_detector.yaml`, `resume_patrol` + `target_cooldown` 20; uçtan uca demo komutu GUI + RViz ile doğrulandı. README kurulum/kullanım yazıldı (R15). Bilinen sorun: Gazebo kapanırken segfault (çalışırken değil).
- 2026-10-27 — S3: LiDAR + IMU entegrasyonu VM'de doğrulandı (`86676fc`, `930c993`). S4: davranış node'u, 26 test, Gazebo'da 3 dk çarpışmasız (`0412a74`). S2: spawn varsayılanı (`da7eac5`). **M3 çekirdeği sağlandı; M2 2/3 (kamera bekliyor).** S0: ADR-020 (davranış parametreleri, `headless`, ortak klasörler), `.flake8`, REQUIREMENTS durumları.
- 2026-11-06 — Rapor taslağı yazıldı, PDF `docs/report/`'a eklendi. Commit geçmişinden Claude satırları kaldırıldı; dokümanlardaki commit hash'leri yeni geçmişe çevrildi.

## Açık konular / riskler

| # | Konu | Sahip | Hedef tarih |
|---|---|---|---|
| 1 | ~~Üye B Linux ortamı~~ — WSL2 + Ubuntu 26.04 hazır | — | ✅ |
| 2 | ~~Üye B bilgileri ve collaborator~~ — Enes Çelik, 1306220032, enescelik00 | — | ✅ |
| 3 | Jetty/Lyrical'da eklenti adları, `gz_frame_id`, camera_info topic'i, teleop `Twist` tipi doğrulaması | S0 | F1 |
| 4 | Commit'lerdeki Claude satırları 2026-11-06'da geçmişten kaldırıldı (kullanıcı kararı); ders yapay zekâ politikasının kontrolü Üye A'da. Üye B klonunu `git fetch origin` + `git reset --hard origin/main` ile güncellemeli | Üye A, Üye B | Teslimden önce |
| 5 | Repo lisansı: `package.xml` Apache-2.0 diyor, LICENSE dosyası yok | Üye A | Teslimden önce |
| 6 | ~~Mesh yön/renk testi~~ — tamam, `.obj` + `.mtl` (ADR-015) | — | ✅ |
| 7 | ~~Odometri ofseti~~ — ADR-017 uygulandı (S1) | — | ✅ |
| 8 | Rapor eksikleri: LiDAR RViz görüntüsü, `ros2 topic hz`/`echo` çıktıları, `rqt_plot` ve `rqt_image_view` pencere görüntüleri | Üye A, Üye B | 7 Kas |
| 9 | Canlı `rqt_plot` IMU grafiği doğrulanmadı; demo komutu açmıyor, ikinci terminalden başlatılmalı | Üye B | 7 Kas |
| 10 | Yedek demo videosu ve sunum provası | Üye A, Üye B | 8 Kas |
