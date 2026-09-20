from database import conn


class Customer:
    

    @staticmethod
    def create_table():
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                contact VARCHAR(100) NOT NULL
                
            )
        """)

        conn.commit()
        cur.close()

    @staticmethod
    def insert_customer(name, contact):
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO customers (name, contact)
            VALUES (%s, %s)
        """, (name, contact))

        conn.commit()
        cur.close()

    @staticmethod
    def update_customer(customer_id, name=None, contact=None):
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM customers WHERE id = %s",
            (customer_id,)
        )

        customer = cur.fetchone()

        if not customer:
            print("Customer not found")
            cur.close()
            return

        update_fields = []
        values = []

        if name:
            update_fields.append("name = %s")
            values.append(name)

        if contact:
            update_fields.append("contact = %s")
            values.append(contact)

        if not update_fields:
            print("Nothing to update")
            cur.close()
            return

        values.append(customer_id)

        update_query = f"""
            UPDATE customers
            SET {', '.join(update_fields)}
            WHERE id = %s
        """

        cur.execute(update_query, tuple(values))

        conn.commit()
        cur.close()

    @staticmethod
    def delete_customer(customer_id):
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM customers WHERE id = %s",
            (customer_id,)
        )

        conn.commit()
        cur.close()

    @staticmethod
    def get_all_customers():
        cur = conn.cursor()

        cur.execute("SELECT * FROM customers")

        customers = cur.fetchall()

        cur.close()

        return customers

    @staticmethod
    def customer_menu():

        while True:
            print("1. Create Table")
            print("2. Insert Customer")
            print("3. Update Customer")
            print("4. Delete Customer")
            print("5. View Customers")
            print("0. Exit")

            choice = input("Enter choice: ")

            if choice == '1':
                Customer.create_table()
                print("Table created")

            elif choice == '2':
                name = input("Enter customer name: ")
                contact = input("Enter customer contact: ")

                Customer.insert_customer(name, contact)
                print("Customer inserted")

            elif choice == '3':
                customer_id = int(input("Enter customer id: "))
                name = input("Enter customer name: ")
                contact = input("Enter customer contact: ")

                Customer.update_customer(
                    customer_id,
                    name,
                    contact
                )

                print("Customer updated")

            elif choice == '4':
                customer_id = int(input("Enter customer id: "))

                Customer.delete_customer(customer_id)
                print("Customer deleted")

            elif choice == '5':
                customers = Customer.get_all_customers()

                for customer in customers:
                    print(customer)

            elif choice == '0':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


#Customer.customer_menu()