import pandas as pd
import numpy as np
import os
from datetime import datetime
from datetime import time

################################################################################################################################

team_name = '028_วอเรนต์ บุฟเฟต์'

################################################################################################################################

output_dir = os.path.expanduser("~/Desktop/competition_api")
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created main directory: {output_dir}")

def load_previous(file_type, teamName):
    output_dir = os.path.expanduser("~/Desktop/competition_api")
    folder_path = os.path.join(output_dir, "Previous", file_type)
    file_path = os.path.join(folder_path, f"{teamName}_{file_type}.csv")
    
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path)
            print(f"Loaded '{file_type}' data for team {teamName}.")
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    else:
        print(f"File not found: {file_path}")
        return None

def save_output(data, file_type, teamName):
    folder_path = output_dir + f"/Result/{file_type}"
    file_path = folder_path + f"/{teamName}_{file_type}.csv"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"Directory created: '{folder_path}'")

    # Save CSV
    data.to_csv(file_path, index=False)
    print(f"{file_type} saved at {file_path}")

statements = []

initial_investment = 10000000 


order_info = {
    'ShareCode' : '', 
    'TradeDateTime': '',
    'OrderPrice' : 0.0,  
    'Volume': 0.0,  
    'Value': 0.0,
    'OrderType' : 'Buy',      
}




portfolio_data = {
    'Table Name': [],
    'File Name': [],
    'Stock name': [],
    'Start Vol': [],
    'Actual Vol': [],
    'Avg Cost': [],
    'Market Price': [],
    'Market Value': [],
    'Amount Cost': [],
    'Unrealized P/L': [],
    '% Unrealized P/L': [],
    'Realized P/L': []
}




#--------------------------------[Simple Moving Average (SMA)]----------------------------------
def SMA(selected_stock,short_window,long_window):
    df_Signal = pd.DataFrame({})
    df_Signal['SMA_Short'] = selected_stock['LastPrice'].rolling(window=short_window).mean()
    df_Signal['SMA_Long']  = selected_stock['LastPrice'].rolling(window=long_window).mean()
    
    df_Signal['Signal'] = 0  # สัญญาณเริ่มต้นเป็น 0
    df_Signal.loc[df_Signal['SMA_Short'] > df_Signal['SMA_Long'], 'Signal'] = 1  # สัญญาณซื้อ
    df_Signal.loc[df_Signal['SMA_Short'] <= df_Signal['SMA_Long'], 'Signal'] = -1  # สัญญาณขาย
    
    df_Signal['Position'] = df_Signal['Signal'].shift(1)
    return df_Signal
#------------------------------------------------------------------------------------------------

   

def Update_portfolio(selected_stock,Match_Oder):
    global portfolio_data,idx,order_info,initial_balance
    stock_name = selected_stock['ShareCode']
    if  stock_name in portfolio_data['Stock name']:
        idx = portfolio_data['Stock name'].index(stock_name)
        if  Match_Oder:  
            order_info['Volume'] -= selected_stock['Volume']
            if  order_info['OrderType'] == 'Buy':
                initial_balance -= selected_stock['Value']
                Cost = portfolio_data['Avg Cost'][idx]*portfolio_data['Actual Vol'][idx]+selected_stock['Value']
                portfolio_data['Actual Vol'][idx] += selected_stock['Volume']
                portfolio_data['Avg Cost'][idx] =  Cost / portfolio_data['Actual Vol'][idx]
            elif order_info['OrderType'] == 'Sell':
                initial_balance += selected_stock['Value']
                portfolio_data['Actual Vol'][idx] -= selected_stock['Volume']
                realized_pnl = (order_info['OrderPrice'] - portfolio_data['Avg Cost'][idx]) * order_info['Volume']
                portfolio_data['Realized P/L'][idx] += realized_pnl
                
        portfolio_data['Market Price'][idx] = selected_stock['LastPrice']
        portfolio_data['Market Value'][idx] = portfolio_data['Actual Vol'][idx] * portfolio_data['Market Price'][idx] 
        portfolio_data['Amount Cost'][idx] = portfolio_data['Actual Vol'][idx] * portfolio_data['Avg Cost'][idx]
        portfolio_data['Unrealized P/L'][idx] = portfolio_data['Market Value'][idx] - portfolio_data['Amount Cost'][idx]
        portfolio_data['% Unrealized P/L'][idx] = (portfolio_data['Unrealized P/L'][idx] / portfolio_data['Amount Cost'][idx]) * 100
    else:
        if  Match_Oder and order_info['OrderType'] == 'Buy':
            portfolio_data['Table Name'].append('Portfolio_file')
            portfolio_data['File Name'].append(team_name)
            portfolio_data['Stock name'].append(stock_name)
            portfolio_data['Start Vol'].append(0)
            portfolio_data['Actual Vol'].append(selected_stock['Volume'])
            Cost = selected_stock['Value']
            Avg_cost = Cost / selected_stock['Volume']
            portfolio_data['Avg Cost'].append(Avg_cost) 
            portfolio_data['Market Price'].append(selected_stock['LastPrice'])
            portfolio_data['Market Value'].append(selected_stock['Value']) 
            portfolio_data['Amount Cost'].append(selected_stock['Volume']*Avg_cost)
            portfolio_data['Unrealized P/L'].append(selected_stock['Value']-selected_stock['Volume']*Avg_cost) 
            portfolio_data['% Unrealized P/L'].append((selected_stock['Value']-selected_stock['Volume']*Avg_cost) / selected_stock['Volume']*Avg_cost * 100)
            portfolio_data['Realized P/L'].append(0)
            idx = portfolio_data['Stock name'].index(stock_name)


def validate_order(selected_stock):
    global order_info, portfolio_data,idx,initial_balance
    validate_sell = False
    validate_buy = False
    
    if  order_info['OrderType'] == 'Sell':
        try:
            idx = portfolio_data['Stock name'].index(selected_stock['ShareCode'][0])
            have_stock = True
            enough_volume = portfolio_data['Actual Vol'][idx] >= order_info['Volume']  
        except ValueError:
            have_stock = False
            enough_volume = False 
        at_least_volume = order_info['Volume'] >= 100
        validate_sell = ( have_stock and enough_volume and at_least_volume ) 
    elif order_info['OrderType'] == 'Buy':   
        at_least_volume = order_info['Volume'] >= 100
        enough_balance = initial_balance >= order_info['Value']
        validate_buy = enough_balance and at_least_volume
        
    return validate_sell or validate_buy

idx = 0 
# process(selected_stock ,df_Signal)
def process(selected_stock,Vol,df_Signal):
    global order_info,portfolio_data
    signal = 0  # สัญญาณเริ่มต้นเป็น 0
    action = None
    order_sended = False
    for i in range(len(selected_stock)):
        #print(selected_stock.iloc[i])
    
        if order_sended:
            if order_info['Volume'] == 0 :
                order_sended = False
                # Close Order and update All Data
            else:
                # Check Match_Oder
                order_time = datetime.strptime(order_info['TradeDateTime'], '%Y-%m-%d %H:%M:%S')
                tick_time = datetime.strptime(selected_stock.iloc[i]['TradeDateTime'], '%Y-%m-%d %H:%M:%S')
                chicklist_condition = {
                    "ShareCode Match" : order_info['ShareCode'] == selected_stock.iloc[i]['ShareCode'],
                    "Time Valid" : order_time <= tick_time,
                    "Price Match" : order_info['OrderPrice'] == selected_stock.iloc[i]['LastPrice'],
                    "Volume Match" : order_info['Volume'] >= selected_stock.iloc[i]['Volume'], #{order_info['Volume'] -ADVANC.iloc[i]['Volume']}
                    "Flag Match" : order_info['OrderType'] != selected_stock.iloc[i]['Flag'],
                }
                Match_Oder = not (False in chicklist_condition.values())
                Update_portfolio(selected_stock.iloc[i],Match_Oder)
                #print(Match_Oder)
                #print(chicklist_condition) 
            # [print(i,portfolio_data[i]) for i in portfolio_data]
            # print('_________________________________________________________________________\n')
            continue
    
        
        signal = df_Signal['Signal'][i]  
        action = None
        if signal: # มีสัญญาณ
            action = ['Buy','Sell'][int(signal < 0)]
            # create order
            order_info['ShareCode'] = selected_stock['ShareCode'][0]
            order_info['TradeDateTime'] = selected_stock.iloc[i]['TradeDateTime']
            order_info['OrderPrice'] = selected_stock.iloc[i]['LastPrice']
            order_info['Volume'] = Vol
            order_info['Value'] = order_info['OrderPrice']*order_info['Volume']
            order_info['OrderType'] = action
            # validate_order and send order
            if validate_order(selected_stock): order_sended = True
        
        
        # try:
        #     print(f'{selected_stock["ShareCode"][0]} action {action} {portfolio_data["Actual Vol"][idx]}')
        # except:
        #     print(f"{selected_stock['ShareCode'][0]} action {action} no stock")
        # #[print(i,portfolio_data[i]) for i in portfolio_data]
        # print('_________________________________________________________________________\n')

def Update_statement():
    pass

def Update_summary():
    pass

# Load the summary file
prev_summary_df = load_previous("summary", team_name)

if prev_summary_df is not None:
    if 'End Line available' in prev_summary_df.columns:
        # ดึงค่าคอลัมน์ 'End Line available' ทั้งหมด
        initial_balance_series = prev_summary_df['End Line available']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not initial_balance_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            first_value = initial_balance_series.iloc[0]
            
            # ลบเครื่องหมายคั่นหลักพันและแปลงเป็น float
            try:
                initial_balance = float(str(first_value).replace(',', '').strip())
                Start_Line_available = initial_balance
                print("End Line available column loaded successfully.")
                print(f"Initial balance (first value): {initial_balance}")
            except ValueError:
                print(f"Error converting '{first_value}' to a float.")
                initial_balance = initial_investment  # ใช้ค่าตั้งต้นในกรณีเกิดข้อผิดพลาด
        else:
            print("'End Line available' column is empty.")
            initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากคอลัมน์ว่าง
    else:
        print("'End Line available' column not found in the file.")
        initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากไม่มีคอลัมน์
else:
    initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากไฟล์ไม่โหลด
    Start_Line_available = initial_investment
    print(f"Initial balance = initial_investment: {initial_investment}")



prev_portfolio_df = load_previous("portfolio", team_name)
print(prev_portfolio_df)

print(portfolio_data)


file_path = '~/Desktop/Daily_Ticks.csv' 
df = pd.read_csv(file_path)

csv_file = "Daily_Ticks.csv"  # ชื่อไฟล์ CSV ของคุณ
df = pd.read_csv(csv_file)

stock_name = ['ADVANC','AOT','BDMS','CPALL','DELTA','GULF','KBANK','PTTEP','SCB','TLI']
selected_stock = [ df[df['ShareCode'] == i].reset_index(drop=True) for i in stock_name]

# ใข้ SMA
df_Signal = [SMA(i,short_window=300,long_window=900) for i in selected_stock]


for i in range(10):
    process(selected_stock[i] ,200,df_Signal[i])
portfolio_data
portfolio_df = pd.DataFrame(portfolio_data)



print(initial_balance)

print('port Value' , portfolio_df['Market Value'].sum())

print("% Return" ,((portfolio_df['Market Value'].sum() + initial_balance - 10000000) / 10000000* 100))