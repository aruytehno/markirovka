class CodeService:
    def get_api_data(self, codes: list[str]) -> list[dict]:
        """
        Возвращает данные по кодам из API ЧЗ.

        Args:
            codes: Список кодов для проверки

        Returns:
            List[dict]: Список результатов проверки кодов
        """
        from infrastructure.api_crpt import check_codes_from_list
        return check_codes_from_list(codes)


    def get_pdf_with_codes(self, codes: list[str]) -> list[tuple[int, str, bytes]]:
        """
        Возвращает список PDF с изображениями кодов, сгруппированных по товарам.

        Args:
            codes: Список кодов для поиска

        Returns:
            List[Tuple[int, str, bytes]]: Список кортежей (количество кодов, название товара, PDF в байтах)
        """
        from services.pdf_processor import get_pdf_with_codes
        from config import PDF_FOLDER

        return get_pdf_with_codes(codes, str(PDF_FOLDER))
