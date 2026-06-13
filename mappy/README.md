# Mappy

Mappy solves the **Vehicle Routing Problem (postman problem)**: given a list of GPS addresses, it clusters them into zones and computes the optimal visiting order for each zone. It also targets scraping highway toll costs from autoroute-eco.fr to find the cheapest route.

## Tech Stack

- **Language:** Rust (2021 edition)
- **Backend:** Raw TCP HTTP server (no framework)
- **Algorithms:** K-Means clustering + Travelling Salesman Problem (nearest-neighbour heuristic)
- **Frontend:** Static HTML/JS served from `static/`

## How to Start

> **Important:** Git's `link.exe` shadows the MSVC linker on this machine. Always use the GNU toolchain.

```bash
SC_BIN="$HOME/.rustup/toolchains/stable-x86_64-pc-windows-gnu/lib/rustlib/x86_64-pc-windows-gnu/bin/self-contained"
export PATH="$SC_BIN:$PATH"
cargo +stable-x86_64-pc-windows-gnu run
```

The server starts on `http://localhost:8080` (or whatever port is configured).

Open `static/index.html` in a browser, or hit the API directly.

## Main API

**POST** `/solve`

```json
{
  "vehicles": [
    { "lat": 48.8566, "lon": 2.3522, "label": "Paris centre" },
    { "lat": 48.8530, "lon": 2.3499, "label": "Stop A" }
  ],
  "zones": 2
}
```

Response: list of zones, each with a color, ordered stops, route polyline, and total distance in km.

## Project Structure

```
src/
  main.rs       — HTTP server + request handling
  clustering.rs — K-Means implementation
  routing.rs    — TSP + haversine distance
  vehicle.rs    — Vehicle / Stop data types
static/         — Frontend assets
```
