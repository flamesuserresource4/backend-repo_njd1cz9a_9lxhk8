"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Offer(BaseModel):
    """
    Microfinance offers (MFO loans)
    Collection name: "offer"
    """
    name: str = Field(..., description="Provider name")
    apr: float = Field(..., ge=0, description="Annual percentage rate (APR) in %")
    min_amount: int = Field(..., ge=0, description="Minimum loan amount")
    max_amount: int = Field(..., ge=0, description="Maximum loan amount")
    term_min_days: int = Field(..., ge=1, description="Minimum term in days")
    term_max_days: int = Field(..., ge=1, description="Maximum term in days")
    approval_rate: Optional[float] = Field(None, ge=0, le=100, description="Estimated approval rate in %")
    rating: Optional[float] = Field(None, ge=0, le=5, description="User rating 0-5")
    description: Optional[str] = Field(None, description="Short description")
    link: Optional[HttpUrl] = Field(None, description="Application URL")
    tags: List[str] = Field(default_factory=list, description="Tags like 'быстро', 'без справок'")
