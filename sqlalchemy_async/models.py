from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


# 设置默认 schema
class Base(DeclarativeBase):
    metadata_schema = "public"


# 示例模型：User
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self):
        return f"<User id={self.id} name={self.name}>"
