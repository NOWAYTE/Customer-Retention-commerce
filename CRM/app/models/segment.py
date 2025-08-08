from .base import BaseModel
from app.extensions import db

@BaseModel.register('CustomerSegment')
class CustomerSegment(BaseModel):
    __tablename__ = 'customer_segments'

    customer_id = db.Column(db.Integer, primary_key=True)
    churn_prob = db.Column(db.Float, nullable=False)
    risk = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'CustomerID': self.customer_id,
            'Churn_Prob': self.churn_prob,
            'Risk': self.risk
        }
