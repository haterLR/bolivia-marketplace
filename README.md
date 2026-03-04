# Bolivia Marketplace (Multi-vendor)

Marketplace multi-vendedor **solo para Bolivia** construido con **Django 5 + DRF + PostgreSQL + Redis + Channels**.

## Stack
- Backend: Django 5, Django REST Framework, JWT (SimpleJWT)
- DB: PostgreSQL
- Realtime: Django Channels + Redis
- Frontend: Django Templates + HTMX
- Contenedores: Docker Compose (`web + db + redis`)
- Tests: pytest + pytest-django

## Funcionalidades
- Moneda BOB en modelos y flujo (`price_bob`, `total_bob`).
- Idioma por defecto `es-BO`, timezone `America/La_Paz`.
- Auth JWT:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
- Roles: `ADMIN`, `VENDEDOR`, `CLIENTE`.
- Seller onboarding:
  - `POST /api/sellers/apply`
  - `GET /api/sellers/me`
  - `GET /api/sellers/{id}`
  - `POST /api/admin/sellers/approve`
- Productos:
  - CRUD vendedor: `/api/products/`
  - Públicos: `GET /api/products/public?city=&category=&min_price=&max_price=`
- Carrito:
  - `GET /api/cart`
  - `POST /api/cart/add`
  - `POST /api/cart/update`
  - `POST /api/cart/remove`
- Checkout multi-vendedor:
  - `POST /api/checkout`
  - separa automáticamente órdenes por seller.
- Pagos:
  - `POST /api/payments/create`
  - `POST /api/payments/upload-proof`
  - `POST /api/payments/webhook/tigomoney`
  - `POST /api/payments/mark-paid` (seller/admin)
- Chat por pedido:
  - WS: `/ws/chat/{order_id}/`
  - `GET /api/chat/threads`
  - `GET /api/chat/threads/{thread_id}/messages`

## Docker setup
```bash
docker compose up --build
```

La app queda en `http://localhost:8000`.

## Variables de entorno (Tigo Money)
- `TIGO_MONEY_API_KEY`
- `TIGO_MONEY_SECRET`

Proveedor implementado en `marketplace/payments.py` con interfaz:
- `create_payment(order, callback_url)`
- `verify_callback(payload, signature)`

> Por defecto usa claves fake para entorno local.

## Probar pagos manuales
1. Crear pedido por checkout.
2. Crear intento de pago en `/api/payments/create` con `method=QR_INTEROP` o `TRANSFERENCIA`.
3. Subir comprobante con `/api/payments/upload-proof`.
4. Seller/Admin confirma con `/api/payments/mark-paid`.

## Arquitectura (alto nivel)
- `users/`: usuario custom, roles, seller profile.
- `marketplace/`: productos, carrito, órdenes, pagos, checkout.
- `chatapp/`: threads/mensajes + websocket channels.
- `templates/`: home, detalle, carrito, checkout, panel vendedor, chat.
- `config/`: settings, ASGI/WSGI, rutas globales.

## Testing
Ejecutar:
```bash
pytest
```

> En tests se usa SQLite automáticamente para facilitar ejecución local.
