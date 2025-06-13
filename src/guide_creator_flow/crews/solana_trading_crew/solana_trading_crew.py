from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from agentipy.agent import SolanaAgentKit
from crewai_tools import SerperDevTool
import os 
from dotenv import load_dotenv

# Import the enhanced tools
from .tools import (
    EnhancedTrendingCryptoTokens, 
    MarketCorrelationTool, 
    NewsImpactTool
)

load_dotenv()

# Initialize Solana agent kit
solana_agent = SolanaAgentKit(
    private_key=os.getenv("SOLANA_PRIVATE_KEY"),
    rpc_url="https://api.mainnet-beta.solana.com"
)

# Enhanced tools initialization
enhanced_trending_tool = EnhancedTrendingCryptoTokens(agent=solana_agent)
correlation_tool = MarketCorrelationTool(agent=solana_agent)
news_impact_tool = NewsImpactTool()

# Enhanced Serper tool with crypto-specific search parameters
serper_tool = SerperDevTool(
    search_params={
        "tbs": "qdr:d",  # Last day for most recent news
        "sort": "date",   # Sort by date
        "num": 10,        # More results for comprehensive analysis
        "q": "(cryptocurrency OR crypto OR bitcoin OR ethereum OR DeFi OR blockchain) AND (analysis OR price OR market OR trading OR investment)"
    }
)

@CrewBase
class EnhancedCryptoTradingCrew:
    """Enhanced Cryptocurrency Market Analysis Crew for institutional-grade analysis"""

    # Configuration files (use the enhanced versions we created)
    agents_config = 'config/agents.yaml'  # Use enhanced config
    tasks_config = 'config/tasks.yaml'    # Use enhanced config

    def __init__(self):
        # Initialize LLM with higher temperature for more creative analysis
        self.llm = LLM(
            model="openai/gpt-4o",
            temperature=0.3,  # Balanced creativity and accuracy
            max_tokens=4000   # Allow for more comprehensive responses
        )
        
    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[enhanced_trending_tool, correlation_tool, news_impact_tool, serper_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False,
            max_iter=3,  # Allow multiple iterations for thorough research
            memory=True
        )

    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_analyst'],
            tools=[enhanced_trending_tool, correlation_tool, serper_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False,
            max_iter=3,
            memory=True
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            tools=[enhanced_trending_tool, correlation_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False,
            max_iter=2,
            memory=True
        )

    @agent
    def risk_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_manager'],
            tools=[enhanced_trending_tool, correlation_tool, serper_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False,
            max_iter=2,
            memory=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.market_researcher(),
            output_file="research.md"  # Shorter filename
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.market_analyst(),
            output_file="analysis.md"  # Shorter filename
        )

    @task
    def risk_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_task'],
            agent=self.risk_manager(),
            output_file="risk.md"  # Shorter filename
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_task'],
            agent=self.report_writer(),
            output_file="report.md",  # Shorter filename
            context=[
                self.research_task(),
                self.analysis_task(),
                self.risk_task()
            ]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Enhanced Cryptocurrency Market Analysis Crew"""
        return Crew(
            agents=[
                self.market_researcher(), 
                self.market_analyst(), 
                self.risk_manager(),
                self.report_writer()
            ],
            tasks=[
                self.research_task(),
                self.analysis_task(), 
                self.risk_task(),
                self.report_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True,  # Enable planning for better coordination
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )

  
    def cleanup(self):
        """Cleanup resources after crew execution"""
        try:
            # Cleanup any resources if needed
            pass
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")


# Additional utility functions for enhanced analysis
    """Utility functions for cryptocurrency analysis"""
    
    @staticmethod
    def calculate_portfolio_metrics(tokens_data: dict) -> dict:
        """Calculate portfolio-level metrics"""
        total_market_cap = sum(data.get('usd_market_cap', 0) for data in tokens_data.values())
        total_volume = sum(data.get('usd_24h_vol', 0) for data in tokens_data.values())
        
        return {
            'total_market_cap': total_market_cap,
            'total_volume': total_volume,
            'avg_volume_ratio': (total_volume / total_market_cap * 100) if total_market_cap > 0 else 0,
            'token_count': len(tokens_data)
        }
    
    @staticmethod
    def generate_risk_score(market_cap: float, volume_ratio: float, price_change: float) -> tuple:
        """Generate a risk score and category for a token"""
        risk_score = 0
        
        # Market cap risk (lower market cap = higher risk)
        if market_cap < 100_000_000:  # < 100M
            risk_score += 3
        elif market_cap < 1_000_000_000:  # < 1B
            risk_score += 2
        elif market_cap < 10_000_000_000:  # < 10B
            risk_score += 1
            
        # Volatility risk (high volume ratio = higher volatility)
        if volume_ratio > 20:
            risk_score += 3
        elif volume_ratio > 10:
            risk_score += 2
        elif volume_ratio > 5:
            risk_score += 1
            
        # Price movement risk
        if abs(price_change) > 20:
            risk_score += 2
        elif abs(price_change) > 10:
            risk_score += 1
            
        # Determine risk category
        if risk_score >= 7:
            risk_category = "VERY HIGH"
        elif risk_score >= 5:
            risk_category = "HIGH"
        elif risk_score >= 3:
            risk_category = "MEDIUM"
        else:
            risk_category = "LOW"
            
        return risk_score, risk_category
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency amounts with appropriate suffixes"""
        if amount >= 1_000_000_000:
            return f"${amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"${amount/1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.2f}K"
        else:
            return f"${amount:.2f}"