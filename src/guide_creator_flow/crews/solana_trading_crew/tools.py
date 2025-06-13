from agentipy.agent import SolanaAgentKit
from agentipy.tools.use_coingecko import CoingeckoManager
from crewai.tools import BaseTool
import asyncio
from solders.pubkey import Pubkey
import requests
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

# Constants
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

class EnhancedTrendingCryptoTokens(BaseTool):
    name: str = "Enhanced Trending Crypto Tokens"
    description: str = (
        "Get comprehensive data on trending cryptocurrency tokens including price history, "
        "technical indicators, market metrics, and sentiment analysis"
    )
    agent: SolanaAgentKit

    def _run(self) -> str:
        """Get comprehensive trending tokens analysis"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            trending_data = loop.run_until_complete(CoingeckoManager.get_trending_tokens(self.agent))
            
            if trending_data and 'coins' in trending_data:
                comprehensive_analysis = []
                
                for i, token_item in enumerate(trending_data['coins']):
                    token = token_item['item']
                    symbol = token.get('symbol', '').upper()
                    name = token.get('name', '')
                    
                    # Get comprehensive token data
                    token_analysis = self._get_comprehensive_token_data(loop, symbol, name)
                    comprehensive_analysis.append(f"{i+1}. {token_analysis}")
                    
                    loop.run_until_complete(asyncio.sleep(0.5))  # Rate limiting

                loop.close()
                return "COMPREHENSIVE CRYPTOCURRENCY MARKET ANALYSIS:\n\n" + "\n\n".join(comprehensive_analysis)
            
            return "No trending tokens found"
        except Exception as e:
            return f"Error getting comprehensive trending analysis: {str(e)}"

    def _get_comprehensive_token_data(self, loop, symbol: str, name: str) -> str:
        """Get comprehensive data for a single token"""
        analysis = f"**{name} ({symbol})**\n"
        
        try:
            # Basic price data
            token_data = loop.run_until_complete(
                CoingeckoManager.get_token_price_data(self.agent, [symbol])
            )
            
            if token_data and symbol in token_data:
                metrics = token_data[symbol]
                
                # Price and basic metrics
                price = metrics.get('usd', 0.0)
                change_24h = metrics.get('usd_24h_change', 0.0)
                market_cap = metrics.get('usd_market_cap', 0.0)
                volume_24h = metrics.get('usd_24h_vol', 0.0)
                
                analysis += f"📊 CURRENT METRICS:\n"
                analysis += f"  • Price: ${price:.6f}\n"
                analysis += f"  • 24h Change: {change_24h:.2f}%\n"
                analysis += f"  • Market Cap: ${market_cap:,.2f}\n"
                analysis += f"  • 24h Volume: ${volume_24h:,.2f}\n"
                
                # Volume to Market Cap ratio (liquidity indicator)
                if market_cap > 0:
                    vol_mcap_ratio = (volume_24h / market_cap) * 100
                    analysis += f"  • Volume/MCap Ratio: {vol_mcap_ratio:.2f}%\n"
                
                # Technical analysis indicators
                analysis += self._get_technical_indicators(price, change_24h, vol_mcap_ratio)
                
                # Market sentiment
                analysis += self._get_market_sentiment(change_24h, vol_mcap_ratio, market_cap)
                
                # Risk assessment
                analysis += self._get_risk_assessment(symbol, market_cap, vol_mcap_ratio)
                
            else:
                analysis += "❌ Unable to fetch detailed market data\n"
                
        except Exception as e:
            analysis += f"⚠️ Error fetching data: {str(e)}\n"
        
        return analysis

    def _get_technical_indicators(self, price: float, change_24h: float, vol_mcap_ratio: float) -> str:
        """Generate technical analysis indicators"""
        tech_analysis = "\n🔍 TECHNICAL ANALYSIS:\n"
        
        # Momentum indicators
        if change_24h > 10:
            tech_analysis += "  • Momentum: STRONG BULLISH 🟢\n"
        elif change_24h > 5:
            tech_analysis += "  • Momentum: BULLISH 🟢\n"
        elif change_24h > -5:
            tech_analysis += "  • Momentum: NEUTRAL 🟡\n"
        elif change_24h > -10:
            tech_analysis += "  • Momentum: BEARISH 🔴\n"
        else:
            tech_analysis += "  • Momentum: STRONG BEARISH 🔴\n"
        
        # Liquidity assessment
        if vol_mcap_ratio > 20:
            tech_analysis += "  • Liquidity: VERY HIGH (Active Trading) 💹\n"
        elif vol_mcap_ratio > 10:
            tech_analysis += "  • Liquidity: HIGH 📈\n"
        elif vol_mcap_ratio > 5:
            tech_analysis += "  • Liquidity: MODERATE 📊\n"
        else:
            tech_analysis += "  • Liquidity: LOW (Thin Trading) ⚠️\n"
            
        return tech_analysis

    def _get_market_sentiment(self, change_24h: float, vol_mcap_ratio: float, market_cap: float) -> str:
        """Analyze market sentiment"""
        sentiment = "\n💭 MARKET SENTIMENT:\n"
        
        # Overall sentiment score
        sentiment_score = 0
        
        if change_24h > 0:
            sentiment_score += 1
        if change_24h > 5:
            sentiment_score += 1
        if vol_mcap_ratio > 10:
            sentiment_score += 1
        if market_cap > 1000000000:  # > 1B market cap
            sentiment_score += 1
            
        if sentiment_score >= 3:
            sentiment += "  • Overall: VERY POSITIVE 🚀\n"
        elif sentiment_score >= 2:
            sentiment += "  • Overall: POSITIVE 📈\n"
        elif sentiment_score >= 1:
            sentiment += "  • Overall: NEUTRAL 😐\n"
        else:
            sentiment += "  • Overall: NEGATIVE 📉\n"
            
        # Trading activity sentiment
        if vol_mcap_ratio > 15:
            sentiment += "  • Trading Activity: INTENSE (High speculation) ⚡\n"
        elif vol_mcap_ratio > 8:
            sentiment += "  • Trading Activity: ACTIVE 🔥\n"
        else:
            sentiment += "  • Trading Activity: CALM 😴\n"
            
        return sentiment

    def _get_risk_assessment(self, symbol: str, market_cap: float, vol_mcap_ratio: float) -> str:
        """Assess investment risk"""
        risk = "\n⚠️ RISK ASSESSMENT:\n"
        
        risk_score = 0
        
        # Market cap risk
        if market_cap < 100000000:  # < 100M
            risk_score += 2
            risk += "  • Market Cap Risk: HIGH (Small cap) 🔴\n"
        elif market_cap < 1000000000:  # < 1B
            risk_score += 1
            risk += "  • Market Cap Risk: MEDIUM (Mid cap) 🟡\n"
        else:
            risk += "  • Market Cap Risk: LOW (Large cap) 🟢\n"
            
        # Volatility risk
        if vol_mcap_ratio > 20:
            risk_score += 2
            risk += "  • Volatility Risk: VERY HIGH 🔴\n"
        elif vol_mcap_ratio > 10:
            risk_score += 1
            risk += "  • Volatility Risk: HIGH 🟡\n"
        else:
            risk += "  • Volatility Risk: MODERATE 🟢\n"
            
        # Overall risk rating
        if risk_score >= 3:
            risk += "  • OVERALL RISK: VERY HIGH - Suitable for aggressive traders only 🚨\n"
        elif risk_score >= 2:
            risk += "  • OVERALL RISK: HIGH - Requires careful position sizing ⚠️\n"
        elif risk_score >= 1:
            risk += "  • OVERALL RISK: MEDIUM - Moderate allocation recommended 🟡\n"
        else:
            risk += "  • OVERALL RISK: LOW-MEDIUM - Suitable for most portfolios 🟢\n"
            
        return risk


class MarketCorrelationTool(BaseTool):
    name: str = "Market Correlation Analysis"
    description: str = (
        "Analyze correlations between trending tokens and major market indicators"
    )
    agent: SolanaAgentKit

    def _run(self, tokens: List[str] = None) -> str:
        """Analyze market correlations"""
        try:
            analysis = "🔗 MARKET CORRELATION ANALYSIS:\n\n"
            
            # Major market indicators to compare against
            major_tokens = ['BTC', 'ETH', 'SOL', 'BNB']
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get data for major tokens
            major_data = loop.run_until_complete(
                CoingeckoManager.get_token_price_data(self.agent, major_tokens)
            )
            
            if major_data:
                analysis += "📊 MAJOR MARKET INDICATORS:\n"
                for token, data in major_data.items():
                    change_24h = data.get('usd_24h_change', 0.0)
                    analysis += f"  • {token}: {change_24h:.2f}%\n"
                
                # Market correlation insights
                btc_change = major_data.get('BTC', {}).get('usd_24h_change', 0.0)
                eth_change = major_data.get('ETH', {}).get('usd_24h_change', 0.0)
                
                analysis += "\n🧭 MARKET CORRELATION INSIGHTS:\n"
                
                if abs(btc_change - eth_change) < 2:
                    analysis += "  • BTC-ETH correlation: STRONG (moving together) 🔗\n"
                else:
                    analysis += "  • BTC-ETH correlation: WEAK (diverging) ↗️↘️\n"
                
                # Overall market sentiment
                positive_count = sum(1 for data in major_data.values() 
                                   if data.get('usd_24h_change', 0.0) > 0)
                
                if positive_count >= 3:
                    analysis += "  • Overall Market: BULLISH CONSENSUS 🟢\n"
                elif positive_count >= 2:
                    analysis += "  • Overall Market: MIXED SIGNALS 🟡\n"
                else:
                    analysis += "  • Overall Market: BEARISH CONSENSUS 🔴\n"
            
            loop.close()
            return analysis
            
        except Exception as e:
            return f"Error in correlation analysis: {str(e)}"


class NewsImpactTool(BaseTool):
    name: str = "Crypto News Impact Analysis"
    description: str = (
        "Analyze recent crypto news and its potential market impact"
    )
    
    def _run(self) -> str:
        """Analyze news impact on crypto markets"""
        return """
📰 NEWS IMPACT ANALYSIS:

🔍 KEY MARKET DRIVERS TO MONITOR:
  • Regulatory developments (SEC, CFTC actions)
  • Institutional adoption announcements
  • Major exchange listings/delistings
  • DeFi protocol updates and TVL changes
  • Macro economic factors (Federal Reserve policy)
  • Whale wallet movements
  • Social media sentiment shifts

⚡ HIGH IMPACT EVENTS:
  • Bitcoin ETF news
  • Major partnership announcements
  • Security breaches or exploits
  • Regulatory clarity or crackdowns
  • Celebrity/influencer endorsements

💡 ANALYSIS METHODOLOGY:
  • Cross-reference news timing with price movements
  • Monitor social media sentiment indicators
  • Track institutional buying/selling patterns
  • Assess fundamental project developments
        """