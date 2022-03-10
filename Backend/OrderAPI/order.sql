SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
SET AUTOCOMMIT = 0;


CREATE DATABASE IF NOT EXISTS `order` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `order`;



DROP TABLE IF EXISTS `order`;
CREATE TABLE IF NOT EXISTS `order` (
  `OrderId` int(11) NOT NULL,
  `FoodId` int(11) NOT NULL,
  `OrderItem` varchar(20) NOT NULL,
  `ItemPrice` float(5,2) NOT NULL,
  `NetItemPrice` float(5,2) NOT NULL,
  `ItemQuantity` int(11) NOT NULL,
  `OrderDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UserId` int(11) NOT NULL,
  `OrderStatus` varchar(20) NOT NULL,
  PRIMARY KEY (`OrderId`, `FoodId`)
) ENGINE=InnoDB  AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO `order` (`OrderId`, `FoodId`, `OrderItem`, `ItemPrice`, `NetItemPrice`, `ItemQuantity`, `UserId`,  `OrderStatus`) VALUES
(1, 1,'Beef Bulgogi', '10.50', '10.50', '2', '1', 'Preparing'),
(1, 2, 'Burrito', '7.00', '7.00','2', '1', 'Preparing'),
(1, 3, 'Chicken', '5.00', '5.00','2', '1', 'Preparing'),
(1, 4, 'Classic_Fries', '3.00', '3.00','2', '1', 'Preparing'),
(1, 5, 'Coke', '2.00', '2.00','2', '1', 'Preparing'),
(1, 6, 'Ice_Lemon', '2.00', '2.00','2', '1', 'Preparing'),
(1, 7, 'Lim', '2.00', '2.00','2', '1', 'Preparing'),
(1, 8, 'Milk_Tea', '3.00', '3.00','2', '1', 'Preparing'),
(1, 9, 'Nachos', '4.00', '4.00','2', '1', 'Preparing'),
(1, 10, 'Nuggets', '6.00', '6.00','2', '1', 'Preparing'),
(1, 11, 'OnionRings', '4.00', '4.00','2', '1', 'Preparing'),
(1, 12, 'Peach_Red', '3.00', '3.00','2', '1', 'Preparing'),
(1, 13, 'Pork', '8.00', '8.00','2', '1', 'Preparing'),
(1, 14, 'Potato_Fries', '3.00', '3.00','2', '1', 'Preparing'),
(1, 15, 'Quesadilla', '5.00', '5.00','2', '1', 'Preparing'),
(1, 16, 'Spicy_Potato_Fries', '4.00', '4.00','2', '1', 'Preparing'),
(1, 17, 'Tarcos', '6.00', '6.00','2', '1', 'Preparing'),
(1, 18, 'Tofu', '3.00', '3.00','2', '1', 'Preparing');
COMMIT;
