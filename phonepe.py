import psycopg2
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px

sql = psycopg2.connect(host='localhost',user='postgres',password=54321,database='phonepe_pluse')
mycursor = sql.cursor()


# Setting Webpage Configurations
st.set_page_config(layout="wide")

# Title
st.header(':violet[Phonepe Pulse Data Visualization ]')
st.write('**(Note)**:-This data between **2018** to **2022** in **INDIA**')

# Selection option
option = st.radio('**Select your option**',('All India', 'State wise','Top Ten categories'),horizontal=True)

if option == 'All India':
    tab1, tab2 = st.tabs(['Transaction','User'])
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            Transaction_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='Transaction_year')
        with col2:
            Transaction_quater = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='Transaction_quater')
        with col3:
            transaction_type = st.selectbox('**Select Transaction type**', ('Recharge & bill payments','Peer-to-peer payments',
            'Merchant payments','Financial Services','Others'),key='transaction_type')

        # Transaction Analysis bar chart query
        mycursor.execute(f"""SELECT State, Transaction_amount FROM aggregated_transaction WHERE Year = '{Transaction_year}' AND quater = '{Transaction_quater}' AND Transaction_type = '{transaction_type}';""")
        ch_query_result = mycursor.fetchall()
        ch_df_query_result = pd.DataFrame(np.array(ch_query_result), columns=['State', 'Transaction_amount'])
        ch_df_query_result1 = ch_df_query_result.set_index(pd.Index(range(1, len(ch_df_query_result)+1))) 

        # Transaction Analysis table query
        mycursor.execute(f"""SELECT State, Transaction_count, Transaction_amount FROM aggregated_transaction WHERE Year = '{Transaction_year}' AND Quater = '{Transaction_quater}' AND Transaction_type = '{transaction_type}';""")
        anly_query_result =  mycursor.fetchall()
        df_anly_query_result = pd.DataFrame(np.array(anly_query_result), columns=['State','Transaction_count','Transaction_amount'])
        anly__df_query_result1 = df_anly_query_result.set_index(pd.Index(range(1, len(df_anly_query_result)+1)))

        # Total Transaction Amount table query
        mycursor.execute(f"""SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE Year = '{Transaction_year}' AND Quater = '{Transaction_quater}' AND Transaction_type = '{transaction_type}';""")
        am_query_result = mycursor.fetchall()
        df_am_query_result = pd.DataFrame(np.array(am_query_result), columns=['Total','Average'])
        df_am_query_result1 = df_am_query_result.set_index(['Average'])

        # Total Transaction Count table query
        mycursor.execute(f"""SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE Year = '{Transaction_year}' AND Quater ='{Transaction_quater}' AND Transaction_type = '{transaction_type}';""")
        co_query_result = mycursor.fetchall()
        df_co_query_result = pd.DataFrame(np.array(co_query_result), columns=['Total','Average'])
        df_co__query_result1 = df_co_query_result.set_index(['Average'])


        # Geo visualization dashboard for Transaction 
        # Drop a State column from ch_df_query_result
        ch_df_query_result.drop(columns=['State'], inplace=True)

        # Clone the gio data
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)

        # Extract state names and sort them in alphabetical order
        state_names_transfer = [feature['properties']['ST_NM'] for feature in data1['features']]
        state_names_transfer.sort()

        # Create a DataFrame with the state names column
        df_state_names_transfer = pd.DataFrame({'State': state_names_transfer})

        # Combine the Gio State name with ch_df_query_result
        df_state_names_transfer['Transaction_amount']=ch_df_query_result

        df_state_names_transfer.to_csv('State_transaction.csv', index=False)# convert dataframe to csv file

        df_transfer = pd.read_csv('State_transaction.csv') # Read csv

        # Geo plot
        fig= px.choropleth(df_transfer,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color='Transaction_amount',
            color_continuous_scale='thermal',
            title = 'Transaction Analysis')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
        st.plotly_chart(fig,use_container_width=True)

        # All India Transaction Analysis Bar chart  /  ----- #
        ch_df_query_result1['State'] = ch_df_query_result1['State'].astype(str)
        ch_df_query_result1['Transaction_amount'] = ch_df_query_result1['Transaction_amount'].astype(float)
        ch_df_query_result1_fig = px.bar(ch_df_query_result1 , x = 'State', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'Transaction Analysis Chart', height = 700,)
        ch_df_query_result1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(ch_df_query_result1_fig,use_container_width=True)

        # All India Total Transaction calculation Table
        st.header(':violet[Total calculation]')

        col4, col5 = st.columns(2)
        with col4:
            st.subheader('Transaction Analysis')
            st.dataframe(anly__df_query_result1)
        with col5:
            st.subheader('Transaction Amount')
            st.dataframe(df_am_query_result1)
            st.subheader('Transaction Count')
            st.dataframe(df_co__query_result1)

# all india user
    with tab2:
            col1, col2 = st.columns(2)
            with col1:
                user_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='user_year')
            with col2:
                user_quater = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='user_quater')

            # SQL Query
            mycursor.execute (f"""SELECT "State", SUM(User_Count) FROM aggregated_user WHERE "Year" = '{user_year}' AND "Quater" = '{user_quater}' GROUP BY "State" ;""")
            user_tab_quary = mycursor.fetchall()
            df_user_tab_quary = pd.DataFrame(np.array(user_tab_quary), columns=['State', 'User Count'])
            df_user_tab_quary_rslt1 = df_user_tab_quary.set_index(pd.Index(range(1, len(df_user_tab_quary)+1)))
            # Total User Count table query
            mycursor.execute(f"""SELECT SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE "Year" = '{user_year}' AND "Quater" = '{user_quater}';""")
            in_us_co_qry_rslt = mycursor.fetchall()
            df_in_us_co_qry_rslt = pd.DataFrame(np.array(in_us_co_qry_rslt), columns=['Total','Average'])
            df_in_us_co_qry_rslt1 = df_in_us_co_qry_rslt.set_index(['Average'])

            #Geo visualization dashboard for User
            df_user_tab_quary.drop(columns=['State'], inplace=True)# Drop a State column from df_in_us_tab_qry_rslt
            # Clone the gio data
            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data2 = json.loads(response.content)
            # Extract state names and sort them in alphabetical order
            state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
            state_names_use.sort()
            # Create a DataFrame with the state names column
            df_state_names_use = pd.DataFrame({'State': state_names_use})
            # Combine the Gio State name with df_in_tr_tab_qry_rslt
            df_state_names_use['User Count']=df_user_tab_quary
            # convert dataframe to csv file
            df_state_names_use.to_csv('State_user.csv', index=False)
            # Read csv
            df_use = pd.read_csv('State_user.csv')
            # Geo plot
            fig_use = px.choropleth(df_use,
                                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                                    featureidkey='properties.ST_NM',
                                    locations='State',
                                    color='User Count'
                                    ,color_continuous_scale='thermal',
                                    title = 'User Analysis')
            fig_use.update_geos(fitbounds="locations", visible=False)
            fig_use.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
            st.plotly_chart(fig_use,use_container_width=True)

            # All India User Analysis Bar chart  
            df_user_tab_quary_rslt1['State'] = df_user_tab_quary_rslt1['State'].astype(str)
            df_user_tab_quary_rslt1['User Count'] = df_user_tab_quary_rslt1['User Count'].astype(int)
            df_user_tab_quary_rslt1_fig = px.bar(df_user_tab_quary_rslt1 , x = 'State', y ='User Count', color ='User Count', color_continuous_scale = 'thermal', title = 'User Analysis Chart', height = 700,)
            df_user_tab_quary_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
            st.plotly_chart(df_user_tab_quary_rslt1_fig,use_container_width=True)

            # All India Total User calculation Table 
            st.header(':violet[Total calculation]')

            col3, col4 = st.columns(2)
            with col3:
                st.subheader('User Analysis')
                st.dataframe(df_user_tab_quary_rslt1)
            with col4:
                st.subheader('User Count')
                st.dataframe(df_in_us_co_qry_rslt1)
#state wise
elif option =='State wise':
    # Select tab
    tab3, tab4 = st.tabs(['Transaction','User'])
    # State wise Transaction 
    with tab3:

        col1, col2,col3 = st.columns(3)
        with col1:
            st_tr_st = st.selectbox('**Select State**',('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_tr_st')
        with col2:
            st_transaction_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='st_transaction_year')
        with col3:
            st_transaction_quater = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='st_transaction_quater')

         # SQL Query

        # Transaction Analysis bar chart query
        mycursor.execute(f"""SELECT Transaction_type, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_transaction_year}' AND Quater = '{st_transaction_quater}';""")
        st_transaction_qry = mycursor.fetchall()
        df_st_transaction_qry = pd.DataFrame(np.array(st_transaction_qry), columns=['Transaction_type', 'Transaction_amount'])
        df_st_transaction_qry_rslt1 = df_st_transaction_qry.set_index(pd.Index(range(1, len(df_st_transaction_qry)+1)))
        
        # Transaction Analysis table query
        mycursor.execute(f"""SELECT Transaction_type, Transaction_count, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_transaction_year}' AND Quater = '{st_transaction_quater}';""")
        st_transaction_anly_qry = mycursor.fetchall()
        df_st_transaction_anly_qry = pd.DataFrame(np.array(st_transaction_anly_qry), columns=['Transaction_type','Transaction_count','Transaction_amount'])
        df_st_transaction_anly_qry_rslt1 = df_st_transaction_anly_qry.set_index(pd.Index(range(1, len(df_st_transaction_anly_qry)+1)))

        # Total Transaction Amount table query
        mycursor.execute(f"""SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_transaction_year}' AND Quater = '{st_transaction_quater}';""")
        st_transaction_amount_qry = mycursor.fetchall()
        df_st_transaction_amount_qry = pd.DataFrame(np.array(st_transaction_amount_qry), columns=['Total','Average'])
        df_st_transaction_amount_qry_rslt1 = df_st_transaction_amount_qry.set_index(['Average'])

        # Total Transaction Count table query
        mycursor.execute(f"""SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year ='{st_transaction_year}' AND Quater = '{st_transaction_quater}';""")
        st_transaction_count = mycursor.fetchall()
        df_st_transaction_count = pd.DataFrame(np.array(st_transaction_count), columns=['Total','Average'])
        df_st_transaction_county_rslt1 = df_st_transaction_count.set_index(['Average'])

        # State wise Transaction Analysis bar chart
        df_st_transaction_qry_rslt1['Transaction_type'] = df_st_transaction_qry_rslt1['Transaction_type'].astype(str)
        df_st_transaction_qry_rslt1['Transaction_amount'] = df_st_transaction_qry_rslt1['Transaction_amount'].astype(float)
        df_st_transaction_qry_rslt1_fig = px.bar(df_st_transaction_qry_rslt1 , x = 'Transaction_type', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'Transaction Analysis Chart', height = 500,)
        df_st_transaction_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_st_transaction_qry_rslt1_fig,use_container_width=True)

        # State wise Total Transaction calculation Table
        st.header(':violet[Total calculation]')

        col4, col5 = st.columns(2)
        with col4:
            st.subheader('Transaction Analysis')
            st.dataframe(df_st_transaction_anly_qry_rslt1)
        with col5:
            st.subheader('Transaction Amount')
            st.dataframe(df_st_transaction_amount_qry_rslt1)
            st.subheader('Transaction Count')
            st.dataframe(df_st_transaction_county_rslt1)

    # State wise User
    with tab4:
        
        col5, col6 = st.columns(2)
        with col5:
            user_state = st.selectbox('**Select State**',('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='user_state')
        with col6:
            user_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='user_year')
        
        # SQL Query

        # User Analysis Bar chart query
        mycursor.execute(f"""SELECT "Quater", SUM(User_Count) FROM aggregated_user WHERE "State" = '{user_state}' AND "Year" = '{user_year}' GROUP BY "Quater";""")
        state_user_query = mycursor.fetchall()
        df_state_user_query = pd.DataFrame(np.array(state_user_query), columns=['Quarter', 'User Count'])
        df_state_user_query_rslt1 = df_state_user_query.set_index(pd.Index(range(1, len(state_user_query)+1)))

        # Total User Count table query
        mycursor.execute(f"""SELECT SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE "State" = '{user_state}' AND "Year" = '{user_year}';""")
        state_user_count = mycursor.fetchall()
        df_state_user_count = pd.DataFrame(np.array(state_user_count), columns=['Total','Average'])
        df_state_user_count_rslt1 = df_state_user_count.set_index(['Average'])

        # All India User Analysis Bar chart 
        df_state_user_query_rslt1['Quarter'] = df_state_user_query_rslt1['Quarter'].astype(int)
        df_state_user_query_rslt1['User Count'] = df_state_user_query_rslt1['User Count'].astype(int)
        df_state_user_query_rslt1_fig = px.bar(df_state_user_query_rslt1 , x = 'Quarter', y ='User Count', color ='User Count', color_continuous_scale = 'thermal', title = 'User Analysis Chart', height = 500,)
        df_state_user_query_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_state_user_query_rslt1_fig,use_container_width=True)

        # State wise User Total User calculation Table
        st.header(':violet[Total calculation]')

        col3, col4 = st.columns(2)
        with col3:
            st.subheader('User Analysis')
            st.dataframe(df_state_user_query_rslt1)
        with col4:
            st.subheader('User Count')
            st.dataframe(df_state_user_count_rslt1)

#Top categories
else:

    # Select tab
    tab5, tab6 = st.tabs(['Transaction','User'])

    #  All India Top Transaction
    with tab5:
        top_transaction_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='top_transaction_year')

        # SQL Query

        # Top Transaction Analysis bar chart query
        mycursor.execute(f"""SELECT "State", SUM("Transaction_amount") As Transaction_amount FROM "top_transaction" WHERE "Year" = 2020 GROUP BY "State" ORDER BY 2 DESC LIMIT 10;""")
        top_transaction_query = mycursor.fetchall()
        df_top_transaction_query = pd.DataFrame(np.array(top_transaction_query), columns=['State', 'Top Transaction amount'])
        df_top_transaction_query_rslt1 = df_top_transaction_query.set_index(pd.Index(range(1, len(top_transaction_query)+1)))

        # Top Transaction Analysis table query
        mycursor.execute(f"""SELECT "State", SUM ("Transaction_amount") as Transaction_amount , SUM("Transaction_count") as Transaction_count  FROM "top_transaction" WHERE "Year" = '{top_transaction_year}' GROUP BY "State" ORDER BY 2 DESC LIMIT 10;""")
        top_transaction_anly_qry = mycursor.fetchall()
        df_top_transaction_anly_qry = pd.DataFrame(np.array(top_transaction_anly_qry), columns=['State', 'Top Transaction amount','Total Transaction count'])
        df_top_transaction_anly_rslt1 = df_top_transaction_anly_qry.set_index(pd.Index(range(1, len(top_transaction_anly_qry)+1)))

        #All India Transaction Analysis Bar chart
        df_top_transaction_query_rslt1['State'] = df_top_transaction_query_rslt1['State'].astype(str)
        df_top_transaction_query_rslt1['Top Transaction amount'] = df_top_transaction_query_rslt1['Top Transaction amount'].astype(float)
        df_top_transaction_query_rslt1_fig = px.bar(df_top_transaction_query_rslt1 , x = 'State', y ='Top Transaction amount', color ='Top Transaction amount', color_continuous_scale = 'thermal', title = 'Top Transaction Analysis Chart', height = 600,)
        df_top_transaction_query_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_top_transaction_query_rslt1_fig,use_container_width=True)

        #All India Total Transaction calculation Table
        st.header(':violet[Total calculation]')
        st.subheader('Top Transaction Analysis')
        st.dataframe(df_top_transaction_anly_rslt1)

    # Top User
    with tab6:
        top_user_year = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='top_user_year')

        # Top User Analysis bar chart 
        mycursor.execute(f"""SELECT "State", SUM("Registered_User") AS Top_user FROM "top_user" WHERE "Year"= 2020 GROUP BY "State" ORDER BY 2 DESC LIMIT 10;""")
        top_user = mycursor.fetchall()
        df_top_user = pd.DataFrame(np.array(top_user), columns=['State', 'Total User count'])
        df_top_user_rslt = df_top_user.set_index(pd.Index(range(1, len(df_top_user)+1)))


        #User Analysis Bar chart
        df_top_user_rslt['State'] = df_top_user_rslt['State'].astype(str)
        df_top_user_rslt['Total User count'] = df_top_user_rslt['Total User count'].astype(float)
        df_top_user_rslt_fig = px.bar(df_top_user_rslt , x = 'State', y ='Total User count', color ='Total User count', color_continuous_scale = 'thermal', title = 'Top User Analysis Chart', height = 600,)
        df_top_user_rslt_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_top_user_rslt_fig,use_container_width=True)

        # All India Total Transaction calculation Table
        st.header(':violet[Total calculation]')
        st.subheader('Total User Analysis')
        st.dataframe(df_top_user_rslt)


                





