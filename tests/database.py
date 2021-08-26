from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker())
