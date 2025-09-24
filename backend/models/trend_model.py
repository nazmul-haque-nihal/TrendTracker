# backend/models/trend_model.py
from backend import db
from datetime import datetime

class Trend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text) # Optional description field
    url = db.Column(db.String(500), nullable=False)
    platform = db.Column(db.String(50), nullable=False) # e.g., 'youtube', 'reddit'
    platform_id = db.Column(db.String(100), nullable=False) # Unique ID on the platform
    author = db.Column(db.String(150)) # Channel/Author name
    thumbnail_url = db.Column(db.String(500))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    engagement_score = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer) # Duration in seconds
    category = db.Column(db.String(100)) # e.g., 'funny', 'sad', 'anime'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'author': self.author,
            'thumbnail_url': self.thumbnail_url,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'engagement_score': self.engagement_score,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'duration': self.duration,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Trend {self.title}>'