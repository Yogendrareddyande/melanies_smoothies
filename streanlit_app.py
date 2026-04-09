import streamlit as st
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input("Name on smoothie:")

try:
    cnx = st.connection("snowflake")
    session = cnx.session()

    fruit_df = session.sql("""
        SELECT FRUIT_NAME
        FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
        ORDER BY FRUIT_NAME
    """).to_pandas()
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        safe_name = name_on_order.replace("'", "''")
        safe_ingredients = ingredients_string.strip().replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")
    st.dataframe(fruit_df, use_container_width=True)

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_df["FRUIT_NAME"].tolist(),
        max_selections=5
    )

    if st.button("Submit Order"):
        if not name_on_order.strip():
            st.warning("Please enter your name.")
        elif not ingredients_list:
            st.warning("Please choose at least one ingredient.")
        else:
            ingredients_string = ", ".join(ingredients_list)
            safe_name = name_on_order.replace("'", "''")
            safe_ingredients = ingredients_string.replace("'", "''")

            insert_sql = f"""
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                VALUES ('{safe_ingredients}', '{safe_name}')
            """
            session.sql(insert_sql).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

except Exception as e:
    st.error("Connection or query failed")
    st.exception(e)
