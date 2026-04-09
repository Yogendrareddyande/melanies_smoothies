import streamlit as st
import pandas as pd

st.set_page_config(page_title="Melanie's Smoothies", page_icon="🥤", layout="centered")

st.title("🥤 Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input("Name on smoothie:")

if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
fruit_df = session.sql("""
    SELECT FRUIT_NAME
    FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
    ORDER BY FRUIT_NAME
""").to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    st.write("Selected ingredients:", ", ".join(ingredients_list))

submit_order = st.button("Submit Order")

if submit_order:
    if not name_on_order.strip():
        st.warning("Please enter your name before placing the order.")
    elif not ingredients_list:
        st.warning("Please choose at least one ingredient.")
    else:
        ingredients_string = ", ".join(ingredients_list)

        # escape single quotes safely
        safe_name = name_on_order.replace("'", "''")
        safe_ingredients = ingredients_string.replace("'", "''")

        insert_sql = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(insert_sql).collect()
        st.success(f"Your smoothie is ordered, {name_on_order}!", icon="✅")
