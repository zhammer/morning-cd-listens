from datetime import datetime
from typing import Callable, Iterable, List, Optional, cast

from sqlalchemy import asc, create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from listens.abc import DbGateway as DbGatewayABC
from listens.definitions import Listen, ListenInput, SortOrder, exceptions
from listens.gateways.sqlalchemy_db_gateway.models import Base, SqlListen


class SqlAlchemyDbGateway(DbGatewayABC):

    def __init__(self, db_name: str, echo: bool = False) -> None:
        self.engine = create_engine(db_name, echo=echo, poolclass=NullPool)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_listen(self, listen_input: ListenInput) -> Listen:
        sql_listen = SqlAlchemyDbGateway._build_sql_listen(listen_input)
        self.session.add(sql_listen)
        self.session.commit()

        return SqlAlchemyDbGateway._pluck_listen(sql_listen)

    def fetch_listen(self, listen_id: str) -> Listen:
        query = self.session.query(SqlListen)
        query = query.filter(SqlListen.id == listen_id)

        sql_listen = query.first()
        if not sql_listen:
            raise exceptions.ListenDoesntExistError(f'Listen with id {listen_id} doesnt exist.')

        return SqlAlchemyDbGateway._pluck_listen(sql_listen)

    def fetch_listens(self,
                      limit: int,
                      sort_time: SortOrder,
                      before_utc: Optional[datetime] = None,
                      after_utc: Optional[datetime] = None) -> List[Listen]:
        query = self.session.query(SqlListen)

        if after_utc:
            query = query.filter(SqlListen.listen_time_utc > after_utc)

        if before_utc:
            query = query.filter(SqlListen.listen_time_utc < before_utc)

        sql_order_function = SqlAlchemyDbGateway._sql_order_function(sort_time)
        query = query.order_by(sql_order_function(SqlListen.listen_time_utc))

        query = query.limit(limit)

        return SqlAlchemyDbGateway._pluck_listens(cast(Iterable[SqlListen], query))

    @staticmethod
    def _build_sql_listen(listen_input: ListenInput) -> SqlListen:
        return SqlListen(
            song_id=listen_input.song_id,
            song_vendor=listen_input.song_provider,
            listener_name=listen_input.listener_name,
            listen_time_utc=listen_input.listen_time_utc,
            note=listen_input.note,
            iana_timezone=listen_input.iana_timezone
        )

    @staticmethod
    def _pluck_listens(sql_listens: Iterable[SqlListen]) -> List[Listen]:
        return [SqlAlchemyDbGateway._pluck_listen(sql_listen) for sql_listen in sql_listens]

    @staticmethod
    def _pluck_listen(sql_listen: SqlListen) -> Listen:
        return Listen(
            id=str(sql_listen.id),
            song_id=sql_listen.song_id,
            song_provider=sql_listen.song_vendor,
            listener_name=sql_listen.listener_name,
            listen_time_utc=sql_listen.listen_time_utc,
            note=sql_listen.note,
            iana_timezone=sql_listen.iana_timezone,
        )

    @staticmethod
    def _sql_order_function(sort_order: SortOrder) -> Callable:
        if sort_order == SortOrder.ASCENDING:
            return cast(Callable, asc)

        elif sort_order == SortOrder.DESCENDING:
            return cast(Callable, desc)

        else:
            raise LookupError('Invalid sort_order')

    def persist_schema(self) -> None:
        """Not part of the DbGatewayABC."""
        Base.metadata.create_all(self.engine)

    def close_connections(self) -> None:
        """Not part of the DbGatewayABC."""
        self.engine.dispose()
