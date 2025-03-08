from datetime import datetime
from typing import Optional, List
from json-orm import (
    Model, 
    Field, 
    select, 
    relationship,
    and_, 
    or_, 
    desc,
    Database
)

# Define models with relationships
class User(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    age: int = Field(index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    posts: List["Post"] = relationship(back_populates="author")
    profile: Optional["UserProfile"] = relationship(back_populates="user")

class Post(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    views: int = Field(default=0)
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    author: User = relationship(back_populates="posts")
    tags: List["Tag"] = relationship(back_populates="posts", link_model="PostTag")

class UserProfile(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    bio: Optional[str]
    avatar_url: Optional[str]
    
    # Relationships
    user: User = relationship(back_populates="profile")

class Tag(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    
    # Many-to-many relationship
    posts: List[Post] = relationship(back_populates="tags", link_model="PostTag")

# Usage Examples
def main():
    # Initialize database
    db = Database("myapp.json")
    
    # Create new user with profile
    with db.transaction():
        user = User(
            username="john_doe",
            email="john@example.com",
            age=30
        )
        db.add(user)
        
        profile = UserProfile(
            user=user,
            bio="Python developer",
            avatar_url="https://example.com/avatar.jpg"
        )
        db.add(profile)
    
    # Complex queries
    active_users = (
        select(User) # SELECT User WHERE is_active = True AND age >= 18 ORDER BY created_at DESC LIMIT 10
        .where(
            and_(
                User.age >= 18,
                User.is_active == True
            )
        )
        .order_by(desc(User.created_at))
        .limit(10)
        .offset(0)
    )
    
    # Joins and relationships
    user_posts = (
        select(User, Post)
        .join(Post)
        .where(User.username == "john_doe")
        .options(relationship(User.posts))
    )
    
    # Aggregations
    post_stats = (
        select(Post.author_id, func.count(Post.id).label("post_count"))
        .group_by(Post.author_id)
        .having(func.count(Post.id) > 5)
    )
    
    # Bulk operations
    db.bulk_insert(User, [
        {"username": "user1", "email": "user1@example.com", "age": 25},
        {"username": "user2", "email": "user2@example.com", "age": 30},
    ])
    
    # Update operations
    (
        update(User)
        .where(User.age < 18)
        .values(is_active=False)
    )
    
    # Delete operations
    (
        delete(Post)
        .where(Post.views == 0)
        .where(Post.created_at < datetime(2024, 1, 1))
    )
    
    # Full text search (if configured)
    posts = (
        select(Post)
        .where(Post.content.match("python programming"))
        .order_by(Post.views.desc())
    )
    
    # Eager loading relationships
    users_with_posts = (
        select(User)
        .options(
            joinedload(User.posts),
            joinedload(User.profile)
        )
        .where(User.is_active == True)
    )
    
    # Pagination helper
    def get_paginated_posts(page: int = 1, per_page: int = 10):
        return (
            select(Post)
            .order_by(desc(Post.created_at))
            .paginate(page=page, per_page=per_page)
        )
    
    # Migration to SQLModel example
    def migrate_to_sqlmodel():
        from sqlmodel import SQLModel, create_engine
        
        # Create SQLModel engine
        engine = create_engine("postgresql://user:pass@localhost/dbname")
        
        # Migrate schema
        SQLModel.metadata.create_all(engine)
        
        # Migrate data
        for user in select(User):
            # User model is compatible with SQLModel
            db.migrate_record(user, engine)

if __name__ == "__main__":
    main()
