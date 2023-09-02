import streamlit as st 



# titulo 
st.markdown("<h1 style='text-align: center;'> SP500 RANKING TOOL 🔎🌟</h1>", unsafe_allow_html=True)


# Add white space
st.write("\n\n")


st.markdown("""
                This tool helps identify the most uptrend oportunities of the SP500 constitutents. The algortihm that chooses 
                the enterprises is rebalanced every 14 days. So make sure you keep loggeed in not to miss anything 	:eyes: 
                :grinning_face_with_star_eyes:
            
            """)


# Add white space
st.write("\n\n")
st.write("\n\n")


st.markdown("##### How it works:")

st.markdown("""

            The app is divided into 4 more pages: 

1. __Ranking:__  Find our top selection of stocks and the results of the model. :first_place_medal:
2. __Backtesting:__ Eventough the past does not dictate the future it surely helps to grasp a brief idea of how well we perform.
3. __Info:__  Get real time information on the stocks you are plannig to buy.  	:money_with_wings:
4. __Similarities:__ Find similiar companies to a given stock, very helpfull if you belive an industry is gonna blow... :boom: :chart_with_upwards_trend:

            
            
            """)



st.markdown("----")

if st.button(':telephone_receiver:'):

    st.header(":mailbox: Get in touch with Us")


    contact_form = """
    <form action="https://formsubmit.co/jossellado@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here"></textarea>
        <button type="submit">Send</button>
    </form>
    """

    st.markdown(contact_form, unsafe_allow_html=True)

    # Use Local CSS File
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    local_css("styles/style_intro.css")



