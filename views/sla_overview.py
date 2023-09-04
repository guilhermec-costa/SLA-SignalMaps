import streamlit as st
from figures import *
from figures import sla_indicator_chart, sla_last_30days, rssi_last_30days, transmissions, port_zero, \
    metrics_boxplot, battery_voltage_last30days, recent_reading, sla_per_city, sla_bat_rssi_all_project
from queries import querie_builder, data_treatement, queries_raw_code
from datetime import datetime
import pandas as pd

def sla_overview(results:querie_builder.Queries, profile_to_simulate) -> None:
    st.write(profile_to_simulate)
    metrics_data_30days = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='SLA_OVER_TIME_ALL_UNITS')
    df_all_unit_services = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='ALL_UNITS')
    df_recent_readings = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='RECENT_READINGS')
    port_zero_data = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='PORT_ZERO')
    #st.write(port_zero_data)
    port_zero_data.drop_duplicates(subset=['created_at','meter_id'], keep='first', inplace=True)

    port_zero_grouped = port_zero_data[['name', 'created_at', 'code']].groupby(by=['name','created_at']).agg({'code':'count'}).reset_index()
    port_zero_grouped.sort_values(by=['created_at'], ascending=True, inplace=True)
    port_zero_grouped.created = port_zero_grouped.created_at.apply(lambda x: x.strftime('%b %d, %Y'))
    port_zero_grouped_onlydate = port_zero_grouped.groupby(by='created_at').agg({'code':'sum'}).reset_index()
    # 
    # df_daily_transmissions = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='DAILY_TRANSMISSIONS')
    # df_daily_transmissions.snapshot_date = df_daily_transmissions.snapshot_date.apply(lambda x: datetime.strptime(x, '%d/%m/%Y').date())
    df_recent_readings.reading_date = df_recent_readings.reading_date.apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
    df_recent_readings.sort_values(by='reading_date', ascending=True, inplace=True)

    # para prevenção de bugs, com mensagens antes de 2000

    
    st.header('SLA: metrics')
    st.markdown('---')
    st.markdown('###')
    tmp_connection = querie_builder.Queries(name='temporary_queries')
    with st.form(key='status_day'):
        status_day = st.date_input('Status day')
        submit_form = st.form_submit_button('Submit query')
        if submit_form:
            new_query = queries_raw_code.all_units_info(status_day)
            df_all_unit_services = pd.DataFrame(tmp_connection.run_single_query(new_query))

    df_recent_readings = df_recent_readings[df_recent_readings['reading_date'].dt.year > 2000]

    metrics_data_30days = data_treatement.clear_dataframe(metrics_data_30days, col_subset='name', vl_to_exclude='Homologação LAB COMGÁS')
    df_all_unit_services = data_treatement.clear_dataframe(df_all_unit_services, col_subset='Unidade de Negócio - Nome', vl_to_exclude='Homologação LAB COMGÁS')
    df_recent_readings = data_treatement.clear_dataframe(df_recent_readings, col_subset='name', vl_to_exclude='Homologação LAB COMGÁS')

    df_sla_per_city = df_all_unit_services.groupby(by='Cidade - Nome').agg({'IEF':'mean', 'Matrícula':'count'}).apply(lambda x: round(x, 2)).sort_values(by='IEF', ascending=True)
    df_sla_all_BU = df_all_unit_services.groupby('Unidade de Negócio - Nome').agg({'IEF':'mean', 'Matrícula':'count'}).reset_index()
    all_metrics_grouped_by_dt = metrics_data_30days.groupby(by='snapshot_date').mean()

    gauge_chart = sla_indicator_chart.gauge_sla_figure(df_sla_all_BU, period=status_day)
    sla_per_city_fig = sla_per_city.sla_per_city(df_sla_per_city)
    all_metrics_fig = sla_bat_rssi_all_project.metrics_all_projects(all_metrics_grouped_by_dt)
    sla_30days = sla_last_30days.sla_last_30days(metrics_data_30days)
    rssi_30days = rssi_last_30days.rssi_last_30days(metrics_data_30days)
    boxplot_metrics = metrics_boxplot.metrics_boxplot(metrics_data_30days)
    battery_voltage30days = battery_voltage_last30days.battery_voltage(metrics_data_30days)
    st.plotly_chart(gauge_chart, use_container_width=True)
    st.markdown('---')
    st.markdown('###')
    st.plotly_chart(sla_per_city_fig, use_container_width=True)
    st.markdown('---')
    st.header('Overall Analysis - Last 30 days :chart_with_upwards_trend:')
    st.markdown('---')
    st.markdown('###')
    st.plotly_chart(all_metrics_fig, use_container_width=True)
    st.markdown('---')
    st.markdown('###')
    st.header('Individual Analysis')
    st.markdown('---')
    sla_tab, rssi_tab, battery_tab = st.tabs(['SLA figure', 'RSSI figure', 'Battery figure'])
    with sla_tab:
        st.plotly_chart(sla_30days, use_container_width=True)
    with rssi_tab:
        st.plotly_chart(rssi_30days, use_container_width=True)
    with battery_tab:
        st.plotly_chart(battery_voltage30days, use_container_width=True)
    st.markdown('---')
    st.markdown('###')
    st.markdown('---')
    st.plotly_chart(boxplot_metrics, use_container_width=True)
    st.markdown('---')
    portzero_overall, portzero_segreg = st.tabs(['Port 0 Overall', 'Port 0 by Bussiness Unit'])
    port_zero_fig_overall = port_zero.port_zero_plot(data=port_zero_grouped_onlydate, x_axis='created_at', y_axis='code')
    port_zero_fig_segreg = port_zero.port_zero_plot(data=port_zero_grouped, x_axis='created_at', y_axis='code', segregate_bu=True)
    with portzero_overall:
        portzero_overall.plotly_chart(port_zero_fig_overall, use_container_width=True)

    with portzero_segreg:
        portzero_segreg.plotly_chart(port_zero_fig_segreg, use_container_width=True)
    st.markdown('---')
    # st.header('Daily Tranmissions Analysis')
    # st.markdown('---')
    # st.markdown('###')
    # daily_transmission_fig = transmissions.daily_transmissions(df_daily_transmissions)
    # st.plotly_chart(daily_transmission_fig, use_container_width=True)
    st.header('Daily Readings Analaysis')
    st.markdown('---')
    recent_readings_fig = recent_reading.recent_reading(data=df_recent_readings)
    st.plotly_chart(recent_readings_fig, use_container_width=True)
