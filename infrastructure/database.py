import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkingCodeDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Создание таблицы checks
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    product_name TEXT,
                    status VARCHAR(20),
                    status_text TEXT,
                    found BOOLEAN DEFAULT FALSE,
                    error TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    check_count INTEGER DEFAULT 1,
                    in_process BOOLEAN DEFAULT FALSE,
                    process_start_date DATETIME
                )
            ''')

            # Создание индексов
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_code ON checks(code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON checks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_updated ON checks(updated_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_in_process ON checks(in_process)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_process_start ON checks(process_start_date)')

            conn.commit()
        logger.info("База данных инициализирована")

    def mark_codes_as_processing(self, codes: List[str]) -> bool:
        """Пометить коды как переданные в обработку"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                placeholders = ','.join(['?' for _ in codes])
                query = f"""
                    UPDATE checks 
                    SET in_process = TRUE, process_start_date = ?
                    WHERE code IN ({placeholders})
                """
                cursor.execute(query, [current_time] + codes)

                conn.commit()
                return True

        except sqlite3.Error as e:
            logger.error(f"Ошибка при отметке кодов как в обработке: {e}")
            return False

    def get_available_codes(self, product_name: str, limit: int) -> List[str]:
        """Получить доступные коды для продукта (только НЕ в обработке)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT code FROM checks 
                    WHERE product_name = ? 
                    AND status = 'INTRODUCED'
                    AND in_process = FALSE
                    LIMIT ?
                ''', (product_name, limit))

                return [row[0] for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении доступных кодов: {e}")
            return []

    def check_old_processed_codes(self) -> bool:
        """Проверить коды в обработке старше 7 дней и обновить их статус"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

                # Находим старые коды в обработке
                cursor.execute('''
                    SELECT code FROM checks 
                    WHERE in_process = TRUE 
                    AND process_start_date < ?
                ''', (seven_days_ago,))
                old_codes = [row[0] for row in cursor.fetchall()]

                if not old_codes:
                    return True

                logger.info(f"Найдено {len(old_codes)} кодов в обработке старше 7 дней")

                # Снимаем пометку обработки для всех старых кодов
                placeholders = ','.join(['?' for _ in old_codes])
                cursor.execute(f'''
                    UPDATE checks 
                    SET in_process = FALSE, process_start_date = NULL 
                    WHERE code IN ({placeholders})
                ''', old_codes)

                conn.commit()
                logger.info(f"Снята пометка обработки с {len(old_codes)} кодов")
                return True

        except sqlite3.Error as e:
            logger.error(f"Ошибка при проверке старых кодов: {e}")
            return False

    def save_check_result(self, result: Dict) -> bool:
        """Сохранение или обновление результата проверки в БД"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Проверяем, существует ли уже код в БД
                cursor.execute(
                    "SELECT id, check_count FROM checks WHERE code = ?",
                    (result['code'],)
                )
                existing = cursor.fetchone()

                if existing:
                    # Обновляем существующую запись
                    check_count = existing[1] + 1
                    cursor.execute('''
                        UPDATE checks 
                        SET product_name = ?, status = ?, status_text = ?, 
                            found = ?, error = ?, updated_at = ?, check_count = ?
                        WHERE code = ?
                    ''', (
                        result.get('product_name'),
                        result.get('status'),
                        result.get('status_text'),
                        result.get('found', False),
                        result.get('error'),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        check_count,
                        result['code']
                    ))
                else:
                    # Вставляем новую запись
                    cursor.execute('''
                        INSERT INTO checks 
                        (code, product_name, status, status_text, found, error)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        result['code'],
                        result.get('product_name'),
                        result.get('status'),
                        result.get('status_text'),
                        result.get('found', False),
                        result.get('error')
                    ))

                conn.commit()
                return True

        except sqlite3.Error as e:
            logger.error(f"Ошибка при сохранении в БД: {e}")
            return False

    def get_code_info(self, code: str) -> Optional[Dict]:
        """Получение информации о коде из БД"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT * FROM checks WHERE code = ?",
                    (code,)
                )
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None

        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении данных: {e}")
            return None