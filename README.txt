Cleaned data in Excel:
- Sort on vessel, datetime
- remove all duplicate lines

Assumptions:
- Travel from port X back to port X w no intermediary stops at any
other port Y will be treated as a non-trip. (Cor: Should this even
be happening or is this a result of current algo not sensitive enough
to a docking? Down to under 50 instances w 7/26 sensitivity)
- Null speed values will be treated as corrupt data and line ignored
(Cor:should null speeds be included as 0? based on proximity of 0ish values
around it? Am I missing trips due to this?)
- If ship is >40 Km from the port, it is not AT the port.
- If ship is at a speed of 0, it is not moving.
- If ship is at a speed of under 0.5, it may not be moving (allows for speed
measurement errors).

Addn Notes:
- Sometimes the vessal(s) end up in weird places w no discernable path.
There may be tools to clean the data up for this?
- Used model w highest rating from several options (Decision Tree),
BUT we're finding it biases based on frequency and doesn't consider
seasonality. Adding a season marker (quarters) seems to help.
- Model is being re-trained for ea vessel. Cargo vessels
should follow routes w no implication from other ships in theory?

Debugging ToDo:
- Create list of short trips - visualize. Logical?
- Spot check first trip predictions from maps created - do they look reasonable?

Questions:

- How far from a port (in km) as listed in ports.csv can we be to be considered
at the port.
- When a ship travels without touching a listed port in ports.csv, and returns
to the starting port - do we treat this as a non-trip, or do we treat this
as a trip going from X to X.


TO DO:

- Incorporate draft in determining if a ship is docked
- Track last known coordinate of a ship
- Use last known coord to find the likliest port of arrival.