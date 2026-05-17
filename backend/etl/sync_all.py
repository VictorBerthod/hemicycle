"""Orchestrator script to run all ETL syncs."""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run(votes_limit: int = 50):
    from etl.sync_deputes import run as sync_deputes_run
    from etl.sync_scrutins import run as sync_scrutins_run

    logger.info("=== Starting full sync ===")

    logger.info("--- Syncing deputes ---")
    sync_deputes_run()

    logger.info("--- Syncing scrutins + votes ---")
    sync_scrutins_run(votes_limit=votes_limit)

    logger.info("=== Full sync complete ===")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    run(votes_limit=limit)
