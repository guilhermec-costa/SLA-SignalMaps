import datetime
from typing import List
import streamlit as st

city_codes = {
    "SAO JOSÉ DOS CAMPOS": 433,
    "GUARULHOS": 434,
    "INDAIATUBA": 435,
    "JACAREÍ": 436,
    "OSASCO": 437,
    "SANTANA DE PARNAIBA": 438,
    "SUZANO": 439,
    "FERRAZ DE VASCONCELOS": 440,
    "TABOAO DA SERRA": 443,
    "SAO PAULO": 447,
    "BRAGANCA PAULISTA": 489,
    "TAUBATE": 490,
    "LORENA": 491,
    "COTIA": 492,
    "LIMEIRA": 494,
    "MAUA": 495,
    "SAO VICENTE": 496,
    "SANTA BARBARA DOESTE": 497,
    "VALINHOS": 498,
    "ITAQUAQUECETUBA": 499,
    "HORTOLANDIA": 500,
    "PAULINIA": 501,
    "SANTOS": 502,
    "JANDIRA": 503,
    "JACAREI": 504,
    "ITUPEVA": 505,
    "RIO CLARO": 506,
    "RIBEIRAO PIRES": 507,
    "SUMARE": 508,
    "ITATIBA": 509,
    "POA": 510,
    "CACAPAVA": 511,
    "MONTE MOR": 512,
    "CAJAMAR": 513,
    "SAO BERNARDO DO CAMPO": 514,
    "TAU":99999,
    "SAO CAETANO DO SUL": 518,
    "EMBU DAS ARTES": 519,
    "JUNDIAI": 520,
    "SANTO ANDRE": 521,
    "DIADEMA": 522,
    "MOGI DAS CRUZES": 523,
    "CAMPOS DO JORDAO": 524,
    "CAMPINAS": 525,
    "SAO JOSE DOS CAMPOS": 526,
    "AMERICANA": 532,
    "TAUBATÉ": 537,
    "SÃO PAULO": 544,
    "LORENA": 545,
    "CAMPOS DO JORDAO": 546,
    "SÃO PAULO": 547,
    "SÃO JOSÉ DOS CAMPOS": 548,
    "TABOAO DA SERRA": 549,
    "GUARULHOS": 550,
    "SANTANA DE PARNAIBA": 551,
    "INDAIATUBA": 552,
    "OSASCO": 553,
    "SUZANO": 554,
    "FERRAZ DE VASCONCELOS": 555,
    "JACAREÍ": 556
}


BU_MAP_COMGAS = {'Inst. Comgás':750, 'Inst. COMGÁS':750, 'Comgás - Instalações 2022':502, 'Comgás - Instalações 2023':741, 'Homologação LAB COMGÁS':747}
BU_MAP_SABESP = {'Condomínios':493, 'Macromedidores - Setorização':494, 'Grandes Consumidores':501}


def all_units_info(period = datetime.datetime.today().date(), company_id=38,
                   bussiness_unts:List[str] = [], addresses = [], residences = [], cities = []) -> str:
    
    if company_id == 38:
        bu_codes = ','.join(tuple(f"{BU_MAP_COMGAS[bu]}" for bu in bussiness_unts)) if bussiness_unts != [] else ','.join(tuple(f"{value}" for value in BU_MAP_COMGAS.values()))
    if company_id == 34:
        bu_codes = ','.join(tuple(f"{BU_MAP_SABESP[bu]}" for bu in bussiness_unts)) if bussiness_unts != [] else ','.join(tuple(f"{value}" for value in BU_MAP_SABESP.values()))

    st.write(bu_codes)
    conv_date = datetime.datetime.strftime(period, format='%Y%m%d')

    where_clause = f"dsl.snapshot_date_int = {conv_date} AND bu.id IN ({bu_codes}) AND r.status = 'ACTIVATED'"
    
    where_conditions = [f"dsl.snapshot_date_int = {conv_date}", f"bu.id IN ({bu_codes})", "r.status = 'ACTIVATED'"]
    or_conditions = []
    and_conditions = []

    if addresses or residences:
        
        if addresses:
            conv_addresses_teste = ','.join(tuple(f"'{address}'" for address in addresses))
            or_conditions.append(f" r.address IN ({conv_addresses_teste})")

        if residences:
            conv_residences_teste = ','.join(tuple(f"'{residence}'" for residence in residences))
            or_conditions.append(f"cs.name IN ({conv_residences_teste})")
       
        where_conditions.append("(" + " OR ".join(or_conditions) + ")")

    if cities:
        conv_cities_teste = ','.join(tuple(f"'{city}'" for city in cities))
        and_conditions.append(f"c.name IN ({conv_cities_teste})")
        where_conditions.append("(" + " AND ".join(and_conditions) + ")")

    where_clause = " AND ".join(where_conditions)
    

    ALL_UNITS = f"""
    SELECT r.rgi "Matrícula", m.serial_number, bu.name "Unidade de Negócio - Nome", c.name "Cidade - Nome", cs.name "Grupo - Nome",
            r.address "Endereço", r.latitude Latitude, r.longitude Longitude, round(dsl.ief * 100, 2) "IEF",
            date(dsl.snapshot_date_int) "data snapshot"
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
    WHERE {where_clause}"""


    return ALL_UNITS

def individual_comparison(addresses:List[str], residences:List[str], startdt:datetime.date, enddt:datetime.date, company_id) -> str:
    if addresses == [] and residences == []:
        st.warning('Select at least one address/residence')
        return "no data" 

    convstart_dt = datetime.datetime.strftime(startdt, format='%Y%m%d')
    convend_dt = datetime.datetime.strftime(enddt, format='%Y%m%d')
    where_clause = f"comp.id = {company_id} AND r.status = 'ACTIVATED' AND dsl.snapshot_date_int IN ({convstart_dt}, {convend_dt})"
    
    where_conditions = [f"comp.id = {company_id}", "r.status = 'ACTIVATED'", f"dsl.snapshot_date_int IN ({convstart_dt}, {convend_dt})"]
    
    if addresses or residences:
        or_conditions = []
        
        if addresses:
            conv_addresses_teste = ','.join(tuple(f"'{address}'" for address in addresses))
            or_conditions.append(f" r.address IN ({conv_addresses_teste})")

        if residences:
            conv_residences_teste = ','.join(tuple(f"'{residence}'" for residence in residences))
            or_conditions.append(f"cs.name IN ({conv_residences_teste})")
        
        where_conditions.append("(" + " OR ".join(or_conditions) + ")")
    where_clause = " AND ".join(where_conditions)



    
    INDIVIDUAL_COMPARISON = f"""
    SELECT bu.name as "Unidade de Negócio - Nome", c.name as "Cidade - Nome", r.address "Endereço", round(dsl.ief * 100, 2) "IEF", cs.name "Grupo - Nome", date(dsl.snapshot_date_int) "data snapshot",
    r.latitude Latitude, r.longitude Longitude
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
    WHERE {where_clause} 
    ORDER BY dsl.snapshot_date_int DESC
    """
    return INDIVIDUAL_COMPARISON

def sla_over_time_all_units(company_id=38):
    SLA_OVER_TIME_ALL_UNITS = f"""
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
    WHERE dsl.id BETWEEN (SELECT min(id) FROM daily_signal_logs dsl WHERE snapshot_date_int = 20230813)
                                                                        AND (SELECT max(id) FROM daily_signal_logs dsl WHERE snapshot_date_int = date(now()))
        AND r.status = 'ACTIVATED' AND c.id = {company_id}
    GROUP BY date(dsl.snapshot_date_int), bu.name
    ORDER BY date(dsl.snapshot_date_int) ASC;
    """

    return SLA_OVER_TIME_ALL_UNITS

def recent_readings(company_id=38):
    RECENT_READINGS = f"""
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
    WHERE rr.recovered = false AND c.id = {company_id}
    GROUP BY bu.name, reading_date
    """
    return RECENT_READINGS

def port_zero(company_id=38):
    if company_id == 38:
        codes = '(750,502,741,747)'
    if company_id == 34:
        codes = '(493, 494, 501)'

    PORT_ZERO = f"""
    select bu.name, date(alarms.created_at) as "created_at", alarms.description, alarms.code, m.id meter_id, alarms.status  from alarms
    inner join meters m
            on m.id = alarms.meter_id 
    inner join residences r
            on m.residence_id = r.id
    inner join commercial_services cs 
            on cs.id = r.commercial_service_id
    inner join business_units bu 
            on bu.id = cs.business_unit_id
    where bu.id IN {codes} and date(alarms.created_at) between (date(now()) - interval '29' day) and date(now()) and alarms.code = 'I5'
    """
    return PORT_ZERO

# DAILY_TRANSMISSIONS = """
# SELECT bu.name, from_unixtime(rr.created_at_uts, '%d/%m/%Y') snapshot_date, count(bu.name) qtd_transmissoes,
# 	q2.total_de_inst_acumulado pontos_ativos, (q2.total_de_inst_acumulado) * 2 qtd_transmissoes_meta
# FROM recent_readings rr
# INNER JOIN meters m
# 	ON m.id = rr.meter_id
# INNER JOIN residences res
# 	ON res.id = m.residence_id 
# INNER JOIN commercial_services cs
# 	ON cs.id = res.commercial_service_id
# INNER JOIN business_units bu
# 	ON bu.id = cs.business_unit_id
# INNER JOIN
# 	( # querie para contagem do total de instalações
# 	SELECT bu1.name, count(*) total_de_inst FROM residences r
# 	INNER JOIN commercial_services cs1 
# 		ON cs1.id = r.commercial_service_id
# 	INNER JOIN business_units bu1 
# 		ON bu1.id = cs1.business_unit_id
# 	WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r.status = 'ACTIVATED'
# 	-- WHERE cs1.name LIKE '%COND. SAO CRISTOVAO%'
# 	GROUP BY bu1.name
# 		) AS quantia_pontos
# 	ON quantia_pontos.name = bu.name
# INNER JOIN (
# 	SELECT q1.activated_at, q1.name, SUM(q2.total_de_inst) AS total_de_inst_acumulado
# 	FROM (
# 			SELECT date(activated_at) AS activated_at, bu1.name, count(*) AS total_de_inst
# 			FROM residences r
# 			INNER JOIN commercial_services cs1 
# 				ON cs1.id = r.commercial_service_id
# 			INNER JOIN business_units bu1 
# 				ON bu1.id = cs1.business_unit_id
# 			WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r.status = 'ACTIVATED'
# 			GROUP BY date(activated_at), bu1.name
# 	) AS q1
# 	INNER JOIN (
# 	    SELECT 
# 	        date(activated_at) AS activated_at, 
# 	        bu1.name, 
# 	        count(*) AS total_de_inst
# 	    FROM residences r1
# 	    INNER JOIN commercial_services cs1 
# 	        ON cs1.id = r1.commercial_service_id
# 	    INNER JOIN business_units bu1 
# 	        ON bu1.id = cs1.business_unit_id
# 	    WHERE bu1.name IN ('Inst. Comgás', 'Comgás - Instalações 2023') AND r1.status = 'ACTIVATED'
# 	    GROUP BY date(activated_at), bu1.name
# 	) AS q2 ON q1.name = q2.name AND q1.activated_at >= q2.activated_at
# 	GROUP BY q1.activated_at, q1.name, q1.total_de_inst
# 	ORDER BY q1.name, q1.activated_at
# ) q2 ON ((q2.name = bu.name) AND date_format(q2.activated_at, '%d/%m/%Y') = from_unixtime(rr.created_at_uts, '%d/%m/%Y'))
# WHERE rr.recovered = FALSE AND res.status = 'ACTIVATED' AND bu.name IN ('Inst. Comgás', 'Comgás - Instalações 2023')
# GROUP BY from_unixtime(rr.created_at_uts, '%d/%m/%Y'), bu.name
# UNION (
# -- QUERY DE INST ACUMULATIVAS E TRANSMISSÕES PARA COMGAS 22 E INST COMGAS
# SELECT bu.name, from_unixtime(rr.created_at_uts, '%d/%m/%Y') snapshot_date, count(bu.name) qtd_transmissoes,
# 	quantia_pontos.total_de_inst pontos_ativos, (quantia_pontos.total_de_inst) * 2 qtd_transmissoes_meta
# FROM recent_readings rr
# INNER JOIN meters m
# 	ON m.id = rr.meter_id
# INNER JOIN residences res
# 	ON res.id = m.residence_id 
# INNER JOIN commercial_services cs
# 	ON cs.id = res.commercial_service_id
# INNER JOIN business_units bu
# 	ON bu.id = cs.business_unit_id
# INNER JOIN
# 	( # querie para contagem do total de instalações
# 	SELECT bu1.name, count(*) total_de_inst FROM residences r
# 	INNER JOIN commercial_services cs1 
# 		ON cs1.id = r.commercial_service_id
# 	INNER JOIN business_units bu1 
# 		ON bu1.id = cs1.business_unit_id
# 	WHERE bu1.name IN ('Comgás - Instalações 2022') AND r.status = 'ACTIVATED'
# 	GROUP BY bu1.name
# 		) AS quantia_pontos
# 	ON quantia_pontos.name = bu.name
# WHERE rr.recovered = FALSE AND res.status = 'ACTIVATED' AND bu.name IN ('Comgás - Instalações 2022')
# GROUP BY from_unixtime(rr.created_at_uts, '%d/%m/%Y'), bu.name)
# """
