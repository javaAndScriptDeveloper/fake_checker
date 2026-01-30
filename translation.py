from deep_translator import GoogleTranslator


class Translator:

    def __init__(self):
        self.supported_translations_list = [
            {
                "label": "Українська",
                "value": "ukrainian"
            },
            {
                "label": "English",
                "value": "english"
            }
        ]

        self.ui_translations = {
            "english": {
                "window_title": "Propaganda Checker App",
                "tab_process": "Text Processor",
                "tab_table": "Result Table",
                "tab_ratings": "Ratings",
                "tab_system_info": "System Info",
                "tab_graph": "Graph",
                "select_source": "Select Source:",
                "select_language": "Select Language:",
                "title_placeholder": "Enter title here...",
                "text_placeholder": "Enter your text here...",
                "process_button": "Process",
                "export_csv": "Export to CSV",
                "fehner_score": "Fehner Score:",
                "calculating": "Calculating...",
                "name": "Name",
                "rating": "Rating",
                "source": "Source",
                "text_data": "Text Data",
                "sentimental_score": "Sentimental Score",
                "triggered_keywords": "Triggered Keywords",
                "triggered_topics": "Triggered Topics",
                "text_simplicity": "Text Simplicity",
                "confidence_factor": "Confidence Factor",
                "clickbait": "Clickbait",
                "subjective": "Subjective",
                "call_to_action": "Call to Action",
                "repeated_take": "Repeated Take",
                "repeated_note": "Repeated Note",
                "total_score": "Total Score",
                "is_propaganda": "Is Propaganda",
                "text_simplicity_deviation": "Text Simplicity Deviation",
                "graph_unavailable": "Neo4j not connected",
                "refresh_graph": "Refresh",
                "sources_label": "Sources",
                "notes_label": "Notes",
                "relationships_label": "Relationships",
                "most_influential": "Most Influential Sources",
                "avg_propaganda_score": "Avg Propaganda Score",
                "note_count": "Note Count",
                "platform": "Platform",
                "connections": "Connections",
            },
            "ukrainian": {
                "window_title": "Перевірка на Пропаганду",
                "tab_process": "Обробка Тексту",
                "tab_table": "Таблиця Результатів",
                "tab_ratings": "Рейтинги",
                "tab_system_info": "Системна Інформація",
                "tab_graph": "Граф",
                "select_source": "Оберіть Джерело:",
                "select_language": "Оберіть Мову:",
                "title_placeholder": "Введіть заголовок тут...",
                "text_placeholder": "Введіть текст тут...",
                "process_button": "Обробити",
                "export_csv": "Експорт у CSV",
                "fehner_score": "Оцінка Фехнера:",
                "calculating": "Обчислення...",
                "name": "Назва",
                "rating": "Рейтинг",
                "source": "Джерело",
                "text_data": "Текстові Дані",
                "sentimental_score": "Сентиментальна Оцінка",
                "triggered_keywords": "Тригерні Слова",
                "triggered_topics": "Тригерні Теми",
                "text_simplicity": "Простота Тексту",
                "confidence_factor": "Фактор Впевненості",
                "clickbait": "Клікбейт",
                "subjective": "Суб'єктивність",
                "call_to_action": "Заклик до Дії",
                "repeated_take": "Повторювана Позиція",
                "repeated_note": "Повторювана Нотатка",
                "total_score": "Загальна Оцінка",
                "is_propaganda": "Чи є Пропагандою",
                "text_simplicity_deviation": "Відхилення Простоти Тексту",
                "graph_unavailable": "Neo4j не підключено",
                "refresh_graph": "Оновити",
                "sources_label": "Джерела",
                "notes_label": "Нотатки",
                "relationships_label": "Зв'язки",
                "most_influential": "Найвпливовіші Джерела",
                "avg_propaganda_score": "Середня Оцінка Пропаганди",
                "note_count": "Кількість Нотаток",
                "platform": "Платформа",
                "connections": "З'єднання",
            }
        }

    def get_ui_text(self, key: str, language: str = "ukrainian") -> str:
        return self.ui_translations.get(language, self.ui_translations["ukrainian"]).get(key, key)

    def translate_to_english(self, text, source_language):
        try:
            translation = GoogleTranslator(source=source_language, target='english').translate(text)
            return translation
        except Exception as e:
            return f"Translation Error: {e}"
