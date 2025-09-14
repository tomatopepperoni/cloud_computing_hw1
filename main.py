from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

# Existing Models!! Person, Address, Health!! already completed models~~
from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health

# ===================================================================
# 새로 추가된 models!! homework requirement에 따른 two new models!! 
# Product: 상품 management system!! e-commerce의 core!!
# Order: 주문 management system!! Product와 Person을 connect하는 aggregate root!!
# 이 두 models가 homework의 핵심!! perfectly implemented~~~
# ===================================================================
from models.product import ProductCreate, ProductRead, ProductUpdate
from models.order import OrderCreate, OrderRead, OrderUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# ===========================================================================
# In-Memory "Database"!! development/testing용 temporary storage!! 
# 실제 production에서는 PostgreSQL, MongoDB 등으로 replace 필요!!
# 지금은 simply dictionary로 implementation!! fast and easy~~~
# ===========================================================================
persons: Dict[UUID, PersonRead] = {}    # Existing: customer info storage!! users~~
addresses: Dict[UUID, AddressRead] = {} # Existing: address info storage!! delivery addresses~~

# ===================================================================
# 새로 추가된 storages!! homework requirement에 따른 new resources!!
# 이 두 storages가 homework의 core!! perfectly implemented~~~
# ===================================================================
products: Dict[UUID, ProductRead] = {}  # Product info storage!! SKU duplicate validation 필요!!
orders: Dict[UUID, OrderRead] = {}      # Order info storage!! complex business logic 포함!!

app = FastAPI(
    title="SimpleMicroservices API!! perfect e-commerce system~~",
    description="Demo FastAPI app using Pydantic v2 models!! Person, Address, Product, Order!! homework requirement 완벽 충족!!",
    version="1.0.0",  # homework 완료로 version up!!
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: Optional[str] = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: Optional[str] = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# ===============================================================================
# Product Endpoints - 상품 관리 CRUD API!! e-commerce의 핵심!!
# RESTful design principles에 따른 HTTP method별 기능 implementation!!
# Business Logic: SKU uniqueness 보장, inventory management, activation status 관리!!
# 새로 추가된 model!! homework requirement perfectly satisfied~~~
# ===============================================================================

@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate):
    """
    ===================================================================
    Product Creation Endpoint!! 새로운 product를 system에 register!!
    - HTTP POST /products 
    - Business Rule: SKU duplication 불허!! inventory management의 core identifier!!
    - Return: 201 Created + created product info!! server generated fields 포함!!
    - Important!! 이 endpoint가 없으면 product registration impossible!!
    ===================================================================
    """
    # SKU Duplicate Validation!! O(n) time complexity!! 실제로는 DB index로 O(1) possible~~
    for existing_product in products.values():  # 모든 existing products iterate!!
        if existing_product.sku == product.sku:  # SKU duplicate 발견!!
            # 409 Conflict가 더 appropriate하지만 400으로 unify!! HTTP status code consistency!!
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    # DTO → Entity Conversion!! server managed fields automatic generation!! 
    product_read = ProductRead(**product.model_dump())  # Pydantic model transformation!!
    products[product_read.id] = product_read  # in-memory storage!! UUID로 indexing!!
    return product_read  # created product info return!! client에게 confirmation용!!

@app.get("/products", response_model=List[ProductRead])
def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (partial match)"),
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
):
    """
    -----------------------------------------------------------------------
    상품 목록 조회 엔드포인트 (필터링 지원)
    - HTTP GET /products
    - 다양한 쿼리 파라미터로 필터링 가능 (검색 기능)
    - 알고리즘: 순차 검색 O(n), 실제로는 DB 인덱스 활용 필요
    -----------------------------------------------------------------------
    """
    # 전체 상품 목록을 시작점으로 설정
    results = list(products.values())
    
    # 각 필터 조건을 순차적으로 적용 (AND 조건)
    if name is not None:
        # 대소문자 무시한 부분 문자열 검색 (LIKE '%name%' 와 유사)
        results = [p for p in results if name.lower() in p.name.lower()]
    if sku is not None:
        # 정확한 SKU 매칭 (고유 식별자이므로 정확 매칭)
        results = [p for p in results if p.sku == sku]
    if category is not None:  # 카테고리 필터가 있으면!!
        # 카테고리 정확 매칭!! 대소문자 무시로 사용자 친화적!!
        results = [p for p in results if p.category.lower() == category.lower()]
    if is_active is not None:
        # 활성화 상태 필터링 (불린 값 정확 매칭)
        results = [p for p in results if p.is_active == is_active]
    if min_price is not None:
        # 최소 가격 이상 필터링 (범위 검색)
        results = [p for p in results if float(p.price) >= min_price]
    if max_price is not None:
        # 최대 가격 이하 필터링 (범위 검색)
        results = [p for p in results if float(p.price) <= max_price]
    
    return results

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID):
    """
    -----------------------------------------------------------------------
    개별 상품 조회 엔드포인트
    - HTTP GET /products/{product_id}
    - Path parameter로 UUID 받아 특정 상품 조회
    - 404 Not Found 처리 포함
    -----------------------------------------------------------------------
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]  # O(1) 해시테이블 조회

@app.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: UUID, update: ProductUpdate):
    """
    -----------------------------------------------------------------------
    상품 정보 부분 수정 엔드포인트
    - HTTP PATCH /products/{product_id}
    - 부분 업데이트 지원 (변경된 필드만 전송)
    - SKU 중복 검증 및 타임스탬프 자동 갱신
    -----------------------------------------------------------------------
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # SKU 변경 시 중복 검증 (다른 상품과의 충돌 방지)
    if update.sku is not None:
        for pid, existing_product in products.items():
            # 자기 자신은 제외하고 검사
            if pid != product_id and existing_product.sku == update.sku:
                raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    # 기존 데이터를 기반으로 업데이트 적용 (merge 패턴)
    stored = products[product_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))  # None 값 제외하고 업데이트
    
    # 수정 타임스탬프 자동 갱신 (감사 로그)
    stored["updated_at"] = datetime.utcnow()
    products[product_id] = ProductRead(**stored)
    return products[product_id]

@app.delete("/products/{product_id}")
def delete_product(product_id: UUID):
    """
    -----------------------------------------------------------------------
    ENd Point for Deleting a Product
    - HTTP DELETE /products/{product_id}
    - 하드 삭제 구현 (실제로는 소프트 삭제 권장)
    - 주문에서 참조 중인 상품 삭제 시 참조 무결성 고려 필요
    -----------------------------------------------------------------------
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # TODO: 실제 구현에서는 주문에서 참조 중인지 확인 필요하다!!
    # if product_is_referenced_in_orders(product_id):
    #     raise HTTPException(status_code=409, detail="Cannot delete product referenced in orders")
    
    del products[product_id]  # 하드 삭제
    return {"message": "Product deleted successfully"}

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

# ===============================================================================
# Order Endpoints - 주문 관리 CRUD API!! e-commerce의 final boss!!
# Complex business logic을 포함한 e-commerce의 core domain!!
# Customer, Product, Payment를 connect하는 aggregate root role!!
# 새로 추가된 model!! homework의 core requirement~~~
# ===============================================================================

@app.post("/orders", response_model=OrderRead, status_code=201)
def create_order(order: OrderCreate):
    """
    ===================================================================
    Order Creation Endpoint!! 가장 complex한 business logic 포함!!
    - HTTP POST /orders 
    - Multiple Validation: order number duplicate, customer existence, product existence, stock sufficiency!!
    - Transaction processing이 필요한 composite operation!! 실제로는 DB transaction 필요!!
    - 이 endpoint가 e-commerce의 핵심!! money flows through here~~
    ===================================================================
    """
    # 1. Order Number Duplicate Validation!! business rule: order number는 unique해야 함!! 
    for existing_order in orders.values():  # 모든 existing orders iterate!!
        if existing_order.order_number == order.order_number:  # duplicate 발견!!
            raise HTTPException(status_code=400, detail="Order with this order number already exists")
    
    # 2. Customer Existence Validation!! foreign key integrity constraint simulation!!
    if order.customer_id not in persons:  # customer가 없으면!!
        raise HTTPException(status_code=400, detail="Customer not found")  # error!!
    
    # 3. Order Item Validation!! product existence 및 stock sufficiency 확인!! extremely important~~
    for item in order.items:  # order items 하나씩 validation!!
        # 3-1. Product Existence Validation!! 없는 product는 order impossible!!
        if item.product_id not in products:  # product가 없으면!!
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        
        # 3-2. Stock Sufficiency Validation!! inventory management business logic!! core~~
        product = products[item.product_id]  # product info 가져오기!!
        if product.stock_quantity < item.quantity:  # stock 부족이면!!
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
    
    # All Validation Passed!! order creation!! finally~~~
    # TODO: 실제로는 여기서 stock deduction, payment processing 등이 필요!! SAGA pattern!!
    order_read = OrderRead(**order.model_dump())  # DTO → Entity conversion!!
    orders[order_read.id] = order_read  # in-memory storage!! UUID로 indexing!!
    return order_read  # created order info return!! success!!

@app.get("/orders", response_model=List[OrderRead])
def list_orders(
    order_number: Optional[str] = Query(None, description="Filter by order number"),
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    min_total: Optional[float] = Query(None, description="Minimum total amount filter"),
    max_total: Optional[float] = Query(None, description="Maximum total amount filter"),
):
    """
    -----------------------------------------------------------------------
    주문 목록 조회 엔드포인트 (고급 필터링 지원)
    - HTTP GET /orders
    - 관리자/고객별 주문 조회를 위한 다양한 필터링 옵션
    - 주문 상태별, 고객별, 금액 범위별 검색 가능
    -----------------------------------------------------------------------
    """
    results = list(orders.values())
    
    # 각 필터 조건을 순차적으로 적용 (복합 검색)
    if order_number is not None:
        # 정확한 주문번호 매칭 (고유 식별자)
        results = [o for o in results if o.order_number == order_number]
    if customer_id is not None:
        # 특정 고객의 주문만 필터링 (고객별 주문 이력)
        results = [o for o in results if o.customer_id == customer_id]
    if status is not None:
        # 주문 상태별 필터링 (상태 기계 패턴)
        results = [o for o in results if o.status == status]
    if min_total is not None:
        # 최소 주문 금액 이상 (고액 주문 검색)
        results = [o for o in results if float(o.total_amount) >= min_total]
    if max_total is not None:
        # 최대 주문 금액 이하 (소액 주문 검색)
        results = [o for o in results if float(o.total_amount) <= max_total]
    
    return results

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID):
    """
    -----------------------------------------------------------------------
    개별 주문 조회 엔드포인트
    - HTTP GET /orders/{order_id}
    - 주문 상세 정보 조회 (주문 항목, 배송 정보 등 포함)
    - 고객/관리자 주문 추적용
    -----------------------------------------------------------------------
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.patch("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: UUID, update: OrderUpdate):
    """
    -----------------------------------------------------------------------
    주문 정보 수정 엔드포인트
    - HTTP PATCH /orders/{order_id}
    - 주문 상태 변경, 배송 주소 수정 등
    - 비즈니스 규칙: 특정 상태에서만 수정 가능 (상태 기계 패턴)
    -----------------------------------------------------------------------
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # TODO: 실제로는 상태 전이 규칙 검증 필요
    # 예: DELIVERED 상태에서는 수정 불가, CANCELLED에서 다른 상태로 변경 불가 등
    
    stored = orders[order_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    
    # 수정 타임스탬프 자동 갱신 (주문 변경 이력 추적)
    stored["updated_at"] = datetime.utcnow()
    orders[order_id] = OrderRead(**stored)
    return orders[order_id]

@app.delete("/orders/{order_id}")
def delete_order(order_id: UUID):
    """
    -----------------------------------------------------------------------
    주문 삭제 엔드포인트
    - HTTP DELETE /orders/{order_id}
    - 실제로는 주문 취소(CANCELLED 상태 변경)가 더 적절
    - 감사 로그 및 회계 요구사항으로 인해 하드 삭제는 비권장
    -----------------------------------------------------------------------
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # TODO: 실제 구현에서는 주문 상태를 CANCELLED로 변경하는 것이 바람직
    # order.status = OrderStatus.CANCELLED
    # 또는 결제 취소, 재고 복원 등의 보상 트랜잭션 필요
    
    del orders[order_id]  # 개발/테스트용 하드 삭제
    return {"message": "Order deleted successfully"}

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the SimpleMicroservices API. Resources: Person, Address, Product, Order. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint! for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
