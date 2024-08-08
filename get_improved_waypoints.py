from improved_waypoints import TOTAL_WAYPOINTS

f = open('improved_waypoints.txt', 'w')
for w in TOTAL_WAYPOINTS:
    f.write('(')
    f.write(str(w.location[0]))
    f.write(', ')
    f.write(str(w.location[1]))
    f.write(')\n')

