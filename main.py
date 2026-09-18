import database
from customers import Customer
from products import Product
from sales import sale as Sale

def main_menu():
    while True:
        print("1. Customer Management")
        print("2. Product Management")
        print("3. Sales Management")
        print("4. Exit Application")
        
        choice = input("Select an option: ")
        
        if choice == "1":
            Customer.customer_menu()
        elif choice == "2":
            Product.product_menu()
        elif choice == "3":
            Sale.sale_menu()
        elif choice == "4":
            print("Exiting App...")
            break  
        else:
            print("Invalid option")
main_menu()