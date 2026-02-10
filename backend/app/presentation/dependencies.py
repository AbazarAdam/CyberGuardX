"""
Shared Dependencies
====================
FastAPI ``Depends()`` callables used by every route module.
Having one ``get_db`` avoids the four duplicated copies that existed before.
"""

from app.infrastructure.database.connection import SessionLocal


def get_db():
    """
    Yield a SQLAlchemy session and guarantee it is closed after the request.

    Usage in a route::

        @router.post("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
