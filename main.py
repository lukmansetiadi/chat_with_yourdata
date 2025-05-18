from mylib.text2sql import to_sql_query, extract_schema, execute_sql_query, get_insight, get_tableimage_code
import streamlit as st

# db_url = "sqlite:///testdb.sqlite"

# version 2 : adding mysql as source and extra information on the prompt
# db_url = "mysql+pymysql://root:password@localhost/chat_with_quran"
# extra_information = """
# extra information on schema:
# ayahid = quran ayah explanation on indonesian translation
# ayahar = quran ayah explanation on arabic translation
# surahar = name of the surah on quran
# type = mecca or medina
# juz = juz number
# """

# version 3 : database sample retail
db_url = "mysql+pymysql://root:password@localhost/classicmodels"
extra_information = """
customers: stores customer’s data.
products: stores a list of scale model cars.
productlines: stores a list of product lines.
orders: stores sales orders placed by customers.
orderdetails: stores sales order line items for every sales order.
payments: stores payments made by customers based on their accounts.
employees: stores employee information and the organization structure such as who reports to whom.
offices: stores sales office data.

please use column amount on payments for profit or sales
"""

schema = extract_schema(db_url)
question = st.text_area("Describe the data you want to retrieve from the database:")

if question:
    sql = to_sql_query(question, schema, extra_information)
    # st.code(sql, wrap_lines=True, language="sql")

    data = ""
    sqllist = sql.split(";")
    if len(sqllist) > 1:
        for sql in sqllist:
            # print(sql)
            if len(sql.strip()) > 5:
                data = data + execute_sql_query(db_url, sql) + "\n"
    else:
        data = execute_sql_query(db_url, sql)
    # st.code(data, wrap_lines=True, language="sql")

    import matplotlib.pyplot as plt
    codeimage = get_tableimage_code(data)
    # st.code(codeimage, wrap_lines=True, language="sql")
    exec(codeimage.replace("plt.show()",""))
    # st.pyplot(plt)

    insight = get_insight(question, data, sql)

    plt.tight_layout()
    st.pyplot(plt)
    st.code(insight, wrap_lines=True, language="sql")

    st.code("QUERY::", wrap_lines=True, language="sql")
    st.code(sql, wrap_lines=True, language="sql")
    st.code("DATA::", wrap_lines=True, language="sql")
    st.code(data, wrap_lines=True, language="sql")
    st.code("MATPLOTLIB CODE::", wrap_lines=True, language="sql")
    st.code(codeimage, wrap_lines=True, language="sql")


