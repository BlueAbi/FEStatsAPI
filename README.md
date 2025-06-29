# FEStatsAPI

---

Welcome to **FEStatsAPI**, your go-to source for base stats and growth rates for all playable characters in the Fire Emblem series! Please note that this API *does not* and *will not* include Fire Emblem Heroes data.

---

## Current Development Status

The API is currently in deep development, with **Fire Emblem: Path of Radiance (FE9)** being the focus. This initial phase includes base stats, growth rates, class, and starting level for FE9 units. The API has been confirmed to be working as of **June 27, 2025**, and efforts are now underway to implement data for the rest of the Fire Emblem games. Future plans include expanding the information beyond just stats.

---

## Endpoint Structure

The current endpoint structure is straightforward, though it may be subject to change as the API expands to include non-player units.

* **Base Stats**: `base_stats/[game_number]/[character_name]`
* **Growth Rates**: `growth_rates/[game_number]/[character_name]`

**Example for FE9 Ike:**

* Base Stats: `base_stats/9/ike`
* Growth Rates: `growth_rates/9/ike`

---

Stay tuned for more updates as we continue to build out the FEStatsAPI!
