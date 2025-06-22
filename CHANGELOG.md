# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Initial support for TAK Protocol v1 (framed XML over TLS)
- Persistent TLS connection for reduced overhead
- CoT generation from USB GPS (NMEA `$GPGGA`) with unique UID per session
- systemd service unit for automatic startup
- Logging system with rotating logs to file

---

## [1.0.0] - 2024-06-21

### Added
- First stable release of USB GPS CoT Transmitter