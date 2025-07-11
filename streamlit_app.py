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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect (
    "Choose up to 5 ingredients.", 
    my_dataframe,
    max_selections=5
    )

ingredients_string = ''
if ingredients_list:
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_fruit = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_fruit, '.')
        st.subheader(fruit_chosen + ' nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_fruit)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
    values ('""" + ingredients_string + "','"+ name_on_order + "')"""

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered '+name_on_order+'!', icon="✅")




