-- SQL скрипт для создания базы данных книжного магазина BookShop
-- Создание всех таблиц, индексов, представлений, процедур и триггеров

-- ====================================================================
-- СОЗДАНИЕ ТАБЛИЦ
-- ====================================================================

-- 1. Категории книг
CREATE TABLE catalog_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    slug VARCHAR(140) NOT NULL UNIQUE
);

CREATE INDEX idx_category_name ON catalog_category(name);

-- 2. Авторы
CREATE TABLE catalog_author (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    UNIQUE(first_name, last_name)
);

CREATE INDEX idx_author_name ON catalog_author(last_name, first_name);

-- 3. Книги
CREATE TABLE catalog_book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    category_id INT NOT NULL REFERENCES catalog_category(id) ON DELETE PROTECT,
    price DECIMAL(10,2) NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0,
    pages INT,
    publication_date DATE,
    cover_image VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_book_category ON catalog_book(category_id, is_active);
CREATE INDEX idx_book_price ON catalog_book(price);
CREATE INDEX idx_book_rating ON catalog_book(rating);

-- 4. Книги-Авторы (Many-to-Many)
CREATE TABLE catalog_bookauthors (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES catalog_book(id) ON DELETE CASCADE,
    author_id INT NOT NULL REFERENCES catalog_author(id) ON DELETE CASCADE,
    UNIQUE(book_id, author_id)
);

CREATE INDEX idx_bookauthors_book ON catalog_bookauthors(book_id);
CREATE INDEX idx_bookauthors_author ON catalog_bookauthors(author_id);

-- 5. Остатки книг
CREATE TABLE catalog_inventory (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL UNIQUE REFERENCES catalog_book(id) ON DELETE CASCADE,
    stock INT NOT NULL DEFAULT 0,
    reserved INT NOT NULL DEFAULT 0
);

-- 6. Профили пользователей
CREATE TABLE users_profile (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_reason TEXT,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    date_of_birth DATE,
    avatar VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profile_user ON users_profile(user_id);

-- 7. Корзины
CREATE TABLE orders_cart (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cart_user ON orders_cart(user_id);

-- 8. Позиции корзины
CREATE TABLE orders_cartitem (
    id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL REFERENCES orders_cart(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES catalog_book(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    UNIQUE(cart_id, book_id)
);

-- 9. Заказы
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'processing',
    total_amount DECIMAL(12,2) DEFAULT 0,
    shipping_address TEXT NOT NULL DEFAULT '',
    shipping_city VARCHAR(100) NOT NULL DEFAULT '',
    shipping_postal_code VARCHAR(20) DEFAULT '',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_order_user_status ON orders_order(user_id, status);
CREATE INDEX idx_order_status_date ON orders_order(status, created_at);

-- 10. Позиции заказа
CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES catalog_book(id) ON DELETE PROTECT,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL
);

CREATE INDEX idx_orderitem_order ON orders_orderitem(order_id);

-- 11. Отзывы
CREATE TABLE reviews_review (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES catalog_book(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL,
    text TEXT,
    is_moderated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, book_id)
);

CREATE INDEX idx_review_book ON reviews_review(book_id);
CREATE INDEX idx_review_user ON reviews_review(user_id);

-- 12. Логи аудита
CREATE TABLE core_auditlog (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    actor_id INT REFERENCES auth_user(id) ON DELETE SET NULL,
    content_type_id INT REFERENCES django_content_type(id) ON DELETE SET NULL,
    object_id INT,
    old_data JSONB,
    new_data JSONB,
    path VARCHAR(255),
    method VARCHAR(10),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_auditlog_content ON core_auditlog(content_type_id, object_id);
CREATE INDEX idx_auditlog_actor ON core_auditlog(actor_id, created_at);
CREATE INDEX idx_auditlog_action ON core_auditlog(action, created_at);

-- 13. Статистика продаж
CREATE TABLE analytics_salesstats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_orders INT NOT NULL DEFAULT 0,
    total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_books_sold INT NOT NULL DEFAULT 0,
    average_order_value DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_salesstats_date ON analytics_salesstats(date);

-- 14. Топ продаваемых книг
CREATE TABLE analytics_topsellingbook (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    book_id INT NOT NULL REFERENCES catalog_book(id) ON DELETE CASCADE,
    quantity_sold INT NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    rank INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, book_id)
);

CREATE INDEX idx_topselling_date ON analytics_topsellingbook(date, rank);

-- 15. Статистика клиентов
CREATE TABLE analytics_customerstats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_customers INT NOT NULL DEFAULT 0,
    new_customers INT NOT NULL DEFAULT 0,
    returning_customers INT NOT NULL DEFAULT 0,
    average_customer_value DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customerstats_date ON analytics_customerstats(date);

-- ====================================================================
-- ПРЕДСТАВЛЕНИЯ (VIEW)
-- ====================================================================

-- Импорт из файла views.sql
-- ВАЖНО: Выполните backend/sql/views.sql отдельно

-- ====================================================================
-- ХРАНИМЫЕ ПРОЦЕДУРЫ
-- ====================================================================

-- Импорт из файла procedures.sql
-- ВАЖНО: Выполните backend/sql/procedures.sql отдельно

-- ====================================================================
-- ТРИГГЕРЫ
-- ====================================================================

-- Импорт из файла triggers.sql
-- ВАЖНО: Выполните backend/sql/triggers.sql отдельно

-- ====================================================================
-- КОММЕНТАРИИ К ТАБЛИЦАМ
-- ====================================================================

COMMENT ON TABLE catalog_category IS 'Категории книг';
COMMENT ON TABLE catalog_author IS 'Авторы книг';
COMMENT ON TABLE catalog_book IS 'Книги';
COMMENT ON TABLE catalog_bookauthors IS 'Связь многие-ко-многим: Книги-Авторы';
COMMENT ON TABLE catalog_inventory IS 'Остатки книг';
COMMENT ON TABLE users_profile IS 'Профили пользователей';
COMMENT ON TABLE orders_cart IS 'Корзины пользователей';
COMMENT ON TABLE orders_cartitem IS 'Позиции в корзине';
COMMENT ON TABLE orders_order IS 'Заказы';
COMMENT ON TABLE orders_orderitem IS 'Позиции в заказе';
COMMENT ON TABLE reviews_review IS 'Отзывы на книги';
COMMENT ON TABLE core_auditlog IS 'Логи аудита системы';
COMMENT ON TABLE analytics_salesstats IS 'Статистика продаж по дням';
COMMENT ON TABLE analytics_topsellingbook IS 'Топ продаваемых книг';
COMMENT ON TABLE analytics_customerstats IS 'Статистика клиентов';



