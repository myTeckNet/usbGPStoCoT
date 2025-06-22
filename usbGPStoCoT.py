import os
import ssl
import socket
import serial
import pynmea2
import uuid
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

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

# === Logging Setup ===
log_dir = "/tmp/gps_logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "usb_gps.log")
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger("GPSLogger")
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

# === CoT XML ===
def create_cot_xml(uid, lat, lon, hae, callsign=CALLSIGN):
    now = datetime.utcnow()
    start = now.isoformat() + "Z"
    stale = (now + timedelta(minutes=2)).isoformat() + "Z"
    return f"""<event version="2.0"
    uid="{uid}"
    type="a-f-G-U"
    how="m-g"
    time="{start}"
    start="{start}"
    stale="{stale}">
    <point lat="{lat}" lon="{lon}" hae="{hae}" ce="9999999.0" le="9999999.0"/>
    <detail>
        <contact callsign="{callsign}"/>
        <remarks>USB GPS position</remarks>
    </detail>
</event>"""

# === GPS Parser ===
def get_gps_data(serial_port=SERIAL_PORT, baudrate=BAUDRATE):
    try:
        with serial.Serial(serial_port, baudrate, timeout=1) as ser:
            while True:
                line = ser.readline().decode(errors='ignore')
                if line.startswith('$GPGGA'):
                    try:
                        msg = pynmea2.parse(line)
                        return float(msg.latitude), float(msg.longitude), float(msg.altitude)
                    except Exception as e:
                        logger.error(f"GPS parse error: {e}")
    except Exception as e:
        logger.error(f"Serial connection error: {e}")
    return None, None, None

# === Transport Senders ===
def send_udp(data, ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            framed = b'\xbf\x00\xbf' + data.encode("utf-8")
            s.sendto(framed, (ip, port))
    except Exception as e:
        logger.error(f"UDP send error: {e}")

def send_tcp(data, ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5) as s:
            framed = b'\xbf\x00\xbf' + data.encode("utf-8")
            s.sendall(framed)
    except Exception as e:
        logger.error(f"TCP send error: {e}")

def open_tls_connection(ip, port):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    if not VERIFY_SERVER_CERT:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    else:
        context.check_hostname = not SKIP_HOSTNAME_VERIFY
        if CA_CERT:
            context.load_verify_locations(cafile=CA_CERT)
    if CLIENT_CERT and CLIENT_KEY:
        context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

    sock = socket.create_connection((ip, port), timeout=5)
    tls_sock = context.wrap_socket(sock, server_hostname=ip)
    return tls_sock

# === Main Loop ===
def main():
    uid = str(uuid.uuid4())
    tls_sock = None

    if PROTOCOL.upper() == "TLS":
        try:
            tls_sock = open_tls_connection(DEST_IP, DEST_PORT)
        except Exception as e:
            logger.error(f"TLS connection failed: {e}")
            return

    while True:
        lat, lon, hae = get_gps_data()
        if None not in (lat, lon, hae):
            cot_xml = create_cot_xml(uid, lat, lon, hae)
            print(cot_xml)

            if PROTOCOL.upper() == "TLS":
                try:
                    framed = b'\xbf\x00\xbf' + cot_xml.encode("utf-8")
                    tls_sock.sendall(framed)
                except Exception as e:
                    logger.error(f"TLS send error: {e}")
                    break  # Optionally reconnect here
            elif PROTOCOL.upper() == "UDP":
                send_udp(cot_xml, DEST_IP, DEST_PORT)
            elif PROTOCOL.upper() == "TCP":
                send_tcp(cot_xml, DEST_IP, DEST_PORT)
            else:
                logger.error(f"Unsupported protocol: {PROTOCOL}")
        else:
            logger.error("Invalid GPS fix.")
        time.sleep(20)

if __name__ == "__main__":
    main()