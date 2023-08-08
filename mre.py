import sqlalchemy as sa  # 1.3.24
from sqlalchemy.ext.declarative import declarative_base

engine = sa.create_engine("postgresql+psycopg2://postgres:password@127.0.0.1/mre")

Base = declarative_base()


class PortfolioWell(Base):
    __tablename__ = "portfolio_well"

    id = sa.Column(sa.Integer, primary_key=True)
    portfolio_id = sa.Column(sa.Integer)
    well_id = sa.Column(sa.Integer)


class OwnerNumber(Base):
    __tablename__ = "owner_number"

    id = sa.Column(sa.Integer, primary_key=True)
    portfolio_id = sa.Column(sa.Integer)


class OwnerNumberWell(Base):
    __tablename__ = "owner_number_well"

    id = sa.Column(sa.Integer, primary_key=True)
    owner_number_id = sa.Column(sa.Integer, sa.ForeignKey(OwnerNumber.id))
    well_id = sa.Column(sa.Integer)

    portfolio_well = sa.orm.relationship(
        PortfolioWell,
        primaryjoin=sa.and_(
            owner_number_id == OwnerNumber.id,
            well_id == PortfolioWell.well_id,
        ),
        secondary=OwnerNumber.__table__,
        secondaryjoin=PortfolioWell.portfolio_id == OwnerNumber.portfolio_id,
        uselist=False,
        viewonly=True,
    )


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sa.orm.sessionmaker(bind=engine)
session = Session()

PORTFOLIO_ID = 1
WELL_ID = 1

portfolio_well = PortfolioWell(portfolio_id=PORTFOLIO_ID, well_id=WELL_ID)
owner_number = OwnerNumber(portfolio_id=PORTFOLIO_ID)
session.add_all([portfolio_well, owner_number])
session.commit()

owner_number_well = OwnerNumberWell(owner_number_id=owner_number.id, well_id=WELL_ID)
session.add(owner_number_well)
session.commit()

assert owner_number_well.portfolio_well == portfolio_well
assert (
    session.query(OwnerNumberWell)
    .options(sa.orm.joinedload(OwnerNumberWell.portfolio_well))
    .one()
    .portfolio_well
    == portfolio_well
)
