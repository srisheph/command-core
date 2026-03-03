# CommandCore – Voice-Driven AI Coding Assistant

## Overview

CommandCore is a voice-driven AI coding assistant built using LangGraph and OpenAI models. It allows users to issue spoken development commands, automatically generates code, executes safe Windows commands, and persists conversational state using checkpointing.

The system is designed to function as an autonomous coding agent that:

* Accepts voice input
* Converts speech to text
* Uses a tool-enabled LLM agent
* Automatically writes code files
* Executes Windows shell commands
* Maintains conversation memory using MongoDB checkpointing
* Generates a spoken summary of performed actions

---

## Architecture

The system is composed of two primary modules:

### 1. `graph.py`

Responsible for building the LangGraph agent.

* Defines the conversation state
* Registers tools (`write_file`, `run_command`)
* Configures LLM with tool binding
* Enforces system constraints
* Compiles the graph with checkpoint support

### 2. `main.py`

Implements the voice-driven execution loop.

* Captures audio via microphone
* Converts speech to text using Google Speech Recognition
* Streams input through LangGraph
* Generates action summaries via OpenAI
* Converts summaries to speech using OpenAI TTS
* Persists state using MongoDBSaver

---

## Key Features

### Tool-Enabled LLM Agent

The assistant is not rule-based. It uses a GPT-4-class model with tool binding, enabling dynamic decisions about:

* When to write files
* When to execute commands
* How to structure generated projects

### Controlled File System Access

The agent is restricted to writing files inside the `chat_gpt` directory.
It cannot access or modify files outside this sandbox.

### Windows-Specific Command Handling

The assistant is explicitly configured for Windows CMD usage:

* Uses `dir`, `mkdir`, `copy`, `type`, etc.
* Avoids Linux-specific commands

### Persistent Memory (Checkpointing)

MongoDB is used as a checkpointer via `MongoDBSaver`.
Each session is associated with a `thread_id`, allowing:

* Conversation continuity
* Stateful interactions
* Multi-step workflows

### Voice-Based Interaction

The assistant:

* Accepts microphone input
* Converts speech to text
* Executes requested actions
* Summarizes its actions
* Speaks back a short summary

---

## Technology Stack

* Python
* LangGraph
* LangChain
* OpenAI GPT models
* MongoDB (Checkpointing)
* SpeechRecognition
* OpenAI Text-to-Speech
* LangSmith (Tracing & Observability)

---

## Setup Instructions

### 1. Clone Repository

```
git clone <your-repository-url>
cd commandcore
```

### 2. Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

Ensure MongoDB is running locally:

```
mongodb://admin:admin@localhost:27017
```

### 5. Run the Assistant

```
python main.py
```

Speak your command when prompted.

---

## Safety Design

* All generated files are saved only inside `chat_gpt/`
* The system does not permit file operations outside the sandbox
* Windows-only command enforcement reduces shell ambiguity
* Tool calls are explicitly defined and traceable

---

## Observability

LangSmith tracing is integrated to monitor:

* Tool usage
* LLM decisions
* Agent execution flow

This enables debugging and performance analysis.

---

## Limitations

* Designed for Windows CMD environments
* Requires local microphone access
* Intended for local execution (voice interaction is not deployable without UI/API layer)
* MongoDB must be running locally

---

## Author

Shephali Srivastava
