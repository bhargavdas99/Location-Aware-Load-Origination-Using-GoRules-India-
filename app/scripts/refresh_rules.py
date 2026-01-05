import json
import asyncio
import logging
import sys
from pathlib import Path

from app.core.database import AsyncSessionLocal
from app.repositories.rules_repository import RulesRepository

# 2. Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("rules_refresher")


async def refresh_rules(file_path: str):
    """
    Reads a JDM JSON file and synchronizes it with the rules repository.
    """
    path = Path(file_path)

    # Validate file existence
    if not path.is_file():
        logger.error(f"File not found at specified path: {file_path}")
        return

    # Load and validate JSON content
    try:
        with open(path, "r", encoding="utf-8") as f:
            new_rules_content = json.load(f)
        logger.info(f"Successfully parsed JSON from {path.name}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {file_path}: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        return

    # Database operation
    async with AsyncSessionLocal() as session:
        repo = RulesRepository(session)
        try:
            # Using 'loan_decision' as the unique key for the GoRules JDM
            await repo.upsert_rule("loan_decision", new_rules_content)
            logger.info("Database upsert successful: 'loan_decision' key updated.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction failed. Rolling back. Error: {e}")
        finally:
            await session.close()


async def main():
    """
    CLI Entry point for the rules refresher script.
    """
    if len(sys.argv) < 2:
        logger.warning("No input file provided.")
        print("\nUsage: python scripts/refresh_rules.py <path_to_json_file>\n")
        sys.exit(1)

    target_file = sys.argv[1]
    logger.info(f"Starting rules refresh for: {target_file}")

    await refresh_rules(target_file)
    logger.info("Process completed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
        sys.exit(0)


# command:
# python -m app.scripts.refresh_rules /media/bhargab/832c94fd-364b-4c9c-a8e7-b86a70ab51c5/coding/Notes/FastAPI/Location-Aware-Load-Origination-Using-GoRules-India-/app/rules/loan_decision.json
