/*
 Navicat Premium Data Transfer

 Source Server         : mysql-3000
 Source Server Type    : MySQL
 Source Server Version : 50646
 Source Host           : localhost
 Source Database       : sky_main

 Target Server Type    : MySQL
 Target Server Version : 50646
 File Encoding         : utf-8

 Date: 12/12/2019 15:03:22 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库
DROP database IF EXISTS `sky_main`;
create database `sky_main` default character set utf8mb4 collate utf8mb4_unicode_ci;
-- 切换到test_data数据库
use sky_main;

-- ----------------------------
--  Table structure for `bao_file`
-- ----------------------------
DROP TABLE IF EXISTS `bao_file`;
CREATE TABLE `bao_file` (
  `file_id` int(11) NOT NULL AUTO_INCREMENT,
  `file_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件的hash值，上传文件的时候会生成',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '如果没有指定文件名，则会随机生成一个',
  `file_type` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '指的是文件的mimetype',
  PRIMARY KEY (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Table structure for `bao_file_user`
-- ----------------------------
DROP TABLE IF EXISTS `bao_file_user`;
CREATE TABLE `bao_file_user` (
  `file_user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `add_time` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_user_state` smallint(6) DEFAULT NULL COMMENT '0 创建 1 损坏或丢失',
  PRIMARY KEY (`file_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Table structure for `bao_login_record`
-- ----------------------------
DROP TABLE IF EXISTS `bao_login_record`;
CREATE TABLE `bao_login_record` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `login_time` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log_ip` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Table structure for `bao_user`
-- ----------------------------
DROP TABLE IF EXISTS `bao_user`;
CREATE TABLE `bao_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sex` smallint(1) DEFAULT NULL COMMENT '性别  0 未设置 1 男性 2 女性',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nickname` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '密码 md5 加密文',
  `status` smallint(3) DEFAULT NULL COMMENT '用户状态 0 未激活 1 正常 2...',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
