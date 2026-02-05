# Titanfall 2 Balanced Teams Ranking System (Python CLI)

## Introduction

Welcome to the simplified **Titanfall 2 Balanced Teams Ranking System**! This project is a Python-based terminal
application designed to create balanced team selections and manage player rankings for the first-person shooter (FPS)
game Titanfall 2.

Unlike the full-stack web version, this lightweight tool runs directly in the command line, focusing purely on the core
logic of Matchmaking Rating (MMR) calculations and team balancing using **SQLAlchemy** and **SQLite**. For the full
version of the app visit https://ranking-system-fullstack-nextjs.vercel.app/

In Titanfall 2's "Capture the Flag" mode, two teams of five players each compete to capture more flags than their
opponents. This system ensures those matches are fair and competitive by intelligently forming teams based on players'
Matchmaking Ratings (MMR).

## Features

### Team Formation

The system analyzes a pool of 10 players (loaded from a database) and automatically assigns them into two teams of five.
The allocation algorithm iterates through player combinations to minimize the total MMR difference between the two
sides, ensuring the match is mathematically as fair as possible.

### Ranking Algorithm

After a match simulation, the user inputs the result in the terminal. The system calculates the new MMR for all players
based on the following factors:

* **Match Outcome:** The winning team gains points while the losing team loses them.
* **Flag Advantage:** The greater the difference in flags captured, the more points are awarded (or deducted).
* **Winstreak (Last 10):** Players receive MMR bonuses based on their performance in their last 10 matches (tracked via
  a binary history system), encouraging consistent performance.

### Data Persistence

* **Automatic Data Loading:** If the database is empty, the system automatically parses a `gracze.txt` file to populate
  the player pool.
* **SQLite Database:** All player stats (MMR, match history) are persisted in a local `titanfall_rank.db` file, ensuring
  progress is saved between program executions.

## More Information

For a visual explanation of the logic behind this ranking system (based on the sister project in Java Spring MVC), you
can watch the video below:

https://www.youtube.com/watch?v=UoY1Vs-6aJ4

## Getting Started

### Prerequisites

To run this project, you need **Python 3** installed on your machine. You also need to install the `SQLAlchemy` library
for database management.

```bash
pip install sqlalchemy
