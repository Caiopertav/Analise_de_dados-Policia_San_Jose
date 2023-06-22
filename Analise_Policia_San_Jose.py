import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot, iplot

#Carregando tabela de prisões
arquivo = 'Arrests_All.csv'
arrests = pd.read_csv(arquivo, sep=',' ,header=0)

# Carregando tabela Acusações 
arquivo2 = 'Charges_All.csv'
charges = pd.read_csv(arquivo2, sep=',' ,header=0)
# Carregando tabela incidente de prisão
arquivo3 = 'Incidents_All.csv'
incidents = pd.read_csv(arquivo3, sep=',' ,header=0)
# Carregando tabela raça codigo e grupo
arquivo4 = 'Race_Codes.csv'
racecode = pd.read_csv(arquivo4, sep=',' ,header=0)

arquivo5 = 'Race_Groups.csv'
racegroup = pd.read_csv(arquivo5, sep=',' ,header=0)

#Gerando numero de incidente através do slicing do GO no
arrests['INCIDENT NO']=arrests['GO NO'].str.slice(6, 15)

#mudando tipo de dados da coluna para tornar tabela mais leve
arrests['PIN']=arrests['PIN'].astype('object')
arrests['RACE']=arrests['RACE'].astype('category')
arrests['SEX']=arrests['SEX'].astype('category')
arrests['ETHNICITY']=arrests['ETHNICITY'].astype('category')
arrests['YOUNG OFFENDER']=arrests['YOUNG OFFENDER'].astype('category')

#visualizando tabela e gerando "INCIDENT NO"
charges['INCIDENT NO']=charges['GO NO'].str.slice(6, 15)
charges.head()

#Retirando as duplicatas identicas, porém ainda há problema do duplo cadastro para acrescentar mais informações
charges=charges.drop_duplicates()
#retirando as duplicatas por mandato emitido
charges.drop(charges[charges["INCIDENT NO"]=="WARRANT C"].index ,inplace=True)

incidents['INCIDENT NO']=incidents['INCIDENT NO'].astype('object')

#Retirando duplicadas identicas nas ocorrencias
incidents=incidents.drop_duplicates()

incidents.dropna(subset=["BLOCK ADDRESS"],inplace=True)


# 1) Qual o crime com mais quantidade de ocorrências? Se houver empate em valor, trazer todos da primeira posição.
colorx=['#00af97','#00af97','#00af97','#00af97','#00af97']


graph1=charges['STATUTE'].value_counts().head(5).reset_index()
graph1.columns = ['STATUTE', 'COUNT']
graph1=graph1.sort_values(by="COUNT", ascending=True)

#grafico1 por estatuto violado
data1=go.Bar(y=graph1['STATUTE'].head(5), x=graph1['COUNT'], orientation='h',
                        textposition='auto', text=graph1['COUNT'], texttemplate='%{text:.2s}',
                        insidetextfont=dict(family='Times', size=12), marker=dict(color = colorx),showlegend=False)

fig1 = go.Figure(data=data1)


#grafico por crime cometido
graph2=charges['CHARGE DESCRIPTION'].value_counts().head(5).reset_index()
graph2.columns = ['CHARGE', 'COUNT']
graph2=graph2.sort_values(by="COUNT", ascending=True)

data2=go.Bar(y=graph2['CHARGE'].head(5), x=graph2['COUNT'], orientation='h',
                        textposition='auto', text=graph2['COUNT'], texttemplate='%{text:.2s}',
                        insidetextfont=dict(family='Times', size=12), marker=dict(color = colorx),showlegend=False)

fig2 = go.Figure(data=data2)


# 2) Qual o crime com mais quantidade por bairro/região? Se houver empate em valor, trazer todos da primeira posição.

df=pd.merge(arrests[['PIN','GO NO','AGE','SEX','RACE','ETHNICITY','ARREST DATE',
                         'ARREST TIME','ARREST LOCATION','ARREST OFFICER NAME']],
                          charges[['GO NO','PIN','STATUTE','CLASS','CHARGE DESCRIPTION',]],
                         on=['GO NO','PIN'], how="left")
#retirar linhas onde não houve preenchimento da localização
df.dropna(subset=["ARREST LOCATION"],inplace=True)
#Retirar linhas onde não há determinada localização de crime
df.drop(df[df["ARREST LOCATION"]=="NO LOCATION INCLUDED IN RECORD"].index ,inplace=True)
#LIMPANDO LINHAS DUPLICADAS IDENTICAS
df=df.drop_duplicates()
#Retirando as com etnia e raça não preenchidas, pois geralmente geral um duplicada sem apenas essa informção
df.dropna(subset=["ETHNICITY","RACE"],inplace=True)

#grafico local de crime por crime mais cometido
graph4=df.pivot_table('PIN',index=['ARREST LOCATION',"CHARGE DESCRIPTION"], aggfunc='count',margins=True)
graph4=graph4.sort_values(by='PIN', ascending=False)
graph4=graph4.head(6)
graph4=graph4['PIN'].reset_index()
graph4=graph4.drop(0)

data4=go.Bar(y=graph4['ARREST LOCATION']+'<br>'+graph4['CHARGE DESCRIPTION'], x=graph4['PIN'], orientation='h',
                        textposition='auto', text=graph4['PIN'], texttemplate='%{text:.2s}',
                        insidetextfont=dict(family='Times', size=12), marker=dict(color = colorx),showlegend=False)

fig4 = go.Figure(data=data4)



#3) Quais os 5 policiais que realizaram mais prisões?

df2=pd.merge(arrests[['PIN','GO NO','AGE','SEX','RACE','ETHNICITY','ARREST DATE',
                         'ARREST TIME','ARREST LOCATION','ARREST OFFICER NAME']],
                          charges[['GO NO','PIN','STATUTE','CLASS','CHARGE DESCRIPTION',]],
                         on=['GO NO','PIN'], how="left")

#retirando linhas onde não houve preenchimento do policial responsável
df2.dropna(subset=["ARREST OFFICER NAME"],inplace=True)

#LIMPANDO LINHAS DUPLICADAS IDENTICAS
df2=df2.drop_duplicates()
#Retirando as com etnia e raça não preenchidas, pois geralmente geral um duplicada sem apenas essa informção
df2.dropna(subset=["ETHNICITY","RACE"],inplace=True)


graph5=df2.pivot_table('PIN',index=["ARREST OFFICER NAME"], aggfunc='count')
graph5=graph5.sort_values(by='PIN', ascending=False).head(5).reset_index().sort_values(by='PIN', ascending=True)

data5=go.Bar(y=graph5['ARREST OFFICER NAME'], x=graph5['PIN'], orientation='h',
                        textposition='auto', text=graph5['PIN'], texttemplate='%{text:.2s}',
                        insidetextfont=dict(family='Times', size=12), marker=dict(color = colorx),showlegend=False)

fig5 = go.Figure(data=data5)



#4) Qual a média, mediana e desvio padrão das prisões realizadas entre 2015 e 2020?
# Carregando tabela prisões realizadas entre 2015 e 2020 
arquivo6 = 'Arrests_2015-2020.csv'
arrests2020 = pd.read_csv(arquivo6, sep=',' ,header=0)

#mudando tipo de dados da coluna para tornar tabela mais leve
arrests2020['PIN']=arrests2020['PIN'].astype('object')
arrests2020['RACE']=arrests2020['RACE'].astype('category')
arrests2020['SEX']=arrests2020['SEX'].astype('category')
arrests2020['ETHNICITY']=arrests2020['ETHNICITY'].astype('category')
arrests2020['YOUNG OFFENDER']=arrests2020['YOUNG OFFENDER'].astype('category')

#LIMPANDO LINHAS DUPLICADAS IDENTICAS
arrests2020=arrests2020.drop_duplicates()
#Retirando as com etnia e raça não preenchidas, pois geralmente geral um duplicada sem apenas essa informção
arrests2020.dropna(subset=["ETHNICITY","RACE"],inplace=True)
#Retirando com esse campo nulo, pois acontece o mesmo fenomeno anterior
arrests2020.dropna(subset=["YOUNG OFFENDER"],inplace=True)

graph6=arrests2020.describe()
graph6['AGE']=round(graph6['AGE'],0)
graph6['ARREST TIME']=round(graph6['ARREST TIME'],0)
graph6=graph6.drop('count')

data6=go.Table(
        header=dict(values=["","Idade","Tempo de prisão (dias)"],
            font=dict(size=10), fill_color='#00af97',
            align="left"),
        cells=dict(
            values=[graph6.index,graph6['AGE'],graph6['ARREST TIME']],
            align = "left"))


#5) Qual a porcentagem por gênero entre os presos?

graph7=arrests2020["SEX"].value_counts().reset_index().drop(2)

data7=go.Pie(labels=graph7['index'] , values=graph7['SEX'], hole=.6,marker=dict(colors=['#00af97','D3D3D3']))



#6) Qual a etnia dos presos, em ordem decrescente?

dfrace=pd.merge(df[['PIN','AGE','SEX','RACE','ETHNICITY','ARREST DATE',
                         'ARREST TIME','ARREST LOCATION','ARREST OFFICER NAME']],
                          racecode[['CODE','RACE']],
                         left_on='RACE', right_on='CODE', how="left")

#LIMPANDO LINHAS DUPLICADAS IDENTICAS
dfrace=dfrace.drop_duplicates()
#Retirando as com etnia e raça não preenchidas, pois geralmente geral um duplicada sem apenas essa informção
dfrace.dropna(subset=["ETHNICITY"],inplace=True)

graph8=dfrace.pivot_table('PIN',index=["RACE_y"], aggfunc='count')
graph8=graph8.sort_values(by='PIN', ascending=False)
graph8=graph8.head(5).reset_index().sort_values(by='PIN', ascending=True)




data8=go.Bar(y=graph8['RACE_y'], x=graph8['PIN'], orientation='h',
                        textposition='auto', text=graph8['PIN'], texttemplate='%{text:.2s}',
                        insidetextfont=dict(family='Times', size=12), marker=dict(color = colorx),showlegend=False)


#7) Em percentual, quantos incidentes ocorreram entre as 18h e 6h?

horapico=df[(df['ARREST TIME']>=600)&(df['ARREST TIME']<=1800)]

horavazia=df[(df['ARREST TIME']<=600)|(df['ARREST TIME']>=1800)]

graph9=[["Crimes entre 18h e 6h","Outros"],[len(horapico),len(horavazia)]]
data9=go.Pie(labels=graph9[0] , values=graph9[1], hole=.6,marker=dict(colors=['#00af97','D3D3D3']))



#gerando Dashboard com subplots

margin=dict(l=5, r=120, t=60, b=0)
fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=("Statutos mais violados", "Crimes entre 18h e 6h", "Violações cometidas por etinia", "Crimes por genero",
                    "Dados estatisticos","","Numero de prisões por policial","8"),
     column_widths=[0.5, 0.5],
    specs=[[{}, {"type": "domain"}],
           [ {}, {"type": "domain"}],
           [{"type": "domain","colspan": 2}, {}],
           [{}, {}]
          ])
    

fig.add_trace(data1,
              row=1, col=1)

fig.add_trace(data9,
              row=1, col=2)

fig.add_trace(data8,
              row=2, col=1)

fig.add_trace(data7,
              row=2, col=2)

fig.add_trace(data6,
              row=3, col=1)

fig.add_trace(data5,
              row=4, col=1)

fig.update_layout(height=1200, width=1000,margin=margin,
                  title_text="Analise Database Policia San Jose")

fig.show()