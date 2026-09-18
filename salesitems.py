from database import conn

class SaleItems:

    @staticmethod
    def create_table():
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id SERIAL PRIMARY KEY,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                CONSTRAINT fk_sale_items_sales
                    FOREIGN KEY (sale_id)
                    REFERENCES sales(id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_sale_items_products
                    FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
        cur.close()

SaleItems().create_table()