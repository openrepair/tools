DROP TABLE IF EXISTS `{tablename}`;
CREATE TABLE `{tablename}` (
  `id_ords` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_provider` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `country` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `problem` text COLLATE utf8mb4_unicode_ci,
  `language_known` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `translator` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_detected` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `en` text COLLATE utf8mb4_unicode_ci,
  `de` text COLLATE utf8mb4_unicode_ci,
  `nl` text COLLATE utf8mb4_unicode_ci,
  `fr` text COLLATE utf8mb4_unicode_ci,
  `it` text COLLATE utf8mb4_unicode_ci,
  `es` text COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `{tablename}`
  ADD PRIMARY KEY (`id_ords`),
  ADD KEY `data_provider` (`data_provider`),
  ADD KEY `country` (`country`),
  ADD KEY `translator` (`translator`),
  ADD KEY `language_known` (`language_known`),
  ADD KEY `lang_detected` (`language_detected`),
  ADD KEY `problem` (`problem`(64));
