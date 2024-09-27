DROP TABLE IF EXISTS `ords_problem_translations`;
CREATE TABLE `ords_problem_translations` (
  `id_ords` varchar(16)  NOT NULL,
  `data_provider` varchar(32)  NOT NULL,
  `country` varchar(3)  NOT NULL,
  `problem` text ,
  `language_known` varchar(2) ,
  `translator` varchar(32) ,
  `language_detected` varchar(2) ,
  `en` text ,
  `de` text ,
  `nl` text ,
  `fr` text ,
  `it` text ,
  `es` text ,
  `da` text ,
  PRIMARY KEY (`id_ords`),
  KEY `data_provider` (`data_provider`),
  KEY `country` (`country`),
  KEY `translator` (`translator`),
  KEY `language_known` (`language_known`),
  KEY `lang_detected` (`language_detected`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;