from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gavel.config.settings import DB_CONNECTION
from gavel.config.settings import DBMS

__ENGINE__ = None


def get_url():
    cred = DB_CONNECTION.get("user", "")
    if cred:
        if "password" in DB_CONNECTION:
            cred = "{user}:{password}".format(**DB_CONNECTION)
        cred += "@"

    location = DB_CONNECTION.get("host", "")
    port = DB_CONNECTION.get("port")
    if port:
        location += ":" + port
    return "{dbms}://{cred}{location}/{database}".format(
        dbms=DBMS, cred=cred, location=location, **DB_CONNECTION
    )


def get_engine():
    global __ENGINE__
    if __ENGINE__ is None:
        __ENGINE__ = create_engine(get_url())
    return __ENGINE__


def with_session(wrapped_function):
    def inside(*args, **kwargs):
        if "session" not in kwargs:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()
            try:
                return wrapped_function(*args, session=session, **kwargs)
            except:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            return wrapped_function(*args, **kwargs)

    return inside


def get_or_create(session, cls, *args, **kwargs):
    obj = get_or_None(session, cls, *args, **kwargs)
    created = False
    if not obj:
        obj = cls(*args, **kwargs)
        session.add(obj)
        created = True
    return obj, created


def get_or_None(session, cls, *args, **kwargs):
    return session.query(cls).filter_by(**kwargs).first()
