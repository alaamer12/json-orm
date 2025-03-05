# JsonDB

A zero-configuration, SQLModel-compatible JSON database for rapid development and prototyping.

## 🚀 Features

- **Zero Configuration**: Start coding immediately without database setup
- **SQLModel Compatible**: Same syntax as SQLModel/SQLAlchemy
- **Type Safe**: Full Python type hints and validation
- **Fast Development**: Perfect for prototypes and MVPs
- **Easy Migration**: Seamless transition to production databases

## 🎯 Perfect For

- Rapid prototyping
- MVP development
- Local development
- Testing and demos
- Small to medium projects
- Learning SQL and ORMs

## 📦 Installation

```bash
pip install jsondb
```

## 🏃 Quick Start

```python
from jsondb import Database, Model, Field, select
from typing import Optional, List
from datetime import datetime

# Define your model
class User(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.now)

# Initialize database
db = Database("myapp.json")

# Create records
user = User(username="john_doe", email="john@example.com")
db.add(user)
db.commit()

# Query data
users = select(User).where(User.username == "john_doe").first()
```

## 🔄 Migration to Production

When ready for production, migrate to SQLModel with the same code:

```python
from sqlmodel import SQLModel, create_engine

# Create SQLModel engine
engine = create_engine("postgresql://user:pass@localhost/dbname")

# Migrate schema
SQLModel.metadata.create_all(engine)

# Migrate data
db.migrate_to_sqlmodel(engine)
```

## 📚 Documentation

- [Features](FEATURES.md) - Supported SQL features
- [Examples](examples.py) - Code examples and patterns
- [Notes](NOTES.md) - Design notes and considerations

## 💡 Key Concepts

### Chunked Storage
Data is stored in manageable chunks for better performance:
```python
db = Database("myapp.json", chunk_size=1000)  # 1000 records per chunk
```

### Type Safety
Full type checking and validation:
```python
class Product(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
```

### Relationships
Support for all relationship types:
```python
class Post(Model):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: User = relationship(back_populates="posts")
```

## 🔍 Query Examples

```python
# Complex queries
users = (
    select(User)
    .where(User.age >= 18)
    .order_by(User.username)
    .limit(10)
)

# Joins
posts = (
    select(Post, User)
    .join(User)
    .where(User.username == "john_doe")
)

# Aggregations
stats = (
    select(User.country, func.count(User.id))
    .group_by(User.country)
    .having(func.count(User.id) > 10)
)
```

## ⚠️ Limitations

- Not for production use
- Limited to single-process access
- No advanced SQL features
- Best for datasets under 100GB
- No concurrent write operations

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by SQLModel and SQLAlchemy
- Built for developers who need a quick start
- Perfect for learning and prototyping

## 📬 Contact

- Issues: [GitHub Issues](https://github.com/yourusername/jsondb/issues)
- Questions: [GitHub Discussions](https://github.com/yourusername/jsondb/discussions)