from database import db
from datetime import datetime

class Meal(db.Model):
    # id, nome, descrição, data/hora, está na dieta?, user_id
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_on_diet = db.Column(db.Boolean, nullable=False, default=True)
    
    # Chave estrangeira para o usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'datetime': self.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'is_on_diet': self.is_on_diet,
            'user_id': self.user_id
        }