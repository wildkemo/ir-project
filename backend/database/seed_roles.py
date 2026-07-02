"""Seed default application roles."""

import logging

from backend.database.session import SessionLocal
from backend.models.role import Role

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    ("User", "Standard application user"),
    ("Admin", "Administrator with elevated privileges"),
]


def seed_roles() -> None:
    """Insert default roles if they do not exist."""
    db = SessionLocal()
    try:
        for name, description in DEFAULT_ROLES:
            existing = db.query(Role).filter(Role.name == name).first()
            if existing is None:
                db.add(Role(name=name, description=description))
                logger.info("Created role: %s", name)
        db.commit()
        logger.info("Role seeding completed")
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_roles()
