from config import PDF_FOLDER

class FreeCodeManager:
    def get_available_products(self) -> list[str]:
        """Возвращает список папок - товаров из data"""
        from utils.file_utils import get_available_products
        return get_available_products(PDF_FOLDER)

    def get_free_codes(self, product_name: str, quantity: int) -> list[str]:
        """Возвращает N свободных кодов для указанного товара"""
        from services.free_code_manager import get_free_codes
        return get_free_codes(product_name, quantity, PDF_FOLDER)