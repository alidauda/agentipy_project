#!/usr/bin/env python
import asyncio
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from crewai.flow.flow import Flow, listen, start
from guide_creator_flow.crews.solana_trading_crew.solana_trading_crew import SolanaTradingCrew

# Define our flow state
class SolanaTradingState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    private_key: str = ""
    target_token: str = ""
    amount: float = 0.0
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    trading_crew: Optional[SolanaTradingCrew] = None

class SolanaTradingFlow(Flow[SolanaTradingState]):
    """Flow for executing trades on Solana blockchain"""

    @start()
    def get_user_input(self):
        """Get input from the user about the trade details"""
        print("\n=== Solana Trading Flow ===\n")

        # Get private key
        while True:
            choice = input("Do you want to (1) Generate a new wallet or (2) Use an existing private key? (1/2): ").strip()
            if choice == "1":
                # TODO: Implement wallet generation
                print("Wallet generation not implemented yet")
                continue
            elif choice == "2":
                self.state.private_key = input("Enter your private key (Base58 encoded string): ").strip()
                if not self.state.private_key:
                    print("Private key cannot be empty. Please try again.")
                    continue
                break
            else:
                print("Invalid choice. Please enter '1' or '2'.")

        # Get target token
        self.state.target_token = input("Enter target token address (e.g., USDC address): ").strip()

        # Get amount
        while True:
            try:
                amount = float(input("Enter amount of SOL to trade: ").strip())
                if amount <= 0:
                    print("Amount must be greater than zero.")
                    continue
                self.state.amount = amount
                break
            except ValueError:
                print("Please enter a valid number.")

        # Optional: Get custom RPC URL
        custom_rpc = input("Enter custom RPC URL (press Enter to use default): ").strip()
        if custom_rpc:
            self.state.rpc_url = custom_rpc

        print(f"\nPreparing to trade {self.state.amount} SOL for token at {self.state.target_token}...\n")
        return self.state

    @listen(get_user_input)
    async def initialize_crew(self, state):
        """Initialize the Solana trading crew"""
        print("Initializing trading crew...")
        
        try:
            self.state.trading_crew = SolanaTradingCrew(
                private_key=state.private_key,
                rpc_url=state.rpc_url
            )
            print("Trading crew initialized successfully.")
            return self.state
        except Exception as e:
            print(f"Error initializing trading crew: {e}")
            return None

    @listen(initialize_crew)
    async def execute_trade(self, state):
        """Execute the trade using the crew"""
        if not state.trading_crew:
            print("Trading crew not initialized. Aborting trade.")
            return None

        print("Executing trade...")
        try:
            result = await state.trading_crew.execute_trade(
                target_token=state.target_token,
                amount=state.amount
            )
            print("\nTrade execution result:")
            print(result)
            return result
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None

async def kickoff():
    """Run the Solana trading flow"""
    flow = SolanaTradingFlow()
    await flow.kickoff()
    print("\n=== Flow Complete ===")

def plot():
    """Generate a visualization of the flow"""
    flow = SolanaTradingFlow()
    flow.plot("solana_trading_flow")
    print("Flow visualization saved to solana_trading_flow.html")

if __name__ == "__main__":
    asyncio.run(kickoff()) 