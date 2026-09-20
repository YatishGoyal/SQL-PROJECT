from database import conn
 

class sale: 
 
    @staticmethod 
    def create_table(): 
        cur = conn.cursor() 
 
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS sales ( 
                id SERIAL PRIMARY KEY, 
                customer_id INTEGER NOT NULL, 
                date DATE NOT NULL, 
                total_amount DECIMAL(10,2) NOT NULL,
                CONSTRAINT fk_sales_customer
    FOREIGN KEY (customer_id)
    REFERENCES customers(id)
    ON DELETE CASCADE

            ) 
        """) 
 
        conn.commit() 
        cur.close() 
 
    @staticmethod 
    def insert_sale(customer_id,date,total_amount): 
        cur = conn.cursor() 
 
        cur.execute(""" 
            INSERT INTO sales (customer_id,date,total_amount) 
            VALUES (%s, %s,%s) 
        """, (customer_id,date,total_amount)) 
 
        conn.commit() 
        cur.close() 
 
    @staticmethod 
    def update_sale(sale_id,customer_id = None,date = None,total_amount = None): 
        cur = conn.cursor() 
 
        cur.execute( 
            "SELECT * FROM sales WHERE id = %s", 
            (sale_id,) 
        ) 
 
        sale = cur.fetchone() 
 
        if not sale: 
            print("sale not found") 
            cur.close() 
            return 
 
        update_fields = [] 
        values = [] 
 
        if customer_id: 
            update_fields.append("customer = %s") 
            values.append(customer_id) 
 
        if date: 
            update_fields.append("date = %s") 
            values.append(date) 

        if total_amount: 
            update_fields.append("total_amount = %s") 
            values.append(total_amount) 
 
        if not update_fields: 
            print("Nothing to update") 
            cur.close() 
            return 
 
        values.append(sale_id) 
 
        update_query = f""" 
            UPDATE sales 
            SET {', '.join(update_fields)} 
            WHERE id = %s 
        """ 
 
        cur.execute(update_query, tuple(values)) 
 
        conn.commit() 
        cur.close() 
 
    @staticmethod 
    def delete_sale(sale_id): 
        cur = conn.cursor() 
 
        cur.execute( 
            "DELETE FROM sales WHERE id = %s", 
            (sale_id,) 
        ) 
 
        conn.commit() 
        cur.close() 

    @staticmethod
    def view_sales():
        cur = conn.cursor()

        cur.execute("SELECT * FROM sales")

        sales = cur.fetchall()

        cur.close()

        return sales

    @staticmethod
    def view_sales_by_id(sale_id):
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM sales WHERE id = %s",
            (sale_id,)
        )

        sales = cur.fetchone()

        cur.close()

        return sales
    @staticmethod
    def view_sales_by_customers(customer_id):
            cur = conn.cursor()
    
            cur.execute(
                "SELECT * FROM sales WHERE id = %s",
                (customer_id,)
            )
    
            sales = cur.fetchone()
    
            cur.close()
    
            return sales
     
 
    @staticmethod 
    def generate_bill(sale_id): 
        cur = conn.cursor() 
     
        cur.execute(
            "SELECT * FROM sales WHERE id = %s",
            (sale_id,)
        ) 
     
        sales_items = cur.fetchall() 
        total_amount = 0 

        for item in sales_items: 
            total_amount += item[4] * item[3] 
     
        cur.close() 
     
        return total_amount 
    @staticmethod
    def total_sales_by_date(start_date,end_date):
        cur = conn.cursor()

        cur.execute("SELECT * FROM sales where date BETWEEN %s AND %s",(start_date,end_date))

        total_sales = cur.fetchone()

        cur.close()

        return total_sales
    @staticmethod
    def get_top_selling_products(start_date,end_date):
            cur = conn.cursor()
    
            cur.execute("SELECT * FROM sales where date BETWEEN %s AND %s",(start_date,end_date))
    
            total_sales = cur.fetchone()
    
            cur.close()
    
            return total_sales
    @staticmethod
    def sale_menu():
        while True:
                    print("\n========== SALES MENU ==========")
                    print("1. Create Table")
                    print("2. Insert Sale")
                    print("3. Update Sale")
                    print("4. Delete Sale")
                    print("5. View Sales")
                    print("6. View Sale by ID")
                    print("7. View Sales by Customer")
                    print("8. Generate Bill")
                    print("9. Total Sales by Date")
                    print("10. Get Top Selling Products")
                    print("0. Exit")
                    print("================================")
            
                    choice = input("Enter choice: ")
            
                    if choice == '1':
                        sale.create_table()
                        print("Table created")
            
                    elif choice == '2':
                        customer_id = int(input("Enter customer id: "))
                        date = input("Enter sale date: ")
                        total_amount = input("Enter sale total_amount: ")
            
                        sale.insert_sale(
                            customer_id,
                            date,
                            total_amount
                        )
            
                        print("Sale inserted")
            
                    elif choice == '3':
                        sale_id = int(input("Enter sale id: "))
                        customer_id = int(input("Enter customer id: "))
                        date = input("Enter sale date: ")
                        total_amount = input("Enter sale total_amount: ")
            
                        sale.update_sale(
                            sale_id,
                            customer_id,
                            date,
                            total_amount
                        )
            
                        print("Sale updated")
            
                    elif choice == '4':
                        sale_id = int(input("Enter sale id: "))
            
                        sale.delete_sale(sale_id)
            
                        print("Sale deleted")
            
                    elif choice == '5':
                        sales = sale.view_sales()
            
                        for sale_data in sales:
                            print(sale_data)
            
                    elif choice == '6':
                        sale_id = int(input("Enter sale id: "))
            
                        sales = sale.view_sales_by_id(sale_id)
            
                        print(sales)
            
                    elif choice == '7':
                        customer_id = int(input("Enter customer id: "))
            
                        sales = sale.view_sales_by_customers(customer_id)
            
                        print(sales)
            
                    elif choice == '8':
                        sale_id = int(input("Enter sale id: "))
            
                        total = sale.generate_bill(sale_id)
            
                        print("Total Bill:", total)
            
                    elif choice == '9':
                        start_date = input("Enter start date: ")
                        end_date = input("Enter end date: ")
            
                        total_sales = sale.total_sales_by_date(
                            start_date,
                            end_date
                        )
            
                        print("Total Sales:", total_sales)
            
                    elif choice == '10':
                        start_date = input("Enter start date: ")
                        end_date = input("Enter end date: ")
            
                        top_products = sale.get_top_selling_products(
                            start_date,
                            end_date
                        )
            
                        print("Top Selling Products:", top_products)
            
                    elif choice == '0':
                        print("Exiting...")
                        break
            
                    else:
                        print("Invalid choice. Please try again.")
             
        

 
 
#sale.sale_menu()