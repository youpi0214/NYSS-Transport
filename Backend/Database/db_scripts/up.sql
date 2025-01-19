DROP Database IF EXISTS NYSS;
CREATE Database IF NOT EXISTS NYSS;
USE NYSS;

CREATE TABLE user (
    email varchar(100),
    name varchar(100) NOT NULL ,
    password varchar(100) NOT NULL ,
    address varchar(1000) NOT NULL ,
    birthday date NOT NULL ,
    phone NUMERIC(10),
    role enum('commuter','admin') DEFAULT 'commuter' NOT NULL ,
    PRIMARY KEY (email),
    CONSTRAINT validEmail CHECK (email LIKE '%@%.%'),
    CONSTRAINT validPhone CHECK (phone > 0)
);

CREATE TABLE creditCard (
    number BIGINT,
    holderName varchar(100) NOT NULL ,
    expirationDate char(5) NOT NULL ,
    PRIMARY KEY (number),
    CONSTRAINT invalidExpirationDate_invalidFormat CHECK (expirationDate LIKE '__/__')
);

CREATE TABLE company (
    name varchar(100),
    PRIMARY KEY (name)
);

CREATE TABLE access (
    id varchar(100),
    name varchar(1000) NOT NULL ,
    price float NOT NULL ,
    company varchar(100),
    type enum('ticket','subscription') NOT NULL,
    duration INT NOT NULL,
    suspended BOOLEAN DEFAULT FALSE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (company) REFERENCES company (name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE commuter(
    user varchar(100),
    creditCard BIGINT ,
    PRIMARY KEY (user),
    FOREIGN KEY (user) REFERENCES user (email) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (creditCard) references creditCard(number) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE admin(
    user varchar(100),
    code varchar(100) NOT NULL UNIQUE ,
    company varchar(100),
    PRIMARY KEY (user),
    FOREIGN KEY (user) REFERENCES user (email) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (company) REFERENCES company (name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE ticket(
    access varchar(100),
    passes integer NOT NULL,
    PRIMARY KEY (access),
    FOREIGN KEY (access) REFERENCES access (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE subscription (
    access varchar(100),
    PRIMARY KEY (access),
    FOREIGN KEY (access) REFERENCES access (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE transaction (
    accessNumber VARCHAR(36),
    transactionNumber BIGINT NOT NULL,
    creditCard BIGINT NOT NULL,
    user varchar(100) NOT NULL,
    accessId varchar(100) NOT NULL ,
    transactionDate DATE NOT NULL ,
    expirationDate DATE NOT NULL ,
    PRIMARY KEY (accessNumber),
    FOREIGN KEY (user) REFERENCES commuter (user)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (accessId) REFERENCES access (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE suspendedAccess (
    access varchar(100),
    deletionDate DATE NOT NULL,
    PRIMARY KEY (access),
    FOREIGN KEY (access) REFERENCES access (id) ON UPDATE CASCADE ON DELETE CASCADE
);


DELIMITER //
-- Trigger to check expiration date before inserting a new credit card
CREATE TRIGGER checkExpirationDateBeforeInsert
BEFORE INSERT ON creditCard
FOR EACH ROW
BEGIN
    -- Declare variables
    DECLARE current_month INT;
    DECLARE current_year INT;
    DECLARE card_month INT;
    DECLARE card_year INT;

    -- Extract current month and year
    SET current_month = MONTH(CURDATE());
    SET current_year = YEAR(CURDATE());
    -- Extract month and year from the new credit card's expiration date
    SET card_month = SUBSTRING(NEW.expirationDate, 1, 2);
    SET card_year = SUBSTRING(NEW.expirationDate, 4, 2);

    -- Check if the expiration date is in the future
    IF (card_year < RIGHT(YEAR(NOW()), 2)) OR
       (card_year = RIGHT(YEAR(NOW()), 2) AND card_month < MONTH(NOW())) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expiration date must be in the future';
    END IF;
END//

DELIMITER ;

DELIMITER //

-- Event to delete suspended accesses daily
CREATE EVENT deleteSuspendedAccess
ON SCHEDULE  EVERY 1 DAY STARTS CURDATE() DO
BEGIN
    -- Declare variables
    DECLARE accessId INT;
    DECLARE complete integer DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT access FROM suspendedAccess WHERE deletionDate <= CURDATE();
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET complete = TRUE;

    OPEN  cur;
    -- Loop through suspended accesses and delete them
    deleteAccesses :LOOP
        FETCH cur INTO accessId;
        -- Check if all accesses are processed
        IF (complete) THEN
            LEAVE deleteAccesses;
        END IF;

        -- Delete the access
        DELETE FROM access WHERE id = accessId;

    end loop deleteAccesses;
    -- Close cursor
    CLOSE cur;
END//

DELIMITER ;


-- ########## 1st migration ##########

DROP FUNCTION IF EXISTS CompanyExists;
DROP PROCEDURE IF EXISTS RegisterCommuter;
DROP PROCEDURE IF EXISTS RegisterAdmin;
DROP PROCEDURE IF EXISTS LoginUser;

DELIMITER //

-- Function to check if a company exists
CREATE FUNCTION CompanyExists(p_company VARCHAR(100)) RETURNS INT DETERMINISTIC
BEGIN
    -- Declare variable to hold the count of companies with the given name
    DECLARE company_count INT;
    -- Count the number of companies with the given name
SELECT COUNT(*) INTO company_count FROM company u WHERE u.name = p_company;
RETURN company_count;
END //

-- Procedure to register a commuter
CREATE PROCEDURE RegisterCommuter(
    IN p_email VARCHAR(100),
    IN p_name VARCHAR(100),
    IN p_password VARCHAR(100),
    IN p_address VARCHAR(1000),
    IN p_dob DATE,
    IN p_phone BIGINT
)
BEGIN
-- Insert user information into the user table
INSERT INTO user (email, name, password, address, birthday, phone, role)
VALUES (p_email, p_name, p_password, p_address, p_dob, p_phone, 'commuter');
-- Insert commuter information into the commuter table
INSERT INTO commuter (user)
VALUES (p_email);
END //

-- Procedure to register an admin
CREATE PROCEDURE RegisterAdmin(
    IN p_email VARCHAR(100),
    IN p_name VARCHAR(100),
    IN p_password VARCHAR(100),
    IN p_address VARCHAR(1000),
    IN p_dob DATE,
    IN p_phone BIGINT,
    IN p_admin_code VARCHAR(100),
    IN p_company VARCHAR(100)
)
BEGIN
    -- Check if the company exists, if not, insert it
    IF (SELECT CompanyExists(p_company)) = 0 THEN
        INSERT INTO company (name)
        VALUES (p_company);
END IF;
    -- Insert user information into the user table
INSERT INTO user (email, name, password, address, birthday, phone, role)
VALUES (p_email, p_name, p_password, p_address, p_dob, p_phone, 'admin');
-- Insert admin information into the admin table
INSERT INTO admin (user, code, company)
VALUES (p_email, p_admin_code, p_company);
END //

-- Procedure to login a user
CREATE PROCEDURE LoginUser(
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(100),
    IN p_admin_code VARCHAR(100)
)
BEGIN
    -- Declare variable to hold the role of the user
    DECLARE user_role ENUM('commuter', 'admin');
    -- Retrieve the role of the user based on email and password
SELECT role INTO user_role FROM user
WHERE email = p_email AND password = p_password;

-- If user role is not found, signal an error
IF user_role IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid email or password';
ELSE
        -- Check user role and perform actions accordingly
        CASE user_role
            WHEN 'commuter' THEN
                -- If user is a commuter, select commuter information
SELECT * FROM commuter WHERE user = p_email;
WHEN 'admin' THEN
                -- If user is an admin, check if admin code is provided
                IF p_admin_code IS NULL THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Admin code is required for admin login';
ELSE
                    -- Select admin information if admin code is provided
SELECT * FROM admin WHERE user = p_email AND code = p_admin_code;
END IF;
END CASE;
END IF;
END; //
DELIMITER ;


-- ########## 2nd migration ##########

DROP FUNCTION IF EXISTS RetrieveWallet;
DROP FUNCTION IF EXISTS AddAccess;



DELIMITER //
-- Function to add an access
CREATE FUNCTION AddAccess(
    p_access_id VARCHAR(100),
    p_access_name VARCHAR(1000),
    p_price FLOAT,
    p_company_name VARCHAR(100),
    p_access_type enum('ticket','subscription'),
    p_duration INT,
    p_numberOfPassage integer
        ) RETURNS VARCHAR(10000) DETERMINISTIC
BEGIN
    -- Declare variable for access info
    DECLARE access_created VARCHAR(10000);

    -- Insert the company if it does not exist
    INSERT IGNORE INTO company (name) VALUES (p_company_name);

    -- Insertion into the table access
INSERT INTO access (id, name, price, company, type, duration)
VALUES (p_access_id, p_access_name, p_price, p_company_name, p_access_type, p_duration);

-- Insertion into the appropriate table based on the access type
IF p_access_type = 'ticket' THEN
        INSERT INTO ticket (access, passes) VALUES (p_access_id, p_numberOfPassage);
    ELSEIF p_access_type = 'subscription' THEN
        INSERT INTO subscription (access) VALUES (p_access_id);
END IF;

    -- Set the JSON array for an added access
    SET access_created = CONCAT(
    '{"accessId": "', p_access_id, '",',
    '"accessName": "', p_access_name, '",',
    '"price": "', p_price, '",',
    '"accessType": "', p_access_type, '",',
    '"duration": "', p_duration, '",',
    '"company": "', p_company_name, '"',
    IF(p_access_type = 'ticket', CONCAT(',"numberOfPassage": "', p_numberOfPassage, '"'), ''),
    '}'
);

RETURN access_created;
END //
DELIMITER ;

-- ########## 3rd migration ##########

DROP PROCEDURE IF EXISTS addCreditcard;
DROP PROCEDURE IF EXISTS replaceCreditcard;
DROP PROCEDURE IF EXISTS deleteCreditcard;


DELIMITER //

-- Procedure to add a credit card to a user's account
CREATE PROCEDURE addCreditcard(IN holder varchar(100), IN cardNumber BIGINT, IN expiration varchar(5),IN userEmail varchar(100))
BEGIN
    -- Declare variable to hold the old card number
    DECLARE oldCardNumber BIGINT;

    -- Check if the user exists
    IF NOT EXISTS (SELECT * FROM commuter WHERE user = userEmail) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User does not exist';
END IF;

    -- Retrieve the current credit card number of the user
SELECT creditCard INTO oldCardNumber FROM commuter WHERE user = userEmail;

-- Check if the new credit card information does not exist in the database
IF NOT EXISTS (SELECT * FROM creditCard WHERE number = cardNumber AND holderName = holder AND expirationDate = expiration) THEN
        INSERT INTO creditCard (holderName, Number, expirationDate) VALUES (holder, cardNumber, expiration);
END IF;

    -- Update the user's credit card information with the new card number
UPDATE commuter SET creditCard = cardNumber WHERE user = userEmail;

-- Check if the old credit card is not associated with any user
IF NOT EXISTS (SELECT * FROM commuter WHERE creditCard = oldCardNumber) THEN
DELETE FROM creditCard WHERE number = oldCardNumber;
END IF;

END //

DELIMITER ;

DELIMITER //

-- Procedure to delete a user's credit card from their account
CREATE PROCEDURE deleteCreditcard ( IN userEmail varchar(100))
BEGIN
    -- Declare variable to hold the old card number
    DECLARE oldCardNumber BIGINT;

    -- Check if the user exists
    IF NOT EXISTS (SELECT * FROM commuter WHERE user = userEmail) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User does not exist';
END IF;

    -- Retrieve the current credit card number of the user
SELECT creditCard FROM commuter WHERE user = userEmail INTO oldCardNumber;
-- Update the user's credit card information to NULL
UPDATE commuter SET creditCard = NULL WHERE user = userEmail;

-- Check if the old credit card is not associated with any user
IF NOT EXISTS (SELECT * FROM commuter WHERE creditCard = oldCardNumber) THEN
DELETE FROM creditCard WHERE number = oldCardNumber;
END IF;

END //

DELIMITER ;

-- ########## 4th migration ##########

DROP FUNCTION IF EXISTS BuyAccess;
DROP PROCEDURE IF EXISTS DeleteAccess;
DROP FUNCTION IF EXISTS GetAccessBought;
DROP FUNCTION IF EXISTS GetCreditCard;


DELIMITER //
-- Function to buy access
CREATE FUNCTION BuyAccess(
    quantity INT,
    p_email VARCHAR(100),
    p_access_id VARCHAR(100)
)
    RETURNS TEXT DETERMINISTIC
BEGIN
    -- Declare variable to hold access details
    DECLARE access_bought_info TEXT;

    -- Declare variables for access details
    DECLARE access_name VARCHAR(100);
    DECLARE access_price FLOAT;
    DECLARE access_type ENUM('ticket', 'subscription');
    DECLARE access_company VARCHAR(100);
    DECLARE access_number VARCHAR(36);
    DECLARE access_expire_date DATE;
    DECLARE access_duration INT;
    DECLARE json_access_bought_info TEXT;
    DECLARE transaction_number BIGINT;
    DECLARE number_of_passage INT;

    -- Declare variables for credit card details
    DECLARE credit_card_number BIGINT;

    -- Check if access is not suspended
    IF ( SELECT suspended FROM access WHERE id = p_access_id AND suspended = TRUE) THEN
        SIGNAL SQLSTATE '45000'
         SET MESSAGE_TEXT = 'Access is suspended';
END IF;

    SET transaction_number = UUID_SHORT();
    SET access_bought_info = '';
    SET json_access_bought_info = '';

    WHILE quantity > 0 DO
            -- Retrieve access details
SELECT A.name, A.price, A.type, A.duration, A.company
FROM access A
WHERE A.id = p_access_id AND suspended = FALSE
    INTO access_name, access_price, access_type, access_duration, access_company;

-- generate access number
SET access_number = REPLACE(SUBSTRING(UUID() FROM 1 FOR 13), '-', '');

            -- check if user has a credit card
SELECT creditCard FROM commuter WHERE user = p_email INTO credit_card_number;
IF credit_card_number IS NULL THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'User does not have a credit card';
END IF;

            -- Calculate expiration date
            IF access_type = 'ticket' THEN
SELECT passes FROM ticket WHERE access = p_access_id INTO number_of_passage;
END IF;

            -- Calculate expiration date
            SET access_expire_date = DATE_ADD(CURDATE(), INTERVAL access_duration DAY);

INSERT INTO transaction (accessNumber, transactionNumber, creditCard, user, accessId, transactionDate, expirationDate)
VALUES (access_number, transaction_number, credit_card_number, p_email, p_access_id, CURDATE(), access_expire_date);

-- Concatenate access details to the access_bought as a JSON object
SET access_bought_info = CONCAT(
                    '{"name": "', access_name, '", "price": "', access_price,
                    '", "accessType": "', access_type, '", "company": "', access_company,
                    '", "outOfSale": ',
                      EXISTS(SELECT 1 FROM suspendedAccess sus WHERE sus.access = p_access_id),
                    ', "accessNumber": "', access_number, '", "transactionDate": "', CURDATE(),
                    IF(access_type = 'ticket', CONCAT('", "numberOfPassage": "', number_of_passage), ''),
                    '", "expirationDate": "', access_expire_date, '", "transactionNumber": "', transaction_number,'"}');

            -- Append the current JSON string to the accumulated JSON strings
            SET json_access_bought_info = CONCAT(json_access_bought_info, ',', access_bought_info);

            SET quantity = quantity - 1;
END WHILE;

    -- Remove the leading comma and add square brackets to make it a valid JSON array
    SET json_access_bought_info = CONCAT('[', SUBSTRING(json_access_bought_info FROM 2), ']');

RETURN json_access_bought_info;
END //
DELIMITER ;

DELIMITER //
-- Function to get access bought by a user
CREATE FUNCTION GetAccessBought(p_email VARCHAR(100))
    RETURNS TEXT DETERMINISTIC
BEGIN
    DECLARE access_bought_info TEXT;

    -- Set group_concat_max_len to accommodate larger strings
SET SESSION group_concat_max_len = 1000000;

-- Retrieve access information for the user
SELECT CONCAT(
               '[',
               GROUP_CONCAT(
                       JSON_OBJECT(
                               'accessNumber', t.accessNumber,
                               'price', a.price,
                               'name', a.name,
                               'accessType', a.type,
                               'transactionDate', t.transactionDate,
                               'expirationDate', t.expirationDate,
                               'outOfSale', a.suspended,
                               'deletionDate', IF(a.suspended, sa.deletionDate, '0'),
                               'numberOfPassage', IF(a.type = 'ticket', tk.passes, '0'),
                               'transactionNumber', t.transactionNumber,
                               'company', a.company
                       )
                           SEPARATOR ','
               ),
               ']'
       ) INTO access_bought_info
FROM transaction t
         JOIN access a ON t.accessId = a.id      -- join to get access details
         LEFT JOIN ticket tk ON a.id = tk.access -- join left to handle tickets since tickets have additional information
         LEFT JOIN suspendedAccess sa ON a.id = sa.access
WHERE t.user = p_email;

-- Reset group_concat_max_len to default value
SET SESSION group_concat_max_len = 1024;

RETURN access_bought_info;
END //
DELIMITER ;


DELIMITER //
-- Procedure to delete access
CREATE PROCEDURE DeleteAccess(IN p_access_id varchar(100))
BEGIN
    -- Declare variables
    DECLARE accessDuration INT;
    DECLARE deleteDate DATE;

    -- Check if access exists
    IF NOT EXISTS (SELECT * FROM access WHERE id = p_access_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Access does not exist';
END IF;

    -- Retrieve access duration
SELECT duration FROM access WHERE id = p_access_id INTO accessDuration;

-- Calculate deletion date
SET deleteDate = DATE_ADD(CURDATE(), INTERVAL accessDuration DAY);

    -- Insert into suspendedaccess table
INSERT INTO suspendedAccess(access,deletionDate) VALUES (p_access_id, deleteDate);

-- Update access status to suspended
UPDATE access SET suspended = TRUE WHERE id = p_access_id;

END //
DELIMITER ;

DELIMITER //
-- Function to return credit card information
CREATE FUNCTION GetCreditCard(p_email VARCHAR(100))
    RETURNS VARCHAR(10000) DETERMINISTIC
BEGIN
    -- Declare variables
    DECLARE credit_card_number BIGINT;
    DECLARE credit_card_holder VARCHAR(100);
    DECLARE credit_card_expiration VARCHAR(5);
    DECLARE credit_card_info VARCHAR(10000);

    -- Retrieve credit card information
SELECT creditCard, holderName, expirationDate
FROM commuter JOIN creditCard ON commuter.creditCard = creditCard.number
WHERE user = p_email
    INTO credit_card_number, credit_card_holder, credit_card_expiration;

-- Construct JSON object for credit card information
SET credit_card_info = CONCAT('{"cardNumber": "', credit_card_number, '", "holder": "', credit_card_holder,
        '", "expirationDate": "', credit_card_expiration, '"}');

RETURN credit_card_info;
END //

DELIMITER ;

INSERT INTO company (name) VALUES('RTC'),('STLevis'),('STM'),('RTL');

