from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from agentipy.agent import SolanaAgentKit
from .tools import TrendingCryptoTokens
from crewai_tools import SerperDevTool
import os 
from dotenv import load_dotenv

load_dotenv()

# Initialize Solana agent kit
solana_agent = SolanaAgentKit(
    private_key=os.getenv("SOLANA_PRIVATE_KEY"),
    rpc_url="https://api.mainnet-beta.solana.com"
)

trending_tokens_tool = TrendingCryptoTokens(agent=solana_agent)
serper_tool = SerperDevTool(
    search_params={
        "tbs": "qdr:m",  # Last month
        "sort": "date",   # Sort by date
        "q": "(site:coingecko.com OR site:coinmarketcap.com OR site:decrypt.co OR site:coindesk.com OR site:theblock.co) OR (cryptocurrency news OR crypto analysis)"  # Prioritize crypto sites but allow broader search
    }
)

@CrewBase
class CryptoTradingCrew:
    """Cryptocurrency Market Analysis Crew for analyzing and reporting on crypto markets"""

    # YAML configuration files
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Initialize LLM
        self.llm = LLM(model="openai/gpt-4o")  # or your preferred model
        
    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[trending_tokens_tool, serper_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_analyst'],
            tools=[trending_tokens_tool, serper_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            tools=[trending_tokens_tool],
            llm=self.llm,
            verbose=True,
            allow_code_execution=False
        )

    @task
    def research_market_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_market_task'],
            agent=self.market_researcher()
        )

    @task
    def analyze_market_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_market_task'],
            agent=self.market_analyst()
        )

    @task
    def write_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_report_task'],
            agent=self.report_writer()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Cryptocurrency Market Analysis Crew"""
        return Crew(
            agents=[self.market_researcher(), self.market_analyst(), self.report_writer()],
            tasks=[self.research_market_task(), self.analyze_market_task(), self.write_report_task()],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

    def cleanup(self):
        """Cleanup resources after crew execution"""
        try:
            # Cleanup any resources if needed
            pass
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")