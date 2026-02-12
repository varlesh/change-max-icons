#!/usr/bin/env python3

# Протестировано в Arch Linux c max-bin-26.4.1.46437
# Этот скрипт заменят имя иконки desktop-файла, а так же иконки трея в бинарнике
# Иконки для трея должны быть размером не более 15KB

import os

desktop_file = "/usr/share/applications/max.desktop"
desktop_icon = "MAX"
target_bin = "/usr/share/max/bin/max"

# Фиксим имя иконки в desktop-файле
os.system(f"sudo sed -i 's|^Icon=.*|Icon={desktop_icon}|' {desktop_file}")

# Сигнатуры иконок трея (32 байта с 80-го офсета оригинала)
PATCH_MAP = {
    # Сигнатура иконки УВЕДОМЛЕНИЯ (D52B45)
    "fc61050000401b494441547801ed7d09dca65575df39f7fd665f98611d664066": "max-tray-unread.png",

    # Сигнатура ОБЫЧНОЙ иконки (D4EAD3)
    "fc610500003d32494441547801ed7d09b8a64575e639f5dd6e1ae8c666919dd8": "max-tray.png"
}

def apply_smart_patch():
    if not os.path.exists(target_bin):
        print(f" Бинарник {target_bin} не найден!")
        return

    # 1. Читаем бинарник в память
    with open(target_bin, 'rb') as f:
        data = bytearray(f.read())

    print("Бинарник найден. Делаю бэкап...")
    os.system(f"sudo cp {target_bin} {target_bin}.bak")

    patched_count = 0

    # 2. Ищем и патчим
    for sig_hex, new_icon_path in PATCH_MAP.items():
        if not os.path.exists(new_icon_path):
            print(f"Файл {new_icon_path} не найден, пропускаю...")
            continue

        sig_bytes = bytes.fromhex(sig_hex)
        with open(new_icon_path, 'rb') as f:
            new_icon_data = f.read()

        start = 0
        while True:
            # Ищем сигнатуру
            idx = data.find(sig_bytes, start)
            if idx == -1: break

            # ВАЖНО: сигнатура начинается с 80-го байта,
            # поэтому реальное начало PNG на 80 байт раньше!
            png_start = idx - 80

            # Заменяем данные
            data[png_start : png_start + len(new_icon_data)] = new_icon_data
            print(f"Пропатчено: {new_icon_path} на смещении {hex(png_start)}")

            patched_count += 1
            start = idx + 1

    # 3. Сохраняем и чистим кэш
    if patched_count > 0:
        with open("max_patched", "wb") as f:
            f.write(data)
        os.system(f"sudo mv max_patched {target_bin}")
        os.system(f"sudo chmod +x {target_bin}")

        # Чистим кэш QML
        os.system(f"rm -rf ~/.cache/MAX/qmlcache")
        print(f"Успех! Заменено вхождений: {patched_count}")
    else:
        print("Ни одна сигнатура не найдена. Проверь бинарник или иконки уже заменены!")

if __name__ == "__main__":
    apply_smart_patch()
