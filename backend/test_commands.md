diff --git a/backend/README.md b/backend/README.md
index e69de29bb2d1d6434b8b29ae775ad8c2e48c5391..73a9dc4a2ad4e774439a12638892d8d53d39b370 100644
--- a/backend/README.md
+++ b/backend/README.md
@@ -0,0 +1,267 @@
+# Руководство по тестированию API в Postman
+
+Этот документ поможет быстро проверить текущее API проекта через **Postman**: настроить окружение, подготовить данные и прогнать базовые сценарии.
+
+## 1) Запуск бэкенда
+
+Из папки `backend`:
+
+```bash
+uv run python run.py
+```
+
+После старта API доступно по адресу:
+
+- `http://localhost:8000`
+- Swagger: `http://localhost:8000/api/docs`
+
+## 2) Подготовка окружения в Postman
+
+1. Откройте **Postman** → **Environments** → **Create environment**.
+2. Назовите окружение, например `FastAPI Local`.
+3. Создайте переменные:
+
+| Variable | Initial value | Current value |
+|---|---|---|
+| `baseUrl` | `http://localhost:8000` | `http://localhost:8000` |
+| `productId` | `1` | `1` |
+| `categoryId` | `1` | `1` |
+
+4. Сохраните окружение и выберите его в правом верхнем углу Postman.
+
+## 3) Рекомендуемая структура коллекции
+
+Создайте коллекцию `FastAPI Shop API` и добавьте запросы в порядке ниже.
+
+---
+
+## 4) Smoke-check API
+
+### 4.1 Health
+
+**GET** `{{baseUrl}}/health`
+
+Ожидаем:
+- HTTP `200`
+- JSON:
+
+```json
+{
+  "status": "healthy"
+}
+```
+
+### 4.2 Root
+
+**GET** `{{baseUrl}}/`
+
+Ожидаем:
+- HTTP `200`
+- Поля `message` и `docs`.
+
+---
+
+## 5) Тестирование категорий
+
+### 5.1 Получить все категории
+
+**GET** `{{baseUrl}}/api/categories`
+
+Ожидаем:
+- HTTP `200`
+- Массив объектов категорий
+- У каждой категории есть `id`, `name`, `slug`
+
+**Tests (Postman):**
+
+```javascript
+pm.test("Status code is 200", function () {
+  pm.response.to.have.status(200);
+});
+
+pm.test("Response is array", function () {
+  const data = pm.response.json();
+  pm.expect(Array.isArray(data)).to.eql(true);
+});
+
+pm.test("Save first category id", function () {
+  const data = pm.response.json();
+  if (data.length > 0) {
+    pm.environment.set("categoryId", data[0].id);
+  }
+});
+```
+
+### 5.2 Получить категорию по ID
+
+**GET** `{{baseUrl}}/api/categories/{{categoryId}}`
+
+Ожидаем:
+- HTTP `200`
+- Объект категории с выбранным `id`
+
+---
+
+## 6) Тестирование продуктов
+
+### 6.1 Получить все продукты
+
+**GET** `{{baseUrl}}/api/products`
+
+Ожидаем:
+- HTTP `200`
+- JSON с полями:
+  - `products` (массив)
+  - `total` (число)
+
+**Tests (Postman):**
+
+```javascript
+pm.test("Status code is 200", function () {
+  pm.response.to.have.status(200);
+});
+
+pm.test("Products envelope is valid", function () {
+  const data = pm.response.json();
+  pm.expect(data).to.have.property("products");
+  pm.expect(data).to.have.property("total");
+  pm.expect(Array.isArray(data.products)).to.eql(true);
+});
+
+pm.test("Save first product id", function () {
+  const data = pm.response.json();
+  if (data.products.length > 0) {
+    pm.environment.set("productId", data.products[0].id);
+  }
+});
+```
+
+### 6.2 Получить продукт по ID
+
+**GET** `{{baseUrl}}/api/products/{{productId}}`
+
+Ожидаем:
+- HTTP `200`
+- Объект продукта
+- Вложенный объект `category`
+
+### 6.3 Получить продукты по категории
+
+**GET** `{{baseUrl}}/api/products/category/{{categoryId}}`
+
+Ожидаем:
+- HTTP `200`
+- JSON формата `ProductListResponse`
+
+---
+
+## 7) Тестирование корзины
+
+> В текущей реализации корзина передаётся между запросами в теле (`cart`) или query-параметрах.
+
+### 7.1 Добавить товар в корзину
+
+**POST** `{{baseUrl}}/api/cart/add`
+
+**Body → raw → JSON**
+
+```json
+{
+  "product_id": {{productId}},
+  "quantity": 2,
+  "cart": {}
+}
+```
+
+Ожидаем:
+- HTTP `200`
+- JSON с полем `cart` (словарь вида `{ "<product_id>": quantity }`)
+
+**Tests (Postman):**
+
+```javascript
+pm.test("Status code is 200", function () {
+  pm.response.to.have.status(200);
+});
+
+pm.test("Cart exists", function () {
+  const data = pm.response.json();
+  pm.expect(data).to.have.property("cart");
+});
+
+pm.test("Persist cart as string", function () {
+  const data = pm.response.json();
+  pm.environment.set("cartJson", JSON.stringify(data.cart));
+});
+```
+
+### 7.2 Обновить количество товара
+
+**PUT** `{{baseUrl}}/api/cart/update`
+
+**Body → raw → JSON**
+
+```json
+{
+  "product_id": {{productId}},
+  "quantity": 3,
+  "cart": {{cartJson}}
+}
+```
+
+Ожидаем:
+- HTTP `200`
+- Обновлённое поле `cart`
+
+### 7.3 Получить детализацию корзины
+
+**GET** `{{baseUrl}}/api/cart`
+
+Передайте query-параметры в формате ключ-значение, например:
+
+- key: `cart_data[1]`, value: `3`
+
+> Где `1` — это `product_id`, `3` — количество.
+
+Ожидаем:
+- HTTP `200`
+- JSON с полями `items`, `total`, `items_count`
+
+---
+
+## 8) Негативные сценарии, которые стоит проверить
+
+1. **Несуществующий продукт**
+   - `GET /api/products/999999`
+   - Ожидаем `404`
+
+2. **Несуществующая категория**
+   - `GET /api/categories/999999`
+   - Ожидаем `404`
+
+3. **Невалидное количество в корзине**
+   - `quantity: 0` в `POST /api/cart/add`
+   - Ожидаем `422`
+
+4. **Неверный тип product_id**
+   - `product_id: "abc"`
+   - Ожидаем `422`
+
+---
+
+## 9) Быстрый чек-лист перед демонстрацией
+
+- [ ] `GET /health` отвечает `200`
+- [ ] Получены категории и сохранён `categoryId`
+- [ ] Получены продукты и сохранён `productId`
+- [ ] Успешно выполнен `POST /api/cart/add`
+- [ ] Успешно выполнен `PUT /api/cart/update`
+- [ ] `GET /api/cart` возвращает `items_count > 0`
+
+---
+
+## 10) Советы по удобству в Postman
+
+- Для каждого запроса добавьте короткое описание (что делает и что ожидается).
+- Используйте **Folders** внутри коллекции: `Health`, `Categories`, `Products`, `Cart`.
+- Если тестируете командой, экспортируйте коллекцию (`v2.1`) и окружение в репозиторий для повторяемости.
