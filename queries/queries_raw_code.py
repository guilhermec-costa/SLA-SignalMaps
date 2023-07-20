ALL_UNITS = """
SELECT dsl.module_id, r.rgi "Matrícula", m.serial_number, devc.pac "deveui",
	devc.serial_number "serial number", bu.name "Unidade de Negócio - Nome", c.name "Cidade - Nome", cs.name "Grupo - Nome",
	r.address "Endereço", r.latitude Latitude, r.longitude Longitude, r.client_name "Seguimento", dsl.module_id "id do módulo",
	round(dsl.ief * 100, 2) "IEF", date(dsl.created_at) "data snapshot"
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
AND dsl.created_at >= date(now())
"""