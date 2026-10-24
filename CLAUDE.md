# CLAUDE.md — SeraBot (BIMU4101 Midterm Project)

Bu dosya projede çalışan **tüm Claude Code oturumlarının** ortak bağlamıdır. Her oturum işe başlamadan önce bu dosyayı ve aşağıdaki "Oturum başlangıcı" listesini okur.

## 1. Proje özeti

- **Ders:** BIMU4101 – Introduction to Mobile Robotics, Midterm Project
- **Robot:** SeraBot — sera (greenhouse) bitki sıraları arasında dolaşan, engellerden kaçan, kamerayla olgun (kırmızı) ürünü fark eden diferansiyel sürüşlü mobil robot.
- **Hedef ortam:** Ubuntu 26.04 + **ROS 2 Lyrical** + **Gazebo Jetty** (gz-sim 10).
- **Repo:** https://github.com/anilcay/Mobile-Robotics-Midterm-Project
- **Ekip (2 kişi → en az 3 sensör tipi):**
  - Üye A — anilcay: LiDAR sorumlusu
  - Üye B — (isim TBD): Kamera sorumlusu
  - Ek sensör IMU: ortak sorumluluk
- **Teslim:** Rapor 8 Kasım 2026 23:59 (hedef: 7 Kasım), sunum + canlı demo 9 Kasım 2026 11:10.

Gereksinimlerin tam listesi: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)

## 2. Oturum başlangıcı (her oturum)

1. Bu dosyayı oku.
2. [docs/INTERFACES.md](docs/INTERFACES.md) — topic, frame, mesaj tipi, boyut sözleşmesi (**tek doğru kaynak**).
3. [docs/PROGRESS.md](docs/PROGRESS.md) — genel durum.
4. Kendi modül dosyan: `docs/modules/<modül>.md` — görevler, sahip olunan dosyalar, açık istekler.
5. Gerekirse [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ve [docs/DECISIONS.md](docs/DECISIONS.md).

## 3. Oturumlar ve dosya sahipliği

Birden fazla Claude oturumu **aynı klasörde** çalışır. Çakışmayı önlemek için her dosyanın tek bir sahibi vardır.

| Oturum | Modül dosyası | Sahip olduğu yollar |
|---|---|---|
| S0 Yönetici | — | `CLAUDE.md`, `docs/` (modül dosyaları hariç), `README.md`, `.github/`, `docker/`, `scripts/`, `src/serabot_description/urdf/serabot.urdf.xacro`, `src/serabot_bringup/rviz/`, tüm `package.xml` / `setup.py` / `CMakeLists.txt` iskeletleri |
| S1 Robot modeli | `docs/modules/description.md` | `src/serabot_description/` (yukarıdaki ana xacro ve `urdf/sensors/` hariç) |
| S2 Simülasyon | `docs/modules/simulation.md` | `src/serabot_gazebo/`, `src/serabot_bringup/launch/`, `src/serabot_bringup/config/bridge/base.yaml` |
| S3a LiDAR (Üye A) | `docs/modules/sensor-lidar.md` | `urdf/sensors/lidar.xacro`, `config/bridge/lidar.yaml`, `serabot_sensors/` içindeki lidar dosyaları |
| S3b Kamera (Üye B) | `docs/modules/sensor-camera.md` | `urdf/sensors/camera.xacro`, `config/bridge/camera.yaml`, `serabot_sensors/` içindeki kamera dosyaları |
| S3c IMU (ortak) | `docs/modules/sensor-imu.md` | `urdf/sensors/imu.xacro`, `config/bridge/imu.yaml`, `serabot_sensors/` içindeki imu dosyaları |
| S4 Davranış | `docs/modules/behavior.md` | `src/serabot_behavior/`, `src/serabot_bringup/config/behavior.yaml` |

**Kurallar:**
- Sadece sahibi olduğun dosyaları değiştir. Başka bir dosyada değişiklik gerekiyorsa kendi modül dosyanın **"Açık istekler"** bölümüne yaz ve kullanıcıya bildir; S0 uygular.
- `docs/INTERFACES.md` içindeki bir şeyi (topic adı, frame, mesaj tipi, boyut) **değiştirme**. Değişiklik gerekiyorsa açık istek olarak yaz. Arayüzler sadece S0 tarafından, `DECISIONS.md` kaydıyla değiştirilir.
- Mevcut çalışan kodu gereksiz yere değiştirme. Büyük değişiklikten (dosya silme, yeniden yapılandırma, arayüz değişikliği) önce kullanıcıya bilgi ver ve onay al.
- İş bitince kendi modül dosyanı güncelle (durum, yapılanlar, doğrulama, açık sorunlar). `docs/PROGRESS.md` dosyasını sadece S0 günceller.

## 4. Geliştirme ortamı ve doğrulama

Geliştirme şu an **Windows 10** üzerinde yapılıyor; ROS 2 / Gazebo yerelde **çalıştırılamıyor**. Bu yüzden:

- Kod Ubuntu 26.04 + Lyrical + Jetty hedeflenerek yazılır; Windows'a özel çözüm yazılmaz.
- Yerelde yapılabilen kontroller yapılır:
  - Python sözdizimi: `python -m py_compile <dosya>`
  - Saf mantık testleri (ROS'suz): `python -m pytest src/serabot_behavior/test`
  - Stil: `python -m flake8 --max-line-length 99 src/`
  - Xacro → URDF dönüşümü (urdf klasöründen): `python -c "import sys, xacro; sys.argv=['xacro','serabot.urdf.xacro']; xacro.main()"` — xacro include'ları göreli yazılır, `$(find ...)` kullanılmaz; böylece ROS'suz kontrol edilebilir.
  - Araçlar (`xacro`, `flake8`, `pytest`) Windows'ta `pip install --user` ile kurulu.
- Linux'ta doğrulanamayan her şey modül dosyasında **"Linux'ta doğrulanmadı"** olarak işaretlenir. Asla "çalışıyor" denmez; "derleniyor / testi geçiyor / doğrulanmadı" diye net yazılır.
- GitHub Actions CI (`ros:lyrical` imajı) ile `colcon build` + testler.
- Simülasyon testi **Üye A'nın test VM'inde Docker ile** yapılabilir (ADR-016, `docs/DEV_ENVIRONMENT.md`): `scripts/sync_to_vm.sh` ile kopyala, `ssh serabot-vm 'cd serabot_ws && docker/run.sh exec "<komut>"'` ile çalıştır. VM'e erişimi olmayan oturumlar ve Üye B için: modül dosyasına çalıştırılacak net komutları ve beklenen sonucu yaz (ADR-011).
- VM'de `sudo` gerektiren bir adım varsa kullanıcıya bildir; şifre asla istenmez/girilmez.
- Proje yolu Türkçe karakter ve boşluk içerebilir; shell komutlarında yolları **tırnak içinde** kullan.

## 5. Kodlama kuralları

**Dil:**
- Kod, değişken/fonksiyon adları, kod yorumları, commit mesajları, `README.md`: **İngilizce**.
- `CLAUDE.md` ve `docs/` altı: **Türkçe**.

**Genel:**
- Paket öneki `serabot_`. Node, topic ve parametre adları `snake_case`.
- Topic, frame ve mesaj tipleri yalnızca `docs/INTERFACES.md`'den alınır; koda yeni topic gömülmez.
- Sayısal ayarlar (hız, eşik, açı) koda gömülmez; ROS parametresi olarak tanımlanır ve `config/*.yaml`'de varsayılan değer verilir.
- Tüm node'lar `use_sim_time: true` ile çalışır.

**Python (rclpy):**
- PEP 8, tip ipuçları, kısa docstring'ler.
- Karar/işleme mantığı ROS'tan bağımsız saf fonksiyon/sınıf olarak ayrı modülde (örn. `logic.py`) yazılır; node dosyası sadece ROS bağlantısı (abonelik, yayın, parametre) yapar. Saf mantık için pytest testi yazılır.
- Sensör aboneliklerinde `qos_profile_sensor_data` kullanılır.
- Her node `main()` fonksiyonu ile `setup.py` `entry_points` üzerinden çalıştırılır. Entry point'ler S0 tarafından önceden kayıtlıdır (`color_detector`, `imu_monitor`, `behavior_node`); yeni node gerekiyorsa açık istek yaz.

**URDF/Xacro:**
- Boyutlar ve kütleler `properties.xacro` içinde `xacro:property` olarak tanımlanır; sihirli sayı yok.
- Her link'in `visual`, `collision` ve geçerli `inertial` bloğu olur (inertia makrosu kullanılır).
- Her sensör kendi dosyasında (`urdf/sensors/<sensör>.xacro`) bir xacro makrosu olarak tanımlanır; link, joint ve `<gazebo>` sensör bloğu bu dosyadadır.
- Ana xacro'nun çağırdığı makro adları ve parametreleri sözleşmedir (`INTERFACES.md` §8). S0'ın oluşturduğu `PLACEHOLDER` dosyalarında sadece makro gövdesi değiştirilir.
- Görsel modeller Blender'da hazırlanan mesh'lerdir; çarpışma modelleri primitiftir. Mesh kuralları: `INTERFACES.md` §4.1 (ADR-012).
- Gazebo dünyaları sadece primitif geometri kullanır (internetten Fuel modeli indirilmez).

**Launch:**
- Python launch dosyaları (`*.launch.py`). Argümanlar `DeclareLaunchArgument` ile, açıklamalı.

## 6. Git kuralları

- Ana dal `main`. Paylaşılan klasörde **branch değiştirme** (diğer oturumları etkiler).
- Commit ve push **sadece kullanıcı isteyince** yapılır.
- Sadece kendi dosyalarını stage'le: `git add <yol>` — `git add -A` / `git add .` kullanma.
- Commit mesajı formatı: `[modül] kısa açıklama` — modüller: `docs`, `description`, `simulation`, `lidar`, `camera`, `imu`, `behavior`, `ci`. Örnek: `[lidar] add gpu_lidar sensor macro and bridge config`
- Üye B (kamera) kendi işini kendi GitHub hesabından commit'ler (ders şartı: commit geçmişi kişisel katkıyı göstermeli). Üye B'nin dosyalarını başka oturum yazmaz.
- `build/`, `install/`, `log/` asla commit'lenmez.
