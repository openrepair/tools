DROP TABLE IF EXISTS `{0}`;
CREATE TABLE `{0}` (
  `product_category_id` int NOT NULL,
  `product_category` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
ALTER TABLE `{0}`
  ADD PRIMARY KEY (`product_category_id`),
  ADD KEY `product_category` (`product_category`);
ALTER TABLE `{0}`
  MODIFY `product_category_id` int NOT NULL AUTO_INCREMENT;
DROP TABLE IF EXISTS `{1}`;
CREATE TABLE `{1}` (
  `id` varchar(32) DEFAULT NULL,
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
  `group_identifier` varchar(64) DEFAULT NULL,
  `event_date` varchar(10) DEFAULT NULL,
  `problem` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
ALTER TABLE `{1}`
  ADD KEY `id` (`id`),
  ADD KEY `product_category` (`product_category`),
  ADD KEY `product_category_id` (`product_category_id`),
  ADD KEY `data_provider` (`data_provider`),
  ADD KEY `product_age` (`product_age`),
  ADD KEY `repair_status` (`repair_status`),
  ADD KEY `repair_barrier_if_end_of_life` (`repair_barrier_if_end_of_life`),
  ADD KEY `event_date` (`event_date`);
ALTER TABLE `{1}` ADD FULLTEXT KEY `problem` (`problem`);