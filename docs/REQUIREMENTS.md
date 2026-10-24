# Gereksinimler ve İzlenebilirlik

Kaynak: *BIMU4101 – Introduction to Mobile Robotics, Midterm Project* dökümanı.
Ekip 2 kişi olduğu için en az **3 farklı sensör tipi** gerekir.

Durum değerleri: `Başlamadı` · `Devam` · `Statik doğrulandı` (Windows'ta derleme/test) · `Linux'ta doğrulandı` · `Tamam`

## Robot

| ID | Gereksinim | Kabul kriteri / kanıt | Modül | Durum |
|---|---|---|---|---|
| R1 | Belirli bir görev/senaryo için özgün mobil robot; sürüş sistemi, boyut ve sensör yerleşimi gerekçelendirilmeli | Raporda SeraBot senaryosu ve tasarım gerekçesi; hazır model (TurtleBot vb.) kullanılmıyor | S1, Rapor | Başlamadı |
| R2 | URDF/Xacro: şasi, en az iki tahrikli tekerlek, gerekli caster | `xacro` hatasız; RViz'de model ve TF ağacı doğru | S1 | Başlamadı |
| R3 | Sürüş tipine uygun Gazebo eklentisi; `/cmd_vel` ile hareket | `ros2 topic pub /cmd_vel ...` veya teleop ile robot Gazebo'da hareket ediyor | S1, S2 | Başlamadı |
| R4 | Engel içeren Gazebo dünyası, robot spawn | Sera dünyası açılıyor, robot spawn oluyor | S2 | Başlamadı |
| R5 | **Tek launch dosyası**: dünya + spawn + RViz | `ros2 launch serabot_bringup bringup.launch.py` hepsini açıyor | S2 | Başlamadı |
| R6 | Boyut, yerleşim ve görünüm ekibe ait (kopya sayılmaması) | Özgün boyutlar `properties.xacro`'da; raporda çizim/ekran görüntüsü | S1 | Başlamadı |

## Sensörler

| ID | Gereksinim | Kabul kriteri / kanıt | Modül | Durum |
|---|---|---|---|---|
| R7 | En az 3 farklı sensör tipi (odometri, joint_states, ground-truth sayılmaz) | LiDAR + kamera + IMU robot modelinde | S3a/b/c | Başlamadı |
| R8 | Her sensörün verisi ROS 2'den okunabiliyor | `ros2 topic echo/hz` çıktıları: `/scan`, `/camera/image_raw`, `/imu` | S3a/b/c | Başlamadı |
| R9 | Her sensör uygun şekilde görselleştiriliyor | RViz LaserScan, RViz Image / rqt_image_view, rqt_plot (IMU) ekran görüntüleri | S3a/b/c | Başlamadı |
| R10 | Her öğrenci en az bir sensörden sorumlu; ek sensörün sorumlusu açıkça belirtilmiş | Raporda katkı tablosu: A=LiDAR, B=Kamera, IMU=ortak | Rapor | Başlamadı |

## Davranış

| ID | Gereksinim | Kabul kriteri / kanıt | Modül | Durum |
|---|---|---|---|---|
| R11 | En az bir sensöre abone olup robot davranışını belirleyen Python/C++ ROS 2 node'u | `serabot_behavior` node'u `/scan` (+`/imu`) okuyup `/cmd_vel` yayınlıyor; engelden kaçma Gazebo'da görülüyor | S4 | Başlamadı |
| R12 | Sunumda giriş topic'leri, mesaj tipleri, karar kuralı ve çıkış komutu açıklanabilmeli | `docs/modules/behavior.md` içinde durum diyagramı ve karar kuralı | S4 | Başlamadı |

## Teslim

| ID | Gereksinim | Kabul kriteri / kanıt | Modül | Durum |
|---|---|---|---|---|
| R13 | Kod public GitHub reposunda | https://github.com/anilcay/Mobile-Robotics-Midterm-Project | S0 | Devam |
| R14 | Her üye kendi işini commit'liyor; geçmiş katkıyı yansıtıyor | Üye A ve Üye B'nin kendi commit'leri | Tümü | Başlamadı |
| R15 | Repo çalıştırmak için gereken her şeyi içeriyor; README'de kurulum ve çalıştırma | Temiz bir Ubuntu 26.04'te README adımlarıyla çalışıyor | S0 | Başlamadı |
| R16 | Rapor `studentAID_studentBID.pdf`, Canvas'a tek teslim — **8 Kasım 2026 23:59** | İsimler, numaralar, repo linki, tasarım, sensörler (topic/mesaj tipi, kanıt), katkı tablosu, paket/node açıklamaları, simülasyon sonuçları | Rapor | Başlamadı |
| R17 | Sunum 9 Kasım 2026 11:10, 8 dk + 2 dk soru; her üye kendi katkısını anlatıyor | Prova yapıldı | Tümü | Başlamadı |
| R18 | Canlı demo: hareket, tüm sensör verileri, görselleştirme, davranış node'u; **yedek demo videosu** | Video kaydı repoda veya bağlantı olarak hazır | Tümü | Başlamadı |

## Ortam notu

Değerlendirme ROS 2 Lyrical + Gazebo Jetty ile yapılır. Farklı sürüm kullanılırsa raporda belirtilmeli.
