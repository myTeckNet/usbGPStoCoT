# 🛰️ USB GPS to TAK CoT Transmitter

This Python script captures real-time GPS data from a USB-connected receiver, formats it as CoT (Cursor on Target) XML, and transmits it over a persistent TLS connection using **TAK Protocol v1**. It’s designed for field-ready deployments like Raspberry Pi nodes feeding into TAK servers.

---

## ⚙️ Features

- Reads NMEA sentences from a USB GPS (e.g. `$GPGGA`)
- Formats location as CoT 2.0 XML with callsign and remarks
- Frames messages with TAK Protocol v1 header (`0xBF 0x00 0xBF`)
- Maintains a persistent TLS connection to reduce overhead
- Configurable via Python constants
- systemd service support for auto-start on boot
- Compatible with TAK Server (8089/TLS + XML)

---

## 📦 Requirements

- Python 3.7+
- USB GPS device (NMEA compatible)
- `pyserial`, `pynmea2`
- Client TLS certificate, private key, and CA bundle

### Install dependencies:

```bash
pip install pyserial pynmea2
```

### Installation:
```
git clone https://github.com/myTeckNet/usbGPStoCoT.git ./usbGPStoCot && cd usbGPStoCot
```
---

## 🚀 Usage
```bash
python3 usbGPStoCoT.py
```
The script reads from the GPS, builds a CoT XML message, frames it, and sends it over TLS every 20 seconds.

---

## 🛠️ Configuration

Inside `usbGPStoCot.py`, adjust
```bash
# === Config ===
DEST_IP = "takserver.ip"    # Change this to your TAK server IP or hostname
DEST_PORT = 8089    # 8087 = UDP, 8088 = TCP, 8089 = TLS
PROTOCOL = "TLS"    # Options: "UDP", "TCP", "TLS"
SERIAL_PORT = "/dev/ttyUSB0" # Change this to your USB GPS device path
BAUDRATE = 4800 # Common baud rate for GPS devices
CALLSIGN = "GPS Receiver"   # Change this to your desired callsign
CLIENT_CERT = "/path/to/cert/client_cert.pem"   # Path to your client certificate
CLIENT_KEY = "/path/to/cert/client_key_nopass.key"  # Path to your client private key
CA_CERT     = "/path/to/cert/ca.pem"    # Path to your CA certificate for server verification
VERIFY_SERVER_CERT = True   # Still verifies the cert chain
SKIP_HOSTNAME_VERIFY = True # Set this to True to ignore CN/SAN mismatch
```

The certificate key is protected by a password before using, we need to remove this password from the certificate key file.  Replace client_cert.key with the target client certificate key file path or name and the out file.
```bash
openssl rsa -in client_cert.key -out client_key_nopass.key
```

---

## 🧩 systemd Service (Optional)

### 1. Edit and save the service file as `usbgpstocot.service`:
```bash
[Unit]
Description=USB GPS CoT Transmitter
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/script/usbGPStoCoT.py
WorkingDirectory=/path/to/script
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. Update the `ExecStart` and `WorkingDirectory` file paths to match your environment.

### 3. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable usbgpstocot.service
sudo systemctl start usbgpstocot.service
```

### 4. Monitor the service output for errors
```bash
journalctl -u usbgpstocot -f
```

---

## 📁 Suggested Directory Layout
```
usbGPStoCot/
├── usbGPStoCot.py
├── client_cert.pem
├── client_key_nopass.key
├── ca.pem
└── uusbgpstocot.service
```