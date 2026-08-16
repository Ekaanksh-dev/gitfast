# Changelog

All notable changes to gitfast are documented here.

---

## [1.0.0] - 2024

### Added

- TIER 1 shortcuts — gs, gc, gcp, gpl
- TIER 2 shortcuts — gb, gnb, gsw, gm, gl, gll, gd, gdf, gcl
- TIER 3 shortcuts — gundo, gundo2, gsave, gpop, gstashes,
                     gdrop, gsquash, gabort, gnuke
- TIER 4 shortcuts — gf, gtag, gtags, gwho, greflog,
                     gshow, gclean, gremotes
- Auto merge conflict resolver — gmerge
- Interactive conflict resolver — gmerge -i
- Conflict strategies — smart, ours, theirs, longer
- Conflict backup system — auto backup before resolving
- Auto push error resolver — fixes rejected push automatically
- Token manager — gtoken setup/test/refresh/revoke/info
- SSH setup — gsetup_ssh
- Credential helper — gsetup_creds
- HTTPS to SSH converter — ghttps_to_ssh
- Shell support — bash, zsh, fish, powershell
- OS support — Ubuntu, Arch, Fedora, macOS, WSL2, Git Bash, Windows
- Auto OS detection
- Auto shell detection
- Secure token storage — Keychain, GNOME Keyring, Windows Credential Manager
- Token expiry checker — warns 14 days before expiry
- Auto updater — gitfast update
- Clean uninstaller — gitfast uninstall

### Technical

- Zero external dependencies — pure Python stdlib only
- Works on Python 3.7+
- Works on any OS with netrc fallback
- MIT License
