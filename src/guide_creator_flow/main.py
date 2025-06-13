#!/usr/bin/env python
import json
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from crewai.flow.flow import Flow, listen, start
from guide_creator_flow.crews.solana_trading_crew.solana_trading_crew import SolanaTradingCrew
from datetime import datetime

# Define our flow state
class SolanaTradingState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    target_token: str = ""
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    action: str = ""  # Store user's chosen action
    trading_crew: Optional[SolanaTradingCrew] = None

class SolanaTradingFlow(Flow[SolanaTradingState]):
    """Flow for analyzing Solana markets and generating reports"""

    @start()
    def get_user_input(self):
        """Get input from the user about the trading operation"""
        print("\n=== Solana Trading Analysis ===\n")

        # Get RPC URL (optional)
        rpc_url = input("Enter Solana RPC URL (press Enter for default): ").strip()
        if rpc_url:
            self.state.rpc_url = rpc_url

        # Get action type
        while True:
            print("\nWhat would you like to do?")
            print("1. Generate general market analysis")
            print("2. Analyze specific token")
            print("3. Analyze trending tokens")
            choice = input("Enter your choice (1-3): ")

            if choice == "1":
                self.state.action = "general"
                break
            elif choice == "2":
                self.state.action = "specific"
                self.state.target_token = input("Enter the token address to analyze: ")
                break
            elif choice == "3":
                self.state.action = "trending"
                break
            else:
                print("Invalid choice. Please try again.")

        print(f"\nInitializing Solana trading analysis...\n")
        return self.state

    @listen(get_user_input)
    async def execute_action(self, state):
        """Execute the user's chosen action"""
        try:
            # Initialize trading crew
            self.state.trading_crew = SolanaTradingCrew(
                rpc_url=state.rpc_url
            )
            
            if state.action == "general":
                print("\nGenerating general market analysis report...")
                result = await self.state.trading_crew.crew().kickoff(
                    inputs={
                        'target_token': None,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
                )
                # Save report to file
                filename = f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(filename, "w") as f:
                    f.write(result)
                print(f"\nReport saved to {filename}")
                return result
            elif state.action == "specific":
                print(f"\nAnalyzing token {state.target_token}...")
                result = await self.state.trading_crew.crew().kickoff(
                    inputs={
                        'target_token': state.target_token,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
                )
                # Save report to file
                filename = f"token_analysis_{state.target_token}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(filename, "w") as f:
                    f.write(result)
                print(f"\nReport saved to {filename}")
                return result
            elif state.action == "trending":
                print("\nAnalyzing trending tokens...")
                result = await self.state.trading_crew.crew().kickoff(
                    inputs={
                        'target_token': None,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
                )
                # Save report to file
                filename = f"trending_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(filename, "w") as f:
                    f.write(result)
                print(f"\nReport saved to {filename}")
                return result
            else:
                print("Invalid action selected.")
                return None
        except Exception as e:
            print(f"Error executing action: {e}")
            return None

def kickoff():
    """Run the Solana trading flow"""
    SolanaTradingFlow().kickoff()
    print("\n=== Flow Complete ===")
    print("Your Solana market analysis reports are ready in the current directory.")

def plot():
    """Generate a visualization of the flow"""
    flow = SolanaTradingFlow()
    flow.plot("solana_trading_flow")
    print("Flow visualization saved to solana_trading_flow.html")

if __name__ == "__main__":
    kickoff()