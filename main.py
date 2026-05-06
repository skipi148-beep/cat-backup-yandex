import json
import requests
from urllib.parse import quote

# Отключаем предупреждения об SSL
requests.packages.urllib3.disable_warnings()

def run_backup():
    print("--- Курсовая работа: Резервное копирование котиков ---")
    
    text = input("1. Введите текст для котика: ").strip()
    token = input("2. Введите ваш ТОКЕН: ").strip()
    group = input("3. Введите название папки: ").strip()

    headers = {
        "Authorization": f"OAuth {token}",
        "Accept": "application/json"
    }

    try:
        # ШАГ 1: СОЗДАНИЕ ПАПКИ
        print(f"\n[Шаг 1] Создаю папку '{group}' на Яндекс.Диске...")
        # ИСПРАВЛЕНО: Правильный адрес API
        folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        f_resp = requests.put(folder_url, headers=headers, params={"path": group})

        if f_resp.status_code in (201, 200):
            print(f"       ✅ Папка успешно подготовлена.")
        elif f_resp.status_code == 409:
            print(f"       ✅ Папка уже существует.")
        else:
            print(f"       ⚠️ Статус папки: {f_resp.status_code}")
        
        # ШАГ 2: СКАЧИВАНИЕ КОТИКА
        print(f"[Шаг 2] Скачиваю котика с текстом '{text}'...")
        cat_url = f"https://cataas.com/cat/says/{quote(text)}"
        cat_resp = requests.get(cat_url, timeout=60, verify=False)
        
        if cat_resp.status_code == 200:
            img_data = cat_resp.content
            file_size = len(img_data)
            print(f"       ✅ Успешно скачано ({file_size} байт)")
            
            # ШАГ 3: ЗАГРУЗКА В ОБЛАКО
            filename = f"{text}.jpg" if text else "cat.jpg"
            full_path = f"{group}/{filename}"
            print(f"[Шаг 3] Загружаю в облако: {full_path}")
            
       
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

            ya_resp = requests.get(
                upload_url, 
                headers=headers, 
                params={"path": full_path, "overwrite": "true"}
            )
            
            if ya_resp.status_code == 200:
                upload_href = ya_resp.json().get("href")
                requests.put(upload_href, data=img_data)
                print(f"       🎉 УСПЕХ! Кот загружен.")

                report = [{"file_name": filename, "size": file_size}]
                with open("upload_info.json", "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=4, ensure_ascii=False)
                print(f"[Шаг 4] Отчет 'upload_info.json' создан успешно.")
            else:
                print(f"❌ Ошибка Яндекса (запрос ссылки): {ya_resp.status_code}")
                if ya_resp.status_code == 401:
                    print("Проверьте ваш ТОКЕН!")
        else:
            print(f"❌ Котик не скачался. Код: {cat_resp.status_code}")

    except Exception as e:
        print(f"\n ОШИБКА РАБОТЫ СКРИПТА: {e}")

if __name__ == "__main__":
    run_backup()
