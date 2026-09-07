from perfecto_cms.core.logging_config import configure_logging
from perfecto_cms.ui.main_window import PerfectoCMSApp


def main() -> None:
    logger = configure_logging()
    logger.info("Starting Perfecto CMS")
    app = PerfectoCMSApp()
    app.mainloop()
