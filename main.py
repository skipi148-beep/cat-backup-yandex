import urllib.request
import urllib.parse
import json
import os
import ssl

# Решаем проблему с SSL-сертификатами (чтобы не было ошибок соединения)
ssl._create_default_https_context = ssl._create_unverified_context

def run_backup():
    print("--- Курсовая работа: Резервное копирование котиков ---")
    
    # 1. Ввод данных (согласно заданию)
    text = input("1. Введите текст для котика: ").strip()
    token = input("2. Введите токен Яндекс.Диска: ").strip()
    group = input("3. Введите название вашей группы (папки): ").strip()
    
    # ПРАВИЛЬНЫЕ ССЫЛКИ
    # Для Cataas: обязательно /cat/says/
    cat_url = f"https://cataas.com/cat/says/{urllib.parse.quote(text)}"
    # Путь для Диска
    disk_path = f"{group}/{text}.jpg"
    
    try:
        # ШАГ 1: СКАЧИВАНИЕ
        print(f"\n[Шаг 1] Скачиваю картинку: {cat_url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req_cat = urllib.request.Request(cat_url, headers=headers)
        
        with urllib.request.urlopen(req_cat, timeout=30) as response:
            img_data = response.read()
            with open("temp_cat.jpg", "wb") as f:
                f.write(img_data)
        
        file_size = os.path.getsize("temp_cat.jpg")
        print(f"       Успешно скачано ({file_size} байт)")

        # ШАГ 2: ПОЛУЧЕНИЕ ССЫЛКИ ДЛЯ ЗАГРУЗКИ НА ЯНДЕКС
        print(f"[Шаг 2] Запрашиваю доступ к API Яндекс.Диска...")
        # Используем правильный адрес API: cloud-api.yandex.net
        params = urllib.parse.urlencode({'path': disk_path, 'overwrite': 'true'})
        api_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?{params}"
        
        req_ya = urllib.request.Request(api_url)
        req_ya.add_header("Authorization", f"OAuth {token}")
        req_ya.add_header("Accept", "application/json")

        with urllib.request.urlopen(req_ya) as ya_res:
            res_json = json.loads(ya_res.read().decode('utf-8'))
            upload_href = res_json.get("href")
            
            # ШАГ 3: ЗАГРУЗКА В ОБЛАКО (метод PUT)
            print(f"[Шаг 3] Загружаю файл в папку '{group}'...")
            with open("temp_cat.jpg", "rb") as f:
                put_req = urllib.request.Request(upload_href, data=f.read(), method="PUT")
                with urllib.request.urlopen(put_req) as final_res:
                    if final_res.status in (200, 201, 202):
                        print("       УСПЕХ! Картинка загружена на Яндекс.Диск.")

        # ШАГ 4: СОЗДАНИЕ ОТЧЕТА (JSON)
                        # [Шаг 4] Отчет
        report = [{"file_name": f"{text}.jpg", "size": file_size}] # Используем file_size
        
        # Определяем путь именно к папке cat_backup
        current_dir = os.path.dirname(os.path.abspath(__file__))
        report_path = os.path.join(current_dir, "upload_info.json")
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
            
        print(f"[Шаг 4] УСПЕХ! Отчет создан: {report_path}")

        # Удаляем временный файл
        if os.path.exists("temp_cat.jpg"):
            os.remove("temp_cat.jpg")

    except Exception as e:
        print(f"\n ОШИБКА: {e}")
        print(" Проверьте: 1. Создана ли папка на Диске. 2. Верен ли токен.")

if __name__ == "__main__":
    run_backup()
