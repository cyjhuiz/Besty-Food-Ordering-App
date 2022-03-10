-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 12, 2020 at 02:17 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


--
-- Database: `user`
CREATE DATABASE IF NOT EXISTS `user` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `user`;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `UserId` int(11) NOT NULL AUTO_INCREMENT,
  `UserEmail` varchar(40) NOT NULL,
  `UserPassword` varchar(20) NOT NULL,
  `UserFirstName` varchar(20) NOT NULL,
  `UserLastName` varchar(20) NOT NULL,
  `UserMobile` varchar(10) NOT NULL,
  `UserTBankId` varchar(20) NULL,
  `UserAccId` varchar(20) NULL,
  `UserPin` varchar(20) NULL,
  PRIMARY KEY (`UserId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`UserId`, `UserEmail`, `UserPassword`,  `UserFirstName`, `UserLastName`,  `UserMobile`, `UserTBankId`, `UserAccId`, `UserPin`) VALUES
(NULL, 'appletan123z@gmail.com', 'apple123', 'Apple', 'Tan',  '6597898969', '7438', 'ILoveESD', '999999'),
(NULL, 'appleteo@gmail.com', 'apple456', 'Apple', 'Teo',  '6591234267', NULL, NULL, NULL),
(NULL, 'appleting@gmail.com', 'apple789', 'Apple', 'Ting',  '6594235567', NULL, NULL, NULL);


COMMIT;

