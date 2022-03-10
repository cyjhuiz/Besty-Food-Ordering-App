SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


CREATE DATABASE IF NOT EXISTS `credit` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `credit`;



DROP TABLE IF EXISTS `credit`;
CREATE TABLE IF NOT EXISTS `credit` (
  `UserId` int(11) NOT NULL,
  `UserCredits` float(5,2) NOT NULL,
  `PointsDatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserId`,`PointsDatetime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `credit` (`UserId`, `UserCredits`) VALUES
('1', '2.5'),
('2', '2.5');

COMMIT;