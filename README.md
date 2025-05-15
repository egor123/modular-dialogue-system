# Modular Dialogue System for NPC Interaction in Games

This repository contains a modular, LLM-augmented dialogue system designed for text-based interaction with non-player characters (NPCs) in narrative-driven games such as RPGs. The system balances narrative coherence with dynamic player input by leveraging modular control logic, factual context, and natural language generation.

---

## Overview

The system is structured as a processing pipeline, where a shared `Data Container` is passed through a series of independent modules. Each module incrementally enriches the container with context, instructions, and personality traits. At the final stage, a large language model (LLM) generates a character-specific response using all collected data.

---

## Pipeline Architecture

1. **Data Container**
   - The player input and dialogue history are added to the `Data Container`.

2. **Preprocessing Module**
   - Normalizes and summarizes input (if lengthy) for downstream processing.

3. **Dialogue Flow Module**
   - Determines the current dialogue state and injects the main intent instruction.
   - Supports Finite State Machines (FSM) and GOAP.

4. **Personality Module**
   - Adjusts instructions and adds behavioral traits that reflect the NPC’s identity (e.g., cautious, humorous, formal).

5. **World State Module**
   - Adds contextual knowledge (facts) from the game environment to ensure responses are grounded in world logic.

6. **Generation Module**
   - Synthesizes the final NPC response using an LLM like LLaMA 3.
   - Incorporates all data: instructions, history, personality, and facts.

---

## Data Container Structure

The `Data Container` acts as the shared mutable state. It includes:

- `input`: Player's input string.
- `history`: List of prior dialogue lines.
- `freedom`: Degree of conversational divergence allowed.
- `urgency`: Importance or speed required in response.
- `facts`: Game world context (non-directive).
- `personality`: NPC traits and modifiers.
- `instructions`: Directive statements for response generation.

---

## Configuration

- Each module is wrapped in a **standardized interface**, enabling flexible swapping of implementations.
- All configurations (e.g., FSM logic, personality rules, world facts) are defined in **JSON** or **YAML** files.
- Custom implementations can subclass base classes to expand or override default logic.

---


## Use Cases

- Role-playing games with free-text player input
- Game AI prototypes needing controllable LLM behavior
- Interactive fiction tools with modular state tracking

---

## Key Features

- Modular and extensible architecture
- Personality-aware LLM responses
- Fact-grounded world state management
- Designed for immersive NPC interaction in games

---

## License

# Non-exclusive licence to reproduce the thesis and make the thesis public

I, **Egor Lukjanenko**,  

1. grant the University of Tartu a free permit (non-exclusive licence) to reproduce, for the purpose of preservation, including for adding to the digital archives of the University of Tartu until the expiry of the term of copyright, my thesis *Modular system for text-based interaction with non-player characters in game environments*, supervised by **Giacomo Magnifico**;

2. grant the University of Tartu a permit to make the thesis specified in point 1 available to the public via the web environment of the University of Tartu, including via the digital archives, under the Creative Commons licence **CC BY-NC-ND 4.0**, which allows, by giving appropriate credit to the author, to reproduce, distribute the work and communicate it to the public, and prohibits the creation of derivative works and any commercial use of the work until the expiry of the term of copyright;

3. am aware of the fact that the author retains the rights specified in points 1 and 2;

4. confirm that granting the non-exclusive licence does not infringe other persons’ intellectual property rights or rights arising from the personal data protection legislation.

<br>

**Egor Lukjanenko**  
15/05/2025