# PydanticAI Airflow Agent Demo

A demo project showing how to build an AI agent that interacts with Apache Airflow using natural language
queries. Built with PydanticAI and Gemini 2.0.

> "What's the status of our payment report DAG?" - Now you can simply ask your agent! 🚀

## Overview

This project demonstrates how to:
- 
- Create a PydanticAI agent that interacts with Airflow's API
- Handle natural language queries about DAG statuses
- Return structured, type-safe responses
- Implement function tools for models to retrieve extra information
- Use Gemini 2.0 for enhanced language understanding

## Prerequisites

- Python 3.12
- Poetry
- Docker
- Astro CLI
- Google Cloud credentials (for Gemini 2.0)

## Quick Start

```bash
# Install dependencies
poetry install

# Start Airflow
make airflow-start

# Run the agent
make run-agent
```
