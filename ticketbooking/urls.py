# a=[1,2,3,4]
# b=a[::-1]
# print(b)
# l1=[1,2,3,4]
# l2=[5,6,7]
# l1.extend(l2)
# print(l1)
# l1.append(l2)
# print(l1)
# def show(**kwargs):
#     print(kwargs['a'])
# show(a=1,b=2)
# a={"a":1,"b":2}
# a.pop("a")
# print(a)



# import hashlib

# def hash_password(password):
#     # Hashing using SHA256 (you can use other algorithms too like SHA1, SHA512, etc.)
#     hashed_password = hashlib.sha256(password.encode()).hexdigest()
#     return hashed_password

# # Example
# password = "my_secure_password123"
# hashed = hash_password(password)
# print(f"Hashed Password: {hashed}")





# using decorator in our api  



































# import bcrypt
# import getpass

# class User:
#     def _init_(self, username, password, age):
#         self.username = username
#         self.hashed_password = self.hash_password(password)
#         self.age = age

#     def hash_password(self, password):
#         return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     def check_eligibility(self):
#         return self.age >= 18


# class UserAuth:
#     def _init_(self):
#         self.users = {}

#     def register_user(self):
#         username = input("Enter username: ")
#         if username in self.users:
#             print("Username already exists.")
#             return False
#         password = getpass.getpass("Enter password: ")
#         age = int(input("Enter age: "))
#         user = User(username, password, age)
#         self.users[username] = user
#         print(f"User '{username}' registered successfully.")
#         return True

#     def authenticate_user(self):
#         username = input("Enter username: ")
#         password = getpass.getpass("Enter password: ")
#         user = self.users.get(username)
#         if not user:
#             print("User not found.")
#             return False
#         if bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
#             print("Authentication successful.")
#             return True
#         else:
#             print("Authentication failed.")
#             return False

#     def check_user_eligibility(self):
#         username = input("Enter username to check eligibility: ")
#         user = self.users.get(username)
#         if not user:
#             print("User not found.")
#             return False
#         if user.check_eligibility():
#             print(f"User '{username}' is eligible (age: {user.age}).")
#         else:
#             print(f"User '{username}' is NOT eligible (age: {user.age}).")


# auth = UserAuth()

# while True:
#     print("\n1. Register\n2. Login\n3. Check Eligibility\n4. Exit")
#     choice = input("Choose an option: ")

#     if choice == '1':
#         auth.register_user()
#     elif choice == '2':
#         auth.authenticate_user()
#     elif choice == '3':
#         auth.check_user_eligibility()
#     elif choice == '4':
#         print("Exiting...")
#         break
#     else:
#         print("Invalid choice.Tryagain.")


















































# import bcrypt

# def hash_password(password):
#     # Generate salt and hash the password
#     salt = bcrypt.gensalt()  # Generate salt
#     hashed_password = bcrypt.hashpw(password.encode(), salt)  # Hash the password with salt
#     return hashed_password

# # Step 3: Taking input from user
# password_input = input("Enter your password: ")  # Taking user input

# # Hash the password
# hashed_password = hash_password(password_input)

# # Display the hashed password
# print(f"Hashed Password: {hashed_password}")

# # Step 4: Verifying the password (for example checking if entered password is correct)
# if bcrypt.checkpw(password_input.encode(), hashed_password):
#     print("Password matches!")
# else:
#     print("Password does not match!")
