import pandas as pd
import numpy as np
import os
from datetime import datetime
from datetime import time

################################################################################################################################

team_name = '028_WarrenBuffet'

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


initial_investment = 10000000 
last_end_line_available = 0
count_win = 0
count_sell = 0
last_trading_day = 0
last_Win_rate = 0

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

statement_data = {
    'Table Name': [],
    'File Name': [],
    'Stock Name': [],
    'Date': [],
    'Time': [],
    'Side': [],
    'Volume': [],
    'Actual Vol':[],
    'Price': [],
    'Amount Cost': [],
    'End Line Available': [],
    'Porfolio value':[],
    'NAV':[]
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
    Match_Oder = False
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
                    "Volume Match" : (order_info['Volume'] >= selected_stock.iloc[i]['Volume']) and (selected_stock.iloc[i]['Volume']>=100), #{order_info['Volume'] -ADVANC.iloc[i]['Volume']}
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


def Update_portfolio(selected_stock,Match_Oder):
    global portfolio_data,idx,order_info,initial_balance,count_win,count_sell
    stock_name = order_info['ShareCode']
    if  stock_name in portfolio_data['Stock name']:
        idx = portfolio_data['Stock name'].index(stock_name)
        if  Match_Oder:  
            order_info['Volume'] -= selected_stock['Volume']
            if  order_info['OrderType'] == 'Buy':
                initial_balance -= selected_stock['Value']

                total_cost = portfolio_data['Avg Cost'][idx] * portfolio_data['Actual Vol'][idx]
                portfolio_data['Actual Vol'][idx] += selected_stock['Volume']
                portfolio_data['Avg Cost'][idx] = (total_cost + (selected_stock['LastPrice'] * selected_stock['Volume'])) / portfolio_data['Actual Vol'][idx]
                
            elif order_info['OrderType'] == 'Sell':
                count_sell+=1
                if order_info['OrderPrice'] > portfolio_data['Avg Cost'][idx]:count_win+=1
                initial_balance += selected_stock['Value']
                portfolio_data['Actual Vol'][idx] -= selected_stock['Volume']
                realized_pnl = (order_info['OrderPrice'] - portfolio_data['Avg Cost'][idx]) * selected_stock['Volume']
                portfolio_data['Realized P/L'][idx] += realized_pnl 
                
        portfolio_data['Market Price'][idx] = selected_stock['LastPrice']
        portfolio_data['Market Value'][idx] = portfolio_data['Actual Vol'][idx] * portfolio_data['Market Price'][idx] 
        portfolio_data['Amount Cost'][idx] = portfolio_data['Actual Vol'][idx] * portfolio_data['Avg Cost'][idx]
        portfolio_data['Unrealized P/L'][idx] = portfolio_data['Market Value'][idx] - portfolio_data['Amount Cost'][idx]
        if portfolio_data['Amount Cost'][idx] > 0:
            portfolio_data['% Unrealized P/L'][idx] = (portfolio_data['Unrealized P/L'][idx] / portfolio_data['Amount Cost'][idx]) * 100
        else:
            portfolio_data['% Unrealized P/L'][idx] = 0  # NaN
        if Match_Oder:
            Update_statement(selected_stock)
    else:
        if  Match_Oder and order_info['OrderType'] == 'Buy':
            initial_balance -= selected_stock['Value']
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
            Update_statement(selected_stock)
                        

def Update_statement(selected_stock):
    global portfolio_data,idx,order_info,initial_balance
    stock_name = order_info['ShareCode']
    statement_time = datetime.strptime(selected_stock['TradeDateTime'], '%Y-%m-%d %H:%M:%S')  
    statement_data['Table Name'].append('Statement_file')
    statement_data['File Name'].append(team_name)
    statement_data['Stock Name'].append(stock_name)
    statement_data['Date'].append(statement_time.strftime('%d/%m/%Y')) # tick date
    statement_data['Time'].append(statement_time.strftime('%H:%M')) # tick time
    statement_data['Side'].append(order_info['OrderType'][0]) # oder side
    statement_data['Volume'].append(selected_stock['Volume']) # tick vol
    statement_data['Actual Vol'].append(portfolio_data['Actual Vol'][idx]) # port vol
    statement_data['Price'].append(order_info['OrderPrice'])
    statement_data['Amount Cost'].append(portfolio_data['Amount Cost'][idx])
    statement_data['End Line Available'].append(initial_balance)
    Portfolio_value = sum(portfolio_data['Market Value'])
    statement_data['Porfolio value'].append(Portfolio_value)
    statement_data['NAV'].append(Portfolio_value + initial_balance)



# Load the previous summary file
prev_summary_df = load_previous("summary", team_name)
if prev_summary_df is not None:
    if 'trading_day' in prev_summary_df.columns:
        trading_day_series = prev_summary_df['trading_day']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not trading_day_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            last_trading_day = trading_day_series.iloc[0]
    else:
        last_trading_day = 0

    if 'Win rate' in prev_summary_df.columns:
        Win_rate_series = prev_summary_df['Win rate']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not Win_rate_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            last_Win_rate = Win_rate_series.iloc[0]
    else:
        last_Win_rate = 0


    if 'Number of wins' in prev_summary_df.columns:
        count_win_series = prev_summary_df['Number of wins']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not count_win_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            count_win = count_win_series.iloc[0]
    else:
        count_win = 0

    if 'Number of matched trades' in prev_summary_df.columns:
        count_sell_series = prev_summary_df['Number of matched trades']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not count_sell_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            count_sell = count_sell_series.iloc[0]
    else:
        count_sell = 0

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


# Load the previous portfolio file
prev_portfolio_df = load_previous("portfolio", team_name)
if prev_portfolio_df is not None:
    for key in prev_portfolio_df:
        portfolio_data[key] = list(prev_portfolio_df[str(key)])
    portfolio_data['Start Vol'] = portfolio_data['Actual Vol'].copy()   
else:
    pass

# Load the previous statement file
prev_statement_df = load_previous("statement", team_name)
if prev_statement_df is not None:
    for key in prev_statement_df:
        statement_data[key] = list(prev_statement_df[str(key)])   
else:
    pass



#----------------------------------------------------[main]---------------------------------------------------
csv_file = "~/Desktop/Daily_Ticks.csv" 
df = pd.read_csv(csv_file)

# สร้าง stock universe
stock_name = ['ADVANC','AOT','BDMS','CPALL','DELTA','GULF','KBANK','PTTEP','SCB','TLI']
selected_stock = [ df[df['ShareCode'] == i].reset_index(drop=True) for i in stock_name]

# ใข้ SMA
df_Signal = [SMA(i,short_window=30,long_window=50) for i in selected_stock]

# เริ่ม trad -> process()
for i in range(len(stock_name)):
    process(selected_stock[i] ,2000,df_Signal[i])
#-------------------------------------------------------------------------------------------------------



lengths = [len(value) for value in portfolio_data.values()]
try:
    # ตรวจสอบความยาวของข้อมูล
    portfolio_df = pd.DataFrame(portfolio_data)
except:
    # ถ้าความยาวไม่เท่ากัน
    max_length = max(lengths)
    for key in portfolio_data.keys():
        # เติมข้อมูลที่ขาดหายไปด้วย NaN
        if len(portfolio_data[key]) < max_length:
            portfolio_data[key] = portfolio_data[key] + [np.nan] * (max_length - len(portfolio_data[key]))

    portfolio_df = pd.DataFrame(portfolio_data)



lengths = [len(value) for value in statement_data.values()]
try:
    # ตรวจสอบความยาวของข้อมูล
    statement_df = pd.DataFrame(statement_data)
except:
    # ถ้าความยาวไม่เท่ากัน
    max_length = max(lengths)
    for key in statement_data.keys():
        # เติมข้อมูลที่ขาดหายไปด้วย NaN
        if len(statement_data[key]) < max_length:
            statement_data[key] = statement_data[key] + [np.nan] * (max_length - len(statement_data[key]))
    statement_df = pd.DataFrame(statement_data)
    


last_end_line_available = statement_df['End Line Available'].iloc[-1]
win_rate = 0
if  count_sell:
    win_rate = (count_win * 100)/ count_sell
elif not count_sell:
    if last_trading_day == 1:
        win_rate = 0
    else:
        win_rate = last_Win_rate

summary_data = {
    'Table Name': ['Sum_file'],
    'File Name': [team_name],
    'trading_day': [last_trading_day+1],  
    'NAV': [portfolio_df['Market Value'].sum() + last_end_line_available],
    'Portfolio value': [portfolio_df['Market Value'].sum()],
    'End Line available': [last_end_line_available],  # Use the correct End Line Available
    'Start Line available':[Start_Line_available],
    'Number of wins': [count_win], 
    'Number of matched trades': [count_sell], #นับ sell เพราะ เทรดbuy sellด้วย volume เท่ากัน
    'Number of transactions:': [len(statement_df)],
    'Net Amount': [statement_df['Amount Cost'].sum()],
    'Unrealized P/L': [portfolio_df['Unrealized P/L'].sum()],
    '% Unrealized P/L': [(portfolio_df['Unrealized P/L'].sum() / initial_investment * 100) if initial_investment else 0],
    'Realized P/L': [portfolio_df['Realized P/L'].sum()],
    'Maximum value': [statement_df['NAV'].max()],
    'Minimum value': [statement_df['NAV'].min()],
    'Win rate': [win_rate],
    'Calmar Ratio': [((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100) / \
                           ((portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000)],
    'Relative Drawdown': [(portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000 / statement_df['End Line Available'].max() * 100],
    'Maximum Drawdown': [(statement_df['NAV'].min() - statement_df['NAV'].max())/statement_df['NAV'].max() * 100],
    '%Return': [((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100)]
}



lengths = [len(value) for value in summary_data.values()]
try:
    # ตรวจสอบความยาวของข้อมูล
    summary_df = pd.DataFrame(summary_data)
except:
    # ถ้าความยาวไม่เท่ากัน
    max_length = max(lengths)
    for key in summary_data.keys():
        # เติมข้อมูลที่ขาดหายไปด้วย NaN
        if len(summary_data[key]) < max_length:
            summary_data[key] = summary_data[key] + [np.nan] * (max_length - len(summary_data[key]))
    summary_df = pd.DataFrame(summary_data)


def round4f(df):
    formatted_df = df.copy()
    for col in formatted_df.select_dtypes(include=['float']):
        formatted_df[col] = formatted_df[col].apply(lambda x: round(x, 4))
    return formatted_df

# round .4f float
portfolio_df = round4f(portfolio_df)
statement_df = round4f(statement_df)
summary_df = round4f(summary_df)

# print output
print(portfolio_df.to_string(header=False, index=False))
print(statement_df.to_string(header=False, index=False))
print(summary_df.to_string(header=False, index=False))

# save output to Result Folder
save_output(portfolio_df, "portfolio", team_name)
save_output(statement_df, "statement", team_name)
save_output(summary_df, "summary", team_name)