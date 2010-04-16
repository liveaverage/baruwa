-- MySQL dump 10.11
--
-- Current Database: baruwa
--

CREATE DATABASE IF NOT EXISTS baruwa;

USE baruwa;
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `audit_log` (
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `user` varchar(20) NOT NULL default '',
  `ip_address` varchar(15) NOT NULL default '',
  `action` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL auto_increment,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `permission_id_refs_id_a7792de1` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `user_id_refs_id_9af0b65a` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL auto_increment,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `group_id_refs_id_f0ee9890` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `permission_id_refs_id_67e79cb` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `blacklist`
--

DROP TABLE IF EXISTS `blacklist`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `blacklist` (
  `id` int(11) NOT NULL auto_increment,
  `to_address` text,
  `to_domain` text,
  `from_address` text,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `blacklist_uniq` (`to_address`(100),`from_address`(100))
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY  (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `maillog`
--

DROP TABLE IF EXISTS `maillog`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `maillog` (
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `id` mediumtext,
  `size` bigint(20) default '0',
  `from_address` mediumtext,
  `from_domain` mediumtext,
  `to_address` mediumtext,
  `to_domain` mediumtext,
  `subject` mediumtext,
  `clientip` mediumtext,
  `archive` mediumtext,
  `isspam` tinyint(1) default '0',
  `ishighspam` tinyint(1) default '0',
  `issaspam` tinyint(1) default '0',
  `isrblspam` tinyint(1) default '0',
  `isfp` tinyint(1) default '0',
  `isfn` tinyint(1) default '0',
  `spamwhitelisted` tinyint(1) default '0',
  `spamblacklisted` tinyint(1) default '0',
  `sascore` decimal(7,2) default '0.00',
  `spamreport` mediumtext,
  `virusinfected` tinyint(1) default '0',
  `nameinfected` tinyint(1) default '0',
  `otherinfected` tinyint(1) default '0',
  `report` mediumtext,
  `ismcp` tinyint(1) default '0',
  `ishighmcp` tinyint(1) default '0',
  `issamcp` tinyint(1) default '0',
  `mcpwhitelisted` tinyint(1) default '0',
  `mcpblacklisted` tinyint(1) default '0',
  `mcpsascore` decimal(7,2) default '0.00',
  `mcpreport` mediumtext,
  `hostname` mediumtext,
  `date` date default NULL,
  `time` time default NULL,
  `headers` mediumtext,
  `quarantined` tinyint(1) default '0',
  KEY `maillog_datetime_idx` (`date`,`time`),
  KEY `maillog_id_idx` (`id`(20)),
  KEY `maillog_clientip_idx` (`clientip`(20)),
  KEY `maillog_from_idx` (`from_address`(200)),
  KEY `maillog_to_idx` (`to_address`(200)),
  KEY `maillog_host` (`hostname`(30)),
  KEY `from_domain_idx` (`from_domain`(50)),
  KEY `to_domain_idx` (`to_domain`(50)),
  KEY `maillog_quarantined` (`quarantined`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `mcp_rules`
--

DROP TABLE IF EXISTS `mcp_rules`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `mcp_rules` (
  `rule` char(100) NOT NULL default '',
  `rule_desc` char(200) NOT NULL default '',
  PRIMARY KEY  (`rule`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sa_rules`
--

DROP TABLE IF EXISTS `sa_rules`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `sa_rules` (
  `rule` varchar(100) NOT NULL default '',
  `rule_desc` varchar(200) NOT NULL default '',
  PRIMARY KEY  (`rule`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `saved_filters`
--

DROP TABLE IF EXISTS `saved_filters`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `saved_filters` (
  `id` int(11) NOT NULL auto_increment,
  `name` text NOT NULL,
  `col` text NOT NULL,
  `operator` text NOT NULL,
  `value` text NOT NULL,
  `username` text NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `unique_filters` (`name`(20),`col`(20),`operator`(20),`value`(20),`username`(20))
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `spamscores`
--

DROP TABLE IF EXISTS `spamscores`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `spamscores` (
  `user` varchar(40) NOT NULL default '',
  `lowspamscore` decimal(10,0) NOT NULL default '0',
  `highspamscore` decimal(10,0) NOT NULL default '0',
  PRIMARY KEY  (`user`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_filters`
--

DROP TABLE IF EXISTS `user_filters`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_filters` (
  `id` int(11) NOT NULL auto_increment,
  `username` varchar(60) NOT NULL default '',
  `filter` text,
  `verify_key` varchar(32) NOT NULL default '',
  `active` enum('N','Y') default 'N',
  PRIMARY KEY  (`id`),
  KEY `user_filters_username_idx` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `users` (
  `username` varchar(60) NOT NULL default '',
  `password` varchar(32) default NULL,
  `fullname` varchar(50) NOT NULL default '',
  `type` enum('A','D','U','R','H') default NULL,
  `quarantine_report` tinyint(1) default '0',
  `spamscore` tinyint(4) default '0',
  `highspamscore` tinyint(4) default '0',
  `noscan` tinyint(1) default '0',
  `quarantine_rcpt` varchar(60) default NULL,
  PRIMARY KEY  (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `whitelist`
--

DROP TABLE IF EXISTS `whitelist`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `whitelist` (
  `id` int(11) NOT NULL auto_increment,
  `to_address` text,
  `to_domain` text,
  `from_address` text,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `whitelist_uniq` (`to_address`(100),`from_address`(100))
) ENGINE=MyISAM AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
