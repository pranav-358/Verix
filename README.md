# Verix AI - Financial Dispute Intelligence Platform

## Overview
Verix AI is an explainable financial dispute intelligence platform that helps consumers and businesses identify, validate, and resolve transaction and invoice discrepancies using structured AI-driven compliance analysis.

## Features
- **Dual-mode operation**: Consumer support and merchant compliance
- **Real-time compliance validation**: Automated rule-based checks
- **AI-powered dispute analysis**: Structured entity extraction and reasoning
- **Live audit matrix**: Transparent compliance decision tracking
- **MIT Licensed**: Open source and freely distributable

## Tech Stack
### Backend
- FastAPI (Python)
- Pydantic for validation
- Google Gemini 1.5 Flash
- Uvicorn server

### Frontend
- HTML5/CSS3
- TailwindCSS
- Lucide Icons
- Vanilla JavaScript

## Installation

### Prerequisites
- Python 3.9+
- Node.js (optional, for frontend development)
- Google Gemini API key (optional, falls back to deterministic mode)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/verix-ai.git
cd verix-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional)

# Start backend server
uvicorn app.main:app --reload --port 8000