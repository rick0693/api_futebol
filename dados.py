import pandas as pd
import requests
from bs4 import BeautifulSoup
import warnings
import tkinter as tk
from tkinter import ttk

# Desativar as mensagens de aviso
warnings.filterwarnings('ignore')


#site https://www.betexplorer.com/football/argentina/copa-de-la-liga-profesional/


# Mapeamento entre nações e ligas
nations_and_leagues = {
    "mexico": "liga-mx",
    "nicaragua": "liga-primera",
    "argentina": "liga-mx",
    "mexico": "liga-mx",
    "mexico": "liga-mx",
    "mexico": "liga-mx",
    "mexico": "liga-mx",
    "mexico": "liga-mx",
    "mexico": "liga-mx",
    

}

# Função para extrair as odds ou texto de uma célula
def get_odd_or_text(td):
    if "data-odd" in td.attrs:
        return td["data-odd"]

    odd = td.select_one("[data-odd]")
    if odd:
        return odd["data-odd"]

    return td.get_text(strip=True)

# Função para coletar os dados com base na nação e na liga selecionadas
def collect_data():
    nation = nation_var.get()
    league = league_var.get()
    
    # Verificar se a nação e liga estão no mapeamento
    if nation in nations_and_leagues and league in nations_and_leagues.values():
        url = f"https://www.betexplorer.com/football/{nation}/{league}/results/"
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        
        # Coletar os dados da tabela
        all_data = []
        for row in soup.select(".table-main tr:has(td)"):
            tds = [get_odd_or_text(td) for td in row.select("td")]
            round_ = row.find_previous("th").find_previous("tr").th.text
            all_data.append([round_, *tds])
            
            
        # Criar um DataFrame pandas com os dados coletados
        df = pd.DataFrame(all_data, columns=["Rodada", "Partida", "Placar", "Odd_H", "Odd_D", "Odd_A", "Date"])
        df['League'] = league
        
        # Dividir a coluna "Partida" em "Casa" e "Fora"
        df['Home'] = [i.split('-')[0] for i in df['Partida']]
        df['Away'] = [i.split('-')[1] for i in df['Partida']]
        
        df = df.iloc[::-1]
        
        df['Goals_H'] = [i.split(':', 1)[0] if ':' in i else '' for i in df['Placar']]
        df['Goals_A'] = [i.split(':', 1)[1] if (':' in i) and (len(i.split(':', 1)) > 1) else '' for i in df['Placar']]
        
        # Função para determinar o resultado (H, D, A)
        def Result(df):
            if df['Goals_H'] > df['Goals_A']:
                return "Vitoria Casa"
            if df['Goals_H'] == df['Goals_A']:
                return "emprate"
            if df['Goals_H'] < df['Goals_A']:
                return "Vitoria fora"
        
        df['Result'] = df.apply(Result, axis=1)
        
        # Substituir nomes das rodadas (1. Round, 2. Round, etc.) por números (1, 2, etc.)
        for i in range(38):
            i = i + 1
            df.replace(str(i) + ". Round", i, inplace=True)
        
        df.reset_index(inplace=True, drop=True)
        df.index = df.index.set_names(['Nº'])
        df = df.rename(index=lambda x: x + 1)
        
        df.drop(['Partida', 'Placar'], axis=1, inplace=True)
        df = df[['League', 'Date', 'Rodada', 'Home', 'Away', 'Odd_H', 'Odd_D', 'Odd_A', 'Goals_H', 'Goals_A', 'Result']]
        
        # Exiba os dados em uma nova janela
        print(df)
    else:
        print("Nação ou liga selecionada não encontrada no mapeamento.")
    df.to_excel(league+"_"+str(nation)+"-"+str(league)+".xlsx")
# Função para exibir os dados em uma interface gráfica tkinter
def display_data(data_frame):
    window = tk.Toplevel()
    window.title(f"Resultados da {league_var.get()} - {nation_var.get()}")
    
    # Crie uma Treeview para exibir os dados em uma tabela
    tree = ttk.Treeview(window, columns=list(data_frame.columns), show="headings")
    
    # Defina os cabeçalhos das colunas
    for col in data_frame.columns:
        tree.heading(col, text=col)
    
    # Adicione os dados ao Treeview
    for i, row in data_frame.iterrows():
        tree.insert("", "end", values=list(row))
    
    # Adicione uma barra de rolagem para navegar pelos dados
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Coloque o Treeview e a barra de rolagem na janela
    tree.pack(fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Crie a janela principal
root = tk.Tk()
root.title("Selecionar Nação e Liga")

# Lista suspensa para selecionar a nação
nations = list(nations_and_leagues.keys())
nation_var = tk.StringVar()
nation_var.set(nations[0])  # Valor padrão
nation_label = ttk.Label(root, text="Selecione a Nação:")
nation_label.pack()
nation_dropdown = ttk.Combobox(root, textvariable=nation_var, values=nations)
nation_dropdown.pack()

# Lista suspensa para selecionar a liga
leagues = list(nations_and_leagues.values())
league_var = tk.StringVar()
league_var.set(leagues[0])  # Valor padrão
league_label = ttk.Label(root, text="Selecione a Liga:")
league_label.pack()
league_dropdown = ttk.Combobox(root, textvariable=league_var, values=leagues)
league_dropdown.pack()

# Botão para coletar dados
collect_button = ttk.Button(root, text="Coletar Dados", command=collect_data)
collect_button.pack()

# Iniciar a interface gráfica
root.mainloop()
