from app import db
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    expenses = relationship('Expense', backref='user', lazy=True)
    earnings = relationship('Earning', backref='user', lazy=True)
    goals = relationship('Goal', backref='user', lazy=True)
    transactions = relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    def __repr__(self):
        return f'<User {self.username}>'


class Expense(db.Model):
    __tablename__ = 'expense'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Expense {self.description} - {self.amount}>'


class Earning(db.Model):
    __tablename__ = 'earning'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Earning {self.description} - {self.amount}>'


class Goal(db.Model):
    __tablename__ = 'goal'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)

    def __repr__(self):
        return f'<Goal {self.description} - {self.target_amount}>'


class Transaction(db.Model):
    __tablename__ = 'transaction'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.description} - {self.amount}>'
