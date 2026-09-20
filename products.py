from database import connection

conn = connection()
class Product:

    @staticmethod
    def create_table():
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name varchar(50),
                description TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)

        conn.commit()
        cur.close()

    @staticmethod
    def insert_product(name, description, price, quantity):
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO products (name, description, price, quantity)
            VALUES (%s, %s, %s, %s)
        """, (name, description, price, quantity))

        conn.commit()
        cur.close()

    @staticmethod
    def update_product(product_id, name=None, description=None, price=None, quantity=None):
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM products WHERE id = %s",
            (product_id,)
        )

        product = cur.fetchone()

        if not product:
            print("product not found")
            cur.close()
            return

        update_fields = []
        values = []

        if name:
            update_fields.append("name = %s")
            values.append(name)

        if description:
            update_fields.append("description = %s")
            values.append(description)

        if price:
            update_fields.append("price = %s")
            values.append(price)

        if quantity:
            update_fields.append("quantity = %s")
            values.append(quantity)

        if not update_fields:
            print("Nothing to update")
            cur.close()
            return

        values.append(product_id)

        update_query = f"""
            UPDATE products
            SET {', '.join(update_fields)}
            WHERE id = %s
        """

        cur.execute(update_query, tuple(values))

        conn.commit()
        cur.close()

    @staticmethod
    def delete_product(product_id):
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM products WHERE id = %s",
            (product_id,)
        )

        conn.commit()
        cur.close()

    @staticmethod
    def view_products():
        cur = conn.cursor()

        cur.execute("SELECT * FROM products")

        products = cur.fetchall()

        cur.close()

        return products

    @staticmethod
    def view_products_by_id(product_id):
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM products WHERE id = %s",
            (product_id,)
        )

        products = cur.fetchall()

        cur.close()

        return products

    @staticmethod
    def product_menu():

        while True:
            print("1. Create Table")
            print("2. Insert product")
            print("3. Update product")
            print("4. Delete product")
            print("5. View products")
            print("6. View products by id")
            print("0. Exit")

            choice = input("Enter choice: ")

            if choice == '1':
                Product.create_table()
                print("Table created")

            elif choice == '2':
                name = input("Enter product name: ")
                description = input("Enter product description: ")
                price = input("Enter product price: ")
                quantity = input("Enter product quantity: ")

                Product.insert_product(
                    name,
                    description,
                    price,
                    quantity
                )

                print("product inserted")

            elif choice == '3':
                product_id = input("Enter product id: ")
                name = input("Enter product name: ")
                description = input("Enter product description: ")
                price = input("Enter product price: ")
                quantity = input("Enter product quantity: ")

                Product.update_product(
                    product_id,
                    name,
                    description,
                    price,
                    quantity
                )

                print("product updated")

            elif choice == '4':
                product_id = int(input("Enter product id: "))

                Product.delete_product(product_id)
                print("product deleted")

            elif choice == '5':
                products = Product.view_products()

                for product in products:
                    print(product)

            elif choice == '6':
                product_id = int(input("Enter product id: "))

                products = Product.view_products_by_id(product_id)

                for product in products:
                    print(product)

            elif choice == '0':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


#Product.product_menu()