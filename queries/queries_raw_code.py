import datetime
from typing import List
from streamlit.elements.time_widgets import DateWidgetReturn
from . import querie_builder
import streamlit as st



cidades = [
    "SAO JOSÉ DOS CAMPOS",
    "GUARULHOS",
    "INDAIATUBA",
    "JACAREÍ",
    "OSASCO",
    "SANTANA DE PARNAIBA",
    "SUZANO",
    "FERRAZ DE VASCONCELOS",
    "TABOAO DA SERRA",
    "SAO PAULO",
    "BRAGANCA PAULISTA",
    "TAUBATE",
    "LORENA",
    "COTIA",
    "COTIA",
    "LIMEIRA",
    "MAUA",
    "SAO VICENTE",
    "SANTA BARBARA DOESTE",
    "VALINHOS",
    "ITAQUAQUECETUBA",
    "HORTOLANDIA",
    "PAULINIA",
    "SANTOS",
    "JANDIRA",
    "JACAREI",
    "ITUPEVA",
    "RIO CLARO",
    "RIBEIRAO PIRES",
    "SUMARE",
    "ITATIBA",
    "POA",
    "CACAPAVA",
    "MONTE MOR",
    "CAJAMAR",
    "SAO BERNARDO DO CAMPO",
    "SAO CAETANO DO SUL",
    "EMBU DAS ARTES",
    "JUNDIAI",
    "SANTO ANDRE",
    "DIADEMA",
    "MOGI DAS CRUZES",
    "CAMPOS DO JORDAO",
    "CAMPINAS",
    "SAO JOSE DOS CAMPOS",
    "AMERICANA",
    "TAU",
    "SAO PAULO",
    "LORENA",
    "CAMPOS DO JORDAO"
]

BUS = [
    'Inst. Comgás', 'Comgás - Instalações 2023',
    'Comgás - Instalações 2022', 'Homologação LAB COMGÁS'
]


def all_units_info(period: DateWidgetReturn = datetime.datetime.today().date(),
                   bussiness_unts:List[str] = ['Inst. Comgás', 'Comgás - Instalações 2022', 'Comgás - Instalações 2023', 'Homologação LAB COMGÁS'], residences:List[str] = ['test'], cities:List[str] = cidades) -> str:
    conv_date = datetime.datetime.strftime(period, format='%Y%m%d')
    conv_busn_unts = ','.join(tuple(f"'{busn_unt}'" for busn_unt in BUS)) if bussiness_unts == [] else ','.join(tuple(f"'{bu}'" for bu in bussiness_unts))
    conv_cities = ','.join(f"'{city}'" for city in cidades) if cities == [] else ','.join(tuple(f"'{city}'" for city in cities))

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
    WHERE bu.name IN ({}) AND r.status = 'ACTIVATED' AND c.name IN ({})
    AND dsl.snapshot_date_int =  {}
    """.format(conv_busn_unts, conv_cities, conv_date)
    return ALL_UNITS

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
WHERE c.id = 38 AND r.status = 'ACTIVATED' AND dsl.snapshot_date_int BETWEEN 20230521 AND date(now())
GROUP BY date(dsl.snapshot_date_int), bu.name
ORDER BY date(dsl.snapshot_date_int) ASC;
"""

RECENT_READINGS = """
SELECT bu.name, from_unixtime(created_at_uts, '%d/%m/%Y') reading_date, count(*) all_readings
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
WHERE c.id = 38 AND rr.recovered = false
GROUP BY bu.name, reading_date
"""

DAILY_TRANSMISSIONS = """
SELECT bu.name, from_unixtime(rr.created_at_uts, '%d/%m/%Y') snapshot_date, count(bu.name) qtd_transmissoes,
	q2.total_de_inst_acumulado pontos_ativos, (q2.total_de_inst_acumulado) * 2 qtd_transmissoes_meta
FROM recent_readings rr
INNER JOIN meters m
	ON m.id = rr.meter_id
INNER JOIN residences res
	ON res.id = m.residence_id 
INNER JOIN commercial_services cs
	ON cs.id = res.commercial_service_id
INNER JOIN business_units bu
	ON bu.id = cs.business_unit_id
INNER JOIN
	( # querie para contagem do total de instalações
	SELECT bu1.name, count(*) total_de_inst FROM residences r
	INNER JOIN commercial_services cs1 
		ON cs1.id = r.commercial_service_id
	INNER JOIN business_units bu1 
		ON bu1.id = cs1.business_unit_id
	WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r.status = 'ACTIVATED'
	-- WHERE cs1.name LIKE '%COND. SAO CRISTOVAO%'
	GROUP BY bu1.name
		) AS quantia_pontos
	ON quantia_pontos.name = bu.name
INNER JOIN (
	SELECT q1.activated_at, q1.name, SUM(q2.total_de_inst) AS total_de_inst_acumulado
	FROM (
			SELECT date(activated_at) AS activated_at, bu1.name, count(*) AS total_de_inst
			FROM residences r
			INNER JOIN commercial_services cs1 
				ON cs1.id = r.commercial_service_id
			INNER JOIN business_units bu1 
				ON bu1.id = cs1.business_unit_id
			WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r.status = 'ACTIVATED'
			GROUP BY date(activated_at), bu1.name
	) AS q1
	INNER JOIN (
	    SELECT 
	        date(activated_at) AS activated_at, 
	        bu1.name, 
	        count(*) AS total_de_inst
	    FROM residences r1
	    INNER JOIN commercial_services cs1 
	        ON cs1.id = r1.commercial_service_id
	    INNER JOIN business_units bu1 
	        ON bu1.id = cs1.business_unit_id
	    WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r1.status = 'ACTIVATED'
	    GROUP BY date(activated_at), bu1.name
	) AS q2 ON q1.name = q2.name AND q1.activated_at >= q2.activated_at
	GROUP BY q1.activated_at, q1.name, q1.total_de_inst
	ORDER BY q1.name, q1.activated_at
) q2 ON ((q2.name = bu.name) AND date_format(q2.activated_at, '%d/%m/%Y') = from_unixtime(rr.created_at_uts, '%d/%m/%Y'))
WHERE rr.recovered = FALSE AND res.status = 'ACTIVATED' AND bu.name IN ('Inst. Comgás', 'Comgás - Instalações 2023')
GROUP BY from_unixtime(rr.created_at_uts, '%d/%m/%Y'), bu.name
UNION (
-- QUERY DE INST ACUMULATIVAS E TRANSMISSÕES PARA COMGAS 22 E INST COMGAS
SELECT bu.name, from_unixtime(rr.created_at_uts, '%d/%m/%Y') snapshot_date, count(bu.name) qtd_transmissoes,
	quantia_pontos.total_de_inst pontos_ativos, (quantia_pontos.total_de_inst) * 2 qtd_transmissoes_meta
FROM recent_readings rr
INNER JOIN meters m
	ON m.id = rr.meter_id
INNER JOIN residences res
	ON res.id = m.residence_id 
INNER JOIN commercial_services cs
	ON cs.id = res.commercial_service_id
INNER JOIN business_units bu
	ON bu.id = cs.business_unit_id
INNER JOIN
	( # querie para contagem do total de instalações
	SELECT bu1.name, count(*) total_de_inst FROM residences r
	INNER JOIN commercial_services cs1 
		ON cs1.id = r.commercial_service_id
	INNER JOIN business_units bu1 
		ON bu1.id = cs1.business_unit_id
	WHERE bu1.name IN ('Comgás - Instalações 2022') AND r.status = 'ACTIVATED'
	GROUP BY bu1.name
		) AS quantia_pontos
	ON quantia_pontos.name = bu.name
WHERE rr.recovered = FALSE AND res.status = 'ACTIVATED' AND bu.name IN ('Comgás - Instalações 2022')
GROUP BY from_unixtime(rr.created_at_uts, '%d/%m/%Y'), bu.name)
"""
