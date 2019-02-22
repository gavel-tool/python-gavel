from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gavel.settings import DB_CONNECTION

__ENGINE__ = None

def get_engine():
    global __ENGINE__
    if __ENGINE__ is None:
        if "password" in DB_CONNECTION:
            cred = "{user}:{password}".format(**DB_CONNECTION)
        else:
            cred = "{user}".format(**DB_CONNECTION)
        __ENGINE__ = create_engine(
            "postgresql://{cred}@{host}:{port}/{database}".format(
                cred=cred, **DB_CONNECTION
            )
        )
    return __ENGINE__


def with_session(wrapped_function):
    def inside(*args, **kwargs):
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            wrapped_function(*args, session=session, **kwargs)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    return inside


def get_or_create(session, cls, *args, **kwargs):
    obj = session.query(cls).filter_by(**kwargs).first()
    created = False
    if not obj:
        obj = cls(*args, **kwargs)
        session.add(obj)
        created = True
    return obj, created
