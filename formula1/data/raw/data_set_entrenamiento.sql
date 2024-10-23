SELECT 
    r.raceId, 
    r.driverId, 
    r.constructorId, 
    d.forename, 
    d.surname, 
    d.nationality, 
    c.name AS constructor_name, 
    cs.points AS constructor_points, 
    r.grid, 
    r.positionOrder AS final_position, 
    r.points AS driver_points, 
    r.fastestLapTime, 
    q.position AS qualifying_position, 
    ds.points AS driver_standing_points, 
    ds.wins AS driver_wins, 
    ci.name AS circuit_name, 
    ci.country AS circuit_country, 
    l.time AS fastest_lap_time, 
    l.position AS lap_position
FROM 
    results r
JOIN 
    drivers d ON r.driverId = d.driverId
JOIN 
    constructors c ON r.constructorId = c.constructorId
JOIN 
    constructorStandings cs ON r.constructorId = cs.constructorId AND r.raceId = cs.raceId
JOIN 
    driverStandings ds ON r.driverId = ds.driverId AND r.raceId = ds.raceId
JOIN 
    qualifying q ON r.raceId = q.raceId AND r.driverId = q.driverId
JOIN 
    races ra ON r.raceId = ra.raceId
JOIN 
    circuits ci ON ra.circuitId = ci.circuitId
LEFT JOIN 
    lapTimes l ON r.raceId = l.raceId AND r.driverId = l.driverId
WHERE 
    ra.year = 2023  -- O el año más reciente disponible
ORDER BY 
    r.raceId, r.driverId;
