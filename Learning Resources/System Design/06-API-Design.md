# API Design - From REST to GraphQL to gRPC

**Mastery Level:** Essential for Staff+ Engineers  
**Interview Weight:** 25-30% of system design interviews  
**Time to Master:** 2-3 weeks  
**Difficulty:** ⭐⭐⭐⭐

---

## 🎯 Why API Design Mastery Matters

At **40+ LPA level**, API design decisions impact:
- **System scalability** - good APIs scale, bad ones don't
- **Developer productivity** - intuitive APIs accelerate development
- **Performance** - efficient protocols reduce latency and bandwidth
- **Maintainability** - well-designed APIs evolve gracefully
- **Security** - proper authentication and rate limiting

**Poor API design = technical debt for years. Great design = competitive advantage.**

---

## 🏗️ API Design Paradigms

### **REST APIs - The Standard**
```
HTTP + JSON + Stateless
GET /users/123
POST /orders
PUT /products/456
DELETE /comments/789
```

### **GraphQL - Query Language**
```
Single Endpoint + Flexible Queries
query {
  user(id: "123") {
    name
    orders {
      id
      total
    }
  }
}
```

### **gRPC - High Performance RPC**
```
Protocol Buffers + HTTP/2 + Streaming
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc StreamOrders(stream OrderRequest) returns (stream Order);
}
```

### **Event-Driven APIs - Reactive**
```
WebSockets + Server-Sent Events + Webhooks
ws://api.example.com/live-updates
POST /webhooks/order-status
```

---

## 🔧 RESTful API Design Mastery

### **Resource-Oriented Design:**

```python
from flask import Flask, request, jsonify
from typing import Dict, List, Optional
import uuid
from datetime import datetime

class RESTfulEcommerceAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup RESTful routes following best practices"""
        
        # Users resource
        self.app.route('/api/v1/users', methods=['GET'])(self.list_users)
        self.app.route('/api/v1/users', methods=['POST'])(self.create_user)
        self.app.route('/api/v1/users/<user_id>', methods=['GET'])(self.get_user)
        self.app.route('/api/v1/users/<user_id>', methods=['PUT'])(self.update_user)
        self.app.route('/api/v1/users/<user_id>', methods=['PATCH'])(self.partial_update_user)
        self.app.route('/api/v1/users/<user_id>', methods=['DELETE'])(self.delete_user)
        
        # Nested resources - user's orders
        self.app.route('/api/v1/users/<user_id>/orders', methods=['GET'])(self.get_user_orders)
        self.app.route('/api/v1/users/<user_id>/orders', methods=['POST'])(self.create_user_order)
        
        # Orders resource (can also be accessed directly)
        self.app.route('/api/v1/orders', methods=['GET'])(self.list_orders)
        self.app.route('/api/v1/orders/<order_id>', methods=['GET'])(self.get_order)
        self.app.route('/api/v1/orders/<order_id>/status', methods=['PATCH'])(self.update_order_status)
        
        # Products with search and filtering
        self.app.route('/api/v1/products', methods=['GET'])(self.search_products)
        self.app.route('/api/v1/products/<product_id>', methods=['GET'])(self.get_product)
        
        # Bulk operations
        self.app.route('/api/v1/products/bulk', methods=['POST'])(self.bulk_create_products)
        self.app.route('/api/v1/orders/bulk', methods=['PATCH'])(self.bulk_update_orders)
    
    def list_users(self):
        """GET /api/v1/users - List users with pagination and filtering"""
        
        # Extract query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 per page
        role = request.args.get('role')
        created_after = request.args.get('created_after')
        search = request.args.get('search')
        
        # Build filters
        filters = {}
        if role:
            filters['role'] = role
        if created_after:
            filters['created_after'] = created_after
        if search:
            filters['search'] = search
        
        # Get users (would query database)
        users, total_count = self.user_service.list_users(
            page=page, 
            limit=limit, 
            filters=filters
        )
        
        # Build pagination metadata
        total_pages = (total_count + limit - 1) // limit
        
        return jsonify({
            'data': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'total_count': total_count,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'links': {
                'self': f'/api/v1/users?page={page}&limit={limit}',
                'next': f'/api/v1/users?page={page+1}&limit={limit}' if page < total_pages else None,
                'prev': f'/api/v1/users?page={page-1}&limit={limit}' if page > 1 else None,
                'first': f'/api/v1/users?page=1&limit={limit}',
                'last': f'/api/v1/users?page={total_pages}&limit={limit}'
            }
        }), 200
    
    def create_user(self):
        """POST /api/v1/users - Create new user"""
        
        try:
            # Validate request body
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400
            
            # Validate required fields
            required_fields = ['email', 'name', 'password']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }), 400
            
            # Validate field formats
            validation_errors = self.validate_user_data(data)
            if validation_errors:
                return jsonify({
                    'error': 'Validation failed',
                    'validation_errors': validation_errors
                }), 400
            
            # Create user
            user = self.user_service.create_user(data)
            
            # Return created user (without password)
            user_response = {k: v for k, v in user.items() if k != 'password'}
            
            return jsonify({
                'data': user_response,
                'message': 'User created successfully'
            }), 201
            
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    
    def validate_user_data(self, data: Dict) -> List[str]:
        """Validate user data and return list of errors"""
        
        errors = []
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if 'email' in data and not re.match(email_pattern, data['email']):
            errors.append('Invalid email format')
        
        # Password strength
        if 'password' in data:
            password = data['password']
            if len(password) < 8:
                errors.append('Password must be at least 8 characters')
            if not re.search(r'[A-Z]', password):
                errors.append('Password must contain uppercase letter')
            if not re.search(r'[a-z]', password):
                errors.append('Password must contain lowercase letter')
            if not re.search(r'\d', password):
                errors.append('Password must contain number')
        
        # Name validation
        if 'name' in data and len(data['name'].strip()) < 2:
            errors.append('Name must be at least 2 characters')
        
        return errors
    
    def search_products(self):
        """GET /api/v1/products - Advanced product search"""
        
        # Extract search parameters
        query = request.args.get('q', '')  # Search query
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        brand = request.args.get('brand')
        in_stock = request.args.get('in_stock', type=bool)
        
        # Sorting
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        # Build search criteria
        search_criteria = {
            'query': query,
            'filters': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'brand': brand,
                'in_stock': in_stock
            },
            'sort': {
                'field': sort_by,
                'order': sort_order
            },
            'pagination': {
                'page': page,
                'limit': limit
            }
        }
        
        # Execute search
        results = self.product_service.search_products(search_criteria)
        
        return jsonify({
            'data': results['products'],
            'facets': results['facets'],  # For filtering UI
            'pagination': results['pagination'],
            'search_metadata': {
                'query': query,
                'total_results': results['total_count'],
                'search_time_ms': results['search_time_ms']
            }
        }), 200
    
    def bulk_update_orders(self):
        """PATCH /api/v1/orders/bulk - Bulk update order statuses"""
        
        try:
            data = request.get_json()
            
            # Validate bulk operation
            if 'operations' not in data:
                return jsonify({'error': 'Missing operations array'}), 400
            
            operations = data['operations']
            if len(operations) > 1000:  # Limit bulk operations
                return jsonify({'error': 'Too many operations (max 1000)'}), 400
            
            # Validate each operation
            validation_errors = []
            for i, operation in enumerate(operations):
                if 'order_id' not in operation:
                    validation_errors.append(f'Operation {i}: missing order_id')
                if 'status' not in operation:
                    validation_errors.append(f'Operation {i}: missing status')
            
            if validation_errors:
                return jsonify({
                    'error': 'Validation failed',
                    'validation_errors': validation_errors
                }), 400
            
            # Execute bulk update
            results = self.order_service.bulk_update_status(operations)
            
            return jsonify({
                'message': 'Bulk update completed',
                'results': {
                    'successful': results['successful_count'],
                    'failed': results['failed_count'],
                    'errors': results['errors']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

# Advanced error handling
class APIErrorHandler:
    def __init__(self, app):
        self.app = app
        self.setup_error_handlers()
    
    def setup_error_handlers(self):
        """Setup comprehensive error handling"""
        
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Bad Request',
                'message': 'The request could not be understood',
                'status_code': 400,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        @self.app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'status_code': 401,
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        @self.app.errorhandler(403)
        def forbidden(error):
            return jsonify({
                'error': 'Forbidden',
                'message': 'Insufficient permissions',
                'status_code': 403,
                'timestamp': datetime.utcnow().isoformat()
            }), 403
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status_code': 404,
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        @self.app.errorhandler(429)
        def rate_limit_exceeded(error):
            return jsonify({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests',
                'status_code': 429,
                'retry_after': error.retry_after if hasattr(error, 'retry_after') else 60,
                'timestamp': datetime.utcnow().isoformat()
            }), 429
        
        @self.app.errorhandler(500)
        def internal_server_error(error):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'status_code': 500,
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': str(uuid.uuid4())  # For tracking
            }), 500
```

### **API Versioning Strategies:**

```python
class APIVersioningStrategies:
    """Different approaches to API versioning"""
    
    def url_versioning(self):
        """Version in URL path"""
        examples = {
            'v1': '/api/v1/users',
            'v2': '/api/v2/users',
            'v3': '/api/v3/users'
        }
        
        pros = [
            'Clear and visible',
            'Easy to route',
            'Cacheable',
            'Easy to test different versions'
        ]
        
        cons = [
            'URL pollution',
            'Multiple endpoints to maintain'
        ]
        
        return {'examples': examples, 'pros': pros, 'cons': cons}
    
    def header_versioning(self):
        """Version in HTTP header"""
        examples = {
            'accept_header': 'Accept: application/vnd.api+json; version=1',
            'custom_header': 'API-Version: 2.0',
            'content_type': 'Content-Type: application/vnd.myapi.v2+json'
        }
        
        implementation = """
        @app.before_request
        def extract_api_version():
            version = request.headers.get('API-Version', '1.0')
            g.api_version = version
        
        def get_user():
            if g.api_version == '1.0':
                return get_user_v1()
            elif g.api_version == '2.0':
                return get_user_v2()
        """
        
        return {'examples': examples, 'implementation': implementation}
    
    def query_parameter_versioning(self):
        """Version as query parameter"""
        examples = {
            'simple': '/api/users?version=2',
            'with_format': '/api/users?v=2&format=json'
        }
        
        # Not recommended for production due to caching issues
        return {'examples': examples, 'recommendation': 'Avoid in production'}
    
    def backward_compatibility_patterns(self):
        """Patterns for maintaining backward compatibility"""
        
        patterns = {
            'additive_changes': {
                'description': 'Add new fields without breaking existing clients',
                'example': {
                    'v1_response': {'id': 1, 'name': 'John'},
                    'v2_response': {'id': 1, 'name': 'John', 'email': 'john@example.com'}
                }
            },
            
            'optional_parameters': {
                'description': 'New parameters should be optional',
                'example': {
                    'v1_endpoint': 'POST /users {name, email}',
                    'v2_endpoint': 'POST /users {name, email, phone?}'
                }
            },
            
            'graceful_degradation': {
                'description': 'Handle missing features gracefully',
                'example': 'If advanced search not available, fall back to basic search'
            },
            
            'deprecation_warnings': {
                'description': 'Warn clients about deprecated features',
                'header': 'Sunset: Sat, 31 Dec 2024 23:59:59 GMT',
                'response_header': 'X-API-Deprecation-Warning: This endpoint is deprecated'
            }
        }
        
        return patterns
```

---

## 🚀 GraphQL API Design

### **GraphQL Schema Design:**

```python
import graphene
from graphene import ObjectType, String, Int, List, Field, Argument
from graphene_sqlalchemy import SQLAlchemyObjectType
from typing import Optional

class User(ObjectType):
    id = String(required=True)
    name = String(required=True)
    email = String(required=True)
    role = String()
    created_at = String()
    
    # Computed fields
    full_name = String()
    order_count = Int()
    
    # Relationships
    orders = List(lambda: Order)
    
    def resolve_full_name(self, info):
        return f"{self.name}"
    
    def resolve_order_count(self, info):
        # Efficient counting without loading all orders
        return info.context['loaders']['user_order_count'].load(self.id)
    
    def resolve_orders(self, info, limit: Optional[int] = None):
        # Use DataLoader to prevent N+1 queries
        return info.context['loaders']['user_orders'].load((self.id, limit))

class Order(ObjectType):
    id = String(required=True)
    user_id = String(required=True)
    total_amount = String()  # Use String for precise decimals
    status = String()
    created_at = String()
    
    # Relationships
    user = Field(User)
    items = List(lambda: OrderItem)
    
    def resolve_user(self, info):
        return info.context['loaders']['user'].load(self.user_id)
    
    def resolve_items(self, info):
        return info.context['loaders']['order_items'].load(self.id)

class OrderItem(ObjectType):
    id = String(required=True)
    order_id = String(required=True)
    product_id = String(required=True)
    quantity = Int()
    price = String()
    
    # Relationships
    product = Field(lambda: Product)
    
    def resolve_product(self, info):
        return info.context['loaders']['product'].load(self.product_id)

class Product(ObjectType):
    id = String(required=True)
    name = String(required=True)
    description = String()
    price = String()
    category = String()
    in_stock = Int()
    
    # Computed fields
    is_available = graphene.Boolean()
    discounted_price = String()
    
    def resolve_is_available(self, info):
        return self.in_stock > 0
    
    def resolve_discounted_price(self, info):
        # Apply business logic for discounts
        user = info.context.get('current_user')
        if user and user.role == 'premium':
            return str(float(self.price) * 0.9)  # 10% discount
        return self.price

class Query(ObjectType):
    # Single resource queries
    user = Field(User, id=String(required=True))
    order = Field(Order, id=String(required=True))
    product = Field(Product, id=String(required=True))
    
    # List queries with filtering and pagination
    users = List(
        User,
        first=Int(default_value=10),
        skip=Int(default_value=0),
        role=String(),
        search=String()
    )
    
    orders = List(
        Order,
        first=Int(default_value=10),
        skip=Int(default_value=0),
        status=String(),
        user_id=String()
    )
    
    products = List(
        Product,
        first=Int(default_value=10),
        skip=Int(default_value=0),
        category=String(),
        in_stock_only=graphene.Boolean(default_value=False),
        search=String()
    )
    
    # Resolvers
    def resolve_user(self, info, id):
        return info.context['loaders']['user'].load(id)
    
    def resolve_users(self, info, first, skip, role=None, search=None):
        filters = {}
        if role:
            filters['role'] = role
        if search:
            filters['search'] = search
        
        return info.context['services']['user'].list_users(
            limit=first,
            offset=skip,
            filters=filters
        )
    
    def resolve_products(self, info, first, skip, category=None, in_stock_only=False, search=None):
        filters = {}
        if category:
            filters['category'] = category
        if in_stock_only:
            filters['in_stock'] = True
        if search:
            filters['search'] = search
        
        return info.context['services']['product'].search_products(
            limit=first,
            offset=skip,
            filters=filters
        )

class CreateUserInput(graphene.InputObjectType):
    name = String(required=True)
    email = String(required=True)
    password = String(required=True)
    role = String(default_value='customer')

class UpdateOrderStatusInput(graphene.InputObjectType):
    order_id = String(required=True)
    status = String(required=True)
    notes = String()

class Mutation(ObjectType):
    create_user = Field(User, input=CreateUserInput(required=True))
    update_order_status = Field(Order, input=UpdateOrderStatusInput(required=True))
    
    def resolve_create_user(self, info, input):
        # Validate input
        validation_errors = self.validate_create_user_input(input)
        if validation_errors:
            raise Exception(f"Validation failed: {validation_errors}")
        
        # Create user using service
        user_data = {
            'name': input.name,
            'email': input.email,
            'password': input.password,
            'role': input.role
        }
        
        user = info.context['services']['user'].create_user(user_data)
        return user
    
    def validate_create_user_input(self, input):
        errors = []
        
        # Email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', input.email):
            errors.append('Invalid email format')
        
        # Password validation
        if len(input.password) < 8:
            errors.append('Password must be at least 8 characters')
        
        return errors

# DataLoader for efficient batching
from aiodataloader import DataLoader

class UserLoader(DataLoader):
    def __init__(self, user_service):
        super().__init__()
        self.user_service = user_service
    
    async def batch_load_fn(self, user_ids):
        users = await self.user_service.get_users_by_ids(user_ids)
        
        # Return users in same order as requested IDs
        user_dict = {user.id: user for user in users}
        return [user_dict.get(user_id) for user_id in user_ids]

class UserOrdersLoader(DataLoader):
    def __init__(self, order_service):
        super().__init__()
        self.order_service = order_service
    
    async def batch_load_fn(self, user_limit_pairs):
        # user_limit_pairs is [(user_id, limit), ...]
        user_ids = [pair[0] for pair in user_limit_pairs]
        limits = {pair[0]: pair[1] for pair in user_limit_pairs}
        
        orders_by_user = await self.order_service.get_orders_by_user_ids(user_ids, limits)
        
        return [orders_by_user.get(user_id, []) for user_id in user_ids]

# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Example GraphQL queries
example_queries = {
    'simple_user_query': '''
        query GetUser($userId: String!) {
            user(id: $userId) {
                id
                name
                email
                orderCount
            }
        }
    ''',
    
    'complex_nested_query': '''
        query GetUserWithOrders($userId: String!) {
            user(id: $userId) {
                id
                name
                email
                orders {
                    id
                    totalAmount
                    status
                    items {
                        id
                        quantity
                        price
                        product {
                            name
                            category
                        }
                    }
                }
            }
        }
    ''',
    
    'search_products': '''
        query SearchProducts($search: String, $category: String, $limit: Int) {
            products(search: $search, category: $category, first: $limit) {
                id
                name
                price
                discountedPrice
                isAvailable
            }
        }
    ''',
    
    'create_user_mutation': '''
        mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
                id
                name
                email
                role
            }
        }
    '''
}
```

---

## ⚡ gRPC High-Performance APIs

### **Protocol Buffer Definitions:**

```protobuf
// user_service.proto
syntax = "proto3";

package ecommerce.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// User messages
message User {
    string id = 1;
    string name = 2;
    string email = 3;
    string role = 4;
    google.protobuf.Timestamp created_at = 5;
    int32 order_count = 6;
}

message GetUserRequest {
    string id = 1;
}

message ListUsersRequest {
    int32 page_size = 1;
    string page_token = 2;
    string role_filter = 3;
    string search_query = 4;
}

message ListUsersResponse {
    repeated User users = 1;
    string next_page_token = 2;
    int32 total_count = 3;
}

message CreateUserRequest {
    string name = 1;
    string email = 2;
    string password = 3;
    string role = 4;
}

message UpdateUserRequest {
    string id = 1;
    User user = 2;
    google.protobuf.FieldMask update_mask = 3;
}

// Order messages  
message Order {
    string id = 1;
    string user_id = 2;
    double total_amount = 3;
    OrderStatus status = 4;
    repeated OrderItem items = 5;
    google.protobuf.Timestamp created_at = 6;
}

enum OrderStatus {
    ORDER_STATUS_UNSPECIFIED = 0;
    ORDER_STATUS_PENDING = 1;
    ORDER_STATUS_CONFIRMED = 2;
    ORDER_STATUS_SHIPPED = 3;
    ORDER_STATUS_DELIVERED = 4;
    ORDER_STATUS_CANCELLED = 5;
}

message OrderItem {
    string id = 1;
    string product_id = 2;
    int32 quantity = 3;
    double price = 4;
}

message GetOrderRequest {
    string id = 1;
}

message CreateOrderRequest {
    string user_id = 1;
    repeated OrderItem items = 2;
}

message UpdateOrderStatusRequest {
    string id = 1;
    OrderStatus status = 2;
    string notes = 3;
}

// Streaming messages
message OrderStatusUpdate {
    string order_id = 1;
    OrderStatus old_status = 2;
    OrderStatus new_status = 3;
    google.protobuf.Timestamp timestamp = 4;
    string notes = 5;
}

message SubscribeOrderUpdatesRequest {
    string user_id = 1;
}

// Service definitions
service UserService {
    // Unary RPCs
    rpc GetUser(GetUserRequest) returns (User);
    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
    rpc CreateUser(CreateUserRequest) returns (User);
    rpc UpdateUser(UpdateUserRequest) returns (User);
    rpc DeleteUser(GetUserRequest) returns (google.protobuf.Empty);
    
    // Server streaming - get user activity feed
    rpc GetUserActivityStream(GetUserRequest) returns (stream ActivityEvent);
    
    // Client streaming - bulk user creation
    rpc BulkCreateUsers(stream CreateUserRequest) returns (BulkCreateUsersResponse);
    
    // Bidirectional streaming - real-time chat
    rpc UserChat(stream ChatMessage) returns (stream ChatMessage);
}

service OrderService {
    // Unary RPCs
    rpc GetOrder(GetOrderRequest) returns (Order);
    rpc CreateOrder(CreateOrderRequest) returns (Order);
    rpc UpdateOrderStatus(UpdateOrderStatusRequest) returns (Order);
    
    // Server streaming - track order status updates
    rpc SubscribeOrderUpdates(SubscribeOrderUpdatesRequest) returns (stream OrderStatusUpdate);
    
    // Client streaming - bulk order processing
    rpc ProcessOrderBatch(stream CreateOrderRequest) returns (BatchProcessResponse);
}
```

### **gRPC Server Implementation:**

```python
import grpc
from concurrent import futures
import asyncio
from typing import Iterator

# Generated from protobuf
import user_service_pb2
import user_service_pb2_grpc
import order_service_pb2
import order_service_pb2_grpc

class UserServicer(user_service_pb2_grpc.UserServiceServicer):
    def __init__(self, user_service, auth_service):
        self.user_service = user_service
        self.auth_service = auth_service
    
    def GetUser(self, request, context):
        """Get single user by ID"""
        
        try:
            # Authentication check
            if not self.auth_service.validate_token(context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid token')
            
            user = self.user_service.get_user(request.id)
            if not user:
                context.abort(grpc.StatusCode.NOT_FOUND, 'User not found')
            
            return user_service_pb2.User(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                order_count=user.order_count
            )
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def ListUsers(self, request, context):
        """List users with pagination and filtering"""
        
        try:
            # Check permissions
            current_user = self.auth_service.get_current_user(context)
            if not current_user.has_permission('read_users'):
                context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Insufficient permissions')
            
            # Parse pagination
            page_size = min(request.page_size or 20, 100)  # Max 100
            offset = self.decode_page_token(request.page_token)
            
            # Build filters
            filters = {}
            if request.role_filter:
                filters['role'] = request.role_filter
            if request.search_query:
                filters['search'] = request.search_query
            
            # Get users
            users, total_count, next_offset = self.user_service.list_users(
                limit=page_size,
                offset=offset,
                filters=filters
            )
            
            # Convert to protobuf
            user_protos = []
            for user in users:
                user_protos.append(user_service_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role,
                    created_at=user.created_at,
                    order_count=user.order_count
                ))
            
            # Generate next page token
            next_page_token = self.encode_page_token(next_offset) if next_offset else ""
            
            return user_service_pb2.ListUsersResponse(
                users=user_protos,
                next_page_token=next_page_token,
                total_count=total_count
            )
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def CreateUser(self, request, context):
        """Create new user"""
        
        try:
            # Permission check
            current_user = self.auth_service.get_current_user(context)
            if not current_user.has_permission('create_users'):
                context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Insufficient permissions')
            
            # Validate input
            validation_errors = self.validate_create_user_request(request)
            if validation_errors:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, 
                            f"Validation failed: {', '.join(validation_errors)}")
            
            # Create user
            user_data = {
                'name': request.name,
                'email': request.email,
                'password': request.password,
                'role': request.role or 'customer'
            }
            
            user = self.user_service.create_user(user_data)
            
            return user_service_pb2.User(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                order_count=0
            )
            
        except Exception as e:
            if 'duplicate email' in str(e).lower():
                context.abort(grpc.StatusCode.ALREADY_EXISTS, 'Email already exists')
            else:
                context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetUserActivityStream(self, request, context):
        """Server streaming - send user activity updates"""
        
        try:
            current_user = self.auth_service.get_current_user(context)
            
            # Check if user can access this activity stream
            if current_user.id != request.id and not current_user.is_admin():
                context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Access denied')
            
            # Stream activity events
            for activity in self.user_service.stream_user_activity(request.id):
                if context.is_cancelled():
                    break
                
                yield user_service_pb2.ActivityEvent(
                    user_id=activity.user_id,
                    event_type=activity.event_type,
                    timestamp=activity.timestamp,
                    data=activity.data
                )
                
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def BulkCreateUsers(self, request_iterator, context):
        """Client streaming - bulk user creation"""
        
        try:
            current_user = self.auth_service.get_current_user(context)
            if not current_user.has_permission('bulk_create_users'):
                context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Insufficient permissions')
            
            created_users = []
            failed_users = []
            
            for create_request in request_iterator:
                try:
                    # Validate each request
                    validation_errors = self.validate_create_user_request(create_request)
                    if validation_errors:
                        failed_users.append({
                            'email': create_request.email,
                            'error': f"Validation failed: {', '.join(validation_errors)}"
                        })
                        continue
                    
                    # Create user
                    user_data = {
                        'name': create_request.name,
                        'email': create_request.email,
                        'password': create_request.password,
                        'role': create_request.role or 'customer'
                    }
                    
                    user = self.user_service.create_user(user_data)
                    created_users.append(user.id)
                    
                except Exception as e:
                    failed_users.append({
                        'email': create_request.email,
                        'error': str(e)
                    })
            
            return user_service_pb2.BulkCreateUsersResponse(
                created_count=len(created_users),
                failed_count=len(failed_users),
                created_user_ids=created_users,
                errors=failed_users
            )
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def validate_create_user_request(self, request):
        """Validate user creation request"""
        
        errors = []
        
        if not request.name or len(request.name.strip()) < 2:
            errors.append('Name must be at least 2 characters')
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not request.email or not re.match(email_pattern, request.email):
            errors.append('Invalid email format')
        
        if not request.password or len(request.password) < 8:
            errors.append('Password must be at least 8 characters')
        
        return errors
    
    def encode_page_token(self, offset):
        """Encode pagination offset as token"""
        import base64
        return base64.b64encode(str(offset).encode()).decode()
    
    def decode_page_token(self, token):
        """Decode pagination token to offset"""
        if not token:
            return 0
        
        try:
            import base64
            return int(base64.b64decode(token.encode()).decode())
        except:
            return 0

class OrderServicer(order_service_pb2_grpc.OrderServiceServicer):
    def __init__(self, order_service, auth_service):
        self.order_service = order_service
        self.auth_service = auth_service
    
    def SubscribeOrderUpdates(self, request, context):
        """Server streaming - real-time order status updates"""
        
        try:
            current_user = self.auth_service.get_current_user(context)
            
            # Users can only subscribe to their own orders
            if current_user.id != request.user_id and not current_user.is_admin():
                context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Access denied')
            
            # Stream order updates
            for update in self.order_service.stream_order_updates(request.user_id):
                if context.is_cancelled():
                    break
                
                yield order_service_pb2.OrderStatusUpdate(
                    order_id=update.order_id,
                    old_status=update.old_status,
                    new_status=update.new_status,
                    timestamp=update.timestamp,
                    notes=update.notes
                )
                
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

# Server setup
def serve():
    # Create services
    user_service = UserService()
    order_service = OrderService()
    auth_service = AuthService()
    
    # Create server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=50),
        options=[
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
        ]
    )
    
    # Add servicers
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(user_service, auth_service), server
    )
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderServicer(order_service, auth_service), server
    )
    
    # Setup TLS
    with open('server.key', 'rb') as f:
        private_key = f.read()
    with open('server.crt', 'rb') as f:
        certificate_chain = f.read()
    
    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)]
    )
    
    # Listen on secure port
    server.add_secure_port('[::]:50051', server_credentials)
    
    print("Starting gRPC server on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

---

## 🔒 API Authentication & Security

### **JWT Authentication Implementation:**

```python
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g

class JWTAuthManager:
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=30)
    
    def generate_tokens(self, user_id: str, user_role: str) -> dict:
        """Generate access and refresh tokens"""
        
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'role': user_role,
            'type': 'access',
            'iat': now,
            'exp': now + self.access_token_expiry,
            'jti': str(uuid.uuid4())  # JWT ID for revocation
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + self.refresh_token_expiry,
            'jti': str(uuid.uuid4())
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expiry.total_seconds())
        }
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Check if token is revoked (would check against blacklist in production)
            if self.is_token_revoked(payload.get('jti')):
                raise jwt.InvalidTokenError('Token has been revoked')
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError('Token has expired')
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError('Invalid token')
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Generate new access token from refresh token"""
        
        try:
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')
            
            # Get user info
            user_id = payload['user_id']
            user = self.user_service.get_user(user_id)
            
            if not user:
                raise jwt.InvalidTokenError('User not found')
            
            # Generate new access token
            return self.generate_tokens(user.id, user.role)
            
        except jwt.InvalidTokenError as e:
            raise e
    
    def is_token_revoked(self, jti: str) -> bool:
        """Check if token is in revocation blacklist"""
        # In production, check against Redis/database
        return False

# Authentication decorators
def require_auth(auth_manager: JWTAuthManager):
    """Decorator to require authentication"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'Authorization header required'}), 401
            
            try:
                # Extract token from "Bearer <token>"
                token_type, token = auth_header.split(' ', 1)
                if token_type.lower() != 'bearer':
                    return jsonify({'error': 'Invalid token type'}), 401
                
                # Verify token
                payload = auth_manager.verify_token(token)
                
                # Store user info in request context
                g.current_user_id = payload['user_id']
                g.current_user_role = payload['role']
                g.token_payload = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Invalid token'}), 401
        
        return decorated_function
    return decorator

def require_role(required_role: str):
    """Decorator to require specific role"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user_role'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if g.current_user_role != required_role and g.current_user_role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Rate limiting
from functools import wraps
import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_cache = defaultdict(deque)  # Fallback for testing
    
    def limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is within rate limit"""
        
        if self.redis_client:
            return self._redis_rate_limit(key, limit, window_seconds)
        else:
            return self._memory_rate_limit(key, limit, window_seconds)
    
    def _redis_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Redis-based sliding window rate limiting"""
        
        now = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current entries
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(uuid.uuid4()): now})
        
        # Set expiry
        pipeline.expire(key, window_seconds)
        
        results = pipeline.execute()
        current_count = results[1]
        
        return current_count < limit
    
    def _memory_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Memory-based rate limiting (for testing)"""
        
        now = time.time()
        window_start = now - window_seconds
        
        # Remove old entries
        requests = self.local_cache[key]
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if under limit
        if len(requests) >= limit:
            return False
        
        # Add current request
        requests.append(now)
        return True

def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator"""
    
    rate_limiter = RateLimiter()
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create rate limit key
            if hasattr(g, 'current_user_id'):
                key = f"rate_limit:user:{g.current_user_id}"
            else:
                key = f"rate_limit:ip:{request.remote_addr}"
            
            # Check rate limit
            if not rate_limiter.limit(key, requests_per_minute, 60):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Example usage
auth_manager = JWTAuthManager('your-secret-key')

@app.route('/api/v1/users')
@require_auth(auth_manager)
@require_role('admin')
@rate_limit(100)  # 100 requests per minute
def list_users():
    return jsonify({'users': []})

@app.route('/api/v1/profile')
@require_auth(auth_manager)
@rate_limit(30)  # 30 requests per minute
def get_profile():
    user_id = g.current_user_id
    return jsonify({'user_id': user_id})
```

---

## ✅ API Design Mastery Checklist

### **RESTful Design**
- [ ] Resource-oriented URL design
- [ ] Proper HTTP methods and status codes
- [ ] Pagination, filtering, and sorting
- [ ] Versioning strategy
- [ ] Error handling and validation

### **GraphQL Expertise**
- [ ] Schema design and type definitions
- [ ] Resolver implementation and DataLoader
- [ ] Query optimization and N+1 prevention
- [ ] Mutations and input validation
- [ ] Subscription handling

### **gRPC Mastery**
- [ ] Protocol Buffer schema design
- [ ] Unary, streaming, and bidirectional RPCs
- [ ] Error handling and status codes
- [ ] Authentication and interceptors
- [ ] Performance optimization

### **Security & Performance**
- [ ] JWT authentication and authorization
- [ ] Rate limiting and abuse prevention
- [ ] Input validation and sanitization
- [ ] API monitoring and analytics
- [ ] Caching and optimization strategies

**Master these API patterns, and you'll design interfaces that developers love to use!** 🎯