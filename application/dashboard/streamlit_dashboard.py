from database_select_functions import *
import streamlit as st


establish_db_connection()

st.title ("Petrolprices in Freiburg")

comparison = st.selectbox('Compare the current price to',['Avg. from last week','Avg. from last 24h'])
avg_now = average_now()
if comparison == "Avg. from last week":
    avg_comparison = average_last_week()
    percentual_difference = (abs(avg_now - avg_comparison) / avg_comparison) * 100.0
    st.text(f"""The current average price in Freiburg is {avg_now}. 
This is a {round(percentual_difference,1)}% difference to last weeks average""")
elif comparison == "Avg. from last 24h":
    avg_comparison = average_last_24_h()
    percentual_difference = (abs(avg_now - avg_comparison) / avg_comparison) * 100.0
    st.text(f"""The current average price in Freiburg is {avg_now}. 
This is a {round(percentual_difference,1)}% difference to the last 24 hours average""")

st.subheader("Cheapest station in Freiburg")
name, price, time, street, number = cheapest_station()

st.text(f"""The currently cheapest station is {name} located at {street} {number},
with a price of {price} Euros.""")
st.text(f"This was recorded at {time}.")

st.subheader("Average prices over the day")
st.caption("The prices are always a weeks average")
df = average_last_week_plot()

st.set_option('deprecation.showPyplotGlobalUse', False)
plt.plot(df["prices"], color='red', linewidth=3)
plt.xlabel("Zeit", fontsize=11, fontweight='bold')
plt.ylabel("E5 Preis", fontsize=11, fontweight='bold')
plt.title("Benzinpreise in Freiburg", fontsize=16, fontweight='bold', loc='left')
plt.axhline(y=np.nanmean(df['prices']), color='#A4A4A4', linestyle='--', linewidth=1,
            label='Durchschnittspreis')
plt.axhline(y=1.98, color='#000000', linestyle='-', linewidth=1.5)
plt.grid(axis='y')
plt.legend(loc='upper right')
plt.xticks(rotation=45)
st.pyplot()