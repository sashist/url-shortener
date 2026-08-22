import sqids
from sqids import Sqids

SQ_ALPAHABET = "k3G7QAe51FCsPW92uEOyq4Bg6Sp8YzVTmnU0liwDdHXLajZrfxNhobJIRcMvKt"


def generate_short_code(url_id: int):
    sqids = Sqids(alphabet=SQ_ALPAHABET, min_length=6)
    short_code = sqids.encode([url_id])
    return short_code
