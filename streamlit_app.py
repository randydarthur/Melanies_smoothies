# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd



# Write directly to the app
st.title(f"Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
    )
name_on_order = st.text_input("Name on Smoothie")
st.write('The name on your Smoothie will be:',name_on_order)

# change to get session in the SniS (Hosted Streamlit) environment
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect (
    "Choose up to 5 ingredients.", 
    my_dataframe,
    max_selections=5
    )

ingredients_string = ''
if ingredients_list:
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' nutrition information')
        my_search_value = session.table("smoothies.public.fruit_options") \
            .select(col('SEARCH_ON')) \
            .filter(col('FRUIT_NAME') == fruit_chosen) \
            .to_pandas()
        search_fruit = my_search_value['SEARCH_ON'].iloc[0] if not my_search_value.empty else search_fruit = fruit_chosen
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_fruit)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
    values ('""" + ingredients_string + "','"+ name_on_order + "')"""

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered '+name_on_order+'!', icon="✅")




