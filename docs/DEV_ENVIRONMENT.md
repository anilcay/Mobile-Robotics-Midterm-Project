# Geliştirme ve Test Ortamı

Proje hedefi Ubuntu 26.04 + ROS 2 Lyrical + Gazebo Jetty'dir (ADR-001). Bu belge, bu ortamın elde olmayan makinelerde nasıl kurulduğunu anlatır.

## 1. Seçenekler

| Ortam | Kim | Nasıl |
|---|---|---|
| Ubuntu 26.04 (yerel/VM) | Üye B (önerilen) | ROS 2 Lyrical + `ros-lyrical-ros-gz` doğrudan apt ile |
| Docker konteyneri | Üye A'nın Ubuntu 20.04 VM'i, Ubuntu 26.04 olmayan her Linux | `docker/` altındaki imaj (ADR-016) |
| GitHub Actions | Herkes (otomatik) | `ros:lyrical` konteynerinde build + test (ADR-014) |

## 2. Docker ortamı

İmaj `ros:lyrical` tabanlıdır; `ros_gz` (Gazebo Jetty), RViz2, xacro, teleop, rqt araçları ve test araçlarını içerir. Repo kökü konteynerde `/ws` olarak bağlanır ve colcon workspace'idir. Konteyner kullanıcısı host kullanıcısıyla aynı UID'ye sahiptir; `build/`, `install/`, `log/` host kullanıcısına ait olur.

Gereksinim: Docker kurulu ve kullanıcı `docker` grubunda; X11 masaüstü oturumu (GUI için).

```bash
docker/run.sh build                 # imajı derle (ilk sefer, ~birkaç GB indirme)
docker/run.sh shell                 # konteynerde etkileşimli kabuk
docker/run.sh exec "colcon build"   # tek komut (ROS ve workspace kaynaklanmış olarak)
docker/run.sh stop                  # konteyneri kaldır
```

GUI uygulamaları (Gazebo, RViz) host'un X sunucusunu kullanır (`DISPLAY`, varsayılan `:0`). Gazebo grafik hatası verirse yazılımsal render:

```bash
docker/run.sh stop && SERABOT_SOFTWARE_GL=1 docker/run.sh start
```

## 3. Üye A'nın test VM'i (Claude erişimi)

- VirtualBox VM `ubuntu`: Ubuntu 20.04, 4 GB RAM, 4 CPU, NAT. ROS 2 Lyrical doğrudan kurulamadığı için Docker ortamı kullanılır.
- SSH: VirtualBox NAT yönlendirmesi `127.0.0.1:2222 → VM:22` (sadece host'tan erişilir), anahtar `~/.ssh/serabot_vm`, Windows `~/.ssh/config` içinde `Host serabot-vm`.
- VM'deki workspace `~/serabot_ws` bir git klonu **değildir**; Windows'taki çalışma ağacı `scripts/sync_to_vm.sh` ile kopyalanır (commit'lenmemiş işler de test edilebilsin diye).
- Claude `sudo` şifresi girmez; `sudo` gereken adımlar VM terminaline yazılır, şifreyi kullanıcı girer.
- Ekran görüntüsü (Windows'tan): `VBoxManage controlvm ubuntu screenshotpng <dosya>`.

Tipik test döngüsü (Windows Git Bash'ten):

```bash
scripts/sync_to_vm.sh
ssh serabot-vm 'cd serabot_ws && docker/run.sh exec "colcon build && colcon test && colcon test-result"'
```

## 4. Doğrulanmış durum ve bilinen notlar (2026-10-24)

- İmaj: `serabot-dev:lyrical` (~4 GB), Gazebo **Jetty 10.5.0**, OpenGL: `llvmpipe` (yazılımsal, VM'de 3D kapalı). `colcon build` + `colcon test` geçiyor.
- RViz2 ~20–30 fps; Gazebo GUI ile gerçek zaman oranı ~%80–85, GUI'siz sürüşte ~%60–75 ölçüldü (sensörler eklenince düşebilir).
- VM ekranı 1400×1050'ye alındı (`xrandr -s 1400x1050`; yeniden başlatınca 800×600'e dönebilir).
- `package://` mesh'leri için workspace mutlaka kaynaklanmalı (`source /ws/install/setup.bash`); `docker/run.sh exec` bunu yapar.
- Gazebo'nun ilk açılışı uzun sürebilir / ilk denemede takılabilir; takılırsa sunucu ve GUI'yi ayrı başlatın: `gz sim -s -r <world>` ve `gz sim -g`.
- Konteyner içinde `pkill -f <desen>` kullanırken desen kendi komut satırınızla eşleşmesin (örn. `pkill -f "^rviz2"`).
- Uzun işler (imaj derleme vb.) SSH oturumuna bağlı çalıştırılmamalı: `setsid nohup ... &`.
- VM ekranı kilitlenirse GUI görüntüsü alınamaz; kilidi kullanıcı açar. Otomatik kilit/ekran karartma kapalı olmalı (VM ayarı, kullanıcı yapar).
- Lyrical'da `ros2 bag record` topic'leri `--topics` ile ister (S4).
- Arka planda (betikten) başlatılan `ros2 launch` / `ros2 bag` SIGINT'i yok sayılmış olarak devralır → `kill -INT` etkisiz, bag `metadata.yaml`'sız kalır. Çözüm: SIGINT'i varsayılana çevirip exec etmek; öksüz süreçleri `pkill -TERM -f "^/opt/ros/lyrical/(lib/robot_state_publisher|lib/ros_gz_bridge|opt/gz_sim_vendor)"` ile kapatmak (S2, S4).
- Gazebo sunucusu nadiren hiç açılmıyor (`ros_gz_sim create` sürekli "Requesting list of world names"; bir kez 18 dk). Test betikleri ilk pozu ~120 s bekleyip yeniden başlatmalı (S4).
- Gerçek zaman oranı (S3 ölçümü, sensörlerle): GUI + RViz ≈ 0.38; GUI'siz + RViz ≈ 0.48; ikisi de kapalı ≈ 0.90. Sensörlerin etkisi ölçülemeyecek kadar küçük; darboğaz yazılımsal render'lı GUI'ler.
- Simülasyon test/ölçüm betikleri: `scripts/sim/` (bkz. CLAUDE.md sahiplik notu).
