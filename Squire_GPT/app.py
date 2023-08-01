import streamlit as st

# Set the page config at the very top of your script
st.set_page_config(page_title="Squire", page_icon="Squire_GPT/ASSETS/pixel_pencil.png", layout='wide')

from chatUI import chatbot_ui_page
from SpearHead_Library import spearhead_library

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "Brain_Storm", "SpearHead_Library"])

    if selection == "Home":
        home_page()
    elif selection == "Brain_Storm":
        chatbot_ui_page()
    elif selection == "SpearHead_Library":
        spearhead_library()
   

def home_page():
    st.title("Welcome to Squire                :scales:")
  
    st.write("This is your account page. On the sidebar you can use the Brain_Storm tool of the SpearHead_Library tool.")



if __name__ == "__main__":
    main()
