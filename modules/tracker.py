from datetime import datetime
from pathlib import Path
import sys

# Принудительно добавляем корень проекта в sys.path для доступа к базе данных
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.models import SessionLocal, TimeLog


def add_time_log(task_name, category, duration_minutes):
  """Функция для добавления записи о потраченном времени"""
  session = SessionLocal()
  try:
    log = TimeLog(
        project_name=task_name,  # Используем имя поля из базы данных: project_name
        category=category,
        duration_minutes=duration_minutes,
        date =datetime.now().date(),
    )
    session.add(log)
    session.commit()
    print(
        f"[Успешно] Записано {duration_minutes} мин. для задачи '{task_name}'"
        f" [Категория: {category}]"
    )
  except Exception as e:
    session.rollback()
    print(f"[Ошибка] Не удалось сохранить лог времени: {e}")
  finally:
    session.close()


def get_all_time_logs():
  """Получить список всех записей учета времени из базы данных"""
  session = SessionLocal()
  logs = session.query(TimeLog).all()
  session.close()
  return logs


def get_total_time():
  """Подсчитать суммарное время на все сессии (в часах и минутах)"""
  logs = get_all_time_logs()
  total_minutes = sum(log.duration_minutes for log in logs)
  hours = total_minutes // 60
  minutes = total_minutes % 60
  return hours, minutes


if __name__ == "__main__":
  # Тестовый запуск трекера
  print("--- Добавляем тестовую сессию учета времени ---")
  add_time_log(
      task_name="Разработка автосортировщика файлов",
      category="Программирование",
      duration_minutes=60,
  )

  print("\n--- Общая статистика по времени ---")
  h, m = get_total_time()
  print(f"Всего потрачено времени на проект: {h} ч. {m} мин.")

  print("\n--- История всех сессий ---")
  for log in get_all_time_logs():
    print(
        f"ID: {log.id} | Задача: {log.project_name} | Категория:"
        f" {log.category} | Время: {log.duration_minutes} мин."
    )