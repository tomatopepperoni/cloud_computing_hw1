from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StringConstraints

# =========================================================================
# Product Model: 전자상거래 시스템의 상품 정보를 관리하는 핵심 도메인 모델!!
# - 상품의 basic info, 가격, inventory 등을 포함!!
# - SKU(Stock Keeping Unit)를 통한 unique identification system 구현!!
# - 재고 관리 및 상품 activation/deactivation 상태 관리!!
# - Pydantic v2를 사용한 강력한 data validation!! super important~~~
# =========================================================================

# Product Category Type Definition - string length constraint로 data integrity 보장!!
# minimum 1자, maximum 50자로 제한해서 DB performance optimization!! 
CategoryType = Annotated[str, StringConstraints(min_length=1, max_length=50)]

# SKU(Stock Keeping Unit) Type Definition - regex pattern으로 format validation!!
# Pattern: 대문자, 숫자, hyphen만 허용하여 standardized SKU format 유지!! 
# Examples: "MBP-2024", "IPH15-256GB" 등등~~ very important!!
SKUType = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9\-]{3,20}$")]


class ProductBase(BaseModel):
    """
    ===================================================================
    ProductBase: 상품의 basic attributes들을 정의하는 base model!! 
    - DDD(Domain Driven Design) pattern 적용으로 domain logic encapsulation!!
    - 모든 Product related models들이 inherit받는 common schema!!
    - Pydantic validation을 통한 data integrity 보장!! super critical~~~
    - E-commerce의 core!! product information을 perfectly manage!!
    ===================================================================
    """
    # Product Name - required field!! length limit으로 UI/DB compatibility 보장!!
    name: str = Field(
        ...,  # required field 표시!! 절대 empty하면 안됨!!
        description="Product name",
        min_length=1,  # empty string 방지!! minimum 1글자는 있어야 함!!
        max_length=200,  # DB VARCHAR limit 고려!! 너무 길면 DB crash!!
        json_schema_extra={"example": "MacBook Pro 16-inch"},
    )
    
    # Product Description - optional field!! marketing 및 SEO purpose로 important!!
    description: Optional[str] = Field(
        None,  # optional field!! 없어도 OK~~
        description="Detailed product description",
        max_length=1000,  # long description 허용하되 limit!! 너무 길면 performance degradation!!
        json_schema_extra={"example": "High-performance laptop with M3 chip"},
    )
    
    # SKU - inventory management의 핵심 identifier!! business logic에서 crucial role!!
    sku: SKUType = Field(
        ...,  # required!! SKU 없으면 inventory management impossible!!
        description="Stock Keeping Unit - unique product identifier (3-20 alphanumeric chars with hyphens)",
        json_schema_extra={"example": "MBP16-M3-512GB"},
    )
    
    # Category - product classification 및 filtering을 위한 taxonomy!! search에 essential!!
    category: CategoryType = Field(
        ...,  # required!! category 없으면 classification impossible!!
        description="Product category (1-50 characters)",
        json_schema_extra={"example": "Electronics"},
    )
    
    # Price - Decimal 사용으로 floating point error 방지!! financial data의 accuracy!!
    price: Decimal = Field(
        ...,  # required!! price 없는 product는 있을 수 없음!!
        description="Product price in USD",
        gt=0,  # 0보다 큰 값만 allow!! negative price 방지!! no free lunch~~
        decimal_places=2,  # cent 단위까지만 allow!! $99.99 format!!
        json_schema_extra={"example": 2499.99},
    )
    
    # Stock Quantity - inventory management system의 core data!! extremely important!!
    stock_quantity: int = Field(
        ...,  # required!! stock quantity 모르면 sale impossible!!
        description="Available stock quantity",
        ge=0,  # negative inventory 방지!! minus stock은 말이 안됨!!
        json_schema_extra={"example": 50},
    )
    
    # Active Status - product exposure control을 위한 flag!! soft delete pattern!!
    is_active: bool = Field(
        True,  # default: active!! new product는 기본적으로 active!!
        description="Whether the product is active/available for sale",
        json_schema_extra={"example": True},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "MacBook Pro 16-inch",
                    "description": "High-performance laptop with M3 chip",
                    "sku": "MBP16-M3-512GB",
                    "category": "Electronics",
                    "price": 2499.99,
                    "stock_quantity": 50,
                    "is_active": True,
                }
            ]
        }
    }


class ProductCreate(ProductBase):
    """
    -----------------------------------------------------------------------
    ProductCreate: 새 상품 생성 시 클라이언트로부터 받는 데이터 모델
    - HTTP POST 요청의 request body로 사용
    - 서버 생성 필드(id, timestamps)는 제외
    - 클라이언트 입력 검증의 첫 번째 관문 역할
    -----------------------------------------------------------------------
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "iPhone 15 Pro",
                    "description": "Latest iPhone with titanium design",
                    "sku": "IPH15PRO-256GB",
                    "category": "Smartphones",
                    "price": 999.99,
                    "stock_quantity": 100,
                    "is_active": True,
                }
            ]
        }
    }


class ProductUpdate(BaseModel):
    """
    -----------------------------------------------------------------------
    ProductUpdate: 상품 정보 부분 수정을 위한 DTO (Data Transfer Object)
    - HTTP PATCH 요청에 사용 (부분 업데이트 지원)
    - 모든 필드가 Optional로 설정되어 선택적 업데이트 가능
    - 비즈니스 로직: 변경되지 않은 필드는 기존 값 유지
    -----------------------------------------------------------------------
    """
    name: Optional[str] = Field(
        None,
        description="Product name",
        min_length=1,
        max_length=200,
        json_schema_extra={"example": "MacBook Pro 16-inch (Updated)"},
    )
    description: Optional[str] = Field(
        None,
        description="Product description",
        max_length=1000,
        json_schema_extra={"example": "Updated product description"},
    )
    sku: Optional[SKUType] = Field(
        None,
        description="Stock Keeping Unit",
        json_schema_extra={"example": "MBP16-M3-1TB"},
    )
    category: Optional[CategoryType] = Field(
        None,
        description="Product category",
        json_schema_extra={"example": "Computers"},
    )
    price: Optional[Decimal] = Field(
        None,
        description="Product price in USD",
        gt=0,
        decimal_places=2,
        json_schema_extra={"example": 2699.99},
    )
    stock_quantity: Optional[int] = Field(
        None,
        description="Available stock quantity",
        ge=0,
        json_schema_extra={"example": 25},
    )
    is_active: Optional[bool] = Field(
        None,
        description="Product availability status",
        json_schema_extra={"example": False},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"price": 2299.99, "stock_quantity": 30},
                {"is_active": False},
                {"description": "Updated with latest features"},
            ]
        }
    }


class ProductRead(ProductBase):
    """
    -----------------------------------------------------------------------
    ProductRead: 클라이언트에게 반환되는 완전한 상품 정보 모델
    - HTTP GET 응답 및 생성/수정 후 응답에 사용
    - 서버 관리 필드들(id, timestamps) 포함
    - 감사(Audit) 정보를 통한 데이터 추적성 제공
    -----------------------------------------------------------------------
    """
    # 서버 생성 UUID - 시스템 내 상품의 고유 식별자
    id: UUID = Field(
        default_factory=uuid4,  # 자동 생성되는 UUID
        description="Server-generated Product ID",
        json_schema_extra={"example": "12345678-1234-4123-8123-123456789012"},
    )
    
    # 생성 타임스탬프 - 감사 로그 및 데이터 분석용
    created_at: datetime = Field(
        default_factory=datetime.utcnow,  # 생성 시점 자동 기록
        description="Creation timestamp (UTC)",
        json_schema_extra={"example": "2025-09-13T10:20:30Z"},
    )
    
    # 수정 타임스탬프 - 변경 이력 추적용
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,  # 수정 시점 자동 기록
        description="Last update timestamp (UTC)",
        json_schema_extra={"example": "2025-09-13T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "12345678-1234-4123-8123-123456789012",
                    "name": "MacBook Pro 16-inch",
                    "description": "High-performance laptop with M3 chip",
                    "sku": "MBP16-M3-512GB",
                    "category": "Electronics",
                    "price": 2499.99,
                    "stock_quantity": 50,
                    "is_active": True,
                    "created_at": "2025-09-13T10:20:30Z",
                    "updated_at": "2025-09-13T12:00:00Z",
                }
            ]
        }
    }
