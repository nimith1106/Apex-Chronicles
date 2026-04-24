# Apex Chronicles – Two‑Player Platform Fighter

A fast‑paced two‑player fighting game built with Pygame. Battle on a multi‑level platform stage, use special power‑ups, and smash your opponent’s health to zero. The game runs in fullscreen and automatically scales to any screen resolution.
## 👥 Team

- **Nesar N R**  
- **Ojus**
- **Nimith O**
- **Nilesh Kumar Prajapati**  
  
## Features

- **Two‑player local combat** – Player 1 (left side) vs Player 2 (right side)
- **Platform‑based movement** – Jump between elevated platforms, avoid falling off the screen
- **Attack & defense system** – Punch your opponent or block incoming damage
- **Power‑ups** – Appear when a player’s health drops low; grant temporary fire fists (bonus damage) or instant healing
- **Dynamic scaling** – Game logic uses an 800×600 base resolution, then scales perfectly to your monitor’s fullscreen resolution
- **Immersive audio** – Background music and sound effects (if assets are provided)
- **Polished UI** – Start screen, how‑to‑play screen with scrollable instructions, game‑over screen

## Controls

| Action | Player 1 (Left) | Player 2 (Right) |
|--------|----------------|------------------|
| Move Left | `A` | `←` |
| Move Right | `D` | `→` |
| Punch | `S` | `↓` |
| Defend | `W` | `↑` |
| Jump | `Z` | `Right Shift` |

- **Defense** reduces incoming damage by 30% for a short time.
- **Punch** deals 5 damage normally, or 10 damage if you have the **Fire Fist** power‑up.

## Power‑ups

Power‑ups spawn on random platforms when **any player’s health drops to 35 or below**. They appear every 10–15 seconds.

| Power‑up | Effect | Duration |
|----------|--------|----------|
| 🔥 Fire Fist (orange orb) | Punch deals 10 damage instead of 5 | 5 seconds |
| ❤️ Health Regen (green orb) | Instantly restores 5 health | Instant |


