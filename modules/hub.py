from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.models import SessionLocal, Snippet

def add_snippet(title, content, language, tags=""):
    """Функция для добавления нового сниппета или заметки в базу знаний"""
    session =SessionLocal()
    try:
        snippet = Snippet(
            title = title,
            content = content,
            language = language,
            tags = tags,
        )
        session.add(snippet)
        session.commit()
        print(f"[Успешно] Сниппет '{title}' сохранен (Язык: {language})")
    except Exception as e:
        session.rollback()
        print(f"[Ошибка] Не удалось сохранить: {e}")
    finally:
        session.close()

def get_all_snippets():
    """Получить список всех сохраненных сниппетов"""
    session = SessionLocal()
    snippet = session.query(Snippet).all()
    session.close()
    return snippet

def search_snippets(keyword):
    """Поиск сниппетов по ключевому слову в названии, язык программирования или тегах"""
    session = SessionLocal()
    results = (
        session.query(Snippet)
        .filter(
            (Snippet.title.ilike(f"%{keyword}%"))
            | (Snippet.language.ilike(f"%{keyword}%"))
            | (Snippet.tags.ilike(f"%{keyword}%"))
        )
        .all()
    )
    session.close()
    return results

if __name__ == "__main__":
    #Тестовый запуск
    print("--- Добавляем тестовый сниппет ---")
    add_snippet(
        title="Настройка Watchdog для папки",
        content=(
          "observer = Observer()\nobserver.schedule(event_handler,"
          " path=path_to_watch)\nobserver.start()"
      ),
      language="Python",
      tags="watchdog, automation, files",
  )

    print("\n--- Все сохраненные сниппеты ---")
    for s in get_all_snippets():
        print(
            f"ID: {s.id} | Название: {s.title} | Язык: {s.language} | Теги:"
            f" {s.tags}\nКод:\n{s.content}\n"
        )