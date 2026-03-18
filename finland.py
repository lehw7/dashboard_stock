import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import datetime
import warnings

# Helper functions for technical indicators
def get_MA(df):
    df['MA10'] = df['Price Close'].rolling(window=10).mean()  # MA10
    df['MA20'] = df['Price Close'].rolling(window=20).mean()  # MA20
    df['MA50'] = df['Price Close'].rolling(window=50).mean()  # MA50
    return df

def get_MACD(df, column='Price Close'):
    df['EMA-12'] = df[column].ewm(span=12, adjust=False).mean()
    df['EMA-26'] = df[column].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA-12'] - df['EMA-26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    return df

def get_RSI(df, column='Price Close', time_window=14):
    delta = df[column].diff()
    gain = delta.where(delta > 0, 0).rolling(window=time_window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=time_window).mean()
    RS = gain / loss
    df['RSI'] = 100 - (100 / (1 + RS))
    return df

def get_bollinger_bands(data, column='Price Close', window=20, num_std=2):
    sma = data[column].rolling(window=window).mean()
    std = data[column].rolling(window=window).std()
    data['Upper Band'] = sma + (std * num_std)
    data['Lower Band'] = sma - (std * num_std)
    data['SMA'] = sma
    return data

def get_MFI(df, high_col='Price High', low_col='Price Low', close_col='Price Close', volume_col='Volume', period=14):
    typical_price = (df[high_col] + df[low_col] + df[close_col]) / 3
    money_flow = typical_price * df[volume_col]
    df['Positive Flow'] = np.where(typical_price > typical_price.shift(1), money_flow, 0)
    df['Negative Flow'] = np.where(typical_price < typical_price.shift(1), money_flow, 0)
    positive_flow_sum = df['Positive Flow'].rolling(window=period).sum()
    negative_flow_sum = df['Negative Flow'].rolling(window=period).sum()
    money_flow_ratio = positive_flow_sum / negative_flow_sum
    df['MFI'] = 100 - (100 / (1 + money_flow_ratio))
    return df

###########################################################################################################
# Plotting functions for the technical indicators

# Candlestick
def plot_candlestick_with_indicators(fig, df, row, column=1, show_bb=True, show_sma=True, show_ma10=True,
                                     show_ma20=True, show_ma50=True):
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Price Open'],
        high=df['Price High'],
        low=df['Price Low'],
        close=df['Price Close'],
        name='Candlestick'),
        row=row, col=column
    )

    # Bollinger Band shaded area
    if show_bb:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Upper Band'],
            name='Upper Band',
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
            row=row, col=column
        )

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Lower Band'],
            name='Lower Band',
            fill='tonexty',  # Fill the area between Upper and Lower bands
            fillcolor='rgba(173, 216, 230, 0.2)',  # Light sky blue with 20% opacity
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
        row = row, col = column
    )

        # Simple Moving Average (SMA)
        if show_sma:
            fig.add_trace(go.Scatter(
        x = df['Date'],
        y = df['SMA'],
        name = '20-Day SMA',
        line = dict(color='orange', width=1.5)),
        row = row, col = column
        )

    # Moving Averages (MA10, MA20, MA50)
    if show_ma10:
        fig.add_trace(go.Scatter(
    x = df['Date'],
    y = df['MA10'],
    name = 'MA10',
    line = dict(color='RoyalBlue', width=1.5)),
    row = row, col = column
    )
    if show_ma20:
        fig.add_trace(go.Scatter(
    x = df['Date'],
    y = df['MA20'],
    name = 'MA20',
    line = dict(color='orange', width=1.5)),
    row = row, col = column
    )
    if show_ma50:
        fig.add_trace(go.Scatter(
    x = df['Date'],
    y = df['MA50'],
    name = 'MA50',
    line = dict(color='grey', width=1.5)),
    row = row, col = column
    )
    return fig

# Line Chart
def plot_line_chart_with_indicators(fig, df, row, column=1, show_bb=True, show_sma=True, show_ma10=True,
                                     show_ma20=True, show_ma50=True):
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Price Close'],
            name='Line Chart',
            line=dict(color='#FF33CC', width=2)
        ),
        row=row, col=column
    )
    # Bollinger Band shaded area
    if show_bb:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Upper Band'],
            name='Upper Band',
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
            row=row, col=column
        )

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Lower Band'],
            name='Lower Band',
            fill='tonexty',  # Fill the area between Upper and Lower bands
            fillcolor='rgba(173, 216, 230, 0.2)',  # Light sky blue with 20% opacity
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
            row=row, col=column
        )

        # Simple Moving Average (SMA)
        if show_sma:
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['SMA'],
                name='20-Day SMA',
                line=dict(color='orange', width=1.5)),
                row=row, col=column
            )

    # Moving Averages (MA10, MA20, MA50)
    if show_ma10:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA10'],
            name='MA10',
            line=dict(color='RoyalBlue', width=1.5)),
            row=row, col=column
        )
    if show_ma20:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA20'],
            name='MA20',
            line=dict(color='orange', width=1.5)),
            row=row, col=column
        )
    if show_ma50:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA50'],
            name='MA50',
            line=dict(color='grey', width=1.5)),
            row=row, col=column
        )
    return fig

# OHLC Chart
def plot_ohlc_chart_with_indicators(fig, df, row, column=1, show_bb=True, show_sma=True, show_ma10=True,
                                     show_ma20=True, show_ma50=True):
    fig.add_trace(
        go.Ohlc(
            x=df['Date'],
            open=df['Price Open'],
            high=df['Price High'],
            low=df['Price Low'],
            close=df['Price Close'],
            name='OHLC',
            line=dict(width=1),
            increasing=dict(line=dict(color='#00CC96')),  # Green for increasing
            decreasing=dict(line=dict(color='#EF553B')),  # Red for decreasing
        ),
        row=row, col=column
    )

    # Bollinger Band shaded area
    if show_bb:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Upper Band'],
            name='Upper Band',
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
            row=row, col=column
        )

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Lower Band'],
            name='Lower Band',
            fill='tonexty',  # Fill the area between Upper and Lower bands
            fillcolor='rgba(173, 216, 230, 0.2)',  # Light sky blue with 20% opacity
            line=dict(color='RoyalBlue', width=1.5),
            mode='lines',
            showlegend=False),
            row=row, col=column
        )

        # Simple Moving Average (SMA)
        if show_sma:
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['SMA'],
                name='20-Day SMA',
                line=dict(color='orange', width=1.5)),
                row=row, col=column
            )

    # Moving Averages (MA10, MA20, MA50)
    if show_ma10:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA10'],
            name='MA10',
            line=dict(color='RoyalBlue', width=1.5)),
            row=row, col=column
        )
    if show_ma20:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA20'],
            name='MA20',
            line=dict(color='orange', width=1.5)),
            row=row, col=column
        )
    if show_ma50:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA50'],
            name='MA50',
            line=dict(color='grey', width=1.5)),
            row=row, col=column
        )
    return fig
#--------------------------------------------------------------------------------

def plot_MACD(fig, df, row, column=1):
    df['Hist-Color'] = np.where(df['Histogram'] < 0, 'red', 'green')
    fig.add_trace(go.Bar(x=df['Date'], y=df['Histogram'], name='Histogram', marker_color=df['Hist-Color']),
                  row=row, col=column)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], name='MACD', line=dict(color='RoyalBlue', width=2)),
                  row=row, col=column)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Signal'], name='Signal', line=dict(color='darkorange', width=2)),
                  row=row, col=column)
    return fig

def plot_RSI(fig, df, row, column=1):
    # Thêm RSI vào biểu đồ
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['RSI'],
            name='RSI',
            line=dict(color='#673AB7', width=2)
        ),
        row=row,
        col=column
    )
    # Tô màu vùng giữa 30 và 70
    fig.add_shape(
        type='rect',
        x0=df['Date'].iloc[0],
        x1=df['Date'].iloc[-1],
        y0=30,
        y1=70,
        fillcolor='#673AB7',
        opacity=0.05,  # Độ trong suốt
        line=dict(color='#673AB7', width=0),
        row=row,
        col=column
    )
    # Vẽ các đường Overbought (70) và Oversold (30) với chú thích
    for y_pos, color, label in zip([70, 30], ['red', 'green'], ['Overbought (70)', 'Oversold (30)']):
        fig.add_shape(
            type='line',
            x0=df['Date'].iloc[0],
            x1=df['Date'].iloc[-1],
            y0=y_pos,
            y1=y_pos,
            line=dict(
                color=color,
                width=2,
                dash='dash'  # Kiểu nét đứt
            ),
            row=row,
            col=column
        )
        # Thêm chú thích vào các đường
        fig.add_trace(
            go.Scatter(
                x=[df['Date'].iloc[-1]],
                y=[y_pos],
                mode="text",
                text=[label],
                textposition="middle right",
                showlegend=False
            ),
            row=row,
            col=column
        )
    return fig

def plot_MFI(fig, df, row, column=1):
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MFI'], name='MFI', line=dict(color='#673AB7', width=2)),
                  row=row, col=column)
    # Tô màu vùng giữa 20 và 80
    fig.add_shape(
        type='rect',
        x0=df['Date'].iloc[0],
        x1=df['Date'].iloc[-1],
        y0=20,
        y1=80,
        fillcolor='#673AB7',
        opacity=0.05,  # Độ trong suốt
        line=dict(color='#673AB7', width=0),
        row=row,
        col=column
    )
    for y_pos, color, label in zip([80, 20], ['red', 'green'], ['Overbought (80)', 'Oversold (20)']):
        fig.add_shape(
            type='line',
            x0=df['Date'].iloc[0],
            x1=df['Date'].iloc[-1],
            y0=y_pos,
            y1=y_pos,
            line=dict(
                color=color,
                width=2,
                dash='dash'  # Kiểu nét đứt
            ),
            row=row,
            col=column
        )
        # Thêm chú thích vào các đường
        fig.add_trace(
            go.Scatter(
                x=[df['Date'].iloc[-1]],
                y=[y_pos],
                mode="text",
                text=[label],
                textposition="middle right",
                showlegend=False
            ),
            row=row,
            col=column
        )
    return fig

def plot_volume(fig, df, row, column=1):
    # Tạo cột màu dựa trên giá đóng cửa và giá mở cửa
    df['Volume Color'] = df.apply(lambda x: 'red' if x['Price Close'] < x['Price Open'] else 'green', axis=1)
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker=dict(color=df['Volume Color']),  # Gắn màu cho các cột
        ),
        row=row,
        col=column
    )
    return fig
####################################################################################################################
# Apply Trading Strategy
def apply_trading_strategy(df, strategy, column='Price Close', risk=0.025):
    """Return the Buy/Sell signals based on the selected strategy."""
    buy_list, sell_list = [], []
    flag = False

    # Chiến lược MACD
    if strategy == "MACD":
        for i in range(1, len(df)):  # Bắt đầu từ i=1 để tránh lỗi khi truy cập df[i-1]
            # Điều kiện 1: MACD cắt Signal Line
            if df['MACD'].iloc[i] > df['Signal'].iloc[i] and not flag:
                buy_list.append(df[column].iloc[i])  # Tín hiệu Mua
                sell_list.append(np.nan)
                flag = True
            elif df['MACD'].iloc[i] < df['Signal'].iloc[i] and flag:
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])  # Tín hiệu Bán
                flag = False

            # Điều kiện 2: MACD cắt đường 0
            elif df['MACD'].iloc[i] > 0 and df['MACD'].iloc[i - 1] < 0:  # MACD cắt lên trên 0
                buy_list.append(df[column].iloc[i])  # Tín hiệu Mua
                sell_list.append(np.nan)
            elif df['MACD'].iloc[i] < 0 and df['MACD'].iloc[i - 1] > 0:  # MACD cắt xuống dưới 0
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])  # Tín hiệu Bán
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)

    # Chiến lược RSI
    elif strategy == "RSI":
        for i in range(len(df)):
            if df['RSI'].iloc[i] < 30 and not flag:  # RSI quá bán (oversold)
                buy_list.append(df[column].iloc[i])
                sell_list.append(np.nan)
                flag = True
            elif df['RSI'].iloc[i] > 70 and flag:  # RSI quá mua (overbought)
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])
                flag = False
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)

    # Chiến lược Bollinger Bands
    elif strategy == "BB":
        for i in range(len(df)):
            if df[column].iloc[i] < df['Lower Band'].iloc[i] and not flag:  # Giá dưới dải dưới
                buy_list.append(df[column].iloc[i])
                sell_list.append(np.nan)
                flag = True
            elif df[column].iloc[i] > df['Upper Band'].iloc[i] and flag:  # Giá trên dải trên
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])
                flag = False
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)

    # Chiến lược MFI
    elif strategy == "MFI":
        for i in range(len(df)):
            if df['MFI'].iloc[i] > 20 and df['MFI'].shift(1).iloc[
                i] <= 20 and not flag:  # Buy signal: MFI crosses above 20
                buy_list.append(df[column].iloc[i])  # Record buy price
                sell_list.append(np.nan)
                flag = True  # Open buy position
            elif df['MFI'].iloc[i] < 80 and df['MFI'].shift(1).iloc[
                i] >= 80 and flag:  # Sell signal: MFI crosses below 80
                buy_list.append(np.nan)
                sell_list.append(df[column].iloc[i])  # Record sell price
                flag = False  # Close buy position
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)

    # Chiến lược MA
    elif strategy == "SMA":
        for i in range(len(df)):
            # Kiểm tra điều kiện cắt lên (Golden Cross)
            if df['MA20'].iloc[i] > df['MA50'].iloc[i] and df['MA20'].iloc[i - 1] <= df['MA50'].iloc[i - 1]:
                buy_list.append(df[column].iloc[i])  # Điểm mua
                sell_list.append(np.nan)  # Không có điểm bán
                flag = True
            # Kiểm tra điều kiện cắt xuống (Death Cross)
            elif df['MA20'].iloc[i] < df['MA50'].iloc[i] and df['MA20'].iloc[i - 1] >= df['MA50'].iloc[i - 1]:
                buy_list.append(np.nan)  # Không có điểm mua
                sell_list.append(df[column].iloc[i])  # Điểm bán
                flag = False
            else:
                # Nếu không có điểm cắt, giữ nguyên
                buy_list.append(np.nan)
                sell_list.append(np.nan)

    # Add the buy/sell lists to the dataframe
    # Đảm bảo độ dài buy_list và sell_list khớp với số dòng của DataFrame
    if len(buy_list) < len(df):
        buy_list.extend([np.nan] * (len(df) - len(buy_list)))
    if len(sell_list) < len(df):
        sell_list.extend([np.nan] * (len(df) - len(sell_list)))

    df['Buy'] = buy_list
    df['Sell'] = sell_list
    return df

def plot_buy_sell_points(fig, df, row, column=1):
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Buy'],
        mode='markers',
        name='Buy Signal',
        marker=dict(color='green', size=10, symbol='triangle-up')),
        row=row, col=column
    )
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Sell'],
        mode='markers',
        name='Sell Signal',
        marker=dict(color='red', size=10, symbol='triangle-down')),
        row=row, col=column
    )
    return fig

##################################################################################################################
# Streamlit interface setup
# Main Header with custom styling
st.markdown(
    """
    <h1 style='text-align: left; color: #1E90FF;'> 📈 FINLAND STOCK TRADING DASHBOARD </h1>
    <p style='text-align: left; color: #666666;'>Analyze stock trading strategies using technical indicators</p>
    """,
    unsafe_allow_html=True,
)

# Sidebar Setup
st.sidebar.header("Settings")
st.sidebar.subheader("Query Parameters")


# Add dynamic and visually engaging content (e.g., stock images, charts)
st.markdown(
    """
    <h4 style='color: #28a745;'>Welcome to the Interactive Stock Trading Dashboard!</h4>
    """,
    unsafe_allow_html=True,
)

# Footer with custom styling
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: left; color: gray; font-size: 14px;'>Developed by Group 5 </p>
    """,
    unsafe_allow_html=True,
)
####################################################################################################################
warnings.filterwarnings('ignore')

# Load the data
url = 'https://drive.google.com/file/d/1xWKphY-ZQegCqWpEO9BC25uPfRIzq7al/view?usp=sharing'
url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
data = df = pd.read_csv(url)
data['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

tickers = data['Ticker'].unique()

ticker = st.sidebar.selectbox("Select Ticker:", options=tickers)
ticker_data = data[data["Ticker"] == ticker]

# Calculate start_date and end_date based on the selected ticker
start_date = ticker_data["Date"].min().date()
end_date = ticker_data["Date"].max().date()

start_date = st.sidebar.date_input("Start Date:", start_date, min_value=start_date, max_value=end_date)
end_date = st.sidebar.date_input("End Date:", end_date, min_value=start_date, max_value=end_date)

filtered_data = data[(data["Ticker"] == ticker) & (data["Date"] >= pd.Timestamp(start_date)) & (
            data["Date"] <= pd.Timestamp(end_date))]

if filtered_data.empty:
    st.error("No data available for the selected parameters.")

else:
    # Display filtered data
    st.markdown(f"## {ticker} - Price Data")
    st.dataframe(filtered_data)


    # Sidebar for selecting Chart to display
    st.sidebar.header("Chart Options")
    chart_type = st.sidebar.selectbox(
        "Select Chart Type",
        ["Candlestick", "Line Chart", "OHLC Chart"]
    )

    # Calculate technical indicators
    filtered_data = get_MACD(filtered_data)
    filtered_data = get_RSI(filtered_data)
    filtered_data = get_bollinger_bands(filtered_data)
    filtered_data = get_MFI(filtered_data)
    filtered_data = get_MA(filtered_data)  # Add this line to calculate MA10, MA20, MA50

    # Sidebar for selecting indicators to display
    show_bb = st.sidebar.checkbox("Show BB", value=True)
    show_macd = st.sidebar.checkbox("Show MACD", value=True)
    show_rsi = st.sidebar.checkbox("Show RSI", value=True)
    show_mfi = st.sidebar.checkbox("Show MFI", value=True)
        # Sidebar for moving averages
    show_ma10 = st.sidebar.checkbox("Show MA10", value=True)
    show_ma20 = st.sidebar.checkbox("Show MA20", value=True)
    show_ma50 = st.sidebar.checkbox("Show MA50", value=True)


    # Sidebar for selecting Buy/Sell strategy
    st.sidebar.header("Trading Strategy Options")
    buy_sell_strategy = st.sidebar.selectbox(
        "Select Buy/Sell Strategy",
        options=["None", "SMA", "MACD", "RSI", "MFI", "BB"])

    if buy_sell_strategy != "None":
        filtered_data = apply_trading_strategy(filtered_data, buy_sell_strategy)

    # Create subplots for charts
    if chart_type == "Candlestick":
        fig = make_subplots(
            rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.1,
            subplot_titles=("Candlestick Chart with Bollinger Bands" if show_bb else "Candlestick Chart",
                            "Volume",
                            "MACD" if show_macd else "",
                            "RSI" if show_rsi else "",
                            "MFI" if show_mfi else "",
                            ),
            row_width=[0.2, 0.2, 0.2, 0.2, 0.6],
        )

        fig = plot_candlestick_with_indicators(
            fig, filtered_data, row=1,
            show_bb=show_bb,
            show_ma10=show_ma10,
            show_ma20=show_ma20,
            show_ma50=show_ma50
        )

        # Other plots for MACD, RSI, etc.
        fig = plot_volume(fig, filtered_data, row=2)

        if show_macd:
            fig = plot_MACD(fig, filtered_data, row=3)
        if show_rsi:
            fig = plot_RSI(fig, filtered_data, row=4)
        if show_mfi:
            fig = plot_MFI(fig, filtered_data, row=5)

        if buy_sell_strategy != "None":
            fig = plot_buy_sell_points(fig, filtered_data, row=1)
#---------------------------------------------------------------------------
    elif chart_type == "Line Chart":
        fig = make_subplots(
            rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.1,
            subplot_titles=("Line Chart with Bollinger Bands" if show_bb else "Line Chart",
                            "Volume",
                            "MACD" if show_macd else "",
                            "RSI" if show_rsi else "",
                            "MFI" if show_mfi else "",
                            ),
            row_width=[0.2, 0.2, 0.2, 0.2, 0.6],
        )

        fig = plot_line_chart_with_indicators(
            fig, filtered_data, row=1,
            show_bb=show_bb,
            show_ma10=show_ma10,
            show_ma20=show_ma20,
            show_ma50=show_ma50
        )

        # Other plots for MACD, RSI, etc.
        fig = plot_volume(fig, filtered_data, row=2)

        if show_macd:
            fig = plot_MACD(fig, filtered_data, row=3)
        if show_rsi:
            fig = plot_RSI(fig, filtered_data, row=4)
        if show_mfi:
            fig = plot_MFI(fig, filtered_data, row=5)

        if buy_sell_strategy != "None":
            fig = plot_buy_sell_points(fig, filtered_data, row=1)

#---------------------------------------------------------------------------
    elif chart_type == "OHLC Chart":
        fig = make_subplots(
            rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.1,
            subplot_titles=("OHLC Chart with Bollinger Bands" if show_bb else "OHLC Chart",
                            "Volume",
                            "MACD" if show_macd else "",
                            "RSI" if show_rsi else "",
                            "MFI" if show_mfi else "",
                            ),
            row_width=[0.2, 0.2, 0.2, 0.2, 0.6],
        )

        fig = plot_ohlc_chart_with_indicators(
            fig, filtered_data, row=1,
            show_bb=show_bb,
            show_ma10=show_ma10,
            show_ma20=show_ma20,
            show_ma50=show_ma50
        )

        # Other plots for MACD, RSI, etc.
        fig = plot_volume(fig, filtered_data, row=2)

        if show_macd:
            fig = plot_MACD(fig, filtered_data, row=3)
        if show_rsi:
            fig = plot_RSI(fig, filtered_data, row=4)
        if show_mfi:
            fig = plot_MFI(fig, filtered_data, row=5)

        if buy_sell_strategy != "None":
            fig = plot_buy_sell_points(fig, filtered_data, row=1)

#-----------------------------------------------------------------------------------------
    fig.update_layout(height=1000, width=1000, title=f"{ticker} - Interactive Dashboard", xaxis_rangeslider_visible=False,
        template="plotly_dark",
        xaxis=dict(
            showgrid=False,  # To hide gridlines
            showticklabels=True,  # Show date labels
            tickformat="%Y-%m-%d",  # Format the date
            tickangle=0  # Rotate the labels if needed
        ),
        xaxis2=dict(
            showgrid=False,
            showticklabels=True,
            tickformat="%Y-%m-%d",
            tickangle=0
        ),
        xaxis3=dict(
            showgrid=False,
            showticklabels=True,
            tickformat="%Y-%m-%d",
            tickangle=0
        ),
        xaxis4=dict(
            showgrid=False,
            showticklabels=True,
            tickformat="%Y-%m-%d",
            tickangle=0
        ),
        xaxis5=dict(
            showgrid=False,
            showticklabels=True,
            tickformat="%Y-%m-%d",
            tickangle=0
        )
    )
    st.plotly_chart(fig)

    st.write(
        "**Disclaimer:** This dashboard is for educational purposes only and does not constitute financial advice.")
