-- PostgreSQL VIEWs для аналитики книжного магазина
-- Создание представлений для упрощения отчетов и аналитики

-- 1. Представление: Статистика продаж по книгам
CREATE OR REPLACE VIEW v_book_sales_stats AS
SELECT 
    b.id AS book_id,
    b.title AS book_title,
    b.isbn,
    c.name AS category_name,
    COUNT(oi.id) AS total_sold,
    COALESCE(SUM(oi.quantity), 0) AS total_quantity_sold,
    COALESCE(SUM(oi.price * oi.quantity), 0) AS total_revenue,
    COALESCE(AVG(oi.price), 0) AS avg_sale_price,
    MAX(o.created_at) AS last_sale_date
FROM catalog_book b
LEFT JOIN catalog_category c ON b.category_id = c.id
LEFT JOIN orders_orderitem oi ON b.id = oi.book_id
LEFT JOIN orders_order o ON oi.order_id = o.id AND o.status != 'cancelled'
GROUP BY b.id, b.title, b.isbn, c.name;

COMMENT ON VIEW v_book_sales_stats IS 'Статистика продаж по каждой книге: количество, доходы, средняя цена';

-- 2. Представление: Доход по категориям
CREATE OR REPLACE VIEW v_category_revenue AS
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    c.slug,
    COUNT(DISTINCT b.id) AS total_books,
    COUNT(DISTINCT oi.id) AS total_orders,
    COALESCE(SUM(oi.quantity), 0) AS total_items_sold,
    COALESCE(SUM(oi.price * oi.quantity), 0) AS total_revenue,
    COALESCE(AVG(oi.price), 0) AS avg_item_price
FROM catalog_category c
LEFT JOIN catalog_book b ON c.id = b.category_id
LEFT JOIN orders_orderitem oi ON b.id = oi.book_id
LEFT JOIN orders_order o ON oi.order_id = o.id AND o.status != 'cancelled'
GROUP BY c.id, c.name, c.slug;

COMMENT ON VIEW v_category_revenue IS 'Статистика продаж и доходов по категориям книг';

-- 3. Представление: История покупок пользователя с деталями
CREATE OR REPLACE VIEW v_user_purchase_history AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    o.id AS order_id,
    o.status AS order_status,
    o.total_amount,
    o.created_at AS order_date,
    COUNT(oi.id) AS items_count,
    STRING_AGG(DISTINCT b.title, ', ') AS books_titles
FROM auth_user u
INNER JOIN orders_order o ON u.id = o.user_id
LEFT JOIN orders_orderitem oi ON o.id = oi.order_id
LEFT JOIN catalog_book b ON oi.book_id = b.id
GROUP BY u.id, u.username, u.email, o.id, o.status, o.total_amount, o.created_at
ORDER BY o.created_at DESC;

COMMENT ON VIEW v_user_purchase_history IS 'Полная история покупок пользователей с деталями заказов';

-- 4. Представление: Топ продаваемых книг
CREATE OR REPLACE VIEW v_top_selling_books AS
SELECT 
    b.id AS book_id,
    b.title,
    c.name AS category,
    SUM(oi.quantity) AS total_sold,
    SUM(oi.price * oi.quantity) AS total_revenue,
    ROUND(AVG(b.rating), 2) AS avg_rating,
    COUNT(DISTINCT r.id) AS reviews_count
FROM catalog_book b
INNER JOIN orders_orderitem oi ON b.id = oi.book_id
INNER JOIN orders_order o ON oi.order_id = o.id AND o.status != 'cancelled'
INNER JOIN catalog_category c ON b.category_id = c.id
LEFT JOIN reviews_review r ON b.id = r.book_id
GROUP BY b.id, b.title, c.name
ORDER BY total_sold DESC
LIMIT 100;

COMMENT ON VIEW v_top_selling_books IS 'Топ продаваемых книг с данными о доходах и отзывах';

-- 5. Представление: Статистика по пользователям
CREATE OR REPLACE VIEW v_user_statistics AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    COUNT(DISTINCT o.id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    MAX(o.created_at) AS last_order_date,
    MIN(o.created_at) AS first_order_date,
    COUNT(DISTINCT r.id) AS reviews_written
FROM auth_user u
LEFT JOIN orders_order o ON u.id = o.user_id AND o.status != 'cancelled'
LEFT JOIN reviews_review r ON u.id = r.user_id
GROUP BY u.id, u.username, u.email;

COMMENT ON VIEW v_user_statistics IS 'Статистика активности и покупок пользователей';

