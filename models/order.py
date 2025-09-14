from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, StringConstraints

# 🛒 =========================================================================
# Order 모델: 전자상거래 주문 관리 시스템의 핵심 도메인 모델!!
# - 복잡한 비즈니스 로직을 포함한 주문 생명주기 관리!! 📊
# - 고객, 상품, 결제 정보를 통합하는 집계 루트(Aggregate Root) 역할!! 🎯
# - 주문 상태 기계(State Machine) 패턴 적용!! 상태 전이 완벽 관리!! ⚡
# - 전자상거래에서 가장 복잡하고 중요한 모델!! 💰
# =========================================================================

# 📊 주문 상태 열거형 - 주문의 생명주기를 명확히 정의!! 매우 중요!!
# 상태 전이: PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED ✅
# 또는 언제든지 CANCELLED로 전이 가능!! 비즈니스 규칙에 따라!! ❌
class OrderStatus(str, Enum):
    PENDING = "pending"        # 💳 결제 대기 중!! 아직 결제 안됨!!
    CONFIRMED = "confirmed"    # ✅ 결제 완료!! 처리 대기 상태!!
    PROCESSING = "processing"  # 📦 주문 처리 중!! 포장, 준비 단계!!
    SHIPPED = "shipped"        # 🚚 배송 시작!! 고객에게 이동 중!!
    DELIVERED = "delivered"    # 🎉 배송 완료!! 고객이 받음!!
    CANCELLED = "cancelled"    # ❌ 주문 취소!! 더 이상 진행 안됨!!

# 🏷️ 주문번호 타입 정의 - 표준화된 주문번호 형식 강제!! 매우 중요!!
# 형식: ORD-YYYYMMDD-NNNN (예: ORD-20250913-0001) 📅
# 날짜 기반으로 주문 추적 및 정렬 용이성 제공!! 운영팀이 좋아함!! 👍
OrderNumberType = Annotated[str, StringConstraints(pattern=r"^ORD-\d{8}-\d{4}$")]


class OrderItem(BaseModel):
    """
    -----------------------------------------------------------------------
    OrderItem: 주문 내 개별 상품 항목을 나타내는 값 객체(Value Object)
    - 주문 시점의 상품 정보를 스냅샷으로 보존 (가격 변동 대응)
    - 비정규화된 데이터 구조로 조회 성능 최적화
    - 주문 후 상품 정보 변경이 기존 주문에 영향 주지 않도록 설계
    -----------------------------------------------------------------------
    """
    # 상품 참조 ID - 외래키 역할, 상품 상세 정보 조회 시 사용
    product_id: UUID = Field(
        ...,
        description="Reference to the Product ID",
        json_schema_extra={"example": "12345678-1234-4123-8123-123456789012"},
    )
    
    # 상품명 캐시 - 조회 성능 향상을 위한 비정규화 (CQRS 패턴)
    product_name: str = Field(
        ...,
        description="Product name (cached for convenience)",
        json_schema_extra={"example": "MacBook Pro 16-inch"},
    )
    
    # 주문 수량 - 양수만 허용하여 비즈니스 규칙 강제
    quantity: int = Field(
        ...,
        description="Quantity ordered",
        gt=0,  # 0개 주문 방지
        json_schema_extra={"example": 2},
    )
    
    # 주문 시점 단가 - 가격 변동에 영향받지 않는 주문 당시 가격 보존
    unit_price: Decimal = Field(
        ...,
        description="Price per unit at time of order",
        gt=0,  # 음수 가격 방지
        decimal_places=2,  # 통화 정밀도
        json_schema_extra={"example": 2499.99},
    )
    
    # 항목별 소계 - 계산된 값이지만 명시적 저장으로 일관성 보장
    subtotal: Decimal = Field(
        ...,
        description="Total for this item (quantity × unit_price)",
        gt=0,  # 음수 소계 방지
        decimal_places=2,  # 통화 정밀도
        json_schema_extra={"example": 4999.98},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "12345678-1234-4123-8123-123456789012",
                    "product_name": "MacBook Pro 16-inch",
                    "quantity": 2,
                    "unit_price": 2499.99,
                    "subtotal": 4999.98,
                }
            ]
        }
    }


class OrderBase(BaseModel):
    order_number: OrderNumberType = Field(
        ...,
        description="Unique order number (format: ORD-YYYYMMDD-NNNN)",
        json_schema_extra={"example": "ORD-20250913-0001"},
    )
    customer_id: UUID = Field(
        ...,
        description="Reference to the Person (customer) ID",
        json_schema_extra={"example": "99999999-9999-4999-8999-999999999999"},
    )
    customer_name: str = Field(
        ...,
        description="Customer name (cached for convenience)",
        json_schema_extra={"example": "Ada Lovelace"},
    )
    customer_email: str = Field(
        ...,
        description="Customer email (cached for convenience)",
        json_schema_extra={"example": "ada@example.com"},
    )
    items: List[OrderItem] = Field(
        ...,
        description="List of ordered items",
        min_length=1,
    )
    subtotal: Decimal = Field(
        ...,
        description="Sum of all item subtotals",
        gt=0,
        decimal_places=2,
        json_schema_extra={"example": 4999.98},
    )
    tax_amount: Decimal = Field(
        ...,
        description="Tax amount",
        ge=0,
        decimal_places=2,
        json_schema_extra={"example": 399.99},
    )
    shipping_amount: Decimal = Field(
        ...,
        description="Shipping cost",
        ge=0,
        decimal_places=2,
        json_schema_extra={"example": 29.99},
    )
    total_amount: Decimal = Field(
        ...,
        description="Total order amount (subtotal + tax + shipping)",
        gt=0,
        decimal_places=2,
        json_schema_extra={"example": 5429.96},
    )
    status: OrderStatus = Field(
        OrderStatus.PENDING,
        description="Current order status",
        json_schema_extra={"example": "pending"},
    )
    shipping_address: str = Field(
        ...,
        description="Shipping address (formatted as single string)",
        json_schema_extra={"example": "123 Main St, New York, NY 10001, USA"},
    )
    notes: Optional[str] = Field(
        None,
        description="Additional order notes or instructions",
        max_length=500,
        json_schema_extra={"example": "Please deliver to front desk"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_number": "ORD-20250913-0001",
                    "customer_id": "99999999-9999-4999-8999-999999999999",
                    "customer_name": "Ada Lovelace",
                    "customer_email": "ada@example.com",
                    "items": [
                        {
                            "product_id": "12345678-1234-4123-8123-123456789012",
                            "product_name": "MacBook Pro 16-inch",
                            "quantity": 2,
                            "unit_price": 2499.99,
                            "subtotal": 4999.98,
                        }
                    ],
                    "subtotal": 4999.98,
                    "tax_amount": 399.99,
                    "shipping_amount": 29.99,
                    "total_amount": 5429.96,
                    "status": "pending",
                    "shipping_address": "123 Main St, New York, NY 10001, USA",
                    "notes": "Please deliver to front desk",
                }
            ]
        }
    }


class OrderCreate(OrderBase):
    """Creation payload for an Order."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_number": "ORD-20250913-0002",
                    "customer_id": "88888888-8888-4888-8888-888888888888",
                    "customer_name": "Grace Hopper",
                    "customer_email": "grace.hopper@navy.mil",
                    "items": [
                        {
                            "product_id": "11111111-1111-4111-8111-111111111111",
                            "product_name": "iPhone 15 Pro",
                            "quantity": 1,
                            "unit_price": 999.99,
                            "subtotal": 999.99,
                        }
                    ],
                    "subtotal": 999.99,
                    "tax_amount": 79.99,
                    "shipping_amount": 9.99,
                    "total_amount": 1089.97,
                    "status": "pending",
                    "shipping_address": "1701 E St NW, Washington, DC 20552, USA",
                    "notes": "Express delivery requested",
                }
            ]
        }
    }


class OrderUpdate(BaseModel):
    """Partial update for an Order; supply only fields to change."""
    status: Optional[OrderStatus] = Field(
        None,
        description="Order status",
        json_schema_extra={"example": "confirmed"},
    )
    shipping_address: Optional[str] = Field(
        None,
        description="Updated shipping address",
        json_schema_extra={"example": "456 Oak Ave, Brooklyn, NY 11201, USA"},
    )
    notes: Optional[str] = Field(
        None,
        description="Updated order notes",
        max_length=500,
        json_schema_extra={"example": "Updated delivery instructions"},
    )
    # Note: Items, amounts, and customer info typically shouldn't be updated after creation
    # but we could add them here if business rules allow

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "confirmed"},
                {"status": "shipped"},
                {"shipping_address": "456 Oak Ave, Brooklyn, NY 11201, USA"},
                {"notes": "Customer requested expedited shipping"},
            ]
        }
    }


class OrderRead(OrderBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Order ID",
        json_schema_extra={"example": "87654321-4321-4321-8321-210987654321"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Order creation timestamp (UTC)",
        json_schema_extra={"example": "2025-09-13T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
        json_schema_extra={"example": "2025-09-13T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "87654321-4321-4321-8321-210987654321",
                    "order_number": "ORD-20250913-0001",
                    "customer_id": "99999999-9999-4999-8999-999999999999",
                    "customer_name": "Ada Lovelace",
                    "customer_email": "ada@example.com",
                    "items": [
                        {
                            "product_id": "12345678-1234-4123-8123-123456789012",
                            "product_name": "MacBook Pro 16-inch",
                            "quantity": 2,
                            "unit_price": 2499.99,
                            "subtotal": 4999.98,
                        }
                    ],
                    "subtotal": 4999.98,
                    "tax_amount": 399.99,
                    "shipping_amount": 29.99,
                    "total_amount": 5429.96,
                    "status": "pending",
                    "shipping_address": "123 Main St, New York, NY 10001, USA",
                    "notes": "Please deliver to front desk",
                    "created_at": "2025-09-13T10:20:30Z",
                    "updated_at": "2025-09-13T12:00:00Z",
                }
            ]
        }
    }
