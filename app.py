import streamlit as st
import pandas as pd
import sqlite3

from database import (
    connect_db,
    create_table,
    create_stock_history
)

from inventory import (
    add_product,
    view_products,
    search_product,
    update_product,
    delete_product,
    stock_in,
    stock_out,
    low_stock_products
)

# Initialize Database
create_table()
create_stock_history()


# Page Configuration
st.set_page_config(
    page_title="Inventory Stock Tracker",
    page_icon="📦",
    layout="wide"
)


# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    /* Dashboard Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #dbe3ef;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }

    /* Metric Labels */
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    /* Metric Values */
    div[data-testid="stMetricValue"] {
        color: #173b65 !important;
        font-size: 30px !important;
        font-weight: 700 !important;
    }

    /* Metric Delta */
    div[data-testid="stMetricDelta"] {
        color: #16a34a !important;
    }

    /* Main Headings */
    h1, h2, h3 {
        color: #173b65 !important;
    }

    /* Success Message */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        font-weight: 600;
    }

    /* Buttons */
    div.stButton > button,
    div.stFormSubmitButton > button {
        background-color: #1769aa;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 10px 20px;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background-color: #0d4f85;
        color: white;
    }
</style>
""", unsafe_allow_html=True)



# Application Title
st.title("📦 Inventory Stock Tracker")
st.caption("Manage your products and stock efficiently.")

st.divider()


# Sidebar Navigation
st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
    "Select Menu",
    [
        "Dashboard",
        "Add Product",
        "Manage Products",
        "Stock In",
        "Stock Out",
        "Low Stock Alert",
        "Stock History"
    ]
)


# Get Product Data
def get_data():

    products = view_products()

    columns = [
        "Product ID",
        "Name",
        "Category",
        "Price",
        "Quantity",
        "Minimum Stock"
    ]

    return pd.DataFrame(products, columns=columns)



# Dashboard
if menu == "Dashboard":

    st.header("📊 Dashboard Overview")
    st.caption("Monitor your inventory performance.")

    df = get_data()

    # Calculate Dashboard Statistics
    total_products = len(df)

    total_stock = int(df["Quantity"].sum()) if not df.empty else 0

    low_stock = len(low_stock_products())

    inventory_value = (
        (df["Price"] * df["Quantity"]).sum()
        if not df.empty else 0
    )

    # Dashboard Metric Cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 Total Products", total_products)

    col2.metric("📊 Total Stock", total_stock)

    col3.metric("⚠️ Low Stock Items", low_stock)

    col4.metric("💰 Inventory Value", f"₹{inventory_value:,.2f}")

    st.divider()

    # Product Inventory
    st.subheader("📋 Product Inventory")

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
                label="📥 Download Inventory Report",
                data=csv,
                file_name="inventory_report.csv",
                mime="text/csv"
            )
    else:
        st.info("No products available. Add your first product.")

    st.divider()

    # Stock Analytics
    st.subheader("📈 Stock Analytics")

    if not df.empty:

        chart_col1, chart_col2 = st.columns(2)

        # Category Wise Stock
        with chart_col1:

            st.write("**Category-wise Stock**")

            category_data = (
                df.groupby("Category")["Quantity"]
                .sum()
                .reset_index()
            )

            category_data = category_data.set_index("Category")

            st.bar_chart(category_data)

        # Top Products by Quantity
        with chart_col2:

            st.write("**Top 5 Products by Quantity**")

            top_products = (
                df.nlargest(5, "Quantity")
                [["Name", "Quantity"]]
                .set_index("Name")
            )

            st.bar_chart(top_products)

        st.divider()

        # Inventory Value Analytics
        st.subheader("💰 Inventory Value Analytics")

        df["Total Value"] = df["Price"] * df["Quantity"]

        value_col1, value_col2 = st.columns(2)

        with value_col1:

            st.write("**Category-wise Inventory Value**")

            category_value = (
                df.groupby("Category")["Total Value"]
                .sum()
                .reset_index()
            )

            category_value = category_value.set_index("Category")

            st.bar_chart(category_value)

        with value_col2:

            st.write("**Top 5 Most Valuable Products**")

            valuable_products = (
                df.nlargest(5, "Total Value")
                [["Name", "Total Value"]]
                .set_index("Name")
            )

            st.bar_chart(valuable_products)

    else:
        st.info("Add products to view stock analytics.")

    st.divider()

    # Low Stock Warning
    st.subheader("⚠️ Low Stock Products")

    low_df = pd.DataFrame(
        low_stock_products(),
        columns=[
            "Product ID", "Name", "Category",
            "Price", "Quantity", "Minimum Stock"
        ]
    )

    if not low_df.empty:

        st.warning("Some products need restocking!")

        st.dataframe(
            low_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("All products have sufficient stock!")



# Add Product
elif menu == "Add Product":

    st.header("➕ Add New Product")
    st.caption("Enter product details to add a new item to your inventory.")

    with st.form("add_product_form"):

        name = st.text_input("Product Name")

        category = st.text_input("Category")

        price = st.number_input(
            "Price (₹)", min_value=0.0, step=10.0
        )

        quantity = st.number_input(
            "Quantity", min_value=0, step=1
        )

        min_stock = st.number_input(
            "Minimum Stock Limit", min_value=0, step=1
        )

        submitted = st.form_submit_button("➕ Add Product")

        if submitted:

            if not name.strip() or not category.strip():

                st.error("❌ Failed! Please enter product name and category.")

            else:
                try:
                    add_product(
                        name.strip(),
                        category.strip(),
                        price,
                        quantity,
                        min_stock
                    )

                    st.success(
                        f"✅ Success! {name} has been added to your inventory."
                    )

                    st.balloons()

                except Exception as e:

                    st.error(f"❌ Product could not be added: {e}")

# Manage Products
elif menu == "Manage Products":

    st.header("📋 Manage Products")

    df = get_data()

    if not df.empty:

        st.subheader("🔍 Search & Filter Products")

        search_col, filter_col = st.columns(2)

        with search_col:
            keyword = st.text_input(
                "Search by Product Name or Category"
            )

        with filter_col:
            categories = ["All"] + sorted(
                df["Category"].dropna().unique().tolist()
            )

            selected_category = st.selectbox(
                "Filter by Category",
                categories
            )

        if keyword:
            results = search_product(keyword)

            df = pd.DataFrame(
                results,
                columns=[
                    "Product ID", "Name", "Category",
                    "Price", "Quantity", "Minimum Stock"
                ]
            )

        if selected_category != "All":
            df = df[
                df["Category"] == selected_category
            ]

        product_id_search = st.number_input(
            "Search by Product ID (0 = All)",
            min_value=0,
            step=1
        )

        if product_id_search > 0:
            df = df[
                df["Product ID"] == product_id_search
            ]

        st.dataframe(df, use_container_width=True)

        st.divider()

        st.subheader("Update Product")

        product_ids = df["Product ID"].tolist()

        if product_ids:

            selected_id = st.selectbox(
                "Select Product ID",
                product_ids
            )

            product = next(
                p for p in view_products()
                if p[0] == selected_id
            )

            with st.form("update_form"):

                new_name = st.text_input(
                    "Product Name", value=product[1]
                )

                new_category = st.text_input(
                    "Category", value=product[2]
                )

                new_price = st.number_input(
                    "Price",
                    min_value=0.0,
                    value=float(product[3])
                )

                new_min = st.number_input(
                    "Minimum Stock",
                    min_value=0,
                    value=int(product[5])
                )

                if st.form_submit_button("Update Product"):

                    if new_name.strip() and new_category.strip():

                        try:
                            update_product(
                                selected_id,
                                new_name.strip(),
                                new_category.strip(),
                                new_price,
                                new_min
                            )

                            st.success("✅ Product updated successfully!")
                            st.balloons()

                        except Exception as e:
                            st.error(f"❌ Update failed: {e}")

                    else:
                        st.error("Name and category cannot be empty.")

            st.divider()

            st.subheader("🗑️ Delete Product")

            all_products = view_products()

            delete_options = {
                p[0]: p[1]
                for p in all_products
            }

            if delete_options:

                delete_id = st.selectbox(
                    "Select Product ID to Delete",
                    list(delete_options.keys()),
                    format_func=lambda pid: f"ID: {pid} - {delete_options[pid]}"
                )

                confirm_delete = st.checkbox(
                    f"Confirm deletion of Product ID {delete_id}"
                )

                if st.button("🗑️ Delete Product"):

                    if confirm_delete:

                        try:
                            delete_product(delete_id)

                            st.success(
                                f"✅ Product '{delete_options[delete_id]}' deleted successfully!"
                            )

                            st.balloons()

                        except Exception as e:
                            st.error(f"❌ Deletion failed: {e}")

                    else:
                        st.warning("⚠️ Please confirm before deleting.")

            else:
                st.info("No products available to delete.")

    else:
        st.info("No products found.")


# Stock In


# Stock In
elif menu == "Stock In":

    st.header("📥 Add Stock")

    products = view_products()

    if products:

        product_options = {
            f"{p[1]} (ID: {p[0]})": p[0]
            for p in products
        }

        selected = st.selectbox(
            "Select Product",
            list(product_options.keys())
        )

        amount = st.number_input(
            "Quantity to Add", min_value=1, step=1
        )

    if st.button("Add Stock"):

            try:
                stock_in(product_options[selected], amount)

                st.success("✅ Stock added successfully!")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Stock addition failed: {e}")
    else:
        st.info("Add a product first.")


# Stock Out
elif menu == "Stock Out":

    st.header("📤 Remove Stock")

    products = view_products()

    if products:

        product_options = {
            f"{p[1]} (Available: {p[4]})": p[0]
            for p in products
        }

        selected = st.selectbox(
            "Select Product",
            list(product_options.keys())
        )

        amount = st.number_input(
            "Quantity to Remove", min_value=1, step=1
        )

        if st.button("Remove Stock"):

            try:
                result = stock_out(product_options[selected], amount)

                if result:
                    st.success("✅ Stock removed successfully!")
                    st.balloons()
                else:
                    st.error("❌ Insufficient stock or invalid product.")

            except Exception as e:
                st.error(f"❌ Stock removal failed: {e}")

    else:
        st.info("No products available.")


# Low Stock Alert
elif menu == "Low Stock Alert":

    st.header("⚠️ Low Stock Alert")
    st.caption("Monitor products that need restocking.")

    low_df = pd.DataFrame(
        low_stock_products(),
        columns=[
            "Product ID", "Name", "Category",
            "Price", "Quantity", "Minimum Stock"
        ]
    )

    if not low_df.empty:

        st.warning(f"⚠️ {len(low_df)} product(s) need restocking!")

        st.dataframe(
            low_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📊 Restocking Summary")

        low_df["Required Stock"] = (
            low_df["Minimum Stock"] - low_df["Quantity"] + 1
        )

        st.dataframe(
            low_df[["Name", "Quantity", "Minimum Stock", "Required Stock"]],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("✅ All products have sufficient stock!")
        st.balloons()


# Stock History
elif menu == "Stock History":

    st.header("📜 Stock Transaction History")
    st.caption("View and monitor all stock movements.")

    conn = connect_db()

    history = pd.read_sql_query("""
        SELECT
            h.id AS 'Transaction ID',
            p.name AS 'Product Name',
            h.transaction_type AS 'Transaction Type',
            h.quantity AS 'Quantity',
            h.transaction_date AS 'Date'
        FROM stock_history h
        LEFT JOIN products p
        ON h.product_id = p.product_id
        ORDER BY h.id DESC
    """, conn)

    conn.close()

    if not history.empty:

        total_transactions = len(history)

        stock_in_total = history[
            history["Transaction Type"] == "STOCK IN"
        ]["Quantity"].sum()

        stock_out_total = history[
            history["Transaction Type"] == "STOCK OUT"
        ]["Quantity"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("📋 Total Transactions", total_transactions)
        col2.metric("📥 Total Stock In", int(stock_in_total))
        col3.metric("📤 Total Stock Out", int(stock_out_total))

        st.divider()

        st.subheader("🔍 Filter Transactions")

        transaction_filter = st.selectbox(
            "Select Transaction Type",
            ["All", "STOCK IN", "STOCK OUT"]
        )

        filtered_history = history.copy()

        if transaction_filter != "All":
            filtered_history = history[
                history["Transaction Type"] == transaction_filter
            ]

        st.subheader("📊 Transaction Records")

        st.dataframe(
            filtered_history,
            use_container_width=True,
            hide_index=True
        )

        filtered_history["Date"] = pd.to_datetime(
            filtered_history["Date"],
            errors="coerce"
        ).dt.strftime("%d-%m-%Y %I:%M:%S %p")

        csv_history = filtered_history.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Stock History",
            data=csv_history,
            file_name="stock_history_report.csv",
            mime="text/csv"
        )
        st.caption(
            f"Showing {len(filtered_history)} transaction(s)."
        )

    else:
        st.info("No transaction history available yet.")


# Footer
st.sidebar.divider()

st.sidebar.caption("Inventory Stock Tracker")

st.sidebar.caption("Developed using Python & SQLite")
