import streamlit as st
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input("Name on smoothie:")

try:
    cnx = st.connection("snowflake")
    session = cnx.session()

    my_dataframe = session.sql("""
        SELECT FRUIT_NAME, SEARCH_ON
        FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
        ORDER BY FRUIT_NAME
    """).to_pandas()
    pd_df = my_dataframe

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        my_dataframe["FRUIT_NAME"].tolist(),
        max_selections=5
    )

    if ingredients_list:
        ingredients_string = ""
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + " "
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
            st.subheader(fruit_chosen + " Nutrition Info")
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            if smoothiefroot_response.status_code == 200:
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.warning(f"No nutrition info found for {fruit_chosen}")

        if st.button("Submit Order"):
            if not name_on_order.strip():
                st.warning("Please enter your name.")
            else:
                safe_name = name_on_order.replace("'", "''")
                safe_ingredients = ingredients_string.strip().replace("'", "''")
                insert_sql = f"""
                    INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                    VALUES ('{safe_ingredients}', '{safe_name}')
                """
                session.sql(insert_sql).collect()
                st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

except Exception as e:
    st.error("Connection or query failed")
    st.exception(e)
