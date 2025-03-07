from app import db
from sqlalchemy import Table, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

# Define the User model with extend_existing=True
class User(db.Model):
    __table__ = Table(
        'user',
        db.Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String(80), unique=True, nullable=False),
        Column('password', String(200), nullable=False),
        extend_existing=True
    )
    expenses = relationship('Expense', backref='user', lazy=True)
    earnings = relationship('Earning', backref='user', lazy=True)
    goals = relationship('Goal', backref='user', lazy=True)
    transactions = relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Expense(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    def __repr__(self):
        return f'<Expense {self.description} - {self.amount}>'


class Earning(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    def __repr__(self):
        return f'<Earning {self.description} - {self.amount}>'


class Goal(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)

    def __repr__(self):
        return f'<Goal {self.description} - {self.target_amount}>'


class Transaction(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.description} - {self.amount}>'
