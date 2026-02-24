-- Örnek Şoförler
INSERT INTO drivers (name, phone) VALUES ('Koray Bey', '05551234567');
INSERT INTO drivers (name, phone) VALUES ('Fuat Bey', '05551234568');
INSERT INTO drivers (name, phone) VALUES ('Kadir Bey', '05551234569');
INSERT INTO drivers (name, phone) VALUES ('Gürkan Bey', '05551234570');

-- Örnek Müşteriler (Fotoğraftaki tablodan)
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Vi Teknik', 4, 'sefer_tasi', 3, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('BBM Grup', 6, 'sefer_tasi', 5, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Pin Teknik', 8, 'sefer_tasi', 4, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Tansu Bey', 4, 'sefer_tasi', 5, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Dofu Veteriner', 4, 'sefer_tasi', 3, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Demet Hanım', 4, 'sefer_tasi', 2, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Dr. Yavuz Yıldız', 4, 'sefer_tasi', 7, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('TSS Sigorta', 5, 'sefer_tasi', 12, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Aybirke Düzgün', 4, 'sefer_tasi', 2, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Sağol Paşa', 8, 'sefer_tasi', 2, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Yıldırım Sağlık', 5, 'sefer_tasi', 7, '3 çeşit olacak');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Osman Tuğrul', 4, 'sefer_tasi', NULL, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Ufuk Mesken Merkez', 6, 'sefer_tasi', 3, 'Çorbalı bol');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Sierra', 5, 'sefer_tasi', 12, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Sezgice', 4, 'sefer_tasi', 7, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Hayges', 6, 'sefer_tasi', 5, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Ramazan Topaloğlu', 4, 'sefer_tasi', 3, 'Yeni firma');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Bear Tell', 4, 'sefer_tasi', 2, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Subaşı Grup', 5, 'sefer_tasi', 10, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Artiz Medya', 4, 'sefer_tasi', 4, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Bianco', 5, 'sefer_tasi', 4, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Beta Makina', 4, 'kuvet', 6, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Vitrin Eczanesi', 4, 'sefer_tasi', 3, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Ufuk Mesken Çayyolu', 4, 'sefer_tasi', NULL, 'Bol kepçe');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Günteks', 4, 'sefer_tasi', 5, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Gülfem Hanım', 4, 'sefer_tasi', NULL, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Agel İnşaat', 5, 'kuvet', 11, 'Nisa Derin Küvet - 14 çeşit 4 kişi olacak');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Jargon Reklam', 4, 'tepsi', 9, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Suat Doğancı', 5, 'poset', 3, NULL);
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Retro', 4, 'kuvet', 10, 'Ana yemek uzun küvet');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Doğan Salata Bar', 5, 'sefer_tasi', 20, 'Salata Bar');
INSERT INTO customers (name, default_variety_count, default_container_type, default_portion_count, special_notes) VALUES ('Çizgi Giyim', 4, 'paket', 20, NULL);

-- Örnek Haftalık Menü
INSERT INTO weekly_menus (week_start_date, status) VALUES ('2026-02-09', 'published');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 0, 1, 'Ezogelin Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 0, 2, 'Etli Bezelye', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 0, 3, 'Pilav', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 0, 4, 'Yoğurt', 'tatli');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 1, 1, 'Yayla Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 1, 2, 'Rosto Köfte-Püre', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 1, 3, 'Makarna', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 1, 4, 'Sütlü Tatlı', 'tatli');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 2, 1, 'Mercimek Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 2, 2, 'Tavuk Döner', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 2, 3, 'Pilav', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 2, 4, 'Ayran', 'icecek');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 3, 1, 'Arpa Şehriye Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 3, 2, 'Kağıt Kebabı', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 3, 3, 'Mısırlı Bulgur Pilavı', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 3, 4, 'Mor Sultan', 'tatli');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 4, 1, 'Mantar Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 4, 2, 'Karışık Izgara', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 4, 3, 'Pilav', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 4, 4, 'Cola', 'icecek');

INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 5, 1, 'Tarhana Çorbası', 'corba');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 5, 2, 'Kıymalı Pide', 'ana_yemek');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 5, 3, 'Salata', 'garnitur');
INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category) VALUES (1, 5, 4, 'Ayran', 'icecek');

-- Örnek Tedarikçiler
INSERT INTO suppliers (name, contact_name, phone, category) VALUES ('Ankara Et', 'Mehmet Bey', '05559876543', 'et');
INSERT INTO suppliers (name, contact_name, phone, category) VALUES ('Taze Sebze Market', 'Ali Bey', '05559876544', 'sebze');
INSERT INTO suppliers (name, contact_name, phone, category) VALUES ('Baklagil A.Ş.', 'Ayşe Hanım', '05559876545', 'kurubaklagil');
