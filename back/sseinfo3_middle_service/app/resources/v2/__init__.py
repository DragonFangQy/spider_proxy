from flask import Blueprint

v2 = Blueprint(
    name="v2",
    import_name=__name__,
    url_prefix="/api/v2",
)

# from . import ideas, data_input
from . import data_output, file_download
