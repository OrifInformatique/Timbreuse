USE `timbreuse2022`;

DELIMITER //

CREATE PROCEDURE `insert_log`(id_badge BIGINT, inside BOOL)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `log_write` (`date`, `id_badge`, `inside`) VALUES (NOW(), id_badge, inside);
    CALL `delete_log_write`;
END//

CREATE PROCEDURE `insert_sync_log`(_date DATETIME, _id_badge BIGINT, _inside BOOL, _id_log INT, _id_user INT, _date_badge DATETIME, _date_modif DATETIME, _date_delete DATETIME)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `log_sync` (`date`, `id_badge`, `inside`, `id_log`, `id_user`, `date_badge`, `date_modif`, `date_delete`)
    VALUES (_date, _id_badge, _inside, _id_log, _id_user, _date_badge, _date_modif, _date_delete)
    ON DUPLICATE KEY UPDATE `date`=_date, `id_badge`=_id_badge, `inside`=_inside, `id_log`=_id_log, `id_user`=_id_user, `date_badge`=_date_badge, `date_modif`=_date_modif, `date_delete`=_date_delete;
    CALL `delete_log_write`;
END//

CREATE PROCEDURE `insert_badge`(id_badge BIGINT, id_user INT)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `badge_write` (`id_badge`, `id_user`) VALUES (id_badge, id_user);
    CALL `delete_badge_write`;
END//

CREATE PROCEDURE `insert_user`(_name TEXT, _surname TEXT)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `user_write` (`name`, `surname`) VALUES (_name, _surname);
    CALL `delete_user_write`;
END//

CREATE PROCEDURE `insert_user_sync`(_id_user int, _name text, _surname text, _date_modif datetime, _date_delete datetime)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `user_sync` (`id_user`, `name`, `surname`, `date_modif`, `date_delete`)
    VALUES (_id_user, _name, _surname, _date_modif, _date_delete)
    ON DUPLICATE KEY UPDATE `id_user`=_id_user, `name`=_name, `surname`=_surname, `date_modif`=_date_modif, `date_delete`=_date_delete;
END//

CREATE PROCEDURE `insert_badge_sync`(_id_badge bigint, _id_user int, _rowid_badge int, _date_modif datetime, _date_delete datetime)
MODIFIES SQL DATA
BEGIN
    INSERT INTO `badge_sync` (`id_badge`, `id_user`, `rowid_badge`, `date_modif`, `date_delete`)
    VALUES (_id_badge, _id_user, _rowid_badge, _date_modif, _date_delete)
    ON DUPLICATE KEY UPDATE `id_badge`=_id_badge, `id_user`=_id_user, `rowid_badge`=_rowid_badge, `date_modif`=_date_modif, `date_delete`=_date_delete;
END//

CREATE PROCEDURE `delete_badge_and_user_write`()
MODIFIES SQL DATA
BEGIN
    CALL `delete_badge_write`;
    CALL `delete_user_write`;
END//

DELIMITER ;
