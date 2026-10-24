# İlerleme

Bu dosyayı sadece S0 (yönetici oturum) günceller; modüller kendi durumunu `docs/modules/<modül>.md` içine yazar.

**Son güncelleme:** 2026-10-24

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

**Kritik tarih:** En geç **30 Ekim**'de Üye B'nin sanal makinesinde Ubuntu 26.04 + Lyrical + Jetty kurulu ve Gazebo çalışıyor olmalı (ADR-011).

## Modül durumu

| Modül | Sorumlu | Durum | Not |
|---|---|---|---|
| S0 Yönetici / docs | Üye A | Devam | Docs v0.1 hazır |
| S1 Robot modeli | Üye A | Başlamadı | |
| S2 Simülasyon | Üye A | Başlamadı | |
| S3a LiDAR | Üye A | Başlamadı | |
| S3b Kamera | Üye B | Başlamadı | Üye B: Ubuntu VM |
| S3c IMU | Ortak | Başlamadı | |
| S4 Davranış | Üye A | Başlamadı | |

## Tamamlananlar

- 2026-10-24 — Proje dökümanı analiz edildi, senaryo (SeraBot), mimari, sensör seti ve plan belirlendi.
- 2026-10-24 — `CLAUDE.md`, `docs/` (REQUIREMENTS, ARCHITECTURE, INTERFACES, DECISIONS, PROGRESS, modül dosyaları) oluşturuldu.
- 2026-10-24 — 5 paketin iskeleti, ana xacro + placeholder makrolar, RViz config (`serabot.rviz`), GitHub Actions CI eklendi. Statik kontroller (xacro, flake8, XML/YAML) Windows'ta geçti; RViz config Linux'ta doğrulanmadı.

## Açık konular / riskler

| # | Konu | Sahip | Hedef tarih |
|---|---|---|---|
| 1 | Üye B'nin VM'inde Linux ortamı (3D hızlandırma açık) — simülasyon testi ve canlı demo için gerekli | Üye B | 30 Eki |
| 2 | Üye B'nin adı, öğrenci no, GitHub hesabı; repoya collaborator olarak eklenmesi | Üye A | 26 Eki |
| 3 | Jetty/Lyrical'da eklenti adları, `gz_frame_id`, camera_info topic'i, teleop `Twist` tipi doğrulaması | S0 | F1 |
| 4 | Commit'lerdeki Claude "Co-Authored-By" satırının ders yapay zekâ politikasına uygunluğu | Üye A | F1 |
| 5 | Repo lisansı | Üye A | F0 |
| 6 | Blender mesh formatının (DAE/glTF/OBJ) RViz2 + Gazebo Jetty uyumu | S1 + Üye B | F1 |
