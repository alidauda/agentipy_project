from crewai.tools import tool
from agentipy.agent import SolanaAgentKit
from agentipy.tools.get_balance import BalanceFetcher
from agentipy.tools.use_coingecko import CoingeckoManager
from solders.pubkey import Pubkey
import asyncio

class SolanaTools:
    def __init__(self, agent: SolanaAgentKit):
        self.agent = agent

    @tool
    async def check_balance(self) -> str:
        """Check the current SOL balance of the wallet"""
        try:
            balance = await BalanceFetcher.get_balance(self.agent)
            return f"Current SOL Balance: {balance:.4f} SOL"
        except Exception as e:
            return f"Error checking balance: {str(e)}"

    @tool
    async def get_token_price_data(self, token_address: str) -> str:
        """Get price data for a specific token"""
        try:
            price_data = await CoingeckoManager.get_token_price_data(self.agent, [token_address])
            if token_address in price_data:
                token_info = price_data[token_address]
                return f"""
                Token Price Data:
                - Current Price: ${token_info.get('usd', 0.0):.8f}
                - 24h Change: {token_info.get('usd_24h_change', 0.0):.2f}%
                - Market Cap: ${token_info.get('usd_market_cap', 0.0):,.2f}
                - 24h Volume: ${token_info.get('usd_24h_vol', 0.0):,.2f}
                """
            return "No price data available for this token"
        except Exception as e:
            return f"Error getting price data: {str(e)}"

    @tool
    async def get_trending_tokens(self) -> str:
        """Get list of trending tokens on Solana"""
        try:
            trending_data = await CoingeckoManager.get_trending_tokens(self.agent)
            if trending_data and 'coins' in trending_data:
                tokens = []
                for token in trending_data['coins'][:5]:  # Get top 5 trending
                    item = token['item']
                    tokens.append(f"- {item.get('name', 'Unknown')} ({item.get('symbol', 'Unknown').upper()})")
                return "Top Trending Tokens:\n" + "\n".join(tokens)
            return "No trending tokens found"
        except Exception as e:
            return f"Error getting trending tokens: {str(e)}" 