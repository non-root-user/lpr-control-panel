import mysql.connector

def initialize_the_database(db):
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS ponies (
        id                  INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        username            VARCHAR(128) NOT NULL UNIQUE,
        password            VARCHAR(128) NOT NULL,
        avatar              MEDIUMBLOB,
        email               VARCHAR(128) UNIQUE,
        discord_tag         VARCHAR(128),
        register_ip         VARCHAR(128),
        register_date       INT(64),
        last_login_ip       VARCHAR(128),
        last_login_date     INT(64),
        language_code       VARCHAR(8),
        permission_level    INT(128) NOT NULL DEFAULT 0
    ); 
    ''')
    db.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS songs (
        id                  INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        artist              VARCHAR(128) NOT NULL,
        title               VARCHAR(256) NOT NULL,
        fs_filename         VARCHAR(256) NOT NULL UNIQUE,
        audio_format        VARCHAR(6),
        genre               VARCHAR(64),
        date_released       VARCHAR(32),
        album_name          VARCHAR(64),
        fs_album_cover      VARCHAR(256),
        is_public           INT(2)
    ); 
    ''')
    db.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS history (
        songID              INT(11) NOT NULL,
        timestamp           INT(11) NOT NULL    
    ); 
    ''')
    db.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS albumarts (
        id                  INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        image               MEDIUMBLOB  
    ); 
    ''')
    db.commit()
