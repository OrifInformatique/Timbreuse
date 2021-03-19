#------------------------------------------------------------
#        Script MySQL.
#------------------------------------------------------------


#------------------------------------------------------------
# Table: t_timbreuse
#------------------------------------------------------------

CREATE TABLE t_timbreuse(
        id_timbreuse Int  Auto_increment  NOT NULL
	,CONSTRAINT t_timbreuse_PK PRIMARY KEY (id_timbreuse)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_section
#------------------------------------------------------------

CREATE TABLE t_section(
        id_section   Int  Auto_increment  NOT NULL ,
        nom_section  Varchar (5) NOT NULL ,
        lieu_section Varchar (50) NOT NULL
	,CONSTRAINT t_section_PK PRIMARY KEY (id_section)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_assures
#------------------------------------------------------------

CREATE TABLE t_assures(
        id_assures       Int  Auto_increment  NOT NULL ,
        nom_assures      Varchar (50) NOT NULL ,
        prenom_assures   Varchar (50) NOT NULL ,
        username_assures Char (5) NOT NULL
	,CONSTRAINT t_assures_PK PRIMARY KEY (id_assures)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_msps
#------------------------------------------------------------

CREATE TABLE t_msps(
        id_msps     Int  Auto_increment  NOT NULL ,
        nom_msps    Varchar (5) NOT NULL ,
        prenom_msps Varchar (5) NOT NULL ,
        admin_msps  Bool NOT NULL
	,CONSTRAINT t_msps_PK PRIMARY KEY (id_msps)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_rfid
#------------------------------------------------------------

CREATE TABLE t_rfid(
        id_rfid  Int  Auto_increment  NOT NULL ,
        uid_rfid Numeric NOT NULL
	,CONSTRAINT t_rfid_PK PRIMARY KEY (id_rfid)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_timbrage
#------------------------------------------------------------

CREATE TABLE t_timbrage(
        id_timbrage  Int  Auto_increment  NOT NULL ,
        in_timbrage  TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP ,
        out_timbrage TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP
	,CONSTRAINT t_timbrage_PK PRIMARY KEY (id_timbrage)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: t_log
#------------------------------------------------------------

CREATE TABLE t_log(
        id_log          Int  Auto_increment  NOT NULL ,
        nom_log         Varchar (5) NOT NULL ,
        description_log Text NOT NULL ,
        heure_log       TimeStamp NOT NULL ,
        admin_log       Int NOT NULL
	,CONSTRAINT t_log_PK PRIMARY KEY (id_log)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: timbreuse_appartient_section
#------------------------------------------------------------

CREATE TABLE timbreuse_appartient_section(
        id_timbreuse Int NOT NULL ,
        id_section   Int NOT NULL
	,CONSTRAINT timbreuse_appartient_section_PK PRIMARY KEY (id_timbreuse,id_section)

	,CONSTRAINT timbreuse_appartient_section_t_timbreuse_FK FOREIGN KEY (id_timbreuse) REFERENCES t_timbreuse(id_timbreuse)
	,CONSTRAINT timbreuse_appartient_section_t_section0_FK FOREIGN KEY (id_section) REFERENCES t_section(id_section)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: section_avoir_msp
#------------------------------------------------------------

CREATE TABLE section_avoir_msp(
        id_section Int NOT NULL ,
        id_msps    Int NOT NULL
	,CONSTRAINT section_avoir_msp_PK PRIMARY KEY (id_section,id_msps)

	,CONSTRAINT section_avoir_msp_t_section_FK FOREIGN KEY (id_section) REFERENCES t_section(id_section)
	,CONSTRAINT section_avoir_msp_t_msps0_FK FOREIGN KEY (id_msps) REFERENCES t_msps(id_msps)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: msp_avoir_badge
#------------------------------------------------------------

CREATE TABLE msp_avoir_badge(
        id_rfid Int NOT NULL ,
        id_msps Int NOT NULL
	,CONSTRAINT msp_avoir_badge_PK PRIMARY KEY (id_rfid,id_msps)

	,CONSTRAINT msp_avoir_badge_t_rfid_FK FOREIGN KEY (id_rfid) REFERENCES t_rfid(id_rfid)
	,CONSTRAINT msp_avoir_badge_t_msps0_FK FOREIGN KEY (id_msps) REFERENCES t_msps(id_msps)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: section_avoir_assure
#------------------------------------------------------------

CREATE TABLE section_avoir_assure(
        id_assures Int NOT NULL ,
        id_section Int NOT NULL
	,CONSTRAINT section_avoir_assure_PK PRIMARY KEY (id_assures,id_section)

	,CONSTRAINT section_avoir_assure_t_assures_FK FOREIGN KEY (id_assures) REFERENCES t_assures(id_assures)
	,CONSTRAINT section_avoir_assure_t_section0_FK FOREIGN KEY (id_section) REFERENCES t_section(id_section)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: assures_avoir_badge
#------------------------------------------------------------

CREATE TABLE assures_avoir_badge(
        id_rfid    Int NOT NULL ,
        id_assures Int NOT NULL
	,CONSTRAINT assures_avoir_badge_PK PRIMARY KEY (id_rfid,id_assures)

	,CONSTRAINT assures_avoir_badge_t_rfid_FK FOREIGN KEY (id_rfid) REFERENCES t_rfid(id_rfid)
	,CONSTRAINT assures_avoir_badge_t_assures0_FK FOREIGN KEY (id_assures) REFERENCES t_assures(id_assures)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: badge_avoir_timbrage
#------------------------------------------------------------

CREATE TABLE badge_avoir_timbrage(
        id_timbrage Int NOT NULL ,
        id_rfid     Int NOT NULL
	,CONSTRAINT badge_avoir_timbrage_PK PRIMARY KEY (id_timbrage,id_rfid)

	,CONSTRAINT badge_avoir_timbrage_t_timbrage_FK FOREIGN KEY (id_timbrage) REFERENCES t_timbrage(id_timbrage)
	,CONSTRAINT badge_avoir_timbrage_t_rfid0_FK FOREIGN KEY (id_rfid) REFERENCES t_rfid(id_rfid)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: timbreuse_avoir_timbrage
#------------------------------------------------------------

CREATE TABLE timbreuse_avoir_timbrage(
        id_timbrage  Int NOT NULL ,
        id_timbreuse Int NOT NULL
	,CONSTRAINT timbreuse_avoir_timbrage_PK PRIMARY KEY (id_timbrage,id_timbreuse)

	,CONSTRAINT timbreuse_avoir_timbrage_t_timbrage_FK FOREIGN KEY (id_timbrage) REFERENCES t_timbrage(id_timbrage)
	,CONSTRAINT timbreuse_avoir_timbrage_t_timbreuse0_FK FOREIGN KEY (id_timbreuse) REFERENCES t_timbreuse(id_timbreuse)
)ENGINE=InnoDB;


#------------------------------------------------------------
# Table: timbreuse_avoir_log
#------------------------------------------------------------
CREATE TABLE timbreuse_avoir_log(
        id_log  Int NOT NULL ,
        id_timbreuse Int NOT NULL        
	,CONSTRAINT timbreuse_avoir_log_PK PRIMARY KEY (id_log,id_timbreuse)

	,CONSTRAINT timbreuse_avoir_log_t_log_FK FOREIGN KEY (id_log) REFERENCES t_log(id_log)
	,CONSTRAINT timbreuse_avoir_log_t_timbreuse0_FK FOREIGN KEY (id_timbreuse) REFERENCES t_timbreuse(id_timbreuse)
)ENGINE=InnoDB;


