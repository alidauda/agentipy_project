from agentipy.agent import SolanaAgentKit
from agentipy.tools.use_coingecko import CoingeckoManager
from crewai.tools import BaseTool
import asyncio
from solders.pubkey import Pubkey

# Constants
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

class TrendingCryptoTokens(BaseTool):
    name: str = "Trending Crypto Tokens"
    description: str = (
        "Get list of trending cryptocurrency tokens across different blockchains"
        "This tool provides a list of the most trending tokens based on their market cap and trading volume"
    )
    agent: SolanaAgentKit

    def _run(self) -> str:
        """Get list of trending tokens"""
        try:
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            trending_data = loop.run_until_complete(CoingeckoManager.get_trending_tokens(self.agent))
            
            if trending_data and 'coins' in trending_data:
                tokens = []
                for i, token_item in enumerate(trending_data['coins']):
                    token = token_item['item']
                    symbol = token.get('symbol', '').upper()
                    name = token.get('name', '')

                    solana_address = None
                    metrics = {}
                    status_message = "Not processed."

                    # Handle Solana native token
                    if symbol == 'SOL':
                        solana_address = str(SOL_MINT)
                        status_message = "Native Solana token."
                    else:
                        try:
                            # Try to get token data
                            token_data = loop.run_until_complete(
                                CoingeckoManager.get_token_price_data(self.agent, [symbol])
                            )
                            if token_data and symbol in token_data:
                                solana_address = symbol
                                metrics = token_data[symbol]
                                status_message = "Token data found."
                        except Exception as e:
                            status_message = f"Error fetching data: {str(e)}"

                    # Format token information
                    token_info = f"{i+1}. {name} ({symbol})\n"
                    token_info += f"Status: {status_message}\n"
                    
                    if metrics:
                        token_info += f"Price: ${metrics.get('usd', 0.0):.6f}\n"
                        token_info += f"24h Change: {metrics.get('usd_24h_change', 0.0):.2f}%\n"
                        token_info += f"Market Cap: ${metrics.get('usd_market_cap', 0.0):,.2f}\n"
                        token_info += f"24h Volume: ${metrics.get('usd_24h_vol', 0.0):,.2f}\n"
                    
                    tokens.append(token_info)
                    loop.run_until_complete(asyncio.sleep(0.5))  # Rate limiting

                loop.close()
                return "Top Trending Tokens:\n" + "\n".join(tokens)
            return "No trending tokens found"
        except Exception as e:
            return f"Error getting trending tokens: {str(e)}"


