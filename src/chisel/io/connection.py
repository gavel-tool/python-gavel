from sqlalchemy import create_engine
from settings import DB_CONNECTION

def get_engine():

    if 'password' in DB_CONNECTION:
        cred = '{user}:{password}'.format(**DB_CONNECTION)
    else:
        cred = '{user}'.format(**DB_CONNECTION)
    return create_engine('postgresql://{cred}@{host}:{port}/{database}'.format(
        cred=cred,
        **DB_CONNECTION
    ))

