import random
import sys
from datetime import datetime, timedelta

from app.repository.database import Database
from app.service.dtos.admin_dtos import AdminFullInfo, Access
from app.service.dtos.commuter_dtos import CommuterFullInfo, CreditCard
from app.service.exceptions import RequestError

'''----------------------------START OF USER GENERATION----------------------------'''

first_names = [
    "Ethan", "Ava", "Liam", "Olivia", "Noah", "Emma", "Mason", "Sophia",
    "Benjamin", "Isabella", "Alexander", "Mia", "William", "Charlotte",
    "James", "Amelia", "Samuel", "Evelyn", "Lucas", "Harper",
    "Henry", "Abigail", "Daniel", "Emily", "Matthew", "Elizabeth",
    "Michael", "Avery", "Elijah", "Sofia", "David", "Ella"
]

# List of last names
last_names = [
    "Anderson", "Martinez", "Hughes", "Peterson", "Bailey",
    "Flores", "Richardson", "Patel", "Nguyen", "Stewart",
    "Mitchell", "Sanchez", "Morris", "Rogers", "Reed",
    "Cook", "Morgan", "Bell", "Murphy", "Bailey",
    "Rivera", "Cooper", "Cox", "Howard", "Ward",
    "Torres", "Peterson", "Gray", "Ramirez", "James",
    "Watson", "Brooks", "Bennett", "Gray", "James", "Jason"
]

companies = ["RTC", "STLevis", "STM", "RTL"]

# List of street names that can be combined with a random number to create a fake address
street_names = [
    "Rue de la Montagne", "Rue de la Commune", "Rue Sainte-Catherine",
    "Boulevard René-Lévesque", "Avenue McGill College", "Rue Sherbrooke",
    "Rue Peel", "Rue Notre-Dame", "Rue Crescent", "Rue Saint-Laurent",
    "Rue Saint-Denis", "Rue Saint-Hubert", "Rue Saint-Jacques",
    "Rue Saint-Paul", "Rue Saint-Antoine", "Rue Saint-Jacques"
]

# List of cities
cities = [
    "Montreal", "Laval", "Longueuil", "Brossard", "Boucherville", "Saint-Bruno",
    "Saint-Lambert", "Saint-Hubert", "Sainte-Julie", "Varennes", "Levis", "Quebec"
]

province = "QC"

# random List of postal codes that are all entirely different
postal_codes = [
    "A0A 1A1", "A2B 3C4",
    "C0A 1A1", "C1B 2C3",
    "B0H 1A1", "B2G 3H4",
    "E1A 1A1", "E2B 2C3",
    "G1A 1A1", "G2B 2C3",
    "K1A 0B1", "L1B 2C3",
    "R0A 0A1", "R1B 1C2",
    "S0A 0A1", "S4A 1B2",
    "T0A 0A1", "T2B 2C3",
    "V0A 0A1", "V1B 1C2",
    "Y0A 1A1",
    "X0A 0A0",
    "X0B 0C0"
]

# List of emails
emails = ["@gmail.com", "@hotmail.com", "@yahoo.com", "@outlook.com", "@icloud.com"]

# List of passwords
passwords = ["password", "123456", "password123", "12345678", "123456789", "qwerty", "abc123"]


# generate a random name
def generate_name():
    return random.choice(first_names) + " " + random.choice(last_names)


def generate_email(full_name):
    return full_name.replace(" ", ".").lower() + random.choice(emails)


# method to generate a random address
def generate_address():
    # Generate a random street number
    street_number = random.randint(1, 9999)

    # Generate a random street name
    street_name = random.choice(street_names)

    # Generate a random city
    city = random.choice(cities)

    # Generate a random postal code
    postal_code = random.choice(postal_codes)

    # Return the address in the format "street_number street_name, city, province, postal_code"
    return f"{street_number} {street_name}, {city}, {province}, {postal_code}"


def generate_admin_code():
    """generate a random code for admin registration, with a checksum at the end.
    this way the only to create an admin is to have the correct code provided by the issuer (NYSS developers)."""

    # Generate a random 5-character alphanumeric string
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

    # Calculate checksum
    checksum = sum(ord(char) for char in random_string) % 10

    # Append checksum to the string
    code = random_string + str(checksum)

    return code


# method to generate a random phone number of 10 digits
def generate_phone_number():
    return ''.join(random.choices('0123456789', k=10))


# method to generate a random date of birth between 1985 and 2005
def random_date_of_birth(start_year, end_year):
    # Define start and end dates
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)

    # Calculate the range of days between start and end dates
    delta = end_date - start_date

    # Generate a random number of days within the range
    random_days = random.randint(0, delta.days)

    # Add the random number of days to the start date
    random_date = start_date + timedelta(days=random_days)

    return random_date.strftime("%Y-%m-%d")


# method to generate a random credit card number of 16 digits
def generate_credit_card_number():
    return ''.join(random.choices('0123456789', k=16))


# method to generate a random credit card expiration date of 3 years from now
def generate_credit_card_expiration_date():
    # Get the current year
    current_year = datetime.now().year

    # Generate a random year between the current year and 3 years from now
    expiration_year = random.randint(current_year, current_year + 3)

    # Generate a random month between 1 and 12
    expiration_month = random.randint(1, 12)

    # Return the expiration date in the format "MM/YY"
    return f"{expiration_month:02}/{expiration_year % 100:02}"


def generate_commuter_data():
    name = generate_name()
    email = generate_email(name)
    address = generate_address()
    tel = generate_phone_number()
    password = random.choice(passwords)
    date_of_birth = random_date_of_birth(1985, 2005)

    commuter_data = {
        "name": name,
        "email": email,
        "address": address,
        "tel": tel,
        "password": password,
        "dateOfBirth": date_of_birth
    }
    return commuter_data


# generate random admin
def generate_admin_data():
    name = generate_name()
    email = generate_email(name)
    address = generate_address()
    tel = generate_phone_number()
    password = random.choice(passwords)
    date_of_birth = random_date_of_birth(1985, 2005)
    admin_code = generate_admin_code()
    company = random.choice(companies)

    admin_data = {
        "name": name,
        "email": email,
        "address": address,
        "tel": tel,
        "password": password,
        "dateOfBirth": date_of_birth,
        "company": company,
        "adminCode": admin_code
    }
    return admin_data


def generate_credit_card_data():
    holder = generate_name()
    card_number = generate_credit_card_number()
    expiration_date = generate_credit_card_expiration_date()

    credit_card_data = {
        "holder": holder,
        "cardNumber": card_number,
        "expirationDate": expiration_date
    }
    return credit_card_data


database: Database = Database()


def add_random_commuters_in_database(number_of_commuters):
    list_of_commuters = []
    for i in range(number_of_commuters):
        try:
            commuter_info = generate_commuter_data()
            list_of_commuters.append(commuter_info)
            credit_card_info = generate_credit_card_data()

            commuter = CommuterFullInfo(**commuter_info)
            commuter.secure_password()
            credit_card = CreditCard(**credit_card_info)

            database.register_commuter(commuter)
            database.add_payment_method(commuter.email, credit_card)
            print(f"Created commuter {i + 1} out of {number_of_commuters}")
        except Exception:
            print(f"Failed to fully create commuter or credit card {i + 1}")

    # we save the list of commuter in a json file, so we can log in with them later
    with open("commuters.json", "w") as file:
        file.write(str(list_of_commuters))
        file.write("\n")


def add_random_admin_in_database(number_of_admins):
    list_of_admins = []
    for i in range(number_of_admins):
        try:
            admin_info = generate_admin_data()
            list_of_admins.append(admin_info)

            admin = AdminFullInfo(**admin_info)
            admin.secure_admin_code()
            admin.secure_password()
            database.register_admin(admin)
            print(f"Created admin {i + 1} out of {number_of_admins}")
        except Exception:
            print(f"Failed to fully create admin {i + 1}")

    # we save the list of admins in a json file, so we can log in with them later
    with open("admins.json", "w") as file:
        file.write(str(list_of_admins))
        file.write("\n")


'''----------------------------END OF USER GENERATION----------------------------'''

'''----------------------------START OF ACCESS GENERATION----------------------------'''
companies = ["RTC", "STLevis", "STM", "RTL"]

# tuples of (name, number of passage, price, duration, company)
ticket_names = [
    ("Bundle of 20 reduced-rate tickets", 20, 61.00, 365, "RTC"),
    ("Bundle of 20 Metropolitan tickets", 20, 70.00, 365, "RTC"),
    ("1 fare", 1, 3.75, 365, "RTC"),
    ("1 passage, Tous modes A2", 1, 3.75, 365, "STM"),
    ("1 passage, Tous modes AB3", 1, 4.50, 365, "STM"),
    ("Passage simple semaine", 1, 3.75, 365, "STLevis"),
    ("Carte de 4 passages", 4, 13.00, 365, "STLevis"),
    ("Carte de 8 passages", 8, 26.00, 365, "STLevis"),
    ("Carte de 12 passages", 12, 38.00, 365, "STLevis"),
    ("1 passage, Tous modes AB", 1, 4.50, 365, "RTL"),
    ("2 passages, Tous modes AB", 2, 9.00, 365, "RTL"),
    ("24 h, Tous modes AB¹", 1, 12.75, 1, "RTL"),
    ("10 passages, Tous modes ABCD", 10, 79.00, 365, "RTL")

]

# tuples of (name, duration, price, company)
subscription_names = [
    ("Monthly pass", 30, 94.50, "RTC"),
    ("Metropolitain", 30, 105.00, "RTC"),
    ("Monthly Bus pass + FLEXauto", 12, 99.00, "RTC"),
    ("5 consecutive days", 5, 85, "RTC"),
    ("1 day-pass", 1, 85, "RTC"),
    ("Hebdo, Tous modes A", 7, 30.00, "STM"),
    ("Mensuel, Tous modes A", 30, 97.00, "STM"),
    ("4 mois, Tous modes A", 120, 226.00, "STM"),
    ("Mensuel, Tous modes ABC", 30, 190.00, "STM"),
    ("Mensuel, Tous modes AB", 30, 155.00, "STM"),
    ("Mensuel STLevis Laisser-passer Mensuel", 30, 96.40, "STLevis"),
    ("Metropolitain", 30, 105.00, "STLevis"),
    ("Mensuel, Tous modes ABCD¹·²", 30, 263.00, "RTL"),
    ("Mensuel, Tous modes ABC¹·²", 30, 190.00, "RTL"),
    ("3 jours, Tous modes ABC¹", 3, 39.00, "RTL"),
    ("3 jours, Tous modes AB¹", 3, 27.00, "RTL"),
]


# generate a json of all the tickets
def generate_tickets():
    tickets = []
    for ticket in ticket_names:
        ticket_data = {
            "accessName": ticket[0],
            "numberOfPassage": ticket[1],
            "price": ticket[2],
            "duration": ticket[3],
            "accessType": "ticket",
            "company": ticket[4]
        }
        tickets.append(ticket_data)
    return tickets


def add_tickets_in_database():
    index = 0
    ticket_list = generate_tickets()
    for ticket in ticket_list:
        access = Access(**ticket)
        database.admin_create_access(access)
        index += 1
        print(f"Created ticket {index}")


def generate_subscriptions():
    subscriptions = []
    for subscription in subscription_names:
        subscription_data = {
            "accessName": subscription[0],
            "price": subscription[2],
            "duration": subscription[1],
            "accessType": "subscription",
            "company": subscription[3]
        }
        subscriptions.append(subscription_data)
    return subscriptions


def add_subscriptions_in_database():
    index = 0
    subscription_list = generate_subscriptions()
    for subscription in subscription_list:
        access = Access(**subscription)
        database.admin_create_access(access)
        index += 1
        print(f"Created subscription {index}")


"""----------------------------END OF ACCESS GENERATION----------------------------"""

if __name__ == "__main__":
    add_tickets_in_database()
    add_subscriptions_in_database()
    add_random_admin_in_database(20)
    add_random_commuters_in_database(100)
