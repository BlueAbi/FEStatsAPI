# FEStatsAPI
An API containing base stats and growth rates for all playable characters in the Fire Emblem series. Doesn't include Heroes, sorry lol. Don't want to deal with that nightmare, and there are plenty of other sources out there anyway.

This is currently still deep in development and is only dealing with FE9 (Path of Radiance) units, their base stats, growth rates, class, and level. No particular reason other than it's my favortie FE game. Once I have confirmed it to run well. I will begin adding units from the other games, then eventually expand the information beyond just stats.

2025-06-27
API is confirmed to be working! Seems to return data just fine. I'm now working on implementing stats for the rest of the games. Stay tuned!

For now, endpoints are going to structured like this. I may change this in the future, as I plan to add more than just Player Units, but I'll cross that bridge when I get there:
For base stats: base_stats/[number of the game in order of release]/[character name]
For growth rates: growth_rates/[number of the game in order of release]/[character name]

Example with FE9 Ike:
base_stats/9/ike
growth_rates/9/ike
