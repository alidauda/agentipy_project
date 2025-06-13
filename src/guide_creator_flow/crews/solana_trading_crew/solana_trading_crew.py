from crewai import Agent, Crew, Process, Task,LLM
from crewai.project import CrewBase, agent, crew, task
from agentipy.agent import SolanaAgentKit
from solders.pubkey import Pubkey
from .tools import SolanaTools
import asyncio
from datetime import datetime



agent = SolanaAgentKit(
            private_key="",
            rpc_url="https://api.mainnet-beta.solana.com"
        )


@CrewBase
class SolanaTradingCrew:
    """Solana Market Analysis Crew for analyzing and reporting on Solana markets"""

    # YAML configuration files
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

   
    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[
                self.tools.get_token_price_data,
                self.tools.get_trending_tokens
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
                self.tools.get_token_price_data,
                self.tools.get_trending_tokens
            ],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
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
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )

     