import requests
import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter

# Credenziali di accesso
USERNAME = "admindama"
PASSWORD = "Damapoint24!"

# Funzione per controllare le credenziali
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Gestione dello stato dell'autenticazione
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Pagina di benvenuto e login
def welcome_page():
    st.title("Benvenuto in DamaPoint Dashboard")
    st.write("Per continuare, effettua il login inserendo username e password.")

    # Campi per inserimento username e password
    input_username = st.text_input("Username")
    input_password = st.text_input("Password", type="password")

    # Controlla le credenziali
    if st.button("Login"):
        if check_credentials(input_username, input_password):
            st.session_state.authenticated = True
            st.success("Accesso effettuato con successo!")
        else:
            st.error("Username o password errati!")


def dashboard():
    # Configura i dettagli della tua API Airtable
    AIRTABLE_API_KEY = "patVvkwrcLfpSQFlN.6284937647e50b10895d44cd1c0829a183bfd24d488be47ca84c9538f90938e3"
    BASE_ID = 'appGyD33GmhodfxlW'  # Il Base ID
    TABLE_ID = 'tblCPYQNiEie2tEyy'  # ID della tabella LEADS NUOVI

    # URL per la chiamata API
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

    # Header per l'autenticazione
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    # Funzione per ottenere tutti i dati da Airtable (gestione della paginazione)
    def get_all_airtable_data():
        all_records = []
        params = {}
        
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                all_records.extend(data['records'])
                
                # Se esiste un 'offset', continuiamo a paginare
                if 'offset' in data:
                    params['offset'] = data['offset']
                else:
                    break
            else:
                st.error(f"Errore nel recupero dei dati: {response.status_code}")
                break

        return all_records

    # Funzione per estrarre la parte del nome dell'istituto dopo il trattino '-'
    def pulisci_nome_istituto(nome_istituto):
        if '-' in nome_istituto:
            return nome_istituto.split('-', 1)[1].strip()  # Prende solo la parte dopo il trattino
        return nome_istituto

    # Otteniamo tutti i dati
    records = get_all_airtable_data()

    # Verifica se i dati sono stati ottenuti correttamente
    # Verifica se i dati sono stati ottenuti correttamente
    if records:
        # Fase 2: Elaborazione dei dati
        fields = [record['fields'] for record in records]
        
        # Numero totale di leads
        num_leads = len(fields)

        # Filtriamo i record con appuntamenti fissati e presentati
        appuntamenti_fissati = [record for record in fields if record.get('Esito telefonata') == 'App. Fissato']
        
        # Filtriamo i record dove il campo "Presentato/a" è True
        presentati = [record for record in fields if record.get('Presentato/a?')]

        # Numero totale di presentati
        num_presentati = len(presentati)

        # Somma totale dell'importo pagato
        importo_totale_pagato = sum(record.get('Importo pagato', 0) for record in fields if 'Importo pagato' in record)
        totale_appuntamenti_fissati = len(appuntamenti_fissati)
        # Estrai gli istituti di origine e puliamo i nomi
        istituti = [pulisci_nome_istituto(record['Istituto di origine']) for record in fields if 'Istituto di origine' in record]

        # Conteggi per istituto
        leads_per_istituto = Counter(istituti)
        appuntamenti_per_istituto = Counter([pulisci_nome_istituto(record['Istituto di origine']) for record in appuntamenti_fissati if 'Istituto di origine' in record])
        presentati_per_istituto = Counter([pulisci_nome_istituto(record['Istituto di origine']) for record in presentati if 'Istituto di origine' in record])
        importo_pagato_settimana_scorsa = 8000  # Esempio, sostituiscilo con il valore reale

        
        # Sommiamo l'importo pagato per istituto
        importo_pagato_per_istituto = {}
        for record in fields:
            istituto = pulisci_nome_istituto(record.get('Istituto di origine', ''))
            importo_pagato = record.get('Importo pagato', 0)
            if istituto:
                if istituto in importo_pagato_per_istituto:
                    importo_pagato_per_istituto[istituto] += importo_pagato
                else:
                    importo_pagato_per_istituto[istituto] = importo_pagato

        # Creiamo un DataFrame per visualizzare i dati aggregati
        df_metrics = pd.DataFrame({
            'Istituto di origine': list(leads_per_istituto.keys()),
            'Leads Generati': list(leads_per_istituto.values()),
            'Appuntamenti Fissati': [appuntamenti_per_istituto.get(istituto, 0) for istituto in leads_per_istituto.keys()],
            'Presentati': [presentati_per_istituto.get(istituto, 0) for istituto in leads_per_istituto.keys()],
            'Importo Pagato': [importo_pagato_per_istituto.get(istituto, 0) for istituto in leads_per_istituto.keys()]
        })
        
    else:
        st.warning("Nessun dato disponibile per la dashboard")
        num_leads = 0
        num_presentati = 0
        importo_totale_pagato = 0
        df_metrics = pd.DataFrame()

    # Sezione laterale (sidebar) per la selezione del tipo di grafico
    st.sidebar.title("DamaPoint Dashboard | benvenuto!")

    grafico_tipo = st.sidebar.selectbox(
        "Scegli il tipo di rappresentazione grafica",
        ["Barre", "Linee", "Torta"]
    )

    # Aggiungi CSS per centrare l'immagine nella sidebar
    st.sidebar.markdown("""
        <style>
        .sidebar-image {
            display: flex;
            justify-content: center;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Percorso dell'immagine (sostituisci con il percorso corretto)
    image_path = "logo.png"  # Sostituisci con il nome del file immagine nella directory del progetto

    # Visualizzazione dell'immagine nella sidebar
    st.sidebar.markdown('<div class="sidebar-image">', unsafe_allow_html=True)
    st.sidebar.image(image_path, use_column_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Simuliamo i valori della settimana scorsa (questi dovresti ottenerli dai tuoi dati)
    leads_settimana_scorsa = 1400  # Esempio, sostituisci con il valore reale
    appuntamenti_fissati_settimana_scorsa = 390  # Esempio, sostituisci con il valore reale
    presentati_settimana_scorsa = 20  # Esempio, sostituisci con il valore reale
    importo_pagato_settimana_scorsa = 8000  # Esempio, sostituisci con il valore reale

    # Calcolo delle variazioni percentuali
    if leads_settimana_scorsa > 0:
        variazione_leads = ((num_leads - leads_settimana_scorsa) / leads_settimana_scorsa) * 100
    else:
        variazione_leads = 0

    if appuntamenti_fissati_settimana_scorsa > 0:
        variazione_appuntamenti_fissati = ((totale_appuntamenti_fissati - appuntamenti_fissati_settimana_scorsa) / appuntamenti_fissati_settimana_scorsa) * 100
    else:
        variazione_appuntamenti_fissati = 0

    if presentati_settimana_scorsa > 0:
        variazione_presentati = ((num_presentati - presentati_settimana_scorsa) / presentati_settimana_scorsa) * 100
    else:
        variazione_presentati = 0

    if importo_pagato_settimana_scorsa > 0:
        variazione_importo_pagato = ((importo_totale_pagato - importo_pagato_settimana_scorsa) / importo_pagato_settimana_scorsa) * 100
    else:
        variazione_importo_pagato = 0



    # Fase 3: Creazione della dashboard con Streamlit
    st.title('Portale Dashboard Leads/Appuntamenti')

    # Crea quattro colonne per visualizzare i dati
    col1, col2, col3, col4 = st.columns(4)

    # Visualizzazione del numero di leads generati con la variazione percentuale nella prima colonna
    with col1:
        st.subheader('')
        st.metric(label="Totale Leads", value=num_leads, delta=f"{variazione_leads:.2f}%")
    

    # Visualizzazione del totale appuntamenti fissati con la variazione percentuale nella seconda colonna
    with col2:
        st.subheader(' ')
        st.metric(label="Appuntamenti Fissati", value=totale_appuntamenti_fissati, delta=f"{variazione_appuntamenti_fissati:.2f}%")


    # Visualizzazione del numero di presentati con la variazione percentuale nella terza colonna
    with col3:
        st.subheader('')
        st.metric(label="Totale Presentati", value=num_presentati, delta=f"{variazione_presentati:.2f}%")
    

    # Visualizzazione del valore dell'importo totale pagato con la variazione percentuale nella quarta colonna
    with col4:
        st.subheader('')
        st.metric(label="Importo Totale Pagato", value=f"€ {importo_totale_pagato:.2f}", delta=f"{variazione_importo_pagato:.2f}%")


    # Nuovo grafico: Leads, Appuntamenti Fissati, Presentati e Importo Pagato per Istituto

    if not df_metrics.empty:
        if grafico_tipo == "Barre":
            fig_leads = px.bar(df_metrics, x='Istituto di origine', 
                            y=['Leads Generati', 'Appuntamenti Fissati', 'Presentati'],
                            barmode='group', 
                            labels={'value': 'Numero', 'Istituto di origine': 'Istituto di Origine'},
                            title="Leads, Appuntamenti Fissati, Presentati per Istituto")
        elif grafico_tipo == "Linee":
            fig_leads = px.line(df_metrics, x='Istituto di origine', 
                                y=['Leads Generati', 'Appuntamenti Fissati', 'Presentati'],
                                labels={'value': 'Numero', 'Istituto di origine': 'Istituto di Origine'},
                                title="Leads, Appuntamenti Fissati, Presentati per Istituto")
        elif grafico_tipo == "Torta":
            st.write("Non è possibile visualizzare più variabili su un grafico a torta.")  # Avviso per l'utente
            fig_leads = None

        if fig_leads:
            st.plotly_chart(fig_leads)
    else:
        st.write("Nessun dato disponibile per questo grafico.")
    st.divider()
    # Nuova sezione: Grafico per Presentati e Importo Pagato per Istituto


    # Crea due colonne per mettere i grafici affiancati
    col1, col2 = st.columns(2)

    # Grafico Presentati per istituto nella prima colonna
    with col1:
        if not df_metrics.empty:
            if grafico_tipo == "Barre":
                fig_presentati = px.bar(df_metrics, x='Istituto di origine', 
                                        y='Presentati', 
                                        labels={'Presentati': 'Numero di Presentati', 'Istituto di origine': 'Istituto di Origine'},
                                        title="Numero di Presentati per Istituto")
            elif grafico_tipo == "Linee":
                fig_presentati = px.line(df_metrics, x='Istituto di origine', 
                                        y='Presentati', 
                                        labels={'Presentati': 'Numero di Presentati', 'Istituto di origine': 'Istituto di Origine'},
                                        title="Numero di Presentati per Istituto")
            elif grafico_tipo == "Torta":
                fig_presentati = px.pie(df_metrics, values='Presentati', names='Istituto di origine', 
                                        title="Percentuale di Presentati per Istituto")

            st.plotly_chart(fig_presentati)
        else:
            st.write("Nessun dato disponibile per il grafico dei presentati.")

    # Grafico Importo Pagato per istituto nella seconda colonna
    with col2:
        if not df_metrics.empty:
            if grafico_tipo == "Barre":
                fig_importo = px.bar(df_metrics, x='Istituto di origine', 
                                    y='Importo Pagato', 
                                    labels={'Importo Pagato': 'Importo Pagato (€)', 'Istituto di origine': 'Istituto di Origine'},
                                    title="Importo Pagato per Istituto")
            elif grafico_tipo == "Linee":
                fig_importo = px.line(df_metrics, x='Istituto di origine', 
                                    y='Importo Pagato', 
                                    labels={'Importo Pagato': 'Importo Pagato (€)', 'Istituto di origine': 'Istituto di Origine'},
                                    title="Importo Pagato per Istituto")
            elif grafico_tipo == "Torta":
                fig_importo = px.pie(df_metrics, values='Importo Pagato', names='Istituto di origine', 
                                    title="Percentuale Importo Pagato per Istituto")

            st.plotly_chart(fig_importo)
        else:
            st.write("Nessun dato disponibile per il grafico dell'importo pagato.")

    st.markdown("---")  # Una linea orizzontale
    # Nuova sezione con due colonne per Esito Telefonata e Motivi


    # Crea due colonne per i nuovi grafici
    col1, col2 = st.columns(2)

    # Grafico Esito Telefonata per numero di occorrenze nella prima colonna
    with col1:
        # Conta le occorrenze dei valori del campo 'Esito telefonata'
        esito_counter = Counter([record.get('Esito telefonata', 'Non specificato') for record in fields])

        # Crea un DataFrame per visualizzare i dati
        df_esito = pd.DataFrame({
            'Esito telefonata': list(esito_counter.keys()),
            'Numero': list(esito_counter.values())
        })

        if grafico_tipo == "Barre":
            fig_esito = px.bar(df_esito, x='Esito telefonata', y='Numero', 
                            labels={'Esito telefonata': 'Esito Telefonata', 'Numero': 'Numero'},
                            title="Dettaglio Esito Telefonata")
        elif grafico_tipo == "Linee":
            fig_esito = px.line(df_esito, x='Esito telefonata', y='Numero', 
                                labels={'Dettaglio Esito telefonata': 'Esito Telefonata', 'Numero': 'Numero'},
                                title="Dettaglio Esito Telefonata")
        elif grafico_tipo == "Torta":
            fig_esito = px.pie(df_esito, values='Numero', names='Esito telefonata', 
                            title="Percentuale Dettaglio Esito Telefonata")

        st.plotly_chart(fig_esito)

    # Grafico Motivi per numero di occorrenze nella seconda colonna
    with col2:
        # Gestione del campo 'Motivi' come array di stringhe multiple
        motivi_counter = Counter()
        for record in fields:
            motivi = record.get('Motivi', [])
            if isinstance(motivi, list):
                motivi_counter.update(motivi)

        # Crea un DataFrame per visualizzare i dati
        df_motivi = pd.DataFrame({
            'Motivi': list(motivi_counter.keys()),
            'Numero': list(motivi_counter.values())
        })

        if grafico_tipo == "Barre":
            fig_motivi = px.bar(df_motivi, x='Motivi', y='Numero', 
                                labels={'Motivi': 'Motivi', 'Numero': 'Numero'},
                                title="Motivo se non Presentato/a")
        elif grafico_tipo == "Linee":
            fig_motivi = px.line(df_motivi, x='Motivi', y='Numero', 
                                labels={'Motivi': 'Motivi', 'Numero': 'Numero'},
                                title="Motivo se non Presentato/a")
        elif grafico_tipo == "Torta":
            fig_motivi = px.pie(df_motivi, values='Numero', names='Motivi', 
                                title="Motivo se non Presentato/a")

        st.plotly_chart(fig_motivi)
    st.divider()

    # Parte interattiva: Selezione istituto e visualizzazione della tabella
    st.subheader('Dettagli degli Appuntamenti per Istituto')
    istituto_selezionato = st.selectbox("Seleziona l'Istituto di Origine", options=df_metrics['Istituto di origine'])

    # Filtriamo i record per l'istituto selezionato e visualizziamo la tabella
    if istituto_selezionato:
        appuntamenti_istituto = df_metrics[df_metrics['Istituto di origine'] == istituto_selezionato]
        st.write(f"Appuntamenti per {istituto_selezionato}:")
        st.dataframe(appuntamenti_istituto)

# Mostra la pagina di benvenuto o la dashboard in base all'autenticazione
if st.session_state.authenticated:
    dashboard()
else:
    welcome_page()
