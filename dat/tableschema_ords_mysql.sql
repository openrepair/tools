DROP TABLE IF EXISTS `{0}`;
CREATE TABLE `{0}` (
  `product_category_id` int NOT NULL,
  `product_category` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`product_category_id`),
  KEY `product_category` (`product_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DROP TABLE IF EXISTS `{1}`;
CREATE TABLE `{1}` (
  `id` varchar(32),
  `data_provider` varchar(32) DEFAULT NULL,
  `country` varchar(3) DEFAULT NULL,
  `partner_product_category` varchar(255) DEFAULT NULL,
  `product_category` varchar(64) DEFAULT NULL,
  `product_category_id` smallint UNSIGNED DEFAULT NULL,
  `brand` varchar(128) DEFAULT NULL,
  `year_of_manufacture` varchar(4) DEFAULT NULL,
  `product_age` varchar(6) DEFAULT NULL,
  `repair_status` varchar(16) DEFAULT NULL,
  `repair_barrier_if_end_of_life` varchar(32) DEFAULT NULL,
  `group_identifier` varchar(128) DEFAULT NULL,
  `event_date` varchar(10) DEFAULT NULL,
  `problem` text,
  PRIMARY KEY `id` (`id`),
  KEY `product_category` (`product_category`),
  KEY `product_category_id` (`product_category_id`),
  KEY `data_provider` (`data_provider`),
  KEY `product_age` (`product_age`),
  KEY `repair_status` (`repair_status`),
  KEY `repair_barrier_if_end_of_life` (`repair_barrier_if_end_of_life`),
  KEY `event_date` (`event_date`),
  FULLTEXT `problem` (`problem`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
