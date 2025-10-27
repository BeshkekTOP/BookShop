-- PostgreSQL триггеры для автоматизации и аудита

-- 1. Триггер: Автоматическое обновление рейтинга книги при добавлении отзыва
CREATE OR REPLACE FUNCTION trigger_update_book_rating()
RETURNS TRIGGER AS $$
BEGIN
    -- Вызываем процедуру обновления рейтинга
    PERFORM update_book_rating(NEW.book_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_rating_trigger
AFTER INSERT OR UPDATE OR DELETE ON reviews_review
FOR EACH ROW
WHEN (NEW.is_moderated = true OR OLD.is_moderated = true)
EXECUTE FUNCTION trigger_update_book_rating();

COMMENT ON TRIGGER update_book_rating_trigger ON reviews_review IS 
'Автоматически обновляет рейтинг книги при изменении модерированных отзывов';

-- 2. Триггер: Валидация запасов при заказе
CREATE OR REPLACE FUNCTION trigger_validate_stock()
RETURNS TRIGGER AS $$
DECLARE
    available_stock INTEGER;
BEGIN
    -- Получаем доступный запас
    SELECT (stock - reserved) INTO available_stock
    FROM catalog_inventory
    WHERE book_id = NEW.book_id;
    
    -- Проверяем достаточность
    IF available_stock < NEW.quantity THEN
        RAISE EXCEPTION 'Insufficient stock. Available: %, requested: %', 
            available_stock, NEW.quantity;
    END IF;
    
    -- Резервируем товар
    UPDATE catalog_inventory
    SET reserved = reserved + NEW.quantity
    WHERE book_id = NEW.book_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_stock_trigger
BEFORE INSERT ON orders_orderitem
FOR EACH ROW
EXECUTE FUNCTION trigger_validate_stock();

COMMENT ON TRIGGER validate_stock_trigger ON orders_orderitem IS 
'Проверяет достаточность запасов и резервирует товар при создании заказа';

-- 3. Триггер: Освобождение запасов при отмене заказа
CREATE OR REPLACE FUNCTION trigger_release_stock()
RETURNS TRIGGER AS $$
BEGIN
    -- Освобождаем зарезервированный товар при отмене заказа
    IF NEW.status = 'cancelled' AND OLD.status != 'cancelled' THEN
        UPDATE catalog_inventory ci
        SET reserved = reserved - oi.quantity
        FROM orders_orderitem oi
        WHERE ci.book_id = oi.book_id
        AND oi.order_id = NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER release_stock_trigger
AFTER UPDATE ON orders_order
FOR EACH ROW
WHEN (NEW.status = 'cancelled' AND OLD.status != 'cancelled')
EXECUTE FUNCTION trigger_release_stock();

COMMENT ON TRIGGER release_stock_trigger ON orders_order IS 
'Освобождает зарезервированные товары при отмене заказа';

-- 4. Триггер: Автоматический расчет итоговой суммы заказа
CREATE OR REPLACE FUNCTION trigger_calculate_order_total()
RETURNS TRIGGER AS $$
DECLARE
    order_total NUMERIC;
BEGIN
    -- Рассчитываем итоговую сумму заказа
    SELECT calculate_order_total(COALESCE(NEW.order_id, OLD.order_id))
    INTO order_total;
    
    -- Обновляем заказ
    UPDATE orders_order
    SET total_amount = order_total
    WHERE id = COALESCE(NEW.order_id, OLD.order_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_order_total_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders_orderitem
FOR EACH ROW
EXECUTE FUNCTION trigger_calculate_order_total();

COMMENT ON TRIGGER calculate_order_total_trigger ON orders_orderitem IS 
'Автоматически пересчитывает итоговую сумму заказа при изменении позиций';

-- 5. Триггер: Логирование изменений книг
CREATE OR REPLACE FUNCTION trigger_log_book_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- Логируем изменения
        INSERT INTO core_auditlog (
            action, actor_id, content_type_id, object_id,
            old_data, new_data, path, method, created_at
        ) VALUES (
            'updated',
            COALESCE(NEW.updated_by_id, OLD.updated_by_id),
            (SELECT id FROM django_content_type WHERE model = 'book' AND app_label = 'catalog'),
            NEW.id,
            row_to_json(OLD)::jsonb,
            row_to_json(NEW)::jsonb,
            '/api/books/' || NEW.id,
            'POST',
            NOW()
        );
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO core_auditlog (
            action, actor_id, content_type_id, object_id,
            new_data, path, method, created_at
        ) VALUES (
            'created',
            NEW.created_by_id,
            (SELECT id FROM django_content_type WHERE model = 'book' AND app_label = 'catalog'),
            NEW.id,
            row_to_json(NEW)::jsonb,
            '/api/books/' || NEW.id,
            'POST',
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Примечание: Этот триггер требует расширения модели Book для хранения изменений
COMMENT ON FUNCTION trigger_log_book_changes IS 
'Логирует все изменения в книгах для аудита';

