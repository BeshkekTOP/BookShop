

-- 1. Процедура: Расчет итоговой стоимости заказа
CREATE OR REPLACE FUNCTION calculate_order_total(order_id_param INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    total_amount NUMERIC;
BEGIN
    SELECT COALESCE(SUM(price * quantity), 0)
    INTO total_amount
    FROM orders_orderitem
    WHERE order_id = order_id_param;
    
    RETURN total_amount;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_order_total IS 'Рассчитывает итоговую стоимость заказа по его ID';

-- 2. Процедура: Обновление рейтинга книги на основе отзывов
CREATE OR REPLACE FUNCTION update_book_rating(book_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    avg_rating NUMERIC;
BEGIN
    SELECT COALESCE(AVG(rating), 0)
    INTO avg_rating
    FROM reviews_review
    WHERE book_id = book_id_param AND is_moderated = true;
    
    UPDATE catalog_book
    SET rating = ROUND(avg_rating, 2)
    WHERE id = book_id_param;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_book_rating IS 'Пересчитывает рейтинг книги на основе модерированных отзывов';

-- 3. Процедура: Пакетное обновление статусов заказов
CREATE OR REPLACE FUNCTION process_bulk_order_status_update(
    status_old VARCHAR,
    status_new VARCHAR,
    days_old INTEGER DEFAULT 0
)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE orders_order
    SET status = status_new, updated_at = NOW()
    WHERE status = status_old
    AND created_at <= NOW() - (days_old || ' days')::INTERVAL;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_bulk_order_status_update IS 'Пакетное обновление статуса заказов с учетом возраста';

-- 4. Процедура: Получение статистики по периодам
CREATE OR REPLACE FUNCTION get_period_stats(
    start_date DATE,
    end_date DATE
)
RETURNS TABLE (
    total_orders BIGINT,
    total_revenue NUMERIC,
    total_items BIGINT,
    avg_order_value NUMERIC,
    unique_customers BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT o.id)::BIGINT AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_revenue,
        COALESCE(SUM(oi.quantity), 0)::BIGINT AS total_items,
        COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
        COUNT(DISTINCT o.user_id)::BIGINT AS unique_customers
    FROM orders_order o
    LEFT JOIN orders_orderitem oi ON o.id = oi.order_id
    WHERE o.status != 'cancelled'
    AND o.created_at::DATE BETWEEN start_date AND end_date;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_period_stats IS 'Получение статистики продаж за указанный период';

-- 5. Процедура: Валидация и обновление остатков
CREATE OR REPLACE FUNCTION update_book_stock(
    book_id_param INTEGER,
    quantity_change INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    current_stock INTEGER;
BEGIN
    -- Получаем текущий запас
    SELECT stock INTO current_stock
    FROM catalog_inventory
    WHERE book_id = book_id_param;
    
    -- Проверяем валидность
    IF current_stock + quantity_change < 0 THEN
        RETURN FALSE;
    END IF;
    
    -- Обновляем запас
    UPDATE catalog_inventory
    SET stock = stock + quantity_change
    WHERE book_id = book_id_param;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_book_stock IS 'Безопасное обновление остатков книги с проверкой валидности';

