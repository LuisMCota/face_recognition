import streamlit as st
import pandas as pd
import plotly.express as px

def apply_filters(df):
    col1, col2 = st.columns(2)
    selected_name = col1.selectbox("Selecciona el nombre del alumno:", options=[""] + list(df['CorrectName'].unique()))
    min_date, max_date = df['Date'].min(), df['Date'].max()
    start_date, end_date = col2.date_input("Selecciona el rango de fechas:", [min_date, max_date])
    
    if selected_name:
        df = df[df['CorrectName'] == selected_name]
    if start_date and end_date:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return df

def display_totals(filtered_df):
    st.write("### Totales de Asistencia")
    total_counts = filtered_df['Status'].value_counts()
    attended_count = total_counts.get('attended', 0)
    tardy_count = total_counts.get('tardy', 0)
    missed_count = total_counts.get('missed', 0)
    total_classes = attended_count + tardy_count + missed_count
    total_attendance = attended_count + tardy_count

    col1, col2, col3 = st.columns(3)
    col1.metric("A Tiempo", attended_count)
    col2.metric("Tarde", tardy_count)
    col3.metric("Ausente", missed_count)

    attendance_percentage = (total_attendance / total_classes) * 100 if total_classes > 0 else 0
    status_message = f"Estado: {'Aprobado' if attendance_percentage >= 80 else 'No aprobado'} ({attendance_percentage:.2f}% de asistencia)"
    st.success(status_message) if attendance_percentage >= 80 else st.error(status_message)

def display_attendance_chart(filtered_df):
    attendance_by_date = filtered_df.groupby(['Date', 'Status']).size().reset_index(name='Count')
    fig = px.bar(attendance_by_date, x='Date', y='Count', color='Status', labels={'Count': 'Cantidad', 'Date': 'Fecha'}, title="Asistencias por Fecha", barmode='stack')
    st.plotly_chart(fig)
