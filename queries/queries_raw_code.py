ALL_UNITS = """
SELECT dsl.module_id, r.rgi "Matrícula", m.serial_number, devc.pac "deveui",
	devc.serial_number "serial number", bu.name "Unidade de Negócio - Nome", c.name "Cidade - Nome", cs.name "Grupo - Nome",
	r.address "Endereço", r.latitude Latitude, r.longitude Longitude, r.client_name "Seguimento", dsl.module_id "id do módulo",
	round(dsl.ief * 100, 2) "IEF", date(dsl.snapshot_date_int) "data snapshot"
FROM daily_signal_logs dsl
INNER JOIN residences r 
	ON (dsl.residence_id = r.id)
INNER JOIN commercial_services cs
	ON (cs.id = r.commercial_service_id)
INNER JOIN cities c
	ON c.id = cs.city_id 
INNER JOIN business_units bu
	ON (bu.id = cs.business_unit_id)
INNER JOIN companies comp
	ON comp.id = bu.company_id
INNER JOIN meters m
	ON (m.residence_id = r.id)
INNER JOIN devices devc
	ON (devc.meter_id = m.id)
WHERE comp.id = 38 AND r.status = 'ACTIVATED'
AND dsl.snapshot_date_int =  date(now())
"""

SLA_OVER_TIME_ALL_UNITS = """
SELECT date(dsl.snapshot_date_int) snapshot_date, bu.name, round(avg(dsl.ief) * 100, 2) sla_mean,
	round(avg(m.last_rssi), 2) rssi_mean, round(avg(m.battery_voltage), 2) battery_voltage_mean
FROM daily_signal_logs dsl
INNER JOIN residences r
	ON r.id = dsl.residence_id
INNER JOIN meters m
	ON m.residence_id = r.id
INNER JOIN commercial_services cs
	ON cs.id = r.commercial_service_id
INNER JOIN business_units bu 
	ON bu.id = cs.business_unit_id
INNER JOIN companies c
	ON c.id = bu.company_id
WHERE c.id = 38 AND r.status = 'ACTIVATED' AND dsl.snapshot_date_int BETWEEN date(now()) - INTERVAL '30' DAY AND date(now()) + INTERVAL '24' HOUR
GROUP BY date(dsl.snapshot_date_int), bu.name
ORDER BY date(dsl.snapshot_date_int) ASC;
"""

RECENT_READINGS = """
SELECT bu.name, from_unixtime(created_at_uts, '%d/%m/%Y') reading_date, count(*) all_readings, sum(rr.recovered) lost_uplinks
FROM recent_readings rr
INNER JOIN meters m
	ON m.id = rr.meter_id
INNER JOIN residences res
	ON res.id = m.residence_id 
INNER JOIN commercial_services cs
	ON cs.id = res.commercial_service_id
INNER JOIN business_units bu
	ON bu.id = cs.business_unit_id
INNER JOIN companies c
	ON c.id = bu.company_id 
WHERE c.id = 38
GROUP BY bu.name, reading_date
"""