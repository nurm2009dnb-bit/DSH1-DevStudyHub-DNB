from pathlib import Path
import sys

# Добавляем корневую директорию в путь для импорта модулей
sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.cleaner import start_cleaner
from modules.hub import add_snippet, get_all_snippets, search_snippets
from modules.tracker import add_time_log, get_all_time_logs, get_total_time

def main_menu():
    while True:
        print("\n" + "=" * 50)
        print(" DevStudyHub - Персональный хаб разраточика и студента ")
        print("=" * 50)
        print("1. 📁 Запустить автосортировщик файлов (Cleaner)")
        print("2. ⏱️ Учет времени и задач (Tracker)")
        print("3. 💡 База знаний и сниппеты (Hub)")
        print("0. 🚪 Выход из программы")

        choice = input("\nВыберите пункт меню (0-3): ").strip()

        if choice == "1":
            target = input(
                "Введите путь к папке для мониторинга (по умолчанию"
                " ./TestDownloads): "
            ).strip()
            if not target:
                target = "./TestDownloads"
            path = Path(target)
            path.mkdir(exist_ok=True)
            print(f"Заруск мониторинга папки: {path.absolute()}")
            start_cleaner(str(path.absolute()))

        elif choice == "2":
            print("\n--- Трекер времени ---")
            print("1. Добавить сессию учета времени")
            print("2. Посмотреть общую статистику и историю")
            sub_choice = input("Выберите действие (1-2): ").strip()

            if sub_choice == "1":
                p_name = input("Название проекта/задачи: ").strip()
                cat = input("Категория (например, Программирование, Учеба): ").strip()
                try:
                    dur = int(input("Длительность в минутах: ").strip())
                    add_time_log(p_name, cat, dur)
                except ValueError:
                    print("[Ошибка] Введите целое число для минут.")

            elif sub_choice == "2":
                h, m = get_total_time()
                print(f"\nВсего потрачено времени: {h} ч. {m} мин.")
                print("\nИстория сессий:")
                for log in get_all_time_logs():
                    print(
                        f"ID: {log.id} | Проект: {log.project_name} | Категория:"
                        f" {log.category} | Время: {log.duration_minutes} мин. | Дата:"
                        f" {log.date}"
          )

        elif choice == "3":
            print("\n--- База знаний и сниппеты ---")
            print("1. Добавить новый сниппет")
            print("2. Посмотреть все сниппеты")
            print("3. Найти сниппет по ключевому слову")
            sub_choice = input("Выберите действие (1-3): ").strip()

            if sub_choice == "1":
                title = input("Название сниппета: ").strip()
                content = input("Содержимое кода: ").strip()
                lang = (
                    input("Язык/технология (по умолчанию Python): ").strip() or "Python"
                )
                tags = input("Теги (через запятую): ").strip()
                add_snippet(title, content, lang, tags)
            elif sub_choice == "2":
                print("\nВсе сохраненные сниппеты:")
                for s in get_all_snippets():
                    print(
                        f"[{s.id}] {s.title} ({s.language}) — Теги: {s.tags}\nКод:\n{s.content}\n"
                        f"{'-'*40}"
                    )
            elif sub_choice == "3":
                kw = input("Введите ключевое слово для поиска: ").strip()
                result = search_snippets(kw)
                print(f"\nНайдено результатов: {len(result)}")
                for s in result:
                    print(
                        f"[{s.id}] {s.title} ({s.language}) — Теги: {s.tags}\nКод:\n{s.content}\n"
                        f"{'-'*40}"
                    )
        elif choice == "0":
            print("Выход из программы. Удачи в учебе и защите диплома!")
            break
        else:
            print("[Ошибка] Неверный выбор. Пожалуйста, введите цифру от 0 до 3.")

if __name__ == "__main__":
    main_menu()