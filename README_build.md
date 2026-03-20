# How to build AmbieZ.exe

## Requirements
- Windows 10/11
- Python 3.10+ (download from https://python.org — check "Add to PATH" during install)

## Steps

1. Put these files in the **same folder** as `AmbieZ.py`:
   - `AmbieZ.spec`
   - `build_AmbieZ.bat`

2. Double-click **`build_AmbieZ.bat`**

3. Wait ~2 minutes. The finished EXE will appear at:
   ```
   dist\AmbieZ.exe
   ```

4. Copy `AmbieZ.exe` anywhere you like — it runs without Python installed.

---

## Manual build (if the bat fails)

Open a terminal in the project folder and run:

```
pip install pyinstaller PySide6 opencv-python-headless numpy mss
pyinstaller AmbieZ.spec --clean --noconfirm
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `python not found` | Re-install Python and tick "Add to PATH" |
| App crashes on launch | Run `AmbieZ.exe` from a terminal to see the error |
| Antivirus flags the EXE | This is a false positive — PyInstaller-packed apps trigger AVs. Add an exclusion. |
| App is slow to start | Normal — PyInstaller single-file EXEs unpack to a temp folder first |
