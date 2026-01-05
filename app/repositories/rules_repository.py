from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business_rules import BusinessRule


class RulesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rule_content(self, rule_key: str) -> dict:
        """Fetch rules JSON content by key."""
        result = await self.db.execute(
            select(BusinessRule).where(BusinessRule.rule_key == rule_key)
        )
        record = result.scalars().first()
        return record.content if record else None

    async def upsert_rule(self, rule_key: str, content: dict):
        """Creates or Updates the rule JSON in one go."""
        result = await self.db.execute(
            select(BusinessRule).where(BusinessRule.rule_key == rule_key)
        )
        record = result.scalars().first()

        if record:
            # Update if it already exists.
            record.content = content
        else:
            # Create new
            new_record = BusinessRule(rule_key=rule_key, content=content)
            self.db.add(new_record)

        await self.db.commit()
