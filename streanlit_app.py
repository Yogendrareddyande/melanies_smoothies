import streamlit as st
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.sql(
    "SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).to_pandas()

st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        safe_name = name_on_order.replace("'", "''")
        safe_ingredients = ingredients_string.replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")
