Cleaned data in Excel:
- Sort on vessel, datetime
- remove all duplicate lines

Assumptions:
- Travel from port X back to port X w no intermediary stops at any
other port Y will be treated as a non-trip.
- Null speed values will be treated as corrupt data and line ignored
- If ship is >3 Km from the port, it is not AT the port.
- If ship is at a speed of 0, it is not moving.
- If ship is at a speed of 0.1, it may not be moving (allows for speed
measurement errors).

Addn Notes:
- Sometimes the vessal(s) end up in weird places w no discernable path.
- Used model w highest rating from several options (Decision Tree),
BUT we're finding it biases based on frequency and doesn't consider
seasonality. Adding trip numbers to 2019 trips and using as basis for
2020 trip predictions will simulate this to some extent. (example vessel
1 w/out added inputs will just run b/ween Asia and US but seasonality
would intuititively suggest that we should be around Europe). Additionally
adding a season marker (quarters) will help.
- Consideration : Should model be re-trained for ea vessel? Cargo vessels
should follow routes w no implication from other ships in theory?
- Current 7/20 leaderboard of 3 has the worst voyage construction w the best
predictions, and best construction w the worst predictions. Why?

Hypothesis: the worst voyage list is likely making obvious errors -
i.e. jumping between nearby ports, or jumping to same port multiple times
on slight movement. This should introduce bad data that can lead to low
voyage score. However, this also would lead to a massive frequency bias towards
the most frequented and largest ports. As a result, the machine learning
model used by the contestant will have a very logical frequency bias that
just happens to hit the larger / busier ports and produces more correct
guesses entirely by chance. The bad initial data collection results in higher
prediction score?

Debugging ToDo:
- Create list of short trips - visualize. Logical?

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