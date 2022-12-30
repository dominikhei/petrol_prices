CREATE TABLE IF NOT EXISTS petrol_data(
                      load_id BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                      id VARCHAR(36) NOT NULL,
                      name VARCHAR(100),
                      price FLOAT(4),
                      street Varchar(100),
                      houseNumber Varchar(20),
                      date DATE,
                      time Varchar(5));