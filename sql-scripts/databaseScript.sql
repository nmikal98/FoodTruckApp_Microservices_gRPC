DROP DATABASE IF EXISTS foodtruckdb;


CREATE DATABASE foodtruckdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE foodtruckdb;



CREATE TABLE IF NOT EXISTS accounts (
	id int(11) NOT NULL AUTO_INCREMENT,
  	username varchar(50) NOT NULL,
  	userPsw varchar(255) NOT NULL,
  	email varchar(100) NOT NULL,
	phoneNumber varchar(50) NOT NULL,
	deliveryAddress varchar(200) NOT NULL,
    PRIMARY KEY (id),
	CONSTRAINT u_person UNIQUE (username)
) DEFAULT CHARSET=utf8;



CREATE TABLE IF NOT EXISTS orders (
	id int(11) NOT NULL AUTO_INCREMENT,
	userid  int(11) NOT NULL,
  	truckname varchar(100) NOT NULL,
  	locations varchar(100) NOT NULL,
	orderDetails LONGTEXT NOT NULL,
	dateofinsert datetime NOT NULL,
    PRIMARY KEY (id),
	FOREIGN KEY (userid) REFERENCES accounts(id)

) DEFAULT CHARSET=utf8;

LOCK TABLES `accounts` WRITE;
INSERT INTO `accounts` VALUES 
(1, 'user', '$2b$12$YrFlS6/VJ3Unojf/hnBi1eKQk1jr1VpzE2/ak016.wl3JdUAfq9zS', 'mail@email.com', '99000000', 'address' );
UNLOCK TABLES;


