import random
import string
from faker import Faker

def generate_unique_user_data(fake):
    email_length = random.randint(7, 15)
    email_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits + '.', k=email_length))
    email = f"{email_prefix}@mail.ru"

    password_length = random.randint(6, 8)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=password_length))

    name_length = random.randint(6, 10)
    name = ''.join(random.choices(string.ascii_letters, k=name_length))

    user_data = {"email": email, "password": password, "name": name}
    return user_data