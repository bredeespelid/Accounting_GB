# Sets
set BAKERIES;
set DAYS ordered;
set VANS;

# Parameters
param DISTANCE{BAKERIES, BAKERIES};
param PRIORITY{DAYS, BAKERIES};

# Variables
var x{VANS, DAYS, BAKERIES, BAKERIES} binary;
var u{VANS, DAYS, BAKERIES} >= 0;
var y{VANS, DAYS, BAKERIES} binary;  # 1 if van v visits bakery i on day d
var max_distance{DAYS};

# Objective: Minimize total distance, prioritize early openings, and balance workload
minimize TotalDistance:
    sum{v in VANS, d in DAYS, i in BAKERIES, j in BAKERIES: i != j} 
        DISTANCE[i,j] * x[v,d,i,j] +
    50 * sum{v in VANS, d in DAYS, i in BAKERIES: i != 'Mindemyren'} 
        PRIORITY[d,i] * y[v,d,i];

 
# Constraints
subject to VisitOncePerDay {d in DAYS, i in BAKERIES: i != 'Mindemyren'}:
    sum{v in VANS} y[v,d,i] = 1;

subject to LinkXY {v in VANS, d in DAYS, i in BAKERIES, j in BAKERIES: i != j}:
    x[v,d,i,j] <= y[v,d,i];

subject to DepartOncePerVan {v in VANS, d in DAYS, i in BAKERIES: i != 'Mindemyren'}:
    sum{j in BAKERIES: j != i} x[v,d,i,j] = y[v,d,i];

subject to ArriveOncePerVan {v in VANS, d in DAYS, j in BAKERIES: j != 'Mindemyren'}:
    sum{i in BAKERIES: i != j} x[v,d,i,j] = y[v,d,j];

subject to SubtourElimination {v in VANS, d in DAYS, i in BAKERIES, j in BAKERIES: i != j and i != 'Mindemyren' and j != 'Mindemyren'}:
    u[v,d,i] - u[v,d,j] + card(BAKERIES) * x[v,d,i,j] <= card(BAKERIES) - 1;

subject to StartAtMindemyren {v in VANS, d in DAYS}:
    sum{j in BAKERIES: j != 'Mindemyren'} x[v,d,'Mindemyren',j] = 1;

subject to EndAtMindemyren {v in VANS, d in DAYS}:
    sum{i in BAKERIES: i != 'Mindemyren'} x[v,d,i,'Mindemyren'] = 1;

subject to MindemyrenFirst {v in VANS, d in DAYS}:
    u[v,d,'Mindemyren'] = 0;
    


subject to VisitPriorityOneFirst {v in VANS, d in DAYS, i in BAKERIES, j in BAKERIES: 
    i != 'Mindemyren' and j != 'Mindemyren' and PRIORITY[d,i] = 1 and PRIORITY[d,j] != 1}:
    u[v,d,i] <= u[v,d,j];
    
subject to MaintainPriorityOrder {v in VANS, d in DAYS, i in BAKERIES, j in BAKERIES: i != j and i != 'Mindemyren' and j != 'Mindemyren'}:
    PRIORITY[d,i] * y[v,d,i] <= PRIORITY[d,j] * y[v,d,j] + 1000 * (1 - x[v,d,i,j]);
    
subject to HorisontVisitedLastOnce {d in DAYS}:
    sum{v in VANS} x[v,d,'Horisont','Mindemyren'] = 1;

subject to MaxDistance {d in DAYS, v in VANS}:
    sum{i in BAKERIES, j in BAKERIES: i != j} DISTANCE[i,j] * x[v,d,i,j] <= max_distance[d];

subject to StartWithPriorityOne {v in VANS, d in DAYS}:
    sum{i in BAKERIES: i != 'Mindemyren' and PRIORITY[d,i] = 1} x[v,d,'Mindemyren',i] = 1;