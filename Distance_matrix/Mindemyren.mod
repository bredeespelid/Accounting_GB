# Sets
set BAKERIES;

# Parameters
param DISTANCE{BAKERIES, BAKERIES};
param TRAVEL_TIME_PER_KM;
param UNLOADING_TIME;

# Variables
var x{BAKERIES, BAKERIES} binary;
var u{BAKERIES} >= 0;

# Objective: Minimize total travel time
minimize TotalTime:
    sum{i in BAKERIES, j in BAKERIES: i != j} 
        (DISTANCE[i,j] * TRAVEL_TIME_PER_KM + UNLOADING_TIME) * x[i,j];

# Constraints
subject to VisitOnce {i in BAKERIES}:
    sum{j in BAKERIES: i != j} x[i,j] = 1;

subject to DepartOnce {j in BAKERIES}:
    sum{i in BAKERIES: i != j} x[i,j] = 1;

subject to SubtourElimination {i in BAKERIES, j in BAKERIES: i != j and i != 'Mindemyren' and j != 'Mindemyren'}:
    u[i] - u[j] + card(BAKERIES) * x[i,j] <= card(BAKERIES) - 1;

subject to StartAtMindemyren:
    sum{j in BAKERIES: j != 'Mindemyren'} x['Mindemyren',j] = 1;

subject to EndAtMindemyren:
    sum{i in BAKERIES: i != 'Mindemyren'} x[i,'Mindemyren'] = 1;

subject to MindemyrenFirst:
    u['Mindemyren'] = 0;