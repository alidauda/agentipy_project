#!/usr/bin/env python
import json
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from crewai.flow.flow import Flow, listen, start
from guide_creator_flow.crews.solana_trading_crew.solana_trading_crew import EnhancedCryptoTradingCrew
from datetime import datetime

def kickoff():
    """Run the enhanced crypto trading flow"""
    # Initialize the enhanced crew
    crypto_crew = EnhancedCryptoTradingCrew()
    
    # Configure analysis parameters
    analysis_inputs = {
        "analysis_date": datetime.now().strftime("%B %Y"),
        "time_horizon": "3-6 months",
        "focus_sectors": "DeFi, Layer 1, Memecoins",
        "risk_tolerance": "moderate",
        "investment_size": "$100K - $1M",
        "client_type": "institutional"
    }
    
    try:
        print("Starting Enhanced Cryptocurrency Market Analysis...")
        result = crypto_crew.crew().kickoff(inputs=analysis_inputs)
        if result:
            print("\n=== Flow Complete ===")
            print("Your enhanced crypto market analysis reports are ready in the current directory.")
            filename = f"crypto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding='utf-8') as f:
                f.write(str(result))
            print(f"Report saved to {filename}")
        else:
            print("Analysis failed. Check logs for details.")
    except Exception as e:
        print(f"Error during crew execution: {str(e)}")
    finally:
        crypto_crew.cleanup()

def plot():
    """Generate a visualization of the flow"""
    flow = EnhancedCryptoTradingCrew()
    flow.plot("enhanced_crypto_trading_flow")
    print("Flow visualization saved to enhanced_crypto_trading_flow.html")

if __name__ == "__main__":
    kickoff()