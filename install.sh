#!/usr/bin/env bash
# Set up inkyframe on a Raspberry Pi:   cd ~/inkyframe && bash install.sh
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="${VENV:-$HOME/.virtualenvs/pimoroni}"

echo "→ system packages"
sudo apt-get update -qq
sudo apt-get install -y -qq fonts-dejavu-core python3-venv >/dev/null
for f in fonts-inter fonts-comic-neue; do          # fonts for the Modern and Playful designs
  sudo apt-get install -y -qq "$f" >/dev/null 2>&1 || echo "  (could not install $f – that design falls back to DejaVu)"
done

if [ ! -x "$VENV/bin/python" ]; then
  echo "→ creating Python environment in $VENV"
  python3 -m venv --system-site-packages "$VENV"
fi
echo "→ Python packages (this can take 10+ minutes on a Pi Zero)"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q "inky[rpi]" -r "$DIR/requirements.txt"
cd "$DIR"

echo "→ fonts for the studio designs (Google Fonts, SIL Open Font License)"
"$VENV/bin/python" -m inkyframe.fonts || echo "  (some fonts could not be downloaded – the app can retry later)"

echo "→ service"
sed -e "s#/home/pi/inkyframe#$DIR#g" -e "s#User=pi#User=$USER#" \
    -e "s#/home/pi/.virtualenvs/pimoroni#$VENV#g" "$DIR/inkyframe.service" \
  | sudo tee /etc/systemd/system/inkyframe.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now inkyframe
sudo systemctl restart inkyframe

echo
echo "Done. Web app: http://$(hostname).local:8080  or  http://$(hostname -I | awk '{print $1}'):8080"
echo "Log:          journalctl -u inkyframe -f"
