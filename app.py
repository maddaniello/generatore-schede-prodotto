import streamlit as st
import pandas as pd
import openai
import anthropic
import json
import time
from typing import Dict, List, Optional, Tuple
import io
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import zipfile
import base64
from pathlib import Path
from PIL import Image
import urllib.request

# Configurazione pagina
st.set_page_config(
    page_title="Moca - Generatore Schede Prodotto",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Personalizzato con i colori del logo
# CSS Personalizzato con i colori del logo + DARK MODE SUPPORT
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Figtree', sans-serif;
    }
    
    /* Colori principali */
    :root {
        --primary-red: #E52217;
        --primary-black: #191919;
        --light-pink: #FFE7E6;
        --gray: #8A8A8A;
        --white: #FFFFFF;
    }
    
    /* ========== DARK MODE SUPPORT ========== */
    [data-testid="stAppViewContainer"] {
        background-color: var(--white);
    }
    
    /* Dark mode override */
    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"] {
            background-color: #1E1E1E !important;
        }
    }
    
    /* Force light background in main content */
    .main .block-container {
        background-color: var(--white);
        padding: 2rem;
        border-radius: 16px;
    }
    
    /* Dark mode text colors */
    @media (prefers-color-scheme: dark) {
        .main .block-container {
            background-color: #2D2D2D !important;
            color: #FFFFFF !important;
        }
        
        /* Step container dark mode */
        .step-container {
            background-color: #2D2D2D !important;
            border: 2px solid #E52217 !important;
            color: #FFFFFF !important;
        }
        
        .step-title {
            color: #FFFFFF !important;
        }
        
        /* Info card dark */
        .info-card {
            background-color: #3A3A3A !important;
            color: #FFFFFF !important;
        }
        
        /* Product preview dark */
        .product-preview {
            background: linear-gradient(135deg, #2D2D2D 0%, #3A3A3A 100%) !important;
            border: 3px solid var(--primary-red) !important;
        }
        
        .product-title-preview {
            color: #FFFFFF !important;
        }
        
        .product-meta {
            background-color: #3A3A3A !important;
        }
        
        .product-field-label {
            color: #CCCCCC !important;
        }
        
        .product-field-content {
            color: #FFFFFF !important;
        }
        
        /* Input fields dark */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background-color: #3A3A3A !important;
            color: #FFFFFF !important;
            border: 2px solid #555555 !important;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #888888 !important;
        }
        
        /* Labels dark */
        label, .stMarkdown p, .stMarkdown li {
            color: #FFFFFF !important;
        }
        
        /* Dataframe dark */
        [data-testid="stDataFrame"] {
            background-color: #2D2D2D !important;
        }
        
        /* Expander dark */
        .streamlit-expanderHeader {
            background-color: #3A3A3A !important;
            color: #FFFFFF !important;
        }
        
        /* File uploader dark */
        [data-testid="stFileUploader"] {
            background-color: #3A3A3A !important;
            border: 2px dashed #E52217 !important;
        }
        
        /* Checkbox dark */
        .stCheckbox label {
            color: #FFFFFF !important;
        }
        
        /* Metric cards - keep red */
        .metric-card {
            background: linear-gradient(135deg, var(--primary-red) 0%, #c91d13 100%) !important;
            color: var(--white) !important;
        }
        
        /* Progress container dark */
        .progress-container {
            background-color: #3A3A3A !important;
        }
        
        /* Code blocks dark */
        code {
            background-color: #3A3A3A !important;
            color: #FFFFFF !important;
        }
        
        /* Tabs dark */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #2D2D2D !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #FFFFFF !important;
        }
        
        /* Multiselect dark */
        .stMultiSelect [data-baseweb="select"] {
            background-color: #3A3A3A !important;
        }
        
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #E52217 !important;
            color: #FFFFFF !important;
        }
        
        /* Slider dark */
        .stSlider [data-testid="stTickBar"] {
            background-color: #3A3A3A !important;
        }
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-red) 0%, #c91d13 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(229, 34, 23, 0.15);
    }
    
    .main-header h1 {
        color: var(--white);
        font-weight: 800;
        font-size: 2.5rem;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        color: var(--light-pink);
        text-align: center;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Step Container */
    .step-container {
        background-color: var(--white);
        border: 2px solid var(--light-pink);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(25, 25, 25, 0.08);
    }
    
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--light-pink);
    }
    
    .step-number {
        background: var(--primary-red);
        color: var(--white);
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
        margin-right: 1rem;
        box-shadow: 0 4px 12px rgba(229, 34, 23, 0.3);
    }
    
    .step-title {
        color: var(--primary-black);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary-red);
        color: var(--white);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(229, 34, 23, 0.3);
    }
    
    .stButton > button:hover {
        background-color: #c91d13;
        box-shadow: 0 6px 20px rgba(229, 34, 23, 0.4);
        transform: translateY(-2px);
    }
    
    /* Progress Bar */
    .progress-container {
        background-color: var(--light-pink);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stProgress > div > div {
        background-color: var(--primary-red);
    }
    
    /* Cards */
    .info-card {
        background-color: var(--light-pink);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Product Preview Card */
    .product-preview {
        background: linear-gradient(135deg, var(--white) 0%, var(--light-pink) 100%);
        border: 3px solid var(--primary-red);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(229, 34, 23, 0.15);
    }
    
    .product-title-preview {
        color: var(--primary-black);
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .product-meta {
        background-color: var(--white);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .product-field-label {
        color: var(--gray);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .product-field-content {
        color: var(--primary-black);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Navigation Buttons */
    .nav-button {
        background-color: var(--primary-black);
        color: var(--white);
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.5rem;
        font-weight: 800;
    }
    
    .nav-button:hover {
        background-color: var(--primary-red);
        transform: scale(1.1);
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, var(--primary-red) 0%, #c91d13 100%);
        color: var(--white);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(229, 34, 23, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 600;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid var(--light-pink);
        border-radius: 8px;
        font-family: 'Figtree', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-red);
        box-shadow: 0 0 0 2px rgba(229, 34, 23, 0.1);
    }
    
    /* Checkbox */
    .stCheckbox > label {
        font-weight: 600;
        color: var(--primary-black);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--light-pink);
        border-radius: 8px;
        font-weight: 600;
        color: var(--primary-black);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--light-pink);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-red);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #c91d13;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--light-pink);
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-red);
    }
</style>
""", unsafe_allow_html=True)

# Classe ProductCardGenerator (identica a prima)
class ProductCardGenerator:
    def filter_relevant_search_results(generator, ean: str, urls: List[str], product_data: Dict, column_mapping: Dict) -> List[str]:
        """
        Filtra i risultati di ricerca EAN escludendo quelli semanticamente non pertinenti.
        Usa l'AI per determinare la rilevanza in base ai dati del prodotto.
        """
        if not urls or len(urls) <= 1:
            return urls  # Se c'è solo 1 risultato o nessuno, non filtrare
        
        # Costruisci contesto prodotto dalle colonne mappate
        product_context = []
        for csv_col, var_name in column_mapping.items():
            value = product_data.get(csv_col, "")
            if pd.notna(value) and str(value).strip():
                product_context.append(f"{var_name}: {value}")
        
        product_context_str = "\n".join(product_context) if product_context else "Informazioni prodotto non disponibili"
        
        # Scrape rapido dei titoli delle pagine
        page_titles = []
        for url in urls[:10]:  # Max 10 URL per evitare timeout
            try:
                response = requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.title.get_text(strip=True) if soup.title else "Titolo non disponibile"
                    
                    # Estrai anche H1 e meta description per più contesto
                    h1 = soup.find('h1')
                    h1_text = h1.get_text(strip=True) if h1 else ""
                    
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    meta_text = meta_desc.get('content') if meta_desc and meta_desc.get('content') else ""
                    
                    page_info = f"URL: {url}\nTitolo: {title}\nH1: {h1_text}\nDescrizione: {meta_text}"
                    page_titles.append(page_info)
                else:
                    page_titles.append(f"URL: {url}\nTitolo: [Errore caricamento]")
            except:
                page_titles.append(f"URL: {url}\nTitolo: [Errore caricamento]")
            
            time.sleep(0.3)  # Rate limiting
        
        # Prompt per AI: valuta rilevanza
        prompt = f"""Sei un esperto analista di e-commerce. Il tuo compito è valutare quali risultati di ricerca sono PERTINENTI al prodotto target.
    
    **PRODOTTO TARGET (EAN: {ean}):**
    {product_context_str}
    
    **RISULTATI RICERCA GOOGLE:**
    {chr(10).join([f"{i+1}. {page}" for i, page in enumerate(page_titles)])}
    
    **COMPITO:**
    Analizza ogni risultato e determina se è PERTINENTE al prodotto target. 
    Un risultato è pertinente se descrive lo STESSO prodotto o un prodotto MOLTO simile nella stessa categoria.
    Un risultato NON è pertinente se descrive un prodotto completamente diverso (altra categoria, altro uso, ecc.)
    
    **IMPORTANTE:**
    - Sii RIGOROSO: anche se l'EAN è presente, se il prodotto descritto è diverso, marcalo come NON pertinente
    - Ignora risultati su marketplace generici che potrebbero avere EAN sbagliati
    - Considera pertinenti solo prodotti della stessa categoria merceologica
    
    Rispondi SOLO con un JSON nel formato:
    {{
        "relevant_indices": [1, 2, ...],
        "reasoning": {{
            "1": "Breve spiegazione perché pertinente o meno",
            "2": "Breve spiegazione perché pertinente o meno",
            ...
        }}
    }}
    
    Includi in "relevant_indices" SOLO gli indici (1-based) dei risultati PERTINENTI.
    """
    
        try:
            # Chiama AI per valutazione
            if generator.ai_provider == "OpenAI":
                response = generator.openai_client.chat.completions.create(
                    model=generator.model,
                    messages=[
                        {"role": "system", "content": "Sei un esperto analista di e-commerce. Rispondi sempre in formato JSON valido."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3  # Bassa temperatura per risposte più deterministiche
                )
                content = response.choices[0].message.content.strip()
            
            elif generator.ai_provider == "Claude":
                response = generator.anthropic_client.messages.create(
                    model=generator.model,
                    max_tokens=1000,
                    temperature=0.3,
                    system="Sei un esperto analista di e-commerce. Rispondi sempre in formato JSON valido.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text.strip()
            else:
                return urls  # Fallback: restituisci tutti gli URL
            
            # Parse risposta JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                relevant_indices = result.get('relevant_indices', [])
                reasoning = result.get('reasoning', {})
                
                # Filtra URL pertinenti (converti da 1-based a 0-based)
                filtered_urls = [urls[i-1] for i in relevant_indices if 0 < i <= len(urls)]
                
                # Log del filtro
                excluded_count = len(urls) - len(filtered_urls)
                if excluded_count > 0:
                    st.warning(f"🔍 **Filtro Semantico EAN {ean}:** Esclusi {excluded_count} risultati non pertinenti")
                    
                    with st.expander(f"📋 Dettagli Filtro EAN {ean}", expanded=False):
                        for i, url in enumerate(urls, 1):
                            if i in relevant_indices:
                                st.success(f"✅ **Risultato {i}** - PERTINENTE")
                                st.caption(f"URL: {url}")
                                if str(i) in reasoning:
                                    st.caption(f"Motivo: {reasoning[str(i)]}")
                            else:
                                st.error(f"❌ **Risultato {i}** - ESCLUSO")
                                st.caption(f"URL: {url}")
                                if str(i) in reasoning:
                                    st.caption(f"Motivo: {reasoning[str(i)]}")
                            st.markdown("---")
                else:
                    st.success(f"✅ **Filtro Semantico EAN {ean}:** Tutti i risultati sono pertinenti")
                
                return filtered_urls if filtered_urls else urls[:1]  # Mantieni almeno 1 URL
            else:
                return urls  # Fallback: JSON parsing fallito
        
        except Exception as e:
            st.warning(f"⚠️ Errore filtro semantico per EAN {ean}: {e}")
            return urls  # Fallback: restituisci tutti gli URL
    
    def deduplicate_products(csv_data: pd.DataFrame, code_column: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Deduplica i prodotti in base al codice prodotto.
    Restituisce:
    - DataFrame con prodotti unici da elaborare
    - Dizionario di mappatura {indice_originale: codice_prodotto}
    """
    if not code_column or code_column not in csv_data.columns:
        return csv_data, {}
    
    # Normalizza i codici prodotto
    csv_data['_normalized_code'] = csv_data[code_column].apply(
        lambda x: str(x).strip().strip("'").strip('"')
    )
    
    # Trova prodotti unici (prima occorrenza di ogni codice)
    unique_products = csv_data.drop_duplicates(subset='_normalized_code', keep='first')
    
    # Crea mappatura: indice_originale -> codice_prodotto
    code_mapping = {}
    for idx, row in csv_data.iterrows():
        code_mapping[idx] = row['_normalized_code']
    
    # Statistiche deduplicazione
    total_products = len(csv_data)
    unique_count = len(unique_products)
    duplicates = total_products - unique_count
    
    if duplicates > 0:
        st.info(f"""
        🔄 **Deduplicazione Intelligente Attivata**
        - Prodotti totali nel CSV: **{total_products}**
        - Prodotti unici da elaborare: **{unique_count}**
        - Duplicati rilevati: **{duplicates}** (verranno riutilizzati i contenuti)
        - Risparmio stimato: **~{(duplicates / total_products * 100):.1f}%** di risorse AI
        """)
    
    return unique_products.drop(columns=['_normalized_code']), code_mapping

def expand_results_to_original(results: List[Dict], code_mapping: Dict, 
                               csv_data: pd.DataFrame, code_column: str) -> List[Dict]:
    """
    Espande i risultati per coprire tutte le righe originali del CSV,
    duplicando i contenuti generati per prodotti con stesso SKU.
    """
    # Crea dizionario: codice_prodotto -> risultato generato
    results_by_code = {}
    for result in results:
        code = result.get('codice_prodotto', '')
        results_by_code[code] = result
    
    # Espandi i risultati per tutte le righe originali
    expanded_results = []
    
    for idx in csv_data.index:
        original_code = str(csv_data.loc[idx, code_column]).strip().strip("'").strip('"')
        
        if original_code in results_by_code:
            # Copia il risultato generato
            expanded_result = results_by_code[original_code].copy()
            
            # Aggiungi eventuali dati specifici della riga (come taglia, colore, ecc.)
            # Questo permette di mantenere le varianti nel CSV finale
            for col in csv_data.columns:
                if col not in expanded_result and col != code_column:
                    expanded_result[f'original_{col}'] = csv_data.loc[idx, col]
            
            expanded_results.append(expanded_result)
        else:
            # Prodotto non generato (errore)
            expanded_results.append({
                'codice_prodotto': original_code,
                'errore': 'ERRORE - NON GENERATO'
            })
    
    return expanded_results
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.serper_api_key = None
        self.ai_provider = None
        self.model = None
        self.product_images = st.session_state.get('product_images_dict', {})
        
    def setup_ai(self, provider: str, api_key: str, model: str) -> bool:
        """Configura il client AI (OpenAI o Claude)"""
        try:
            self.ai_provider = provider
            self.model = model
            
            if provider == "OpenAI":
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.openai_client.models.list()
                return True
            elif provider == "Claude":
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
                return True
        except Exception as e:
            st.error(f"❌ Errore nella configurazione {provider}: {e}")
            return False
    
    def setup_serper(self, api_key: str) -> bool:
        """Configura Serper.dev API"""
        try:
            self.serper_api_key = api_key
            response = requests.post(
                'https://google.serper.dev/search',
                headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
                json={'q': 'test', 'num': 1}
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"❌ Errore configurazione Serper: {e}")
            return False
    
    def load_images_from_zip(self, zip_file) -> Dict[str, List[bytes]]:
        """Carica immagini da file ZIP"""
        images_dict = {}
        supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
        
        total_files = 0
        skipped_files = 0
        invalid_images = 0
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    total_files += 1
                    
                    if (file_name.endswith('/') or 
                        file_name.startswith('__MACOSX') or 
                        '/__MACOSX' in file_name or
                        file_name.startswith('.') or
                        '/.DS_Store' in file_name or
                        file_name.endswith('.DS_Store') or
                        '._' in file_name):
                        skipped_files += 1
                        continue
                    
                    file_ext = Path(file_name).suffix.lower()
                    
                    if file_ext in supported_formats:
                        file_stem = Path(file_name).stem
                        product_code = file_stem.strip().strip("'").strip('"')
                        
                        if '_' in product_code:
                            parts = product_code.split('_')
                            last_part = parts[-1].lower()
                            
                            if (parts[-1].isdigit() or 
                                last_part in ['front', 'back', 'side', 'top', 'bottom', 
                                             'fronte', 'retro', 'lato', 'sopra', 'sotto',
                                             '1', '2', '3', '4', '5']):
                                product_code = '_'.join(parts[:-1])
                        
                        product_code = product_code.strip().strip("'").strip('"')
                        
                        image_data = zip_ref.read(file_name)
                        
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            img.verify()
                            
                            if product_code not in images_dict:
                                images_dict[product_code] = []
                            images_dict[product_code].append(image_data)
                            
                        except Exception as e:
                            invalid_images += 1
                            continue
                    else:
                        skipped_files += 1
                
                self.product_images = images_dict
                st.session_state.product_images_dict = images_dict
                
                total_images = sum(len(imgs) for imgs in images_dict.values())
                
                return images_dict
                
        except Exception as e:
            st.error(f"❌ Errore nel caricamento dello ZIP: {e}")
            return {}
    
    def encode_image_to_base64(self, image_data: bytes) -> str:
        """Converte immagine in base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    def analyze_image_with_openai(self, image_data: bytes, image_index: int = 1, total_images: int = 1) -> str:
        """Analizza immagine con GPT-4 Vision"""
        try:
            base64_image = self.encode_image_to_base64(image_data)
            
            if total_images > 1:
                context_text = f"""Analizza questa immagine prodotto (immagine {image_index} di {total_images}). 
IMPORTANTE: Concentrati SOLO sul prodotto, IGNORA completamente eventuali persone/modelli presenti.

Descrivi in modo dettagliato:"""
            else:
                context_text = """Analizza questa immagine prodotto in modo dettagliato.
IMPORTANTE: Concentrati SOLO sul prodotto, IGNORA completamente eventuali persone/modelli presenti.

Descrivi:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""{context_text}
1. Tipo di prodotto e categoria
2. Caratteristiche visibili del PRODOTTO (colori, materiali, texture, pattern)
3. Design e stile del PRODOTTO
4. Dettagli distintivi
5. Forma e silhouette
6. Contesto d'uso
7. Qualità percepita

NON menzionare persone. Descrivi SOLO il prodotto.
Rispondi in italiano."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return ""
    
    def analyze_image_with_claude(self, image_data: bytes, image_index: int = 1, total_images: int = 1) -> str:
        """Analizza immagine con Claude Vision"""
        try:
            base64_image = self.encode_image_to_base64(image_data)
            
            img = Image.open(io.BytesIO(image_data))
            format_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'WEBP': 'image/webp',
                'GIF': 'image/gif'
            }
            media_type = format_map.get(img.format, 'image/jpeg')
            
            if total_images > 1:
                context_text = f"""Analizza questa immagine prodotto (immagine {image_index} di {total_images}). 
IMPORTANTE: Concentrati SOLO sul prodotto, IGNORA completamente eventuali persone/modelli presenti.

Descrivi in modo dettagliato:"""
            else:
                context_text = """Analizza questa immagine prodotto in modo dettagliato.
IMPORTANTE: Concentrati SOLO sul prodotto, IGNORA completamente eventuali persone/modelli presenti.

Descrivi:"""
            
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": f"""{context_text}
1. Tipo di prodotto e categoria
2. Caratteristiche visibili del PRODOTTO (colori, materiali, texture, pattern)
3. Design e stile del PRODOTTO
4. Dettagli distintivi
5. Forma e silhouette
6. Contesto d'uso
7. Qualità percepita

NON menzionare persone. Descrivi SOLO il prodotto.
Rispondi in italiano."""
                            }
                        ]
                    }
                ],
            )
            
            return response.content[0].text
            
        except Exception as e:
            return ""
    
    def analyze_product_image(self, product_code: str) -> Tuple[Optional[bytes], str]:
        """Analizza immagine prodotto"""
        normalized_code = str(product_code).strip().strip("'").strip('"')
        
        if normalized_code in st.session_state.image_analysis_db:
            analysis = st.session_state.image_analysis_db[normalized_code]
            return None, analysis
        
        return None, ""
    
    def pre_analyze_all_images(self, product_codes: List[str]) -> Dict[str, str]:
        """Pre-analizza tutte le immagini"""
        analysis_db = {}
        
        codes_with_images = [code for code in product_codes if code in self.product_images]
        
        if not codes_with_images:
            return {}
        
        total_images = sum(len(self.product_images[code]) for code in codes_with_images)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        image_count = 0
        
        for code in codes_with_images:
            images_list = self.product_images[code]
            num_images = len(images_list)
            
            product_analyses = []
            
            for img_index, image_data in enumerate(images_list, 1):
                image_count += 1
                status_text.text(f"Analizzando immagine {image_count}/{total_images}: {code}")
                
                if self.ai_provider == "OpenAI":
                    analysis = self.analyze_image_with_openai(image_data, img_index, num_images)
                elif self.ai_provider == "Claude":
                    analysis = self.analyze_image_with_claude(image_data, img_index, num_images)
                else:
                    analysis = ""
                
                if analysis:
                    product_analyses.append(f"[Immagine {img_index}]: {analysis}")
                
                progress_bar.progress(image_count / total_images)
                time.sleep(1)
            
            if product_analyses:
                if len(product_analyses) == 1:
                    combined_analysis = product_analyses[0].replace("[Immagine 1]: ", "")
                else:
                    combined_analysis = f"PRODOTTO CON {len(product_analyses)} IMMAGINI:\n\n" + "\n\n".join(product_analyses)
                
                analysis_db[code] = combined_analysis
        
        progress_bar.empty()
        status_text.empty()
        
        st.session_state.image_analysis_db = analysis_db
        st.session_state.images_analyzed = True
        
        return analysis_db
    
    def search_ean_on_google(self, ean: str, num_results: int = 5) -> List[str]:
        """Cerca EAN su Google"""
        if not self.serper_api_key:
            return []
        
        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers={
                    'X-API-KEY': self.serper_api_key,
                    'Content-Type': 'application/json'
                },
                json={
                    'q': f'{ean} prodotto',
                    'num': num_results,
                    'gl': 'it',
                    'hl': 'it'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                urls = []
                
                if 'organic' in data:
                    for result in data['organic'][:num_results]:
                        if 'link' in result:
                            urls.append(result['link'])
                
                return urls
            else:
                return []
                
        except Exception as e:
            return []
    
    def scrape_product_page(self, url: str) -> str:
        """Scrape contenuto pagina prodotto"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                                    'aside', 'form', 'iframe', 'noscript', 'svg']):
                    element.decompose()
                
                for element in soup.find_all(class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in 
                    ['menu', 'nav', 'sidebar', 'footer', 'header', 'cookie', 
                     'popup', 'modal', 'ad', 'banner', 'social', 'share']
                )):
                    element.decompose()
                
                for element in soup.find_all(id=lambda x: x and any(
                    keyword in str(x).lower() for keyword in 
                    ['menu', 'nav', 'sidebar', 'footer', 'header', 'cookie']
                )):
                    element.decompose()
                
                extracted_parts = []
                
                if soup.title:
                    title_text = soup.title.get_text(strip=True)
                    extracted_parts.append(f"TITOLO: {title_text}")
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    extracted_parts.append(f"DESCRIZIONE: {meta_desc['content']}")
                
                h1_tags = soup.find_all('h1')
                for h1 in h1_tags[:3]:
                    h1_text = h1.get_text(strip=True)
                    if h1_text:
                        extracted_parts.append(f"H1: {h1_text}")
                
                main_content = soup.find('main') or soup.find('article') or soup.find(class_=lambda x: x and 'content' in str(x).lower())
                
                if main_content:
                    text = main_content.get_text(separator=' ', strip=True)
                else:
                    text = soup.get_text(separator=' ', strip=True)
                
                text = re.sub(r'\s+', ' ', text)
                text = re.sub(r'[\r\n\t]+', ' ', text)
                
                combined = " | ".join(extracted_parts) + " | CONTENUTO: " + text
                
                return combined[:1500]
            
            else:
                return self._scrape_with_raw_request(url)
        
        except requests.exceptions.RequestException as e:
            return self._scrape_with_raw_request(url)
        
        except Exception as e:
            return ""
    
    def _scrape_with_raw_request(self, url: str) -> str:
        """Metodo alternativo scraping"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                soup = BeautifulSoup(html, 'html.parser')
                
                for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                    element.decompose()
                
                title = soup.title.get_text(strip=True) if soup.title else ""
                
                text = soup.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text)
                
                combined = f"TITOLO: {title} | CONTENUTO: {text}"
                return combined[:1500]
        
        except Exception as e:
            return ""
    
        def get_ean_context(self, ean: str, product_code: str = None, product_data: Dict = None, 
                        column_mapping: Dict = None) -> str:
        """Ottieni contesto da EAN con filtro semantico"""
        ean_log = {
            'timestamp': datetime.now().isoformat(),
            'ean': ean,
            'product_code': product_code or 'N/A',
            'search_results': [],
            'filtered_results': [],
            'excluded_results': [],
            'scraped_data': [],
            'total_characters': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0
        }
        
        # Cerca su Google
        urls = self.search_ean_on_google(ean)
        
        if not urls:
            st.warning(f"⚠️ Nessun risultato trovato per EAN: {ean}")
            ean_log['status'] = 'no_results'
            st.session_state.ean_logs.append(ean_log)
            return ""
        
        st.info(f"🔍 Trovati {len(urls)} risultati per EAN: {ean}")
        ean_log['search_results'] = urls
        
        # ✅ FILTRO SEMANTICO: Valuta pertinenza risultati
        if product_data and column_mapping:
            with st.spinner(f"🧠 Analisi semantica risultati per EAN {ean}..."):
                filtered_urls = filter_relevant_search_results(
                    self, ean, urls, product_data, column_mapping
                )
                
                ean_log['filtered_results'] = filtered_urls
                ean_log['excluded_results'] = [url for url in urls if url not in filtered_urls]
                
                urls = filtered_urls
        
        if not urls:
            st.error(f"❌ Tutti i risultati sono stati esclusi come non pertinenti per EAN: {ean}")
            ean_log['status'] = 'all_filtered'
            st.session_state.ean_logs.append(ean_log)
            return ""
        
        st.success(f"✅ Procedo con {len(urls)} risultati pertinenti")
        
        # Scrape contenuto
        contexts = []
        
        for i, url in enumerate(urls):
            content = ""
            for attempt in range(2):
                content = self.scrape_product_page(url)
                if content:
                    break
                elif attempt == 0:
                    time.sleep(2)
            
            scrape_log = {
                'url': url,
                'position': i + 1,
                'characters_extracted': len(content),
                'success': bool(content)
            }
            
            if content:
                contexts.append(content)
                ean_log['successful_scrapes'] += 1
                scrape_log['preview'] = content[:200]
            else:
                ean_log['failed_scrapes'] += 1
                scrape_log['preview'] = None
            
            ean_log['scraped_data'].append(scrape_log)
            time.sleep(0.5)
        
        combined_context = "\n\n".join(contexts)
        ean_log['total_characters'] = len(combined_context)
        
        if combined_context:
            ean_log['status'] = 'success'
            st.success(f"✅ Estratti {len(contexts)} contenuti pertinenti ({len(combined_context)} caratteri)")
        else:
            ean_log['status'] = 'failed'
            st.warning(f"⚠️ Nessun contenuto estratto per EAN: {ean}")
        
        st.session_state.ean_logs.append(ean_log)
        
        return combined_context
    
    def create_prompt(self, product_data: Dict, site_info: Dict, column_mapping: Dict, 
                     additional_instructions: str, fields_to_generate: List[str], 
                     ean_context: str = "", image_analysis: str = "") -> str:
        """Crea prompt per AI"""
        
        product_info = []
        for csv_col, var_name in column_mapping.items():
            value = product_data.get(csv_col, "")
            if pd.notna(value) and str(value).strip():
                product_info.append(f"{var_name}: {value}")
        
        product_info_str = "\n".join(product_info)
        
        ean_section = ""
        if ean_context:
            ean_section = f"""
INFORMAZIONI DA RICERCA EAN:
{ean_context[:3000]}
"""
        
        image_section = ""
        if image_analysis:
            image_section = f"""
ANALISI VISIVA DEL PRODOTTO:
{image_analysis}

IMPORTANTE: Utilizza le informazioni visive per arricchire le descrizioni.
"""
        
        fields_instructions = []
        fields_json = {}
        
        if "Titolo Prodotto" in fields_to_generate:
            fields_instructions.append("1. TITOLO PRODOTTO: Accattivante e informativo, max 80 caratteri")
            fields_json["titolo"] = "..."
        
        if "Short Description" in fields_to_generate:
            fields_instructions.append("2. SHORT DESCRIPTION: Breve e coinvolgente, max 160 caratteri")
            fields_json["short_description"] = "..."
        
        if "Description" in fields_to_generate:
            fields_instructions.append("3. DESCRIPTION: Completa e dettagliata, max 1000 caratteri")
            fields_json["description"] = "..."
        
        if "Bullet Points" in fields_to_generate:
            fields_instructions.append("4. BULLET POINTS: 5 punti chiave caratteristiche/benefici")
            fields_json["bullet_points"] = ["...", "...", "...", "...", "..."]
        
        if "Meta Title" in fields_to_generate:
            fields_instructions.append("5. META-TITLE SEO: Ottimizzato per motori di ricerca, max 60 caratteri")
            fields_json["meta_title"] = "..."
        
        if "Meta Description" in fields_to_generate:
            fields_instructions.append("6. META-DESCRIPTION SEO: Ottimizzata per CTR, max 155 caratteri")
            fields_json["meta_description"] = "..."
        
        if "URL" in fields_to_generate:
            fields_instructions.append("7. URL SLUG: URL-friendly, solo minuscole e trattini, max 80 caratteri")
            fields_json["url_slug"] = "..."
        
        fields_instructions_str = "\n".join(fields_instructions)
        
        prompt = f"""Sei un esperto copywriter specializzato in e-commerce e SEO.

INFORMAZIONI SITO:
- Nome sito: {site_info['site_name']}
- URL: {site_info['site_url']}
- Tone of voice: {site_info['tone_of_voice']}

DATI PRODOTTO:
{product_info_str}
{ean_section}
{image_section}

ISTRUZIONI AGGIUNTIVE:
{additional_instructions if additional_instructions else "Nessuna istruzione specifica"}

COMPITO:
Genera ESATTAMENTE i seguenti elementi per questo prodotto:

{fields_instructions_str}

FORMATO RISPOSTA (JSON):
{json.dumps(fields_json, indent=2, ensure_ascii=False)}

Importante: Rispondi SOLO con il JSON, senza testo aggiuntivo."""

        return prompt
    
    def generate_with_openai(self, prompt: str) -> Optional[str]:
        """Genera contenuto con OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un esperto copywriter per e-commerce. Rispondi sempre e solo in formato JSON valido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return None
    
    def generate_with_claude(self, prompt: str) -> Optional[str]:
        """Genera contenuto con Claude"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system="Sei un esperto copywriter per e-commerce. Rispondi sempre e solo in formato JSON valido.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return None
    
        def generate_product_content(self, product_data: Dict, site_info: Dict, 
                                column_mapping: Dict, additional_instructions: str,
                                fields_to_generate: List[str], ean_column: str = None,
                                product_code: str = None, use_image_analysis: bool = False) -> Optional[Dict]:
        """Genera contenuti prodotto con filtro semantico EAN"""
        max_retries = 3
        retry_delay = 1
        
        image_analysis = ""
        if use_image_analysis and product_code:
            image_data, image_analysis = self.analyze_product_image(product_code)
        
        # ✅ Passa product_data e column_mapping per filtro semantico
        ean_context = ""
        if ean_column and ean_column in product_data:
            ean = str(product_data[ean_column])
            if ean and ean.strip() and ean != 'nan':
                ean_context = self.get_ean_context(ean, product_code, product_data, column_mapping)
        
        for attempt in range(max_retries):
            try:
                prompt = self.create_prompt(product_data, site_info, column_mapping, 
                                          additional_instructions, fields_to_generate, 
                                          ean_context, image_analysis)
                
                if self.ai_provider == "OpenAI":
                    content = self.generate_with_openai(prompt)
                elif self.ai_provider == "Claude":
                    content = self.generate_with_claude(prompt)
                else:
                    return None
                
                if not content:
                    continue
                
                try:
                    result = json.loads(content)
                    return result
                except json.JSONDecodeError:
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                        return result
                    else:
                        if attempt == max_retries - 1:
                            return None
                        continue
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    return None
                else:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
        
        return None

# Inizializzazione Session State
def initialize_session_state():
    """Inizializza session state"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = 'idle'
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'total_products' not in st.session_state:
        st.session_state.total_products = 0
    if 'batch_size' not in st.session_state:
        st.session_state.batch_size = 10
    if 'fields_to_generate' not in st.session_state:
        st.session_state.fields_to_generate = ["Titolo Prodotto", "Description", "Meta Title", "Meta Description"]
    if 'ean_logs' not in st.session_state:
        st.session_state.ean_logs = []
    if 'use_image_analysis' not in st.session_state:
        st.session_state.use_image_analysis = False
    if 'images_loaded' not in st.session_state:
        st.session_state.images_loaded = False
    if 'image_analysis_db' not in st.session_state:
        st.session_state.image_analysis_db = {}
    if 'images_analyzed' not in st.session_state:
        st.session_state.images_analyzed = False
    if 'product_images_dict' not in st.session_state:
        st.session_state.product_images_dict = {}
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'site_info' not in st.session_state:
        st.session_state.site_info = {}
    if 'ai_configured' not in st.session_state:
        st.session_state.ai_configured = False
    if 'serper_configured' not in st.session_state:
        st.session_state.serper_configured = False
    if 'generator' not in st.session_state:
        st.session_state.generator = ProductCardGenerator()
    if 'preview_index' not in st.session_state:
        st.session_state.preview_index = 0
    # NUOVI per deduplicazione
    if 'unique_products' not in st.session_state:
        st.session_state.unique_products = None
    if 'code_mapping' not in st.session_state:
        st.session_state.code_mapping = {}
    if 'original_csv_data' not in st.session_state:
        st.session_state.original_csv_data = None

def process_batch(generator, batch_data, site_info, column_mapping, additional_instructions, 
                 code_column, start_index, fields_to_generate, ean_column, use_image_analysis):
    """Elabora batch prodotti"""
    batch_results = []
    
    for i, (_, row) in enumerate(batch_data.iterrows()):
        current_index = start_index + i
        
        if code_column:
            raw_code = row[code_column]
            product_code = str(raw_code).strip().strip("'").strip('"')
        else:
            product_code = f"PROD_{current_index+1}"
        
        # ✅ Passa product_data e column_mapping per il filtro semantico
        generated_content = generator.generate_product_content(
            row.to_dict(), site_info, column_mapping, additional_instructions,
            fields_to_generate, ean_column, product_code, use_image_analysis
        )
        
        if generated_content:
            result_row = {'codice_prodotto': product_code}
            
            if "Titolo Prodotto" in fields_to_generate:
                result_row['titolo'] = generated_content.get('titolo', '')
            if "Short Description" in fields_to_generate:
                result_row['short_description'] = generated_content.get('short_description', '')
            if "Description" in fields_to_generate:
                result_row['description'] = generated_content.get('description', '')
            if "Bullet Points" in fields_to_generate:
                bullets = generated_content.get('bullet_points', [])
                result_row['bullet_points'] = ' | '.join(bullets) if isinstance(bullets, list) else bullets
            if "Meta Title" in fields_to_generate:
                result_row['meta_title'] = generated_content.get('meta_title', '')
            if "Meta Description" in fields_to_generate:
                result_row['meta_description'] = generated_content.get('meta_description', '')
            if "URL" in fields_to_generate:
                result_row['url_slug'] = generated_content.get('url_slug', '')
            
            batch_results.append(result_row)
        else:
            result_row = {
                'codice_prodotto': product_code,
                'errore': 'ERRORE - NON GENERATO'
            }
            batch_results.append(result_row)
        
        time.sleep(0.5)
    
    return batch_results

def render_product_preview():
    """Renderizza anteprima scheda prodotto"""
    if not st.session_state.results:
        return
    
    st.markdown('<div class="product-preview">', unsafe_allow_html=True)
    
    # Navigazione
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col1:
        if st.button("◀", key="prev_product", disabled=(st.session_state.preview_index == 0)):
            st.session_state.preview_index = max(0, st.session_state.preview_index - 1)
            st.rerun()
    
    with col2:
        st.markdown(f"<p style='text-align: center; color: #8A8A8A; font-weight: 600;'>Prodotto {st.session_state.preview_index + 1} di {len(st.session_state.results)}</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button("▶", key="next_product", disabled=(st.session_state.preview_index >= len(st.session_state.results) - 1)):
            st.session_state.preview_index = min(len(st.session_state.results) - 1, st.session_state.preview_index + 1)
            st.rerun()
    
    # Dati prodotto
    product = st.session_state.results[st.session_state.preview_index]
    
    # Titolo
    if 'titolo' in product:
        st.markdown(f'<h2 class="product-title-preview">{product["titolo"]}</h2>', unsafe_allow_html=True)
    
    # Codice
    st.markdown(f'<p style="text-align: center; color: #8A8A8A; font-size: 0.9rem; margin-bottom: 2rem;">Codice: <strong>{product["codice_prodotto"]}</strong></p>', unsafe_allow_html=True)
    
    # Short Description
    if 'short_description' in product and product['short_description']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">📝 Short Description</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-field-content">{product["short_description"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Description
    if 'description' in product and product['description']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">📄 Description</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-field-content">{product["description"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bullet Points
    if 'bullet_points' in product and product['bullet_points']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">🎯 Bullet Points</p>', unsafe_allow_html=True)
        bullets = product['bullet_points'].split(' | ') if isinstance(product['bullet_points'], str) else product['bullet_points']
        for bullet in bullets:
            st.markdown(f'<p class="product-field-content">• {bullet}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Meta Title
    if 'meta_title' in product and product['meta_title']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">🔍 Meta Title SEO</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-field-content">{product["meta_title"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Meta Description
    if 'meta_description' in product and product['meta_description']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">🔍 Meta Description SEO</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-field-content">{product["meta_description"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # URL Slug
    if 'url_slug' in product and product['url_slug']:
        st.markdown('<div class="product-meta">', unsafe_allow_html=True)
        st.markdown('<p class="product-field-label">🔗 URL Slug</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-field-content" style="font-family: monospace; background-color: #FFE7E6; padding: 0.5rem; border-radius: 4px;">{product["url_slug"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔴 Moca - Generatore Schede Prodotto</h1>
        <p>Genera schede prodotto professionali con AI, ricerca EAN e analisi immagini</p>
    </div>
    """, unsafe_allow_html=True)
    
    generator = st.session_state.generator
    
    # Progress Indicator
    steps = ["Configurazione AI", "Caricamento Dati", "Mappatura Colonne", "Opzioni Avanzate", "Generazione", "Risultati"]
    
    progress_pct = (st.session_state.current_step / len(steps))
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.progress(progress_pct)
    
    progress_text = f"**Step {st.session_state.current_step} di {len(steps)}:** {steps[st.session_state.current_step - 1]}"
    st.markdown(f"<p style='text-align: center; color: #191919; font-weight: 600; margin-top: 1rem;'>{progress_text}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # STEP 1: Configurazione AI
    if st.session_state.current_step == 1:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('''
        <div class="step-header">
            <div class="step-number">1</div>
            <h2 class="step-title">Configurazione AI</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("Seleziona il provider AI e inserisci le API keys necessarie per iniziare.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ai_provider = st.selectbox(
                "🤖 Provider AI",
                ["OpenAI", "Claude"],
                help="Seleziona quale AI utilizzare per generare i contenuti"
            )
            
            if ai_provider == "OpenAI":
                model_options = {
                    "GPT-4o": "gpt-4o",
                    "GPT-4o Mini": "gpt-4o-mini",
                    "GPT-4 Turbo": "gpt-4-turbo-preview"
                }
            else:
                model_options = {
                    "Claude 4 Sonnet": "claude-sonnet-4-20250514",
                    "Claude 3.7 Sonnet": "claude-3-7-sonnet-20250219",
                    "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022"
                }
            
            selected_model_name = st.selectbox(
                "🔧 Modello",
                list(model_options.keys())
            )
            selected_model = model_options[selected_model_name]
            
            api_key = st.text_input(
                f"🔑 API Key {ai_provider}",
                type="password",
                help=f"Inserisci la tua API Key {ai_provider}"
            )
        
        with col2:
            st.markdown("### 🔍 Serper.dev (Opzionale)")
            st.info("La ricerca EAN permette di arricchire i contenuti con informazioni da Google.")
            
            serper_key = st.text_input(
                "🔑 API Key Serper.dev",
                type="password",
                help="Necessaria solo per la ricerca EAN"
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottone avanti
        if api_key:
            if st.button("➡️ Avanti: Caricamento Dati", type="primary", use_container_width=True):
                with st.spinner("Configurazione AI in corso..."):
                    if generator.setup_ai(ai_provider, api_key, selected_model):
                        st.session_state.ai_configured = True
                        
                        if serper_key:
                            if generator.setup_serper(serper_key):
                                st.session_state.serper_configured = True
                        
                        st.session_state.current_step = 2
                        st.rerun()
                    else:
                        st.error("❌ Configurazione AI fallita. Controlla l'API Key.")
        else:
            st.warning("⚠️ Inserisci almeno l'API Key del provider AI per continuare.")
    
    # STEP 2: Caricamento Dati
    elif st.session_state.current_step == 2:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('''
        <div class="step-header">
            <div class="step-number">2</div>
            <h2 class="step-title">Caricamento Catalogo</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("Carica il file CSV contenente i dati dei prodotti.")
        
        uploaded_file = st.file_uploader(
            "📁 Carica CSV Prodotti",
            type=['csv'],
            help="Il CSV deve contenere almeno una colonna con i codici prodotto"
        )
        
        if uploaded_file is not None:
            try:
                csv_data = pd.read_csv(uploaded_file)
                st.session_state.csv_data = csv_data
                
                st.success(f"✅ CSV caricato con successo! Trovati **{len(csv_data)}** prodotti.")
                
                with st.expander("👀 Anteprima Dati", expanded=True):
                    st.dataframe(csv_data.head(10), use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⬅️ Indietro", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                with col2:
                    if st.button("➡️ Avanti: Mappatura Colonne", type="primary", use_container_width=True):
                        st.session_state.current_step = 3
                        st.rerun()
                
            except Exception as e:
                st.error(f"❌ Errore nel caricamento del CSV: {e}")
        else:
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
    
    # STEP 3: Mappatura Colonne
    elif st.session_state.current_step == 3:
        if st.session_state.csv_data is None:
            st.warning("⚠️ Nessun CSV caricato. Torna allo step 2.")
            if st.button("⬅️ Torna Indietro"):
                st.session_state.current_step = 2
                st.rerun()
            return
        
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('''
        <div class="step-header">
            <div class="step-number">3</div>
            <h2 class="step-title">Mappatura Colonne</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("Associa ogni colonna del CSV a una variabile descrittiva per l'AI.")
        
        suggested_vars = [
            "codice_prodotto", "nome_prodotto", "categoria", "marca",
            "materiale", "colore", "dimensioni", "peso", "prezzo",
            "caratteristiche", "descrizione_breve", "ean"
        ]
        
        column_mapping = {}
        ean_column = None
        
        cols = st.columns(2)
        for i, column in enumerate(st.session_state.csv_data.columns):
            with cols[i % 2]:
                st.markdown(f"**📊 Colonna CSV:** `{column}`")
                example_value = st.session_state.csv_data[column].iloc[0] if not st.session_state.csv_data[column].empty else 'N/A'
                st.caption(f"Esempio: {str(example_value)[:50]}")
                
                var_name = st.selectbox(
                    f"Variabile per '{column}':",
                    [""] + suggested_vars + ["Custom"],
                    key=f"mapping_{i}"
                )
                
                if var_name == "Custom":
                    var_name = st.text_input(
                        f"Nome personalizzato per '{column}':",
                        key=f"custom_{i}"
                    )
                
                if var_name and var_name != "":
                    column_mapping[column] = var_name
                    
                    if var_name.lower() == "ean":
                        ean_column = column
                
                st.markdown("---")
        
        st.session_state.column_mapping = column_mapping
        st.session_state.ean_column = ean_column
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        with col2:
            if column_mapping:
                if st.button("➡️ Avanti: Opzioni Avanzate", type="primary", use_container_width=True):
                    st.session_state.current_step = 4
                    st.rerun()
            else:
                st.warning("⚠️ Mappa almeno una colonna per continuare")
    
    # STEP 4: Opzioni Avanzate
    elif st.session_state.current_step == 4:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('''
        <div class="step-header">
            <div class="step-number">4</div>
            <h2 class="step-title">Configurazione Avanzata</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        # Informazioni Sito
        st.subheader("🌐 Informazioni Sito")
        col1, col2 = st.columns(2)
        
        with col1:
            site_name = st.text_input("Nome del sito:", placeholder="Il Mio Shop")
            site_url = st.text_input("URL del sito:", placeholder="https://ilmioshop.com")
        
        with col2:
            tone_options = {
                "Professionale e formale": "professionale e formale",
                "Amichevole e casual": "amichevole e casual",
                "Tecnico e dettagliato": "tecnico e dettagliato",
                "Moderno e trendy": "moderno e trendy",
                "Personalizzato": "personalizzato"
            }
            
            tone_choice = st.selectbox("Tone of voice:", list(tone_options.keys()))
            
            if tone_choice == "Personalizzato":
                tone_of_voice = st.text_area("Descrivi il tone of voice:")
            else:
                tone_of_voice = tone_options[tone_choice]
        
        additional_instructions = st.text_area(
            "📝 Istruzioni Aggiuntive (opzionale):",
            placeholder="Esempio: Usa emoji, includi materiale nel titolo, max 60 caratteri per titolo"
        )
        
        st.markdown("---")
        
        # Campi da Generare
        st.subheader("📝 Campi da Generare")
        
        all_fields = [
            "Titolo Prodotto",
            "Short Description",
            "Description",
            "Bullet Points",
            "Meta Title",
            "Meta Description",
            "URL"
        ]
        
        selected_fields = st.multiselect(
            "Seleziona i campi da generare:",
            all_fields,
            default=st.session_state.fields_to_generate
        )
        
        st.session_state.fields_to_generate = selected_fields
        
        st.markdown("---")
        
        # Analisi Immagini
        st.subheader("🖼️ Analisi Immagini (Opzionale)")
        
        use_images = st.checkbox(
            "Attiva analisi immagini con AI",
            value=st.session_state.use_image_analysis,
            help="Carica un ZIP con immagini prodotto per arricchire le descrizioni"
        )
        st.session_state.use_image_analysis = use_images
        
        if use_images:
            images_zip = st.file_uploader(
                "📦 Carica ZIP con immagini prodotti",
                type=['zip'],
                help="Nome file = codice prodotto (es: SKU123.jpg)"
            )
            
            if images_zip and not st.session_state.images_loaded:
                with st.spinner("📦 Caricamento immagini..."):
                    images_dict = generator.load_images_from_zip(images_zip)
                    if images_dict:
                        st.session_state.images_loaded = True
                        generator.product_images = images_dict
                        st.success(f"✅ Caricate {sum(len(imgs) for imgs in images_dict.values())} immagini per {len(images_dict)} prodotti")
            
            # Pre-analisi immagini
            if st.session_state.images_loaded and not st.session_state.images_analyzed:
                if st.button("🚀 Avvia Pre-Analisi Immagini", type="secondary"):
                    # Trova codice prodotto
                    code_column = None
                    for csv_col, var_name in st.session_state.column_mapping.items():
                        if any(keyword in var_name.lower() for keyword in ['codice', 'code', 'id', 'sku']):
                            code_column = csv_col
                            break
                    
                    if code_column:
                        product_codes = set(str(code).strip().strip("'").strip('"') for code in st.session_state.csv_data[code_column])
                        image_codes = set(generator.product_images.keys())
                        matches = product_codes & image_codes
                        
                        if matches:
                            normalized_matches = [str(code).strip().strip("'").strip('"') for code in matches]
                            with st.spinner("🔄 Pre-analisi immagini in corso..."):
                                generator.pre_analyze_all_images(normalized_matches)
                                st.success("✅ Pre-analisi completata!")
                        else:
                            st.error("❌ Nessuna corrispondenza tra codici CSV e immagini")
        
        st.markdown("---")
        
        # Configurazione Batch
        st.subheader("⚙️ Impostazioni Elaborazione")
        
        col1, col2 = st.columns(2)
        with col1:
            batch_size = st.slider("Dimensione batch:", 5, 50, st.session_state.batch_size, 5)
            st.session_state.batch_size = batch_size
        
        with col2:
            delay_between_batches = st.slider("Pausa tra batch (secondi):", 1, 10, 3)
        
        st.session_state.site_info = {
            'site_name': site_name,
            'site_url': site_url,
            'tone_of_voice': tone_of_voice
        }
        st.session_state.additional_instructions = additional_instructions
        st.session_state.delay_between_batches = delay_between_batches
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        with col2:
            if site_name and site_url and selected_fields:
                if st.button("➡️ Avanti: Genera Schede", type="primary", use_container_width=True):
                    st.session_state.current_step = 5
                    st.rerun()
            else:
                st.warning("⚠️ Compila tutti i campi obbligatori")
    
    # STEP 5: Generazione
# STEP 5: Generazione
elif st.session_state.current_step == 5:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('''
    <div class="step-header">
        <div class="step-number">5</div>
        <h2 class="step-title">Generazione Schede Prodotto</h2>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.processing_status == 'idle':
        st.markdown("### 🎯 Pronto per generare le schede prodotto!")
        
        # DEDUPLICAZIONE: Trova prodotti unici
        code_column = None
        for csv_col, var_name in st.session_state.column_mapping.items():
            if any(keyword in var_name.lower() for keyword in ['codice', 'code', 'id', 'sku']):
                code_column = csv_col
                break
        
        if code_column:
            unique_products, code_mapping = deduplicate_products(st.session_state.csv_data, code_column)
            st.session_state.unique_products = unique_products
            st.session_state.code_mapping = code_mapping
            st.session_state.original_csv_data = st.session_state.csv_data.copy()
        else:
            st.session_state.unique_products = st.session_state.csv_data
            st.session_state.code_mapping = {}
        
        # Riepilogo configurazione
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"""
        **📊 Riepilogo Configurazione:**
        - 🛍️ Righe totali nel CSV: **{len(st.session_state.csv_data)}**
        - 🎯 Prodotti unici da elaborare: **{len(st.session_state.unique_products)}**
        - 📝 Campi da generare: **{len(st.session_state.fields_to_generate)}**
        - 🤖 AI Provider: **{generator.ai_provider}**
        - 🔍 Ricerca EAN: **{'✅ Attiva' if st.session_state.serper_configured else '❌ Non attiva'}**
        - 🖼️ Analisi Immagini: **{'✅ Attiva' if st.session_state.use_image_analysis else '❌ Non attiva'}**
        - ⚙️ Batch size: **{st.session_state.batch_size}**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
        with col2:
            if st.button("🚀 Avvia Generazione", type="primary", use_container_width=True):
                st.session_state.processing_status = 'processing'
                st.session_state.total_products = len(st.session_state.unique_products)
                st.session_state.current_index = 0
                st.session_state.results = []
                st.rerun()
    
    elif st.session_state.processing_status == 'processing':
        st.markdown("### ⚡ Elaborazione in corso...")
        
        # Progress metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{st.session_state.current_index}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Prodotti Elaborati</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            progress_pct = (st.session_state.current_index / st.session_state.total_products * 100) if st.session_state.total_products > 0 else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{progress_pct:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Completamento</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            remaining = st.session_state.total_products - st.session_state.current_index
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{remaining}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Rimanenti</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.progress(st.session_state.current_index / st.session_state.total_products if st.session_state.total_products > 0 else 0)
        
        # Trova colonna codice
        code_column = None
        for csv_col, var_name in st.session_state.column_mapping.items():
            if any(keyword in var_name.lower() for keyword in ['codice', 'code', 'id']):
                code_column = csv_col
                break
        
        # Elabora batch SUI PRODOTTI UNICI
        start_idx = st.session_state.current_index
        end_idx = min(start_idx + st.session_state.batch_size, len(st.session_state.unique_products))
        
        if start_idx < len(st.session_state.unique_products):
            batch_data = st.session_state.unique_products.iloc[start_idx:end_idx]
            
            with st.spinner(f"Elaborando prodotti unici {start_idx+1}-{end_idx}..."):
                batch_results = process_batch(
                    generator, batch_data, st.session_state.site_info, 
                    st.session_state.column_mapping,
                    st.session_state.additional_instructions, code_column, start_idx,
                    st.session_state.fields_to_generate, 
                    st.session_state.get('ean_column', None) if st.session_state.serper_configured else None,
                    st.session_state.use_image_analysis
                )
                
                st.session_state.results.extend(batch_results)
                st.session_state.current_index = end_idx
            
            if st.session_state.current_index < len(st.session_state.unique_products):
                time.sleep(st.session_state.delay_between_batches)
                st.rerun()
            else:
                # ESPANSIONE: Duplica i risultati per tutte le righe originali
                st.markdown("### 🔄 Espansione risultati a tutte le righe...")
                
                if st.session_state.code_mapping:
                    with st.spinner("Applicando i contenuti generati a tutte le varianti..."):
                        expanded_results = expand_results_to_original(
                            st.session_state.results,
                            st.session_state.code_mapping,
                            st.session_state.original_csv_data,
                            code_column
                        )
                        st.session_state.results = expanded_results
                        st.success(f"✅ Risultati espansi a {len(expanded_results)} righe totali!")
                
                st.session_state.processing_status = 'completed'
                st.session_state.current_step = 6
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # STEP 6: Risultati
    elif st.session_state.current_step == 6:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('''
        <div class="step-header">
            <div class="step-number">6</div>
            <h2 class="step-title">Risultati Finali</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        st.success(f"🎉 Elaborazione completata! **{len(st.session_state.results)}** schede prodotto generate.")
        
        # Statistiche
        st.subheader("📊 Statistiche Generazione")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(st.session_state.results)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Prodotti</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            valid_titles = [r for r in st.session_state.results if r.get('titolo') and r.get('titolo') != 'ERRORE - NON GENERATO']
            avg_title_len = sum(len(str(r.get('titolo', ''))) for r in valid_titles) / len(valid_titles) if valid_titles else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_title_len:.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Lung. Media Titolo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            valid_descs = [r for r in st.session_state.results if r.get('description')]
            avg_desc_len = sum(len(str(r.get('description', ''))) for r in valid_descs) / len(valid_descs) if valid_descs else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_desc_len:.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Lung. Media Desc</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            success_count = len([r for r in st.session_state.results if not r.get('errore')])
            success_rate = (success_count / len(st.session_state.results)) * 100 if st.session_state.results else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{success_rate:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Tasso Successo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Anteprima Schede Prodotto
        st.subheader("👀 Anteprima Schede Prodotto")
        render_product_preview()
        
        st.markdown("---")
        
        # Download
        st.subheader("📥 Download Risultati")
        
        df_results = pd.DataFrame(st.session_state.results)
        csv_buffer = io.StringIO()
        df_results.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_string = csv_buffer.getvalue()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Scarica CSV Completo",
                data=csv_string,
                file_name=f"schede_prodotto_moca_{int(time.time())}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.session_state.ean_logs:
                json_logs = json.dumps(st.session_state.ean_logs, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📊 Scarica Log EAN",
                    data=json_logs,
                    file_name=f"ean_logs_{int(time.time())}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col3:
            if st.button("🔄 Nuova Elaborazione", use_container_width=True):
                # Reset completo
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown("---")
        
        # Tabella completa risultati
        with st.expander("📋 Visualizza Tabella Completa", expanded=False):
            st.dataframe(df_results, use_container_width=True)
        
        # Statistiche EAN se disponibili
        if st.session_state.ean_logs:
            with st.expander("🔍 Statistiche Ricerca EAN", expanded=False):
                total_ean = len(st.session_state.ean_logs)
                successful = len([log for log in st.session_state.ean_logs if log.get('status') == 'success'])
                failed = len([log for log in st.session_state.ean_logs if log.get('status') == 'failed'])
                no_results = len([log for log in st.session_state.ean_logs if log.get('status') == 'no_results'])
                
                total_scraped = sum(log.get('successful_scrapes', 0) for log in st.session_state.ean_logs)
                total_chars = sum(log.get('total_characters', 0) for log in st.session_state.ean_logs)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔍 EAN Processati", total_ean)
                with col2:
                    st.metric("✅ Successi", successful)
                with col3:
                    st.metric("📄 Pagine Estratte", total_scraped)
                with col4:
                    st.metric("📊 Caratteri Totali", f"{total_chars:,}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <p style='color: #8A8A8A; font-size: 0.9rem; margin: 0;'>
            <strong>Moca</strong> - Generatore Schede Prodotto v3.0<br>
            Powered by AI • Ricerca EAN • Analisi Immagini<br>
            © 2025 Daniele Pisciottano
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
