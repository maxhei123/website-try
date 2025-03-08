import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import crypto_utils as cu
import technical_indicators as ti

# Page configuration
st.set_page_config(
    page_title="Crypto Analysis Tool",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def format_coin_name(coin_id):
    """Format coin ID to a more readable name"""
    return coin_id.replace('-', ' ').title()

def plot_with_indicators(df, indicators):
    fig = go.Figure()

    # Candlestick chart with hover info
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price",
        hoverinfo="all",
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Roboto"
        )
    ))

    # Add technical indicators based on selection
    if 'MA' in indicators:
        ma20 = ti.calculate_ma(df['close'], 20)
        ma50 = ti.calculate_ma(df['close'], 50)
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=ma20, 
            name="MA20", 
            line=dict(color='orange'),
            hovertemplate="MA20: $%{y:,.2f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=ma50, 
            name="MA50", 
            line=dict(color='blue'),
            hovertemplate="MA50: $%{y:,.2f}<extra></extra>"
        ))

    if 'EMA' in indicators:
        ema20 = ti.calculate_ema(df['close'], 20)
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=ema20, 
            name="EMA20", 
            line=dict(color='purple'),
            hovertemplate="EMA20: $%{y:,.2f}<extra></extra>"
        ))

    if 'Bollinger Bands' in indicators:
        upper, middle, lower = ti.calculate_bollinger_bands(df['close'])
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=upper, 
            name="Upper BB", 
            line=dict(color='gray', dash='dash'),
            hovertemplate="Upper BB: $%{y:,.2f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=lower, 
            name="Lower BB", 
            line=dict(color='gray', dash='dash'),
            hovertemplate="Lower BB: $%{y:,.2f}<extra></extra>"
        ))

    if 'Support/Resistance' in indicators:
        support, resistance = ti.identify_support_resistance(df)
        for level in support[:3]:  # Show top 3 levels
            fig.add_hline(
                y=level, 
                line_color="green", 
                line_dash="dash", 
                opacity=0.5,
                annotation_text=f"Support: ${level:,.2f}"
            )
        for level in resistance[:3]:
            fig.add_hline(
                y=level, 
                line_color="red", 
                line_dash="dash", 
                opacity=0.5,
                annotation_text=f"Resistance: ${level:,.2f}"
            )

    fig.update_layout(
        title="Price Analysis with Technical Indicators",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        height=600,
        hoverdistance=100,
        spikedistance=1000,
        xaxis=dict(
            showspikes=True,
            spikethickness=2,
            spikecolor="#999999",
            spikemode="across",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
        ),
        yaxis=dict(
            showspikes=True,
            spikethickness=2,
            spikecolor="#999999",
            spikemode="across",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            tickformat='$,.2f'
        )
    )

    return fig

def main():
    st.title("Advanced Cryptocurrency Analysis")

    # Sidebar
    st.sidebar.header("Analysis Settings")

    # Get available cryptocurrencies
    crypto_list = cu.get_available_cryptocurrencies()
    selected_crypto = st.sidebar.selectbox(
        "Select Cryptocurrency",
        options=crypto_list,
        format_func=format_coin_name,
        index=0
    )

    timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        ["24h", "7d", "30d", "90d", "1y"],
        index=2
    )

    # Technical Analysis Settings
    st.sidebar.header("Technical Indicators")
    indicators = st.sidebar.multiselect(
        "Select Indicators",
        ["MA", "EMA", "RSI", "MACD", "Bollinger Bands", "Support/Resistance"],
        default=["MA"]
    )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Get and display data
        df = cu.get_historical_data(selected_crypto, timeframe)
        if df is not None:
            # Main price chart with selected indicators
            fig = plot_with_indicators(df, indicators)
            st.plotly_chart(fig, use_container_width=True)

            # Additional indicators in separate charts
            if "RSI" in indicators:
                rsi = ti.calculate_rsi(df['close'])
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI"))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(title="RSI Indicator", height=200, template="plotly_dark")
                st.plotly_chart(fig_rsi, use_container_width=True)

            if "MACD" in indicators:
                macd, signal, hist = ti.calculate_macd(df['close'])
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=macd, name="MACD"))
                fig_macd.add_trace(go.Scatter(x=df.index, y=signal, name="Signal"))
                fig_macd.add_trace(go.Bar(x=df.index, y=hist, name="Histogram"))
                fig_macd.update_layout(title="MACD Indicator", height=200, template="plotly_dark")
                st.plotly_chart(fig_macd, use_container_width=True)

    with col2:
        # Market Analysis
        st.subheader("Market Analysis")
        market_data = cu.get_market_data(selected_crypto)
        if market_data:
            # Current price and 24h change
            col_price, col_change = st.columns(2)
            with col_price:
                st.metric("Current Price", f"${market_data['current_price']:,.2f}")
            with col_change:
                st.metric("24h Change", f"{market_data['price_change_percentage_24h']:.2f}%")

            # 24h High/Low
            col_high, col_low = st.columns(2)
            with col_high:
                st.metric("24h High", f"${market_data['high_24h']:,.2f}")
            with col_low:
                st.metric("24h Low", f"${market_data['low_24h']:,.2f}")

            # All-time High/Low
            col_ath, col_atl = st.columns(2)
            with col_ath:
                st.metric("All-Time High", f"${market_data['ath']:,.2f}")
            with col_atl:
                st.metric("All-Time Low", f"${market_data['atl']:,.2f}")

            # Market Cap and Volume
            st.metric("Market Cap", f"${market_data['market_cap']:,.0f}")
            st.metric("24h Volume", f"${market_data['total_volume']:,.0f}")

        # Technical Analysis Summary
        st.subheader("Technical Analysis Summary")
        if df is not None:
            latest_close = df['close'].iloc[-1]
            ma20 = ti.calculate_ma(df['close'], 20).iloc[-1]
            ma50 = ti.calculate_ma(df['close'], 50).iloc[-1]
            rsi = ti.calculate_rsi(df['close']).iloc[-1]

            # Trend Analysis
            trend = "Bullish" if ma20 > ma50 else "Bearish"
            st.write(f"Trend: {trend}")

            # RSI Analysis
            rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            st.write(f"RSI Signal: {rsi_signal}")

            # Support/Resistance
            support, resistance = ti.identify_support_resistance(df)
            st.write("Key Levels:")
            st.write(f"Support: ${support[0]:,.2f}")
            st.write(f"Resistance: ${resistance[0]:,.2f}")

        # Meme Coins Comparison
        st.subheader("Compare with Meme Coins")
        meme_coins = ["dogecoin", "shiba-inu", "pepe", "floki"]
        compare_with = st.multiselect(
            "Compare with other meme coins",
            [coin for coin in meme_coins if coin in crypto_list and coin != selected_crypto],
            default=[meme_coins[0]] if meme_coins[0] != selected_crypto and meme_coins[0] in crypto_list else None
        )

        if compare_with:
            comparison_data = cu.get_comparison_data([selected_crypto] + compare_with)
            if comparison_data is not None:
                fig_comp = go.Figure()
                for coin in comparison_data.columns:
                    fig_comp.add_trace(go.Scatter(
                        x=comparison_data.index,
                        y=comparison_data[coin],
                        name=format_coin_name(coin)
                    ))
                fig_comp.update_layout(
                    title="30-Day Price Comparison (Normalized)",
                    yaxis_title="Price Change (%)",
                    height=300,
                    template="plotly_dark"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

if __name__ == "__main__":
    main()
  
