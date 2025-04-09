from faker import Faker



def generate_unique_user_data(fake):

    email = fake.email()
    password = fake.password()
    name = fake.name()
    user_data = {"email": email, "password": password, "name": name}
    return user_data