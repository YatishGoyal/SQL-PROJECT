import streamlit as st
import pandas as pd
from datetime import date

from database import connection
from customers import Customer
from products import Product
from sales import sale as Sale
from salesitems import SaleItems


st.set_page_config(
    page_title="Smart Billing",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #292929;
}

[data-testid="stMetric"] {
    background-color: #151515;
    border: 1px solid #292929;
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    border-radius: 8px;
}

.app-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 3px;
}

.app-subtitle {
    color: #8b8b8b;
    margin-bottom: 28px;
}

.page-title {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 4px;
}

.page-subtitle {
    color: #8b8b8b;
    margin-bottom: 25px;
}

.card {
    background-color: #151515;
    border: 1px solid #292929;
    border-radius: 14px;
    padding: 20px;
}

.small-text {
    color: #888;
    font-size: 13px;
}

.total-box {
    background-color: #151515;
    border: 1px solid #292929;
    border-radius: 14px;
    padding: 20px;
    text-align: right;
}

.total-label {
    color: #888;
    font-size: 14px;
}

.total-value {
    font-size: 30px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


conn = connection()


def execute_query(query, params=(), fetch=True):

    cur = conn.cursor()

    try:
        cur.execute(query, params)

        if fetch:
            result = cur.fetchall()
        else:
            result = None

        conn.commit()

        return result

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()


def initialize_tables():

    try:
        Customer.create_table()
        Product.create_table()
        Sale.create_table()
        SaleItems.create_table()

        return True

    except Exception as e:
        st.error(f"Database error: {e}")
        return False


if "initialized" not in st.session_state:

    initialize_tables()

    st.session_state.initialized = True


if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


if "cart" not in st.session_state:
    st.session_state.cart = []


def get_counts():

    customers = execute_query(
        "SELECT COUNT(*) FROM customers"
    )[0][0]

    products = execute_query(
        "SELECT COUNT(*) FROM products"
    )[0][0]

    sales = execute_query(
        "SELECT COUNT(*) FROM sales"
    )[0][0]

    revenue = execute_query(
        """
        SELECT COALESCE(SUM(total_amount), 0)
        FROM sales
        """
    )[0][0]

    low_stock = execute_query(
        """
        SELECT COUNT(*)
        FROM products
        WHERE quantity < 10
        """
    )[0][0]

    return customers, products, sales, revenue, low_stock


def dashboard():

    st.markdown(
        '<div class="app-title">Smart Billing</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-subtitle">Billing, inventory and customer management in one place.</div>',
        unsafe_allow_html=True
    )

    try:

        customer_count, product_count, sales_count, revenue, low_stock = get_counts()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Customers",
            customer_count
        )

        col2.metric(
            "Products",
            product_count
        )

        col3.metric(
            "Sales",
            sales_count
        )

        col4.metric(
            "Revenue",
            f"₹{float(revenue):,.2f}"
        )

        st.write("")

        left, right = st.columns([2, 1])

        with left:

            st.subheader("Revenue Overview")

            sales_data = execute_query("""
                SELECT date, SUM(total_amount)
                FROM sales
                GROUP BY date
                ORDER BY date
            """)

            if sales_data:

                df = pd.DataFrame(
                    sales_data,
                    columns=["Date", "Revenue"]
                )

                df["Date"] = pd.to_datetime(df["Date"])

                st.line_chart(
                    df.set_index("Date")
                )

            else:

                st.info("No sales data available yet.")

        with right:

            st.subheader("Inventory")

            if low_stock > 0:

                st.warning(
                    f"{low_stock} product(s) have low stock."
                )

            else:

                st.success(
                    "All products have healthy stock."
                )

            st.write("")

            st.subheader("Quick Actions")

            if st.button(
                "➕ Add Customer",
                use_container_width=True
            ):
                st.session_state.page = "Customers"
                st.rerun()

            if st.button(
                "📦 Add Product",
                use_container_width=True
            ):
                st.session_state.page = "Products"
                st.rerun()

            if st.button(
                "💰 Create Sale",
                use_container_width=True
            ):
                st.session_state.page = "Sales"
                st.rerun()

        st.write("")

        st.subheader("Recent Sales")

        recent_sales = execute_query("""
            SELECT
                s.id,
                c.name,
                s.date,
                s.total_amount
            FROM sales s
            LEFT JOIN customers c
                ON s.customer_id = c.id
            ORDER BY s.id DESC
            LIMIT 10
        """)

        if recent_sales:

            df = pd.DataFrame(
                recent_sales,
                columns=[
                    "Sale ID",
                    "Customer",
                    "Date",
                    "Amount"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No sales recorded yet.")

    except Exception as e:

        st.error(f"Dashboard error: {e}")


def customers_page():

    st.markdown(
        '<div class="page-title">Customers</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Manage your customer records.</div>',
        unsafe_allow_html=True
    )

    customers = Customer.get_all_customers()

    col1, col2 = st.columns([3, 1])

    with col1:

        search = st.text_input(
            "Search customer",
            placeholder="Search by name..."
        )

    with col2:

        st.write("")

        add_customer = st.button(
            "➕ Add Customer",
            use_container_width=True
        )

    if add_customer:

        st.session_state.add_customer = True

    if st.session_state.get("add_customer", False):

        with st.form("add_customer_form"):

            st.subheader("Add Customer")

            name = st.text_input("Customer Name")
            contact = st.text_input("Contact")

            submitted = st.form_submit_button(
                "Save Customer",
                use_container_width=True
            )

            if submitted:

                if not name or not contact:

                    st.error("Please fill all fields.")

                else:

                    try:

                        Customer.insert_customer(
                            name,
                            contact
                        )

                        st.success("Customer added successfully.")

                        st.session_state.add_customer = False

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

    if search:

        customers = [
            customer
            for customer in customers
            if search.lower() in str(customer[1]).lower()
        ]

    st.write("")

    if customers:

        df = pd.DataFrame(
            customers,
            columns=[
                "ID",
                "Name",
                "Contact"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No customers found.")

    st.divider()

    st.subheader("Customer Actions")

    action = st.selectbox(
        "Choose action",
        [
            "None",
            "Update Customer",
            "Delete Customer"
        ]
    )

    if action == "Update Customer":

        customer_id = st.number_input(
            "Customer ID",
            min_value=1,
            step=1
        )

        name = st.text_input("New Name")
        contact = st.text_input("New Contact")

        if st.button(
            "Update Customer",
            use_container_width=True
        ):

            try:

                Customer.update_customer(
                    int(customer_id),
                    name,
                    contact
                )

                st.success("Customer updated.")

                st.rerun()

            except Exception as e:

                st.error(str(e))

    elif action == "Delete Customer":

        customer_id = st.number_input(
            "Customer ID",
            min_value=1,
            step=1
        )

        st.warning(
            "Deleting a customer may also delete related sales if ON DELETE CASCADE is enabled."
        )

        if st.button(
            "Delete Customer",
            type="primary",
            use_container_width=True
        ):

            try:

                Customer.delete_customer(
                    int(customer_id)
                )

                st.success("Customer deleted.")

                st.rerun()

            except Exception as e:

                st.error(str(e))


def products_page():

    st.markdown(
        '<div class="page-title">Products</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Manage products and inventory.</div>',
        unsafe_allow_html=True
    )

    products = Product.view_products()

    total_products = len(products)

    low_stock = sum(
        1 for product in products
        if int(product[4]) < 10
    )

    inventory_value = sum(
        float(product[3]) * int(product[4])
        for product in products
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Products",
        total_products
    )

    col2.metric(
        "Low Stock",
        low_stock
    )

    col3.metric(
        "Inventory Value",
        f"₹{inventory_value:,.2f}"
    )

    st.write("")

    search = st.text_input(
        "Search product",
        placeholder="Search by product name..."
    )

    if search:

        products = [
            product
            for product in products
            if search.lower() in str(product[1]).lower()
        ]

    if products:

        product_rows = []

        for product in products:

            if int(product[4]) == 0:
                status = "Out of Stock"
            elif int(product[4]) < 10:
                status = "Low Stock"
            else:
                status = "In Stock"

            product_rows.append(
                [
                    product[0],
                    product[1],
                    product[2],
                    float(product[3]),
                    product[4],
                    status
                ]
            )

        df = pd.DataFrame(
            product_rows,
            columns=[
                "ID",
                "Name",
                "Description",
                "Price",
                "Quantity",
                "Status"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No products found.")

    st.divider()

    action = st.selectbox(
        "Product Action",
        [
            "None",
            "Add Product",
            "Update Product",
            "Delete Product"
        ]
    )

    if action == "Add Product":

        with st.form("add_product_form"):

            name = st.text_input("Product Name")
            description = st.text_area("Description")
            price = st.number_input(
                "Price",
                min_value=0.0,
                step=0.01
            )
            quantity = st.number_input(
                "Quantity",
                min_value=0,
                step=1
            )

            submitted = st.form_submit_button(
                "Save Product",
                use_container_width=True
            )

            if submitted:

                try:

                    Product.insert_product(
                        name,
                        description,
                        price,
                        quantity
                    )

                    st.success("Product added.")

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

    elif action == "Update Product":

        product_id = st.number_input(
            "Product ID",
            min_value=1,
            step=1
        )

        name = st.text_input("New Name")
        description = st.text_area("New Description")
        price = st.number_input(
            "New Price",
            min_value=0.0,
            step=0.01
        )
        quantity = st.number_input(
            "New Quantity",
            min_value=0,
            step=1
        )

        if st.button(
            "Update Product",
            use_container_width=True
        ):

            try:

                Product.update_product(
                    int(product_id),
                    name,
                    description,
                    price,
                    quantity
                )

                st.success("Product updated.")

                st.rerun()

            except Exception as e:

                st.error(str(e))

    elif action == "Delete Product":

        product_id = st.number_input(
            "Product ID",
            min_value=1,
            step=1
        )

        if st.button(
            "Delete Product",
            type="primary",
            use_container_width=True
        ):

            try:

                Product.delete_product(
                    int(product_id)
                )

                st.success("Product deleted.")

                st.rerun()

            except Exception as e:

                st.error(str(e))


def sales_page():

    st.markdown(
        '<div class="page-title">Sales</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Create and manage sales.</div>',
        unsafe_allow_html=True
    )

    today = date.today()

    today_sales = execute_query(
        """
        SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
        FROM sales
        WHERE date = %s
        """,
        (today,)
    )[0]

    total_sales = execute_query(
        """
        SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
        FROM sales
        """
    )[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Sales",
        total_sales[0]
    )

    col2.metric(
        "Total Revenue",
        f"₹{float(total_sales[1]):,.2f}"
    )

    col3.metric(
        "Today's Sales",
        today_sales[0]
    )

    col4.metric(
        "Today's Revenue",
        f"₹{float(today_sales[1]):,.2f}"
    )

    st.divider()

    tab1, tab2 = st.tabs(
        [
            "Create Sale",
            "Sales History"
        ]
    )

    with tab1:

        customers = execute_query(
            """
            SELECT id, name
            FROM customers
            ORDER BY name
            """
        )

        products = execute_query(
            """
            SELECT id, name, price, quantity
            FROM products
            ORDER BY name
            """
        )

        if not customers:

            st.warning(
                "Create a customer before creating a sale."
            )

        elif not products:

            st.warning(
                "Create a product before creating a sale."
            )

        else:

            customer_options = {
                f"{customer[0]} - {customer[1]}": customer[0]
                for customer in customers
            }

            selected_customer = st.selectbox(
                "Customer",
                list(customer_options.keys())
            )

            sale_date = st.date_input(
                "Sale Date",
                value=date.today()
            )

            st.subheader("Add Products")

            product_options = {
                f"{product[0]} - {product[1]} | ₹{float(product[2]):.2f}": product
                for product in products
            }

            selected_product_name = st.selectbox(
                "Product",
                list(product_options.keys())
            )

            selected_product = product_options[
                selected_product_name
            ]

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1
            )

            available_quantity = int(selected_product[3])

            st.caption(
                f"Available stock: {available_quantity}"
            )

            if st.button(
                "Add to Cart",
                use_container_width=True
            ):

                if quantity > available_quantity:

                    st.error(
                        "Not enough stock available."
                    )

                else:

                    existing = False

                    for item in st.session_state.cart:

                        if item["product_id"] == selected_product[0]:

                            item["quantity"] += quantity
                            existing = True
                            break

                    if not existing:

                        st.session_state.cart.append(
                            {
                                "product_id": selected_product[0],
                                "name": selected_product[1],
                                "quantity": quantity,
                                "price": float(selected_product[2])
                            }
                        )

                    st.success("Product added to cart.")

            st.divider()

            st.subheader("Sale Items")

            if st.session_state.cart:

                cart_data = []

                total = 0

                for item in st.session_state.cart:

                    subtotal = (
                        item["quantity"] *
                        item["price"]
                    )

                    total += subtotal

                    cart_data.append(
                        [
                            item["name"],
                            item["quantity"],
                            item["price"],
                            subtotal
                        ]
                    )

                df = pd.DataFrame(
                    cart_data,
                    columns=[
                        "Product",
                        "Quantity",
                        "Price",
                        "Subtotal"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                col1, col2 = st.columns([3, 1])

                with col2:

                    st.markdown(
                        f"""
                        <div class="total-box">
                            <div class="total-label">
                                Total Amount
                            </div>
                            <div class="total-value">
                                ₹{total:,.2f}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.write("")

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Clear Cart",
                        use_container_width=True
                    ):

                        st.session_state.cart = []

                        st.rerun()

                with col2:

                    if st.button(
                        "Create Sale",
                        type="primary",
                        use_container_width=True
                    ):

                        try:

                            customer_id = customer_options[
                                selected_customer
                            ]

                            cur = conn.cursor()

                            cur.execute(
                                """
                                INSERT INTO sales
                                (customer_id, date, total_amount)
                                VALUES (%s, %s, %s)
                                RETURNING id
                                """,
                                (
                                    customer_id,
                                    sale_date,
                                    total
                                )
                            )

                            sale_id = cur.fetchone()[0]

                            for item in st.session_state.cart:

                                cur.execute(
                                    """
                                    INSERT INTO sale_items
                                    (sale_id, product_id, quantity, price)
                                    VALUES (%s, %s, %s, %s)
                                    """,
                                    (
                                        sale_id,
                                        item["product_id"],
                                        item["quantity"],
                                        item["price"]
                                    )
                                )

                                cur.execute(
                                    """
                                    UPDATE products
                                    SET quantity = quantity - %s
                                    WHERE id = %s
                                    """,
                                    (
                                        item["quantity"],
                                        item["product_id"]
                                    )
                                )

                            conn.commit()

                            cur.close()

                            st.session_state.cart = []

                            st.success(
                                f"Sale #{sale_id} created successfully."
                            )

                            st.session_state.selected_sale = sale_id

                        except Exception as e:

                            conn.rollback()

                            st.error(
                                f"Could not create sale: {e}"
                            )

            else:

                st.info(
                    "Your sale is empty. Add products above."
                )

    with tab2:

        sales = execute_query(
            """
            SELECT
                s.id,
                c.name,
                s.date,
                s.total_amount
            FROM sales s
            LEFT JOIN customers c
                ON s.customer_id = c.id
            ORDER BY s.id DESC
            """
        )

        if sales:

            df = pd.DataFrame(
                sales,
                columns=[
                    "Sale ID",
                    "Customer",
                    "Date",
                    "Total Amount"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No sales found.")


def sale_items_page():

    st.markdown(
        '<div class="page-title">Sale Items</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">View products included in a sale.</div>',
        unsafe_allow_html=True
    )

    sale_id = st.number_input(
        "Sale ID",
        min_value=1,
        step=1
    )

    if st.button(
        "View Sale",
        use_container_width=True
    ):

        items = execute_query(
            """
            SELECT
                si.id,
                p.name,
                si.quantity,
                si.price,
                si.quantity * si.price
            FROM sale_items si
            JOIN products p
                ON si.product_id = p.id
            WHERE si.sale_id = %s
            """,
            (int(sale_id),)
        )

        if items:

            df = pd.DataFrame(
                items,
                columns=[
                    "Item ID",
                    "Product",
                    "Quantity",
                    "Price",
                    "Subtotal"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            total = sum(
                float(item[4])
                for item in items
            )

            st.metric(
                "Total Amount",
                f"₹{total:,.2f}"
            )

        else:

            st.info("No items found for this sale.")


def analytics_page():

    st.markdown(
        '<div class="page-title">Analytics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Understand your sales and inventory.</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input(
            "Start Date",
            value=date.today()
        )

    with col2:

        end_date = st.date_input(
            "End Date",
            value=date.today()
        )

    if start_date > end_date:

        st.error(
            "Start date cannot be after end date."
        )

        return

    total = execute_query(
        """
        SELECT COALESCE(SUM(total_amount), 0)
        FROM sales
        WHERE date BETWEEN %s AND %s
        """,
        (
            start_date,
            end_date
        )
    )[0][0]

    sales_count = execute_query(
        """
        SELECT COUNT(*)
        FROM sales
        WHERE date BETWEEN %s AND %s
        """,
        (
            start_date,
            end_date
        )
    )[0][0]

    col1, col2 = st.columns(2)

    col1.metric(
        "Sales",
        sales_count
    )

    col2.metric(
        "Revenue",
        f"₹{float(total):,.2f}"
    )

    st.divider()

    st.subheader("Revenue by Date")

    revenue_data = execute_query(
        """
        SELECT date, SUM(total_amount)
        FROM sales
        WHERE date BETWEEN %s AND %s
        GROUP BY date
        ORDER BY date
        """,
        (
            start_date,
            end_date
        )
    )

    if revenue_data:

        df = pd.DataFrame(
            revenue_data,
            columns=[
                "Date",
                "Revenue"
            ]
        )

        df["Date"] = pd.to_datetime(df["Date"])

        st.line_chart(
            df.set_index("Date")
        )

    else:

        st.info("No sales in this date range.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Top Selling Products")

        top_products = execute_query(
            """
            SELECT
                p.name,
                SUM(si.quantity) AS quantity_sold
            FROM sale_items si
            JOIN products p
                ON si.product_id = p.id
            JOIN sales s
                ON si.sale_id = s.id
            WHERE s.date BETWEEN %s AND %s
            GROUP BY p.id, p.name
            ORDER BY quantity_sold DESC
            LIMIT 5
            """,
            (
                start_date,
                end_date
            )
        )

        if top_products:

            df = pd.DataFrame(
                top_products,
                columns=[
                    "Product",
                    "Quantity Sold"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No product sales found.")

    with col2:

        st.subheader("Sales by Customer")

        customer_sales = execute_query(
            """
            SELECT
                c.name,
                COUNT(s.id),
                SUM(s.total_amount)
            FROM sales s
            JOIN customers c
                ON s.customer_id = c.id
            WHERE s.date BETWEEN %s AND %s
            GROUP BY c.id, c.name
            ORDER BY SUM(s.total_amount) DESC
            """,
            (
                start_date,
                end_date
            )
        )

        if customer_sales:

            df = pd.DataFrame(
                customer_sales,
                columns=[
                    "Customer",
                    "Sales",
                    "Revenue"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No customer sales found.")


def sidebar():

    with st.sidebar:

        st.markdown(
            "## 🧾 Smart Billing"
        )

        st.caption(
            "Billing & Inventory"
        )

        st.divider()

        pages = {
            "🏠 Dashboard": "Dashboard",
            "👥 Customers": "Customers",
            "📦 Products": "Products",
            "💰 Sales": "Sales",
            "🧾 Sale Items": "Sale Items",
            "📊 Analytics": "Analytics"
        }

        for label, page in pages.items():

            if st.button(
                label,
                use_container_width=True
            ):

                st.session_state.page = page

                st.rerun()

        st.divider()

        try:

            conn.cursor().execute("SELECT 1")

            st.success(
                "Database Connected"
            )

        except:

            st.error(
                "Database Offline"
            )


sidebar()


if st.session_state.page == "Dashboard":

    dashboard()

elif st.session_state.page == "Customers":

    customers_page()

elif st.session_state.page == "Products":

    products_page()

elif st.session_state.page == "Sales":

    sales_page()

elif st.session_state.page == "Sale Items":

    sale_items_page()

elif st.session_state.page == "Analytics":

    analytics_page()

