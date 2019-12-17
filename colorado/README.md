# OSM Colorado
Play with Colorado OpenStreetMap data

The game idea is this:
1. Download high-level OSM data for the state of CO
2. Move armies along highways
3. Conquer a city by being the sole occupant for a while (think Age of Wonders)
4. Build city defenses
5. Defend cities against NPC attackers [and other players]
6. Build additional armies in cities

Still hung up on what geometries to use. Options (mix and match):
- Counties as polygons
- Cities as polygons
- Cities as nodes
- Highways as segments
- Everything as pixels
- Terrain as polygons

New game idea! Shipping company:
 1. Accept jobs shipping stuff
 2. Park vehicles at offices when not in use
 3. Switch out drivers at offices
 4. Do repairs at offices
 5. Buy more vehicles
 6. Buy more offices
 7. Offices cost less in sparse areas, but are harder to staff and maintain, repairs take longer
 8. If a vehicle breaks down, send out a tow truck and another vehicle
 9. Rent if you don't own them
10. Larger jobs need larger vehicles
11. Larger vehicles need larger offices and more maintenance
12. Time limit on each job
13. Penalty for not completing a job in time, or just no money

Tweaks!
 1. Cities build up shippable goods over time
 2. Cities build up need for goods over time
 3. Must build a warehouse in a city before a route can be established
 4. Build a garage to repair and tow vehicles
 5. Vehicles autorepair when they enter cities with a garage
 6. Build an office to hire drivers, buy vehicles, ...
 7. Vehicle degrades over time
 8. If it dips too low, vehicle max health drops
 9. Established routes run themselves
10. Purchases in small towns are cheap, but rentals and upkeep are not
11. 

## Files

play.py: Master script, copied from map.py
play.ipynb: Development playground

