import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# ฟังก์ชันสำหรับอ่านไฟล์ CSV
def load_data(statement_file, summary_file, portfolio_file):
    statement_df = pd.read_csv(statement_file)
    summary_df = pd.read_csv(summary_file)
    portfolio_df = pd.read_csv(portfolio_file)
    return statement_df, summary_df, portfolio_df

# ฟังก์ชันสำหรับแสดงกราฟแท่งเทียน
def plot_candlestick(df, stock_name):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'] + ' ' + df['Time'],
                                          open=df['Price'],
                                          high=df['Price'],
                                          low=df['Price'],
                                          close=df['Price'],
                                          name=stock_name)])
    fig.update_layout(title=f'Candlestick Chart for {stock_name}',
                      xaxis_title='Date & Time',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    return fig

# ฟังก์ชันสำหรับแสดงข้อมูลการเทรด
def display_trading_board(statement_df, selected_stock):
    st.title("Trading Dashboard")
    
    # แสดงข้อมูล Statement ในกรอบ
    stock_data = statement_df[statement_df['Stock Name'] == selected_stock]
    
    # สร้างกราฟแท่งเทียน
    candlestick_fig = plot_candlestick(stock_data, selected_stock)
    candlestick_chart = st.empty()  # สร้างพื้นที่ว่างสำหรับกราฟแท่งเทียน
    candlestick_chart.plotly_chart(candlestick_fig, use_container_width=True, key="candlestick_initial")

    # แสดงข้อมูล Statement ในรูปแบบตาราง
    st.subheader("Statement Data")
    statement_container = st.empty()  # สร้างพื้นที่ว่างสำหรับอัปเดตข้อมูล
    
    for index, row in stock_data.iterrows():
        # แสดงข้อมูลในตาราง
        statement_data = {
            "Time": f"{row['Date']} {row['Time']}",
            "Side": row['Side'],
            "Volume": row['Volume'],
            "Actual Vol": row['Actual Vol'],
            "Price": row['Price'],
            "Amount Cost": row['Amount Cost']
        }
        statement_container.dataframe(pd.DataFrame([statement_data]), use_container_width=True)
        
        # อัปเดตกราฟแท่งเทียน
        candlestick_fig = plot_candlestick(stock_data.iloc[:index + 1], selected_stock)
        candlestick_chart.plotly_chart(candlestick_fig, use_container_width=True, key=f"candlestick_{index}")
        
        time.sleep(0.5)  # Delay for replay effect

# ฟังก์ชันหลัก
def main():
    st.sidebar.title("Upload Files")
    statement_file = st.sidebar.file_uploader("Upload Statement CSV", type=["csv"])
    summary_file = st.sidebar.file_uploader("Upload Summary CSV", type=["csv"])
    portfolio_file = st.sidebar.file_uploader("Upload Portfolio CSV", type=["csv"])

    if statement_file and summary_file and portfolio_file:
        statement_df, summary_df, portfolio_df = load_data(statement_file, summary_file, portfolio_file)
        
        # เลือกหุ้น
        stock_names = statement_df['Stock Name'].unique()
        selected_stock = st.sidebar.selectbox("Select Stock", stock_names)

        # แสดงข้อมูลการเทรด
        display_trading_board(statement_df, selected_stock)

        # แสดงข้อมูล Summary
        st.subheader("Summary Data")
        st.write(summary_df)

        # แสดงข้อมูล Portfolio
        st.subheader("Portfolio Data")
        st.write(portfolio_df)

if __name__ == "__main__":
    main()