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
-- Database: `food`
CREATE DATABASE IF NOT EXISTS `food` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `food`;

-- --------------------------------------------------------

--
-- Table structure for table `food`
--

DROP TABLE IF EXISTS `food`;
CREATE TABLE IF NOT EXISTS `food` (
  `FoodId` int(11) NOT NULL AUTO_INCREMENT,
  `FoodName` varchar(20) NOT NULL,
  `FoodPrice` float(5,2) NOT NULL,
  `FoodCategory` varchar(20) NOT NULL,
  `FoodImgUrl` varchar(80) NOT NULL,
  `FoodAvailability` varchar(20) NOT NULL DEFAULT "Available",
  PRIMARY KEY (`FoodId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `food`
--

INSERT INTO `food` (`FoodId`, `FoodName`, `FoodPrice`, `FoodImgUrl`, `FoodCategory`, `FoodAvailability`) VALUES
(NULL, 'Beef Bulgogi', 10.50 , "https://betsy-food-img.s3.amazonaws.com/1.2021-04-04.09:46:31.jpg", 'Korean Bowl', "Available"),
(NULL, 'Fries', 3.50 , "https://betsy-food-img.s3.amazonaws.com/2.2021-04-04.09:46:31.jpg", 'Small Bites', "Available"),
(NULL, 'Coke', 2.00 , "https://betsy-food-img.s3.amazonaws.com/3.2021-04-04.09:46:31.jpg", 'Drinks', "Available");


COMMIT;

