from pathlib import Path
import sys
import threading
import customtkinter as ctk

sys.path.append(str(Path(__file__).resolve().parent))
from modules.cleaner import start_cleaner
from modules.hub import add_snippet, search_snippets
from modules.tracker import add_time_log, get_total_time

# Настройка темы интерфейса
ctk.set_appearance_mode("System")  # Подстраивается под тему Windows
ctk.set_default_color_theme("blue")


class DevStudyHubApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("DevStudyHub - Органайзер файлов")
    self.geometry("700x500")
    self.resizable(False, False)

    # Создание вкладок (Tabs)
    self.tabview = ctk.CTkTabview(self, width=660, height=460)
    self.tabview.pack(padx=20, pady=20)

    self.tab_cleaner = self.tabview.add("📁 Авто-Cleaner")
    self.tab_tracker = self.tabview.add("⏱️ Трекер времени")
    self.tab_hub = self.tabview.add("💡 База знаний")

    self.setup_cleaner_tab()
    self.setup_tracker_tab()
    self.setup_hub_tab()

  # --- Вкладка 1: Cleaner ---
  def setup_cleaner_tab(self):
    label = ctk.CTkLabel(
        self.tab_cleaner,
        text="Автосортировщик файлов",
        font=("Arial", 16, "bold"),
    )
    label.pack(pady=20)

    self.path_entry = ctk.CTkEntry(
        self.tab_cleaner,
        width=450,
        placeholder_text="Путь к папке (например, ./TestDownloads)",
    )
    self.path_entry.pack(pady=10)
    self.path_entry.insert(0, "./TestDownloads")

    self.start_cleaner_btn = ctk.CTkButton(
        self.tab_cleaner,
        text="Запустить мониторинг",
        command=self.run_cleaner_thread,
    )
    self.start_cleaner_btn.pack(pady=20)

    self.cleaner_status = ctk.CTkLabel(
        self.tab_cleaner, text="Статус: Остановлен", text_color="gray"
    )
    self.cleaner_status.pack(pady=10)

  def run_cleaner_thread(self):
    path = self.path_entry.get().strip()
    Path(path).mkdir(exist_ok=True)
    self.cleaner_status.configure(
        text=f"Статус: Работает ({path})", text_color="green"
    )
    # Запускаем в отдельном потоке, чтобы графическое окно не зависало
    threading.Thread(
        target=start_cleaner, args=(path,), daemon=True
    ).start()

  # --- Вкладка 2: Трекер времени ---
  def setup_tracker_tab(self):
    label = ctk.CTkLabel(
        self.tab_tracker,
        text="Учет учебного и рабочего времени",
        font=("Arial", 16, "bold"),
    )
    label.pack(pady=15)

    self.task_entry = ctk.CTkEntry(
        self.tab_tracker, width=400, placeholder_text="Название проекта / задачи"
    )
    self.task_entry.pack(pady=5)

    self.cat_entry = ctk.CTkEntry(
        self.tab_tracker,
        width=400,
        placeholder_text="Категория (Программирование, Учеба)",
    )
    self.cat_entry.pack(pady=5)

    self.time_entry = ctk.CTkEntry(
        self.tab_tracker,
        width=400,
        placeholder_text="Длительность в минутах (например, 45)",
    )
    self.time_entry.pack(pady=5)

    save_btn = ctk.CTkButton(
        self.tab_tracker, text="Сохранить сессию", command=self.save_time
    )
    save_btn.pack(pady=15)

    self.time_stats_label = ctk.CTkLabel(
        self.tab_tracker,
        text="Всего времени потрачено: 0 ч. 0 мин.",
        font=("Arial", 14),
    )
    self.time_stats_label.pack(pady=10)
    self.update_time_display()

  def save_time(self):
    t_name = self.task_entry.get()
    cat = self.cat_entry.get()
    try:
      dur = int(self.time_entry.get())
      if t_name and cat:
        add_time_log(t_name, cat, dur)
        self.update_time_display()
        self.task_entry.delete(0, "end")
        self.cat_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
    except ValueError:
      pass

  def update_time_display(self):
    h, m = get_total_time()
    self.time_stats_label.configure(
        text=f"Всего времени потрачено: {h} ч. {m} мин."
    )

  # --- Вкладка 3: База знаний ---
  def setup_hub_tab(self):
    label = ctk.CTkLabel(
        self.tab_hub,
        text="База знаний и сниппетов кода",
        font=("Arial", 16, "bold"),
    )
    label.pack(pady=10)

    self.hub_title = ctk.CTkEntry(
        self.tab_hub, width=450, placeholder_text="Название сниппета"
    )
    self.hub_title.pack(pady=5)

    self.hub_lang = ctk.CTkEntry(
        self.tab_hub, width=450, placeholder_text="Язык (Python, C#, etc.)"
    )
    self.hub_lang.pack(pady=5)

    self.hub_content = ctk.CTkTextbox(self.tab_hub, width=450, height=100)
    self.hub_content.pack(pady=5)
    self.hub_content.insert("0.0", "Code or tip...")

    save_hub_btn = ctk.CTkButton(
        self.tab_hub, text="Save to database", command=self.save_snippet_gui
    )
    save_hub_btn.pack(pady=10)

  def save_snippet_gui(self):
    title = self.hub_title.get()
    lang = self.hub_lang.get() or "Python"
    content = self.hub_content.get("0.0", "end").strip()
    if title and content:
      add_snippet(title, content, lang, tags="app")
      self.hub_title.delete(0, "end")
      self.hub_lang.delete(0, "end")
      self.hub_content.delete("0.0", "end")


if __name__ == "__main__":
  app = DevStudyHubApp()
  app.mainloop()