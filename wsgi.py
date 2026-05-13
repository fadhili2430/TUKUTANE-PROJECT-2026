import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

from app import start_app, db
from app.utils import populate_initial_data

app = start_app()

with app.app_context():
    try:
        db.create_all()
        logger.info("db.create_all() completed successfully")
    except Exception as e:
        logger.error(f"db.create_all() failed: {e}", exc_info=True)

    try:
        populate_initial_data()
        logger.info("populate_initial_data() completed successfully")
    except Exception as e:
        logger.error(f"populate_initial_data() failed: {e}", exc_info=True)

application = app
