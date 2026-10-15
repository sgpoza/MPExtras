#!/bin/bash
# Mario Party 4 - DX Patcher (macOS/Linux port of patch.bat)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VERSION="1.05.3"

# tools/pyisotools.exe and tools/dolphintool.exe are Windows binaries and can't
# run on macOS. pyisotools also ships as a real Python package with the same
# CLI, so we use that instead. dolphintool has no macOS build, so RVZ
# conversion falls back to a manual step via Dolphin's GUI (see below).
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required but was not found. Install Python 3 and try again."
    exit 1
fi
VENV_DIR="tools/.venv"
if [ ! -x "$VENV_DIR/bin/python3" ]; then
    echo "Setting up pyisotools (one-time setup)..."
    python3 -m venv "$VENV_DIR" || { echo "Failed to create venv."; exit 1; }
    "$VENV_DIR/bin/pip" install -q pyisotools || { echo "Failed to install pyisotools."; exit 1; }
fi
PYISOTOOLS=("$VENV_DIR/bin/python3" -m pyisotools)

has_working_dolphintool() {
    [ -x "tools/dolphintool" ] && file "tools/dolphintool" 2>/dev/null | grep -q "Mach-O"
}

echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
echo "Mario Party 4 - DX Patcher!"
echo "How do you wish to export your game."
echo
echo "1: RVZ (Recommended for Dolphin)"
echo "2: ISO (Recommended for SwissGC)"
echo "3: Exit Patcher"
echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="

PATCHER=""
while true; do
    read -n 1 -p "Select an option (1-3): " choice
    echo
    case "$choice" in
        1) PATCHER="RVZ"; break ;;
        2) PATCHER="ISO"; break ;;
        3) exit 0 ;;
        *) echo "Invalid option." ;;
    esac
done

echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
echo "Setting up patcher!"
echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="

rm -rf tmp

shopt -s nullglob
iso_files=("$SCRIPT_DIR"/*.iso)
rvz_files=("$SCRIPT_DIR"/*.rvz)

if [ ${#iso_files[@]} -eq 0 ] && [ ${#rvz_files[@]} -eq 0 ]; then
    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "No ISO or RVZ files found in the same directory as the script."
    echo "Place the Mario Party 4 (USA) ISO or RVZ in the script's directory and run it again."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo
    read -n 1 -s -r -p "Press any key to exit..."
    echo
    exit 0
fi

clear
mkdir -p tmp

if [ ${#rvz_files[@]} -gt 0 ]; then
    F="${rvz_files[0]}"

    if ! has_working_dolphintool; then
        clear
        echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
        echo "dolphintool.exe is a Windows binary and can't run on macOS, so an .rvz"
        echo "source file can't be converted to ISO automatically here."
        echo "Use Dolphin's GUI (right-click the .rvz -> Convert File...) to make an"
        echo ".iso first, then run this script again."
        echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
        rm -rf tmp
        exit 1
    fi

    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Converting RVZ to ISO! This is needed to patch the game..."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    "tools/dolphintool" convert -i "$F" -f "iso" -o "tmp/tmp.iso"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Extracting Gamespace!  This may take awhile depending on computer speed..."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    "${PYISOTOOLS[@]}" "tmp/tmp.iso" E "--dest=tmp/"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Copying mod data!"
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    mkdir -p "tmp/root"
    cp -R "store/." "tmp/root/"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Rebuilding! This may take awhile depending on computer speed..."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    "${PYISOTOOLS[@]}" "tmp/root/" B "--dest=../game.iso"

elif [ ${#iso_files[@]} -gt 0 ]; then
    F="${iso_files[0]}"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Extracting Gamespace!  This may take awhile depending on computer speed..."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    "${PYISOTOOLS[@]}" "$F" E "--dest=tmp/"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Copying mod data!"
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    mkdir -p "tmp/root"
    cp -R "store/." "tmp/root/"

    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Rebuilding! This may take awhile depending on computer speed..."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    "${PYISOTOOLS[@]}" "tmp/root/" B "--dest=../../tmp/game.iso"
fi

if [ "$PATCHER" = "RVZ" ] && has_working_dolphintool; then
    clear
    "tools/dolphintool" convert -i "tmp/game.iso" -o "Mario Party 4 (USA) [DX] ($VERSION).rvz" -f "rvz" -b "131072" -c "zstd" -l "5"
    rm -f "tmp/game.iso"
    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Success! Your game is located in \"Mario Party 4 (USA) [DX] ($VERSION).rvz\""
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
elif [ "$PATCHER" = "RVZ" ]; then
    clear
    mv "tmp/game.iso" "Mario Party 4 (USA) [DX] ($VERSION).iso"
    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Success! Your game is located in \"Mario Party 4 (USA) [DX] ($VERSION).iso\""
    echo
    echo "Note: dolphintool.exe is a Windows binary and can't convert to RVZ on"
    echo "macOS. To compress it, open the .iso in Dolphin, right-click it in the"
    echo "game list, and choose \"Convert File...\" -> RVZ."
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
fi

if [ "$PATCHER" = "ISO" ]; then
    clear
    mv "tmp/game.iso" "Mario Party 4 (USA) [DX] ($VERSION).iso"
    clear
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
    echo "Success! Your game is located in \"Mario Party 4 (USA) [DX] ($VERSION).iso\""
    echo "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ="
fi

rm -rf tmp

echo
read -n 1 -s -r -p "Press any key to exit..."
echo
exit 0
