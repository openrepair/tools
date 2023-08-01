DROP TABLE IF EXISTS `ords_problem_translations`;
CREATE TABLE `ords_problem_translations` (
  `id_ords` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_provider` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `country` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `problem` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `language_known` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `translator` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_detected` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `en` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `de` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `nl` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `fr` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `it` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `es` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `da` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


ALTER TABLE `ords_problem_translations`
  ADD PRIMARY KEY (`id_ords`),
  ADD KEY `data_provider` (`data_provider`),
  ADD KEY `country` (`country`),
  ADD KEY `translator` (`translator`),
  ADD KEY `language_known` (`language_known`),
  ADD KEY `lang_detected` (`language_detected`),
  ADD KEY `problem` (`problem`(64));
