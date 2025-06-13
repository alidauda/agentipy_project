from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from agentipy.agent import SolanaAgentKit
from solders.pubkey import Pubkey
from .tools import TrendingTokens, TokenPriceData
import asyncio
from datetime import datetime
import os 
from dotenv import load_dotenv
load_dotenv()

# Initialize Solana agent kit
agent = SolanaAgentKit(
    private_key=os.getenv("SOLANA_PRIVATE_KEY"),
    rpc_url="https://api.mainnet-beta.solana.com"
)

@CrewBase
class SolanaTradingCrew:
    """Solana Market Analysis Crew for analyzing and reporting on Solana markets"""

    # YAML configuration files
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Initialize tools with the Solana agent
        self.trending_tokens_tool = TrendingTokens(agent=agent)
        self.token_price_data_tool = TokenPriceData(agent=agent)

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[
                self.trending_tokens_tool,
                self.token_price_data_tool
            ],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_analyst'],
            tools=[
                self.trending_tokens_tool,
                self.token_price_data_tool
            ],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            tools=[
                self.trending_tokens_tool,
                self.token_price_data_tool
            ],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @task
    def research_market_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_market_task']
        )

    @task
    def analyze_market_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_market_task']
        )

    @task
    def write_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_report_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Solana Market Analysis Crew"""
        return Crew(
            agents=[self.market_researcher(), self.market_analyst(), self.report_writer()   ],  # Automatically created by the @agent decorator
            tasks=[self.research_market_task(), self.analyze_market_task(), self.write_report_task()],  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True
        )

     