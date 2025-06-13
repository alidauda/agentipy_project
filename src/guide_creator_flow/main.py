#!/usr/bin/env python
import json
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from crewai.flow.flow import Flow, listen, start
from guide_creator_flow.crews.solana_trading_crew.solana_trading_crew import CryptoTradingCrew
from datetime import datetime



def kickoff():
    """Run the crypto trading flow"""
    crew = CryptoTradingCrew()
    try:
        response = crew.crew().kickoff()
        print("\n=== Flow Complete ===")
        print("Your crypto market analysis reports are ready in the current directory.")
        filename = f"crypto_market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(str(response))
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"Error during crew execution: {str(e)}")
    finally:
        crew.cleanup()

def plot():
    """Generate a visualization of the flow"""
    flow = CryptoTradingCrew()
    flow.plot("crypto_trading_flow")
    print("Flow visualization saved to crypto_trading_flow.html")

if __name__ == "__main__":
    kickoff()