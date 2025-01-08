from datetime import datetime
from enum import Enum
from app import db


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    EXPIRED = "expired"

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate = db.Column(db.Float, nullable=False, default=0.0)
    webhook_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)

    transactions = db.relationship('Transaction', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, balance={self.balance}, commission_rate={self.commission_rate})>"

    def is_admin(self):
        return self.role == UserRole.ADMIN


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='transactions')

    def __repr__(self):
        return (f"<Transaction(id={self.id}, amount={self.amount}, commission={self.commission}, "
                f"status={self.status.value}, user_id={self.user_id})>")
