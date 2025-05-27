from django.views.generic import TemplateView
from django.db import connection
from web_project import TemplateLayout

import json

class DashboardsView(TemplateView):
    template_name = 'dashboard_analytics.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        with connection.cursor() as cursor:
            # Total sales
            cursor.execute("""
                SELECT SUM(quantity * unit_price)
                FROM order_details
            """)
            total_sales = cursor.fetchone()[0] or 0

            # Customers list
            cursor.execute("""
                SELECT
                    company AS Company,
                    CONCAT(first_name, ' ', last_name) AS Full_Name,
                    job_title AS Job_Title,
                    address AS Address,
                    city AS City,
                    zip_postal_code AS Zip_Code
                FROM customers;
            """)
            customers = cursor.fetchall()
            columns = ['Company', 'Full_Name', 'Job_Title', 'Address', 'City', 'Zip_Code']
            customers_list = [dict(zip(columns, row)) for row in customers]

            # Total customers
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0] or 0

            # Sales by country (top 5)
            cursor.execute("""
                SELECT city, SUM(quantity * unit_price) AS total_sales
                FROM customers, order_details
                GROUP BY customers.city
                ORDER BY total_sales DESC
                LIMIT 5
            """)
            sales_by_country = cursor.fetchall()
            sales_labels = [row[0] for row in sales_by_country]
            sales_values = [float(row[1]) for row in sales_by_country]

            # Top 5 employees
            cursor.execute("""
                SELECT first_name, last_name, job_title, city
                FROM employees
                LIMIT 5
            """)
            employees = cursor.fetchall()

            # Top 5 most expensive products
            cursor.execute("""
                SELECT
                    product_name,
                    list_price,
                    category
                FROM
                    products
                ORDER BY
                    list_price DESC
                LIMIT 5;
            """)
            products = cursor.fetchall()
            product_columns = ['Product_Name', 'List_Price', 'Category']
            top_products = [dict(zip(product_columns, row)) for row in products]
            product_names = [p['Product_Name'] for p in top_products]
            product_prices = [p['List_Price'] for p in top_products]


        # Pack into context
        context.update({
            'total_sales': total_sales,
            'total_customers': total_customers,
            'sales_labels': json.dumps(sales_labels),
            'sales_values': json.dumps(sales_values),
            'employees': employees,
            'customers': customers_list,
            'top_products': top_products,
            'product_names': json.dumps(product_names),
            'product_prices': json.dumps([float(price) for price in product_prices])
        })

        return context
