from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StringConstraints

# -----------------------------------------------------------------------
# Product 모델: 전자상거래 시스템의 상품 정보를 관리하는 핵심 도메인 모델
# - 상품의 기본 정보, 가격, 재고 등을 포함
# - SKU(Stock Keeping Unit)를 통한 고유 식별 시스템 구현
# - 재고 관리 및 상품 활성화/비활성화 상태 관리
# -----------------------------------------------------------------------

# 상품 카테고리 타입 정의 - 문자열 길이 제한으로 데이터 무결성 보장
CategoryType = Annotated[str, StringConstraints(min_length=1, max_length=50)]

# SKU(Stock Keeping Unit) 타입 정의 - 정규표현식으로 형식 검증
# 패턴: 대문자, 숫자, 하이픈만 허용하여 표준화된 SKU 형식 유지
SKUType = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9\-]{3,20}$")]


class ProductBase(BaseModel):
    """
    -----------------------------------------------------------------------
    ProductBase: 상품의 기본 속성들을 정의하는 베이스 모델
    - DDD(Domain Driven Design) 패턴 적용으로 도메인 로직 캡슐화
    - 모든 Product 관련 모델들이 상속받는 공통 스키마
    - Pydantic 검증을 통한 데이터 무결성 보장
    -----------------------------------------------------------------------
    """
    # 상품명 - 필수 필드, 길이 제한으로 UI/DB 호환성 보장
    name: str = Field(
        ...,  # 필수 필드 표시
        description="Product name",
        min_length=1,  # 빈 문자열 방지
        max_length=200,  # DB VARCHAR 제한 고려
        json_schema_extra={"example": "MacBook Pro 16-inch"},
    )
    
    # 상품 설명 - 선택적 필드, 마케팅 및 SEO 용도
    description: Optional[str] = Field(
        None,  # 선택적 필드
        description="Detailed product description",
        max_length=1000,  # 긴 설명 허용하되 제한
        json_schema_extra={"example": "High-performance laptop with M3 chip"},
    )
    
    # SKU - 재고 관리의 핵심 식별자, 비즈니스 로직에서 중요한 역할
    sku: SKUType = Field(
        ...,
        description="Stock Keeping Unit - unique product identifier (3-20 alphanumeric chars with hyphens)",
        json_schema_extra={"example": "MBP16-M3-512GB"},
    )
    
    # 카테고리 - 상품 분류 및 필터링을 위한 분류 체계
    category: CategoryType = Field(
        ...,
        description="Product category (1-50 characters)",
        json_schema_extra={"example": "Electronics"},
    )
    
    # 가격 - Decimal 사용으로 부동소수점 오차 방지 (금융 데이터의 정확성)
    price: Decimal = Field(
        ...,
        description="Product price in USD",
        gt=0,  # 0보다 큰 값만 허용 (음수 가격 방지)
        decimal_places=2,  # 센트 단위까지만 허용
        json_schema_extra={"example": 2499.99},
    )
    
    # 재고 수량 - 재고 관리 시스템의 핵심 데이터
    stock_quantity: int = Field(
        ...,
        description="Available stock quantity",
        ge=0,  # 음수 재고 방지
        json_schema_extra={"example": 50},
    )
    
    # 활성화 상태 - 상품 노출 제어를 위한 플래그 (소프트 삭제 패턴)
    is_active: bool = Field(
        True,  # 기본값: 활성화
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
