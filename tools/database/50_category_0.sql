INSERT INTO categories (id, menu) VALUES (0, '{"en": "Building"}');
UPDATE items SET categorie_id = 0 WHERE item IN (0, 1) AND categorie_id = 10;
