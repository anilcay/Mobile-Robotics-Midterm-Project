# İlerleme

Bu dosyayı sadece S0 (yönetici oturum) günceller; modüller kendi durumunu `docs/modules/<modül>.md` içine yazar.

**Son güncelleme:** 2026-10-26

## Takvim

| Faz | Tarih | Çıktı / bitiş kriteri | Durum |
|---|---|---|---|
| F0 Ortam ve iskelet | 24–26 Eki | Repo, `CLAUDE.md`, docs; paket iskeletleri; CI (`colcon build`) | Devam |
| F1 Robot + dünya | 26–28 Eki | URDF/Xacro, sera dünyası, tek launch; `/cmd_vel` ile hareket — **M1** | Başlamadı |
| F2 Sensörler | 29 Eki–1 Kas | LiDAR, kamera, IMU entegre; topic'ler okunuyor, görselleştiriliyor — **M2** | Başlamadı |
| F3 Davranış | 1–3 Kas | Engelden kaçma (+ opsiyonel hedefe yönelme) Gazebo'da çalışıyor — **M3** | Başlamadı |
| F4 Entegrasyon | 4–5 Kas | Uçtan uca test, ekran görüntüleri, yedek demo videosu, README | Başlamadı |
| F5 Rapor | 5–7 Kas | Rapor 7 Kasım'da teslim (son tarih 8 Kasım 23:59) | Başlamadı |
| Sunum | 9 Kas 11:10 | 8 dk sunum + demo, 2 dk soru | — |

**Linux ortamı:** Üye A VM'inde Docker ile hazır (ADR-016). Üye B kendi ortamını en geç 30 Ekim'de kurmalı (kamera geliştirmesi).

## Modül durumu

| Modül | Sorumlu | Durum | Not |
|---|---|---|---|
| S0 Yönetici / docs | Üye A | Devam | Docs v0.1 hazır |
| S1 Robot modeli | Üye A | Büyük ölçüde tamam | ADR-017 uygulandı, konsept B `.obj` mesh'leri bağlı, iki renk seti, tekerlek küre çarpışması; VM'de build, `check_urdf`, yerinde dönüş testi geçti (`708aa3d`, `fb8286b`). Kalan: sensörler eklenince kendi gövdesini görme kontrolü |
| S2 Simülasyon | Üye A | Büyük ölçüde tamam | Primitif + süslü sera dünyası (78.7k üçgen), `base.yaml`, tek launch; VM'de tek komutla açılış, sürüş, RViz doğrulandı (`07c19ff`, `df593b5`). Kalan: launch spawn varsayılanını INTERFACES v0.8'e çekmek; sensörlerle RTF ölçümü |
| S3a LiDAR | Üye A | Başlamadı | |
| S3b Kamera | Üye B | Başlamadı | Üye B: Ubuntu VM |
| S3c IMU | Ortak | Başlamadı | |
| S4 Davranış | Üye A | Başlamadı | |

## Tamamlananlar

- 2026-10-24 — Proje dökümanı analiz edildi, senaryo (SeraBot), mimari, sensör seti ve plan belirlendi.
- 2026-10-24 — `CLAUDE.md`, `docs/` (REQUIREMENTS, ARCHITECTURE, INTERFACES, DECISIONS, PROGRESS, modül dosyaları) oluşturuldu.
- 2026-10-24 — 5 paketin iskeleti, ana xacro + placeholder makrolar, RViz config (`serabot.rviz`), GitHub Actions CI eklendi. Statik kontroller (xacro, flake8, XML/YAML) Windows'ta geçti; RViz config Linux'ta doğrulanmadı.
- 2026-10-24 — CI yeşil (`2c66c08`): build, xacro + check_urdf, colcon test.
- 2026-10-24 — Mesh formatı `.glb` (yedek `.obj`) olarak belirlendi (ADR-015); S1 Blender 5.2.3'e yerel köprüyle bağlandı.
- 2026-10-24 — S1: primitif robot modeli, `display.launch.py`, konsept B (Saksı) Blender modeli (15.6k üçgen), yön/renk test küpü (`9ba0913`, `e343019`; CI yeşil). S0 incelemesi: TF ağacı, tekerlek eksenleri ve DiffDrive parametreleri sözleşmeyle uyumlu. S1 açık isteği uygulandı: `.gitignore`'a `*.blend1`.
- 2026-10-24 — **Linux test ortamı hazır (ADR-016):** Üye A'nın VM'inde Docker ile Lyrical + Gazebo Jetty 10.5.0; Claude SSH ile erişiyor (`docs/DEV_ENVIRONMENT.md`). `colcon build` + `colcon test` geçti.
- 2026-10-24 — **S1 Linux doğrulaması (S0 tarafından, VM):** adım 1 `check_urdf` ✅; adım 2 RViz model görüntüsü ✅; adım 3 SDF + sürtünme (caster `mu`=0, tekerlek 1) ✅; adım 4 Gazebo'da spawn, ileri sürüş ve dönüş, `/odom`, `/tf`, `/joint_states` ✅ (yerinde dönüşte gövde ~0.12 m yarıçaplı yay çiziyor — odometri ofseti, aşağıdaki açık konu #7); adım 5 mesh yön/renk testi ✅ → format `.obj` + `.mtl` (ADR-015 sonucu, INTERFACES v0.5).
- 2026-10-24 — S1: ADR-017 uygulandı, `.obj` mesh'ler URDF'e bağlandı, Gazebo/RViz renk setleri, tekerlek küre çarpışması; VM'de doğrulandı (`708aa3d`, `fb8286b`). S0: S1 açık istekleri INTERFACES v0.7'ye işlendi (ADR-019).
- 2026-10-26 — Karma sera dünyası kararı (ADR-018, INTERFACES §4.2).
- 2026-10-26 — **M1 (robot + dünya + tek launch) Linux'ta sağlandı.** S2: sera dünyası (primitif çarpışma + Blender süsleri), `base.yaml`, `bringup.launch.py`; VM'de doğrulandı. Gerçek zaman oranı ≈ 0.39 (GUI + RViz, sensörsüz, 30 s ortalama) — süsler etkilemiyor, darboğaz yazılımsal render. S0: S2 istekleri uygulandı (spawn varsayılanı INTERFACES v0.8, `python3-yaml`), konteynere `--init` (öksüz süreç birikmesi).

## Açık konular / riskler

| # | Konu | Sahip | Hedef tarih |
|---|---|---|---|
| 1 | Üye B'nin Linux ortamı (Ubuntu 26.04 önerilir; Docker yedek) — kamera geliştirmesi için. Simülasyon testi artık Üye A VM'inde de yapılabiliyor (ADR-016) | Üye B | 30 Eki |
| 2 | Üye B'nin adı, öğrenci no, GitHub hesabı; repoya collaborator olarak eklenmesi | Üye A | 26 Eki |
| 3 | Jetty/Lyrical'da eklenti adları, `gz_frame_id`, camera_info topic'i, teleop `Twist` tipi doğrulaması | S0 | F1 |
| 4 | Commit'lerdeki Claude "Co-Authored-By" satırının ders yapay zekâ politikasına uygunluğu | Üye A | F1 |
| 5 | Repo lisansı | Üye A | F0 |
| 6 | ~~Mesh yön/renk testi~~ — tamam, `.obj` + `.mtl` (ADR-015) | — | ✅ |
| 7 | ~~Odometri ofseti~~ — ADR-017 uygulandı (S1) | — | ✅ |
