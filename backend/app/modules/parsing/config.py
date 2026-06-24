POINTS_PER_INCH = 72  # количество точек на дюйм

DEFAULT_DPI = 200  # разрешение по умолчанию
DEFAULT_TOP_PAD = 10  # отступ сверху блока
DEFAULT_BOTTOM_PAD = 10  # отступ снизу блока

INK_THRESHOLD = 200  # порог для точки (0...255)
INK_GAP_TOLERANCE_PT = 3.0  # допустимый зазор между точками (в точках)
MIN_CROP_HEIGHT = 5  # минимальная высота обрезки

SECTION_HEADING_SIZE_RATIO = 1.20  # соотношение размера заголовка к размеру текста
LEFT_MARGIN_TOLERANCE = 4  # допустимый зазор между левым краем и текстом
MAX_PREFIX_BEFORE_HEADING = 10  # максимальная длина префикса перед заголовком
LINE_OVERLAP_RATIO = 0.15  # соотношение перекрытия линий
FALLBACK_TEXT_SIZE = 10.0  # размер текста по умолчанию

FOOTER_REGION_RATIO = 0.88  # соотношение области колонтитула к размеру страницы
MAX_PAGE_NUMBER_LENGTH = 4  # максимальная длина номера страницы
MIN_FOOTER_GAP_RATIO = 1.5  # мин. соотношение зазора колонтитула к размеру страницы

BOLD_FONT_MARKERS = ("BX", "BOLD")
ITALIC_FONT_MARKERS = ("TI", "ITALIC", "OBLIQUE")

UNTITLED = "текст"

DEFAULT_KEYWORDS = (
    "Определение",
    "Теорема",
    "Лемма",
    "Доказательство",
    "Следствие",
    "Замечание",
    "Пример",
    "Свойство",
    "Утверждение",
)
